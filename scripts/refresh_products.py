#!/usr/bin/env python3
"""Maintenance mensuelle : vérifie que chaque ASIN existe encore sur Amazon
via l'endpoint structuré ScraperAPI + rafraîchit stars/avis. Marque les morts."""
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
KEY = os.environ.get("SCRAPER_API_KEY")
GUIDES = ROOT / "src/content/guides"
DEALS = ROOT / "src/data/deals.json"


def check_asin(asin: str) -> dict | None:
    """Retourne {stars, avis} si le produit existe encore, sinon None."""
    url = (
        "https://api.scraperapi.com/structured/amazon/search"
        f"?api_key={KEY}&query={asin}&country=fr"
    )
    try:
        r = requests.get(url, timeout=60)
        if r.status_code != 200:
            return None
        for p in r.json().get("results", []):
            if p.get("asin") == asin:
                return {"stars": p.get("stars"), "avis": p.get("total_reviews")}
        return {} if r.json().get("results") else None
    except Exception:
        return None


def main() -> int:
    if not KEY:
        print("SCRAPER_API_KEY absent : skip.")
        return 0
    updated, dead = 0, []

    for f in sorted(GUIDES.glob("*.mdx")):
        txt = f.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.S)
        if not m:
            continue
        fm, body = yaml.safe_load(m.group(1)), m.group(2)
        changed = False
        for p in fm.get("products") or []:
            asin = p.get("asin")
            if not asin:
                continue
            res = check_asin(asin)
            if res is None or res == {}:
                dead.append((f.name, p["nom"], asin))
                continue
            if res.get("stars") and p.get("stars") != res["stars"]:
                p["stars"], p["avis"] = res["stars"], res.get("avis")
                changed, updated = True, updated + 1
        if changed:
            f.write_text(
                "---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False) + "---\n" + body,
                encoding="utf-8",
            )

    if DEALS.exists():
        deals = json.loads(DEALS.read_text())
        ch = False
        for d in deals:
            if not d.get("asin"):
                continue
            res = check_asin(d["asin"])
            if res is None or res == {}:
                dead.append(("deals.json", d["nom"], d["asin"]))
                continue
            if res.get("stars") and d.get("stars") != res["stars"]:
                d["stars"], d["avis"] = res["stars"], res.get("avis")
                ch, updated = True, updated + 1
        if ch:
            DEALS.write_text(json.dumps(deals, ensure_ascii=False, indent=2) + "\n")

    print(f"{updated} produits maj")
    if dead:
        print("ASINs morts/introuvables :")
        for src, nom, asin in dead:
            print(f"  - {src} : {nom} ({asin})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

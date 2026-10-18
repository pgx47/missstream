#!/usr/bin/env python3
"""Régénère dupes.json / packs.json / lookbook.json via DeepSeek à partir du
catalogue produits réel (guides + deals). ASINs strictement issus du catalogue."""
import json
import os
import re
import sys
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ROOT / "src/content/guides"
DEALS = ROOT / "src/data/deals.json"
LLM_KEY = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
LLM_BASE = os.environ.get("LLM_BASE_URL") or "https://api.deepseek.com/v1"
MODEL = os.environ.get("LLM_MODEL") or "deepseek-flash"


def catalog() -> list[dict]:
    prods = []
    for f in sorted(GUIDES.glob("*.mdx")):
        m = re.match(r"^---\n(.*?)\n---", f.read_text(encoding="utf-8"), re.S)
        if not m:
            continue
        fm = yaml.safe_load(m.group(1))
        for p in fm.get("products") or []:
            if p.get("asin"):
                prods.append({"nom": p["nom"], "asin": p["asin"], "cat": fm.get("category")})
    if DEALS.exists():
        for d in json.loads(DEALS.read_text()):
            if d.get("asin"):
                prods.append({"nom": d["nom"], "asin": d["asin"], "cat": d.get("categorie")})
    return prods


def ask(prompt: str) -> list | dict | None:
    from openai import OpenAI

    client = OpenAI(api_key=LLM_KEY, base_url=LLM_BASE)
    r = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Réponds uniquement en JSON valide, sans markdown."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    txt = r.choices[0].message.content.strip().strip("`").lstrip("json").strip()
    try:
        return json.loads(txt)
    except Exception:
        return None


def main() -> int:
    if not LLM_KEY:
        print("LLM_KEY absent : skip.")
        return 0
    prods = catalog()
    if len(prods) < 6:
        print("Catalogue trop pauvre : skip.")
        return 0
    cat = json.dumps(prods, ensure_ascii=False)

    packs = ask(
        f"Catalogue produits : {cat}\n\n"
        "Crée 3 packs setup par budget (debutante~150€, creator~400€, studio~900€) "
        "en choisissant UNIQUEMENT des produits du catalogue (garde nom + asin exacts). "
        "Format JSON : [{id, nom, budget, accroche, items:[{nom, asin}]}]. 3 à 5 items par pack."
    )
    if packs:
        (ROOT / "src/data/packs.json").write_text(json.dumps(packs, ensure_ascii=False, indent=2) + "\n")
        print("packs.json régénéré")

    dupes = ask(
        f"Catalogue produits : {cat}\n\n"
        "Trouve 5 paires original-cher / dupe-abordable avec des produits du catalogue "
        "(mêmes asins). Format : [{titre, original:{nom,prix,asin}, dupe:{nom,prix,asin}, gain}]."
    )
    if dupes:
        (ROOT / "src/data/dupes.json").write_text(json.dumps(dupes, ensure_ascii=False, indent=2) + "\n")
        print("dupes.json régénéré")

    lookbook = ask(
        f"Catalogue produits : {cat}\n\n"
        "Propose 6 ambiances de setup (titre, description 1 phrase, 3 produits du catalogue "
        "avec nom + asin exacts). Format : [{titre, description, produits:[{nom, asin}]}]."
    )
    if lookbook:
        # conserver les images existantes en mappant par titre approximatif
        old = {}
        lf = ROOT / "src/data/lookbook.json"
        if lf.exists():
            for a in json.loads(lf.read_text()):
                old[a["titre"].lower()[:12]] = a.get("image")
        imgs = ["pink-white", "minimal", "neon", "podcast", "cat", "chair"]
        for i, a in enumerate(lookbook):
            a["image"] = old.get(a["titre"].lower()[:12]) or f"/images/lookbook/{imgs[i % 6]}.webp"
        lf.write_text(json.dumps(lookbook, ensure_ascii=False, indent=2) + "\n")
        print("lookbook.json régénéré")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Actualise src/data/deals.json en scrapant Amazon via ScraperAPI (TOS-safe).

- Aucun prix figé n'est stocké : seulement nom, ASIN, catégorie, badge promo.
- Sans SCRAPER_API_KEY, le fichier existant est conservé (exit 0).
"""

import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DEALS_FILE = ROOT / "src/data/deals.json"
SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")
AMAZON_TAG = os.environ.get("AMAZON_TAG", "duckurbate-21")

SEARCHES = [
    ("micro streaming rose blanc USB", "Micros"),
    ("casque gaming oreilles chat rose", "Casques"),
    ("chaise gaming rose pastel", "Chaises"),
    ("clavier mécanique pastel blanc", "Claviers"),
    ("ring light streaming", "Éclairage"),
    ("webcam 4k streaming", "Webcams"),
    ("bras micro blanc", "Accessoires"),
    ("tapis souris XXL pastel", "Accessoires"),
]

MAX_DEALS = 12


def scrape_search(query: str, categorie: str) -> list[dict]:
    url = f"https://www.amazon.fr/s?k={urllib.parse.quote(query)}"
    api = (
        "https://api.scraperapi.com?api_key="
        f"{SCRAPER_API_KEY}&url={urllib.parse.quote(url)}&country_code=fr"
    )
    r = requests.get(api, timeout=60)
    if r.status_code != 200:
        print(f"  HTTP {r.status_code} pour '{query}'")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    deals = []
    for item in soup.select("div[data-asin][data-component-type='s-search-result']"):
        asin = item.get("data-asin", "").strip()
        title_el = item.select_one("h2 span") or item.select_one("h2")
        if not asin or not title_el:
            continue
        nom = re.sub(r"\s+", " ", title_el.get_text()).strip()
        if len(nom) < 8:
            continue

        has_coupon = bool(item.select_one(".s-coupon-highlight-color")) or (
            "coupon" in item.get_text().lower()
        )
        deals.append(
            {
                "asin": asin,
                "nom": nom[:110],
                "categorie": categorie,
                "badge": "Promo en cours" if has_coupon else "Bien noté",
                "note": None,
            }
        )
        if len(deals) >= 3:
            break
    return deals


def main() -> int:
    if not SCRAPER_API_KEY:
        print("SCRAPER_API_KEY absent : deals.json conservé tel quel.")
        return 0

    seen, all_deals = set(), []
    for query, categorie in SEARCHES:
        print(f"Recherche : {query}")
        try:
            for d in scrape_search(query, categorie):
                if d["asin"] not in seen:
                    seen.add(d["asin"])
                    all_deals.append(d)
        except Exception as e:
            print(f"  Erreur '{query}' : {e}")
        if len(all_deals) >= MAX_DEALS:
            break

    if not all_deals:
        print("Aucun deal récupéré : deals.json inchangé.")
        return 0

    deals = [d for d in all_deals if d["badge"] == "Promo en cours"] or all_deals
    DEALS_FILE.write_text(
        json.dumps(deals[:MAX_DEALS], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(deals[:MAX_DEALS])} deals écrits dans {DEALS_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

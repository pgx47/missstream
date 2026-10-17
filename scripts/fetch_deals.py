#!/usr/bin/env python3
"""Actualise src/data/deals.json via l'endpoint structuré ScraperAPI/Amazon.

- Vrais ASINs + vraies images produits (téléchargées en local, WebP).
- Aucun prix figé stocké : badge "Promo en cours" seulement si Amazon le signale.
- Sans SCRAPER_API_KEY : fichier conservé tel quel (exit 0).
"""

import io
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DEALS_FILE = ROOT / "src/data/deals.json"
IMG_DIR = ROOT / "public/images/deals/products"
SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")

SEARCHES = [
    ("micro streaming rose blanc USB", "Micros"),
    ("casque gaming oreilles chat rose", "Casques"),
    ("chaise gaming rose pastel", "Chaises"),
    ("clavier mécanique pastel blanc", "Claviers"),
    ("ring light streaming", "Éclairage"),
    ("webcam 4k streaming", "Webcams"),
    ("bras micro blanc", "Accessoires"),
    ("tapis souris XXL pastel", "Accessoires"),
    ("stream deck blanc", "Stream Deck"),
    ("carte acquisition hdmi stream", "Capture"),
]

MAX_DEALS = 20

CATEGORY_IMAGES = {
    "Micros": "/images/deals/micros.webp",
    "Casques": "/images/deals/casques.webp",
    "Chaises": "/images/deals/chaises.webp",
    "Claviers": "/images/deals/claviers.webp",
    "Éclairage": "/images/deals/eclairage.webp",
    "Webcams": "/images/deals/webcams.webp",
    "Accessoires": "/images/deals/accessoires.webp",
    "Bureaux": "/images/deals/bureaux.webp",
    "Stream Deck": "/images/deals/stream-deck.webp",
    "Capture": "/images/deals/capture.webp",
}


def amazon_search(query: str) -> list[dict]:
    """Recherche Amazon via l'API structurée ScraperAPI."""
    url = (
        "https://api.scraperapi.com/structured/amazon/search"
        f"?api_key={SCRAPER_API_KEY}&query={urllib.parse.quote(query)}&country=fr"
    )
    r = requests.get(url, timeout=60)
    if r.status_code != 200:
        print(f"  HTTP {r.status_code} pour '{query}'")
        return []
    return r.json().get("results", [])


def download_image(url: str, asin: str) -> str | None:
    """Image produit Amazon -> public/images/deals/products/{asin}.webp"""
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    out = IMG_DIR / f"{asin}.webp"
    if out.exists():
        return f"/images/deals/products/{asin}.webp"
    try:
        raw = requests.get(url, timeout=30).content
        from PIL import Image

        img = Image.open(io.BytesIO(raw)).convert("RGB")
        img.thumbnail((800, 800))
        img.save(out, "WEBP", quality=80)
        return f"/images/deals/products/{asin}.webp"
    except Exception as e:
        print(f"  image KO {asin} : {e}")
        return None


def result_to_deal(p: dict, categorie: str) -> dict | None:
    asin = (p.get("asin") or "").strip()
    nom = re.sub(r"\s+", " ", p.get("name") or "").strip()
    if not asin or len(nom) < 8:
        return None
    if p.get("is_limited_deal"):
        badge = "Promo en cours"
    elif p.get("is_best_seller"):
        badge = "Best-seller"
    else:
        badge = "Bien noté"
    image = download_image(p["image"], asin) if p.get("image") else None
    return {
        "asin": asin,
        "nom": nom[:110],
        "categorie": categorie,
        "badge": badge,
        "note": None,
        "image": image or CATEGORY_IMAGES.get(categorie),
    }


def main() -> int:
    if not SCRAPER_API_KEY:
        print("SCRAPER_API_KEY absent : deals.json conservé tel quel.")
        return 0

    seen, all_deals = set(), []
    for query, categorie in SEARCHES:
        print(f"Recherche : {query}")
        try:
            for p in amazon_search(query):
                d = result_to_deal(p, categorie)
                if d and d["asin"] not in seen:
                    seen.add(d["asin"])
                    all_deals.append(d)
        except Exception as e:
            print(f"  Erreur '{query}' : {e}")
        if len(all_deals) >= MAX_DEALS:
            break

    if not all_deals:
        print("Aucun deal récupéré : deals.json inchangé.")
        return 0

    promos = [d for d in all_deals if d["badge"] == "Promo en cours"]
    deals = (promos + [d for d in all_deals if d["badge"] != "Promo en cours"])[:MAX_DEALS]
    DEALS_FILE.write_text(
        json.dumps(deals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{len(deals)} deals écrits dans {DEALS_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

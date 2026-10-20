#!/usr/bin/env python3
"""Ajoute automatiquement de nouveaux profils streamers/créatrices dans
src/data/streamers.json : DeepSeek propose les profils + le setup, ScraperAPI
enrichit ASINs/images, unavatar récupère l'avatar Twitch/Twitter."""
import io
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

import requests
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src/data/streamers.json"
IMG_S = ROOT / "public/images/streamers"
IMG_P = ROOT / "public/images/products"
SKEY = os.environ.get("SCRAPER_API_KEY")
LLM_KEY = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
LLM_BASE = os.environ.get("LLM_BASE_URL") or "https://api.deepseek.com/v1"
MODEL = os.environ.get("LLM_MODEL") or "deepseek-flash"
MAX_NEW = int(os.environ.get("MAX_NEW", 3))


def ask(prompt: str, max_tokens: int = 3000):
    from openai import OpenAI

    client = OpenAI(api_key=LLM_KEY, base_url=LLM_BASE)
    r = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Réponds uniquement en JSON valide, sans markdown."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
        max_tokens=max_tokens,
    )
    txt = r.choices[0].message.content.strip().strip("`").lstrip("json").strip()
    return json.loads(txt)


def avatar(slug: str, handle: str) -> str | None:
    for src in (f"twitch/{handle}", f"twitter/{handle}", f"instagram/{handle}"):
        try:
            r = requests.get(f"https://unavatar.io/{src}", timeout=20)
            if len(r.content) > 5000:
                img = Image.open(io.BytesIO(r.content)).convert("RGB")
                img.thumbnail((400, 400))
                IMG_S.mkdir(parents=True, exist_ok=True)
                img.save(IMG_S / f"{slug}.webp", "WEBP", quality=85)
                return f"/images/streamers/{slug}.webp"
        except Exception:
            continue
    return None


def enrich_product(p: dict) -> None:
    """Nom de produit -> asin + image réelle via ScraperAPI."""
    if not SKEY or p.get("asin"):
        return
    try:
        r = requests.get(
            f"https://api.scraperapi.com/structured/amazon/search?api_key={SKEY}&query={urllib.parse.quote(p['nom'])}&country=fr",
            timeout=60,
        )
        res = r.json().get("results", [])
        if not res:
            return
        h = res[0]
        asin = (h.get("asin") or "").strip()
        if not asin:
            return
        p["asin"] = asin
        p.pop("query", None)
        if h.get("image"):
            IMG_P.mkdir(parents=True, exist_ok=True)
            out = IMG_P / f"{asin}.webp"
            if not out.exists():
                img = Image.open(io.BytesIO(requests.get(h["image"], timeout=30).content)).convert("RGB")
                img.thumbnail((600, 600))
                img.save(out, "WEBP", quality=80)
    except Exception:
        pass


def main() -> int:
    if not LLM_KEY:
        print("LLM_KEY absent : skip.")
        return 0
    streamers = json.loads(DATA.read_text())
    existing = {s["slug"] for s in streamers}
    names = ", ".join(s["nom"] for s in streamers)

    try:
        sugg = ask(
            f"Liste de streamers déjà présents : {names}.\n"
            "Propose 3 streamers ou créatrices de contenu français(e)s pertinents pour un site "
            "de setups cozy/pastel/streaming (priorité créatrices et profils esport connus). "
            "Ne propose PAS de profil déjà présent.\n"
            'Format : [{"slug":"prenom","nom":"Nom","twitch":"handle twitch","jeu":"jeu principal"},...]'
        )
    except Exception as e:
        print(f"LLM KO : {e}")
        return 0

    added = 0
    for cand in (sugg or [])[:MAX_NEW]:
        slug = re.sub(r"[^a-z0-9-]", "", cand.get("slug", "").lower())
        if not slug or slug in existing:
            continue
        handle = cand.get("twitch") or slug
        try:
            profile = ask(
                f"Streamer/créatrice : {cand['nom']} (jeu principal : {cand.get('jeu','variété')}, twitch : {handle}).\n"
                "Génère l'objet JSON complet :\n"
                "- bio : 1 phrase courte\n"
                "- description_longue : ~80 mots sur son style/setup\n"
                "- biographie_longue : ~300 mots en 2 paragraphes (parcours puis analyse du setup)\n"
                "- jeu_principal : jeu/format court\n"
                "- setup : 4-5 objets {cat (Audio|Périphériques|PC & Image|Éclairage), nom (produit réel exact), "
                "avis (1 phrase honnête)} — matériel réel qu'iel utilise ou du même segment\n"
                "Format : un seul objet JSON."
            )
            items = profile.get("setup", [])
            for p in items:
                enrich_product(p)
            streamers.append({
                "slug": slug,
                "nom": cand["nom"],
                "bio": profile.get("bio", ""),
                "description_longue": profile.get("description_longue", ""),
                "biographie_longue": profile.get("biographie_longue", ""),
                "jeu_principal": profile.get("jeu_principal") or cand.get("jeu", ""),
                "image": avatar(slug, handle) or "/images/streamers/gotaga.webp",
                "reseaux": {"twitch": handle},
                "setup": items,
            })
            existing.add(slug)
            added += 1
            print(f"+ {cand['nom']} ({slug}) — {len(items)} produits")
        except Exception as e:
            print(f"skip {cand.get('nom')} : {e}")

    if added:
        DATA.write_text(json.dumps(streamers, ensure_ascii=False, indent=2) + "\n")
    print(f"{added} profil(s) ajouté(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

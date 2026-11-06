#!/usr/bin/env python3
"""Veille RSS Google News -> brèves MDX pour la section Actualités de missstream.xyz.

Image : og:image de la source via ScraperAPI -> Unsplash -> pool local.
Publie au plus 1 brève par exécution.
"""

import os
import random
import re
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path

import feedparser
import requests
from scraper_api import get as scraper_get
import yaml
from bs4 import BeautifulSoup
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "src/content/news"
FALLBACK_DIR = ROOT / "public/images/fallbacks"

RSS_URL = (
    "https://news.google.com/rss/search?q="
    + urllib.parse.quote(
        '("Elgato" OR "Logitech" OR "Razer" OR "HyperX" OR "Fifine" OR "Twitch" OR "TikTok" '
        'OR "setup streaming") when:7d'
    )
    + "&hl=fr&gl=FR&ceid=FR:fr"
)

SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

if os.environ.get("DEEPSEEK_API_KEY"):
    _base, _key, _model = "https://api.deepseek.com", os.environ["DEEPSEEK_API_KEY"], "deepseek-flash"
elif os.environ.get("OPENROUTER_API_KEY"):
    _base, _key, _model = "https://openrouter.ai/api/v1", os.environ["OPENROUTER_API_KEY"], "deepseek/deepseek-v4.1-flash"
elif os.environ.get("ANTHROPIC_API_KEY"):
    _base, _key, _model = "https://api.anthropic.com/v1/", os.environ["ANTHROPIC_API_KEY"], "claude-sonnet-4-5"
else:
    _base = _key = _model = None

client = OpenAI(
    base_url=os.environ.get("LLM_BASE_URL") or _base,
    api_key=_key,
)
MODEL = os.environ.get("LLM_MODEL") or _model or "deepseek-flash"

def get_news_image(article_url: str, slug: str) -> str:
    print("Recherche d'une image d'illustration...")

    if SCRAPER_API_KEY:
        try:
            api = (
                f"https://api.scraperapi.com?api_key={SCRAPER_API_KEY}"
                f"&url={urllib.parse.quote(article_url)}"
            )
            r = scraper_get(api, timeout=20)
            if r.status_code == 200:
                og = BeautifulSoup(r.text, "html.parser").find("meta", property="og:image")
                if og and og.get("content", "").startswith("http"):
                    return og["content"]
        except Exception as e:
            print(f"Échec ScraperAPI : {e}")

    if UNSPLASH_ACCESS_KEY:
        try:
            q = random.choice(
                ["pastel desk setup", "aesthetic workspace pink", "cozy desk pastel",
                 "white desk minimalist", "kawaii desk setup", "pink keyboard desk"]
            )
            r = requests.get(
                f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(q)}"
                "&orientation=landscape&per_page=5",
                headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
                timeout=15,
            )
            results = r.json().get("results", [])
            if results:
                return random.choice(results)["urls"]["regular"]
        except Exception as e:
            print(f"Échec Unsplash : {e}")

    pool = sorted(FALLBACK_DIR.glob("*.webp"))
    return f"/images/fallbacks/{random.choice(pool).name}" if pool else "/images/fallbacks/news-fallback-1.webp"
def build_description(summary: str, body: str) -> str:
    """Génère une description factuelle unique de 140 à 160 caractères.

    Le résumé RSS sert de base ; s'il est trop court, on complète avec les
    premières phrases du corps généré, puis on tronque sur une frontière de mot.
    """
    from html import unescape

    def clean(value: str) -> str:
        text = re.sub(r"<[^>]+>", " ", value or "")
        return re.sub(r"\s+", " ", unescape(text)).strip()

    def truncate(text: str, limit: int = 160) -> str:
        if len(text) <= limit:
            return text
        cut = text.rfind(" ", 0, limit)
        out = text[: cut if cut > 80 else limit].rstrip(" ,;:—-")
        return out if out.endswith((".", "!", "?", "…")) else f"{out}…"

    base = clean(summary)
    if not base:
        base = clean(body)
    if not base:
        return FALLBACK_DESCRIPTION

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean(body)) if s.strip()]
    desc = base
    for sentence in sentences:
        if len(desc) >= 140:
            break
        if sentence not in desc:
            desc = f"{desc.rstrip('.')}. {sentence}"
    if len(desc) < 140:
        rest = clean(body)
        if rest and rest not in desc:
            desc = f"{desc} {rest}"

    return truncate(desc, 160)


def slugify(value: str) -> str:
    """Slug lisible : les accents sont translittérés, pas supprimés."""
    import unicodedata

    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(c for c in normalized if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")[:60]


FALLBACK_DESCRIPTION = (
    "Ce que cette nouveauté change pour votre setup de stream et votre création de contenu."
)


def main() -> int:
    feed = feedparser.parse(RSS_URL)
    NEWS_DIR.mkdir(parents=True, exist_ok=True)

    for entry in feed.entries[:8]:
        title = re.sub(r"\s*-\s*[^-]+$", "", entry.title)  # retire le nom du média
        slug = slugify(title)
        filepath = NEWS_DIR / f"{slug}.mdx"
        if filepath.exists():
            continue

        print(f"Nouvelle actualité détectée : {title}")
        prompt = f"""Tu es la rédactrice en chef du blog "Miss Stream", un média dédié aux setups de
streaming esthétiques, pastel et cozy pour les créatrices de contenu (Twitch, YouTube, TikTok).

Actualité :
Titre : {title}
Résumé : {entry.summary}
Source : {entry.link}

Rédige une brève de ~400 mots en Markdown (sans frontmatter, on l'ajoute nous-mêmes) :
1. Résume l'annonce ou la nouveauté de façon claire et factuelle.
2. Explique en quoi c'est utile pour une créatrice de contenu ou pour l'esthétique d'un setup.
3. Ton moderne, bienveillant, orienté design et tech. Pas de jargon tech-bro.
4. N'invente AUCUN fait non présent dans le résumé. Pas de prix figés.
5. INTERDIT : "Plongeons dans l'univers", "Il est important de noter", "En conclusion", emojis.

Sors uniquement le corps Markdown de la brève."""

        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
            )
            body = resp.choices[0].message.content
            body = re.sub(r"^```(markdown|mdx)?\n|```$", "", body.strip()).strip()

            image = get_news_image(entry.link, slug)
            description = build_description(entry.summary, body)
            frontmatter = {
                "title": title.replace('"', "'"),
                "description": description if description else "Ce que cette nouveauté change pour votre setup de stream et votre création de contenu.",
                "publishDate": datetime.now().strftime("%Y-%m-%d"),
                "category": "news",
                "image": image,
                "sourceUrl": entry.link,
            }
            mdx = (
                "---\n"
                + yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
                + "---\n\n"
                + body
                + "\n"
            )
            filepath.write_text(mdx, encoding="utf-8")
            print(f"Brève publiée : {filepath}")
        except Exception as e:
            print(f"Erreur de génération pour '{title}' : {e}")
            continue

        break  # une seule brève par run

    return 0
if __name__ == "__main__":
    sys.exit(main())
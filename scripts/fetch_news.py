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
from seo_text import is_article_url, slugify, title_key
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
def _clean_meta(value: str) -> str:
    """Nettoie un texte scrapé destiné à une meta description.

    Supprime le HTML, les marqueurs Markdown (#, *, >, `), les noms de médias
    collés en fin de résumé (ex. « Le Monde.fr. ») et les espaces multiples.
    """
    from html import unescape

    text = re.sub(r"<[^>]+>", " ", value or "")
    text = unescape(text)
    text = re.sub(r"(?m)^\s*#{1,6}\s*", " ", text)
    text = text.replace("**", "").replace("__", "")
    text = re.sub(r"[#>*`]", " ", text)
    text = re.sub(r"(?:^|\s)[|•·]\s*", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"\s*[\w-]+\.(?:fr|com|be|ch|net|org)\.?\s*$", "", text, flags=re.I).strip()
    return text


def build_description(summary: str, body: str) -> str:
    """Génère une description factuelle unique de 140 à 160 caractères.

    Le résumé RSS sert de base s'il est complet ; un résumé tronqué (ou absent)
    est ignoré au profit des premières phrases du corps généré. Le résultat est
    toujours nettoyé des marqueurs Markdown et des noms de médias scrapés.
    """

    def truncate(text: str, limit: int = 160) -> str:
        if len(text) <= limit:
            return text
        window = text[:limit]
        for sep in (". ", "! ", "? "):
            idx = window.rfind(sep)
            if idx >= 100:
                return window[: idx + 1].strip()
        cut = text.rfind(" ", 0, limit)
        out = text[: cut if cut > 80 else limit].rstrip(" ,;:—-")
        return out if out.endswith((".", "!", "?", "…")) else f"{out}…"

    clean_summary = _clean_meta(summary)
    if "…" in clean_summary or "..." in clean_summary:
        clean_summary = ""
    base = clean_summary or _clean_meta(body)
    if not base:
        return FALLBACK_DESCRIPTION

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", _clean_meta(body)) if s.strip()]
    desc = base
    for sentence in sentences:
        if len(desc) >= 140:
            break
        if sentence not in desc:
            desc = f"{desc.rstrip('.')}. {sentence}"

    result = _clean_meta(truncate(desc, 160))
    return result or FALLBACK_DESCRIPTION


def existing_news_keys() -> tuple[set[str], set[str]]:
    """Titres et URLs sources déjà publiés, pour ne jamais doubler une brève."""
    titles: set[str] = set()
    sources: set[str] = set()
    for path in NEWS_DIR.glob("*.mdx"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end == -1:
            continue
        try:
            meta = yaml.safe_load(text[3:end])
        except yaml.YAMLError:
            continue
        if not isinstance(meta, dict):
            continue
        if meta.get("title"):
            titles.add(title_key(meta["title"]))
        url = str(meta.get("sourceUrl") or "").strip()
        if url and is_article_url(url):
            sources.add(url.split("?", 1)[0])
    return titles, sources


FALLBACK_DESCRIPTION = (
    "Ce que cette nouveauté change pour votre setup de stream et votre création de contenu."
)


def main() -> int:
    feed = feedparser.parse(RSS_URL)
    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    known_titles, known_sources = existing_news_keys()

    for entry in feed.entries[:8]:
        title = re.sub(r"\s*-\s*[^-]+$", "", entry.title)  # retire le nom du média
        source_key = (entry.link or "").split("?", 1)[0]
        if title_key(title) in known_titles:
            print(f"Déjà publiée (même titre), on passe : {title}")
            continue
        if is_article_url(entry.link) and source_key in known_sources:
            print(f"Déjà publiée (même source), on passe : {title}")
            continue
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
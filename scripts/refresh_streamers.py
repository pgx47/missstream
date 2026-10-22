#!/usr/bin/env python3
"""Refresh trimestriel : re-enrichit les produits (ASINs/images/notes)
de chaque streamer + regénère bio courte via DeepSeek."""
import io, json, os, urllib.parse
from pathlib import Path
import requests
from PIL import Image
from scraper_api import get as sget

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src/data/streamers.json"
LLM_KEY = os.environ.get("DEEPSEEK_API_KEY")
LLM_BASE = os.environ.get("LLM_BASE_URL") or "https://api.deepseek.com/v1"
MODEL = os.environ.get("LLM_MODEL") or "deepseek-chat"
SKEY = os.environ.get("SCRAPER_API_KEY")


def enrich_asin(nom: str):
    try:
        r = sget(f"https://api.scraperapi.com/structured/amazon/search?api_key={SKEY}&query={urllib.parse.quote(nom)}&country=fr", timeout=60)
        hits = r.json().get("results", [])
        if hits:
            a = hits[0]["asin"]
            out = ROOT / f"public/images/products/{a}.webp"
            if not out.exists() and hits[0].get("image"):
                img = Image.open(io.BytesIO(requests.get(hits[0]["image"], timeout=30).content)).convert("RGB")
                img.thumbnail((600, 600)); img.save(out, "WEBP", quality=80)
            return a
    except Exception:
        return None


s = json.loads(DATA.read_text())
for st in s:
    for p in st.get("setup", []):
        if not p.get("asin"):
            a = enrich_asin(p["nom"])
            if a:
                p["asin"] = a
    # refresh bio courte si manquante
    if not st.get("bio") and LLM_KEY:
        from openai import OpenAI
        c = OpenAI(api_key=LLM_KEY, base_url=LLM_BASE)
        r = c.chat.completions.create(model=MODEL, messages=[{"role": "user",
            "content": f"Bio courte (2 phrases) de la streameuse/streamer {st['nom']} ({st.get('jeu_principal','')}) pour une fiche setup. Ton chaleureux."}], temperature=0.6, max_tokens=150)
        st["bio"] = r.choices[0].message.content.strip()
DATA.write_text(json.dumps(s, ensure_ascii=False, indent=2))
print("streamers refreshed", len(s))

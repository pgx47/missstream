#!/usr/bin/env python3
"""Backfill : régénère les images lookbook + couvertures d'articles via
Cloudflare Workers AI FLUX (sans watermark). Git = source de vérité."""
import io, os, re, base64, glob, json, sys
from pathlib import Path
import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
ACCT = os.environ["CLOUDFLARE_ACCOUNT_ID"]
TOKEN = os.environ.get("CF_AI_TOKEN") or os.environ["CLOUDFLARE_API_TOKEN"]
MODEL = "@cf/black-forest-labs/flux-1-schnell"
URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/ai/run/{MODEL}"

def flux(prompt: str) -> bytes:
    r = requests.post(URL, headers={"Authorization": f"Bearer {TOKEN}"}, json={
        "prompt": f"Photorealistic cozy aesthetic streaming desk setup, {prompt}, soft ambient lighting, 8k, shot on 35mm, no text, no watermark, no people",
        "steps": 4,
    }, timeout=60)
    r.raise_for_status()
    return base64.b64decode(r.json()["result"]["image"])

def save(data: bytes, rel: str) -> str:
    from PIL import Image
    img = Image.open(io.BytesIO(data)).convert("RGB")
    out = ROOT / "public" / rel.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "WEBP", quality=82)
    return rel

# 1. Lookbook
lb = ROOT / "src/data/lookbook.json"
items = json.loads(lb.read_text())
for a in items:
    slug = re.sub(r"[^a-z0-9]+", "-", a["titre"].lower()).strip("-")
    try:
        a["image"] = save(flux(a["titre"] + ", " + a.get("description", "")), f"/images/lookbook/{slug}.webp")
        print("lookbook ok", a["titre"])
    except Exception as e:
        print("lookbook FAIL", a["titre"], e)
lb.write_text(json.dumps(items, ensure_ascii=False, indent=2))

# 2. Couvertures d'articles pollinations/absentes
for f in glob.glob(str(ROOT / "src/content/*/*.mdx")):
    txt = Path(f).read_text(encoding="utf-8")
    fm_m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not fm_m:
        continue
    fm = yaml.safe_load(fm_m.group(1))
    img = fm.get("image", "") or ""
    if not os.environ.get("ALL_GUIDES") and img and "pollinations.ai" not in img:
        continue
    title = fm.get("title", "")
    slug = Path(f).stem
    try:
        fm["image"] = save(flux(title), f"/images/guides/{slug}.webp")
        new_fm = yaml.dump(fm, allow_unicode=True, sort_keys=False)
        Path(f).write_text("---\n" + new_fm + "---" + txt[fm_m.end() - 4:], encoding="utf-8")
        print("article ok", slug)
    except Exception as e:
        print("article FAIL", slug, e)
print("done")

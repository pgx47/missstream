#!/usr/bin/env python3
"""Génère une épingle Pinterest 1000x1500 depuis l'image + titre d'un guide.
Usage: python scripts/make_pin.py <slug>  (dans le même run que generate_article)"""
import sys, json, re
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parent.parent
slug = sys.argv[1]
f = ROOT / f"src/content/guides/{slug}.mdx"
txt = f.read_text(encoding="utf-8")
fm = yaml.safe_load(re.match(r"^---\n(.*?)\n---", txt, re.S).group(1))
from PIL import Image, ImageDraw, ImageFont
src = fm["image"].split("?")[0]
if src.startswith("http"):
    import io, requests
    img = Image.open(io.BytesIO(requests.get(src, timeout=30).content)).convert("RGB")
else:
    img_path = ROOT / ("public" + src if src.startswith("/") else src)
    img = Image.open(img_path).convert("RGB")
W, H = 1000, 1500
w, h = img.size; r = W / w
img = img.resize((W, int(h * r)), Image.LANCZOS)
top = (img.height - H) // 2
img = img.crop((0, max(top, 0), W, max(top, 0) + H))
# bandeau bas
ov = Image.new("RGBA", (W, 320), (250, 240, 246, 235))
img.paste(Image.alpha_composite(img.convert("RGBA"), Image.new("RGBA", img.size, (0,0,0,0))).convert("RGB"), (0,0))
base = img.convert("RGBA"); base.alpha_composite(ov, (0, H - 320))
d = ImageDraw.Draw(base)
try:
    fb = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 46)
    fs = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 28)
except Exception:
    fb = fs = ImageFont.load_default()
title = fm["title"]
# wrap
words, lines, cur = title.split(), [], ""
for w_ in words:
    t = (cur + " " + w_).strip()
    if d.textlength(t, font=fb) > W - 120: lines.append(cur); cur = w_
    else: cur = t
lines.append(cur)
y = H - 320 + 40
for ln in lines[:3]:
    d.text((60, y), ln, font=fb, fill="#1f2937"); y += 58
d.text((60, H - 80), "missstream.xyz", font=fs, fill="#f472b6")
out = ROOT / "public/images/pins"; out.mkdir(parents=True, exist_ok=True)
pin_path = out / f"{slug}.png"
base.convert("RGB").save(pin_path, "PNG")
print(f"pin: public/images/pins/{slug}.png")

# Publication automatique si le token Pinterest est configuré
import os, base64, requests
token = os.environ.get("PINTEREST_ACCESS_TOKEN")
board = os.environ.get("PINTEREST_BOARD_ID")
if token and board:
    try:
        url = f"https://api.pinterest.com/v5/pins"
        r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json={
            "board_id": board,
            "title": fm["title"][:100],
            "description": (fm.get("description") or "")[:500],
            "link": f"https://missstream.xyz/articles/{slug}/",
            "media_source": {
                "source_type": "image_base64",
                "content_type": "image/png",
                "data": base64.b64encode(pin_path.read_bytes()).decode(),
            },
        }, timeout=30)
        print("pin publiée" if r.status_code in (200, 201) else f"pinterest {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"pinterest KO : {e}")

#!/usr/bin/env python3
"""Quality gate : image obligatoire, max 4 AffiliateBox, pas de pollinations,
dupes aux ASINs distincts. Auto-répare ou rejette le fichier."""
import glob, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANNED = ("pollinations.ai", "amazon-adsystem.com")
FALLBACKS = sorted((ROOT / "public/images/fallbacks").glob("*.webp"))
fallback = f"/images/fallbacks/{FALLBACKS[0].name}" if FALLBACKS else "/images/hero-setup.webp"

def fm_body(txt):
    parts = txt.split("---", 2)
    return (parts[1], parts[2]) if len(parts) >= 3 else (None, None)

def fix_file(f):
    txt = Path(f).read_text(encoding="utf-8")
    fm, body = fm_body(txt)
    if fm is None or not body.strip():
        return "delete"
    changed = False

    # 1. image valide
    m = re.search(r"^image:\s*(.+)$", fm, re.M)
    img = (m.group(1).strip("'\"") if m else "")
    if not img or any(b in img for b in BANNED) or not re.match(r"^(/|https?://)", img):
        fm = re.sub(r"^image:.*$", f"image: {fallback}", fm, count=1, flags=re.M) if m else fm + f"image: {fallback}\n"
        changed = True

    # 2. cap AffiliateBox à 4 + rien avant le premier ##
    boxes = [m.start() for m in re.finditer(r"<AffiliateBox", body)]
    first_h2 = body.find("\n##")
    if len(boxes) > 4:
        cut = boxes[4]
        end = body.find("\n", cut)
        # supprime la ligne tag excédentaire et les suivantes
        keep, extras = body[:cut], body[cut:]
        lines = extras.split("\n\n")
        lines = [l for l in lines if "<AffiliateBox" not in l]
        body = keep + "\n\n".join(lines)
        changed = True
    if first_h2 > -1:
        boxes = [m.start() for m in re.finditer(r"<AffiliateBox", body)]
        if boxes and boxes[0] < first_h2:
            body = re.sub(r"<AffiliateBox[^>]*/>\s*", "", body, count=1)
            changed = True
    if changed:
        Path(f).write_text("---" + fm + "---" + body, encoding="utf-8")
    return "ok"

n_fix = 0
for f in glob.glob(str(ROOT / "src/content/*/*.mdx")):
    r = fix_file(f)
    if r == "delete":
        Path(f).unlink(); print("deleted", f)
    elif r == "ok":
        # recount fixes
        txt = Path(f).read_text(encoding="utf-8")
        if txt.count("<AffiliateBox") <= 4 and "pollinations.ai" not in txt:
            continue

# 3. dupes asin distincts
dpath = ROOT / "src/data/dupes.json"
if dpath.exists():
    data = json.loads(dpath.read_text())
    clean = [d for d in data if (d.get("original", {}).get("asin") or d.get("original", {}).get("query"))
             and (d.get("dupe", {}).get("asin") or d.get("dupe", {}).get("query"))
             and d.get("original", {}).get("asin") != d.get("dupe", {}).get("asin")]
    if len(clean) != len(data):
        dpath.write_text(json.dumps(clean, ensure_ascii=False, indent=2))
        print("dupes cleaned", len(data) - len(clean), "retirés")

print("quality gate OK")
sys.exit(0)

#!/usr/bin/env python3
"""Expansion hebdomadaire : +4 items déco, +1 thème lookbook (si <12),
+1 paire de dupes. DeepSeek propose, ScraperAPI enrichit ASIN+image."""
import io, json, os, re, urllib.parse
from pathlib import Path
import requests
from PIL import Image
from scraper_api import get as sget

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "public/images/products"
LLM_KEY = os.environ.get("DEEPSEEK_API_KEY")
LLM_BASE = os.environ.get("LLM_BASE_URL") or "https://api.deepseek.com/v1"
MODEL = os.environ.get("LLM_MODEL") or "deepseek-chat"


def ask(prompt: str, max_tokens: int = 2500):
    from openai import OpenAI
    client = OpenAI(api_key=LLM_KEY, base_url=LLM_BASE)
    r = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Réponds uniquement en JSON valide, sans markdown."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=max_tokens,
    )
    txt = r.choices[0].message.content.strip().strip("`").lstrip("json").strip()
    return json.loads(txt)


def asin_for(query: str):
    try:
        r = sget(f"https://api.scraperapi.com/structured/amazon/search?api_key={os.environ.get('SCRAPER_API_KEY')}&query={urllib.parse.quote(query)}&country=fr", timeout=60)
        hits = r.json().get("results", [])
        if not hits:
            return None
        h = hits[0]
        a = h["asin"]
        out = IMG / f"{a}.webp"
        if not out.exists() and h.get("image"):
            img = Image.open(io.BytesIO(requests.get(h["image"], timeout=30).content)).convert("RGB")
            img.thumbnail((600, 600))
            out.parent.mkdir(parents=True, exist_ok=True)
            img.save(out, "WEBP", quality=80)
        return a, h.get("name", "")[:60]
    except Exception as e:
        print("asin fail", query, e)
        return None


# ---------- DECO ----------
dpath = ROOT / "src/data/deco_items.json"
deco = json.loads(dpath.read_text())
existing_deco = {x["asin"] for x in deco}
if len(deco) < 80:
    cats = list({x["cat"] for x in deco})
    noms = [x["nom"] for x in deco[:40]]
    try:
        res = ask(f"""Propose 8 objets déco streaming TENDANCE et variés (pas de doublons avec : {noms[:25]}).
Catégories possibles : {cats} + 'rangement'.
Réponds JSON : {{"items": [{{"nom": str, "cat": str, "prix": "≈ X €", "desc": str, "query": str}}]}}""")
        added = 0
        for it in res.get("items", []):
            if added >= 4 or not it.get("query"):
                continue
            r = asin_for(it["query"])
            if not r or r[0] in existing_deco:
                continue
            existing_deco.add(r[0])
            deco.append({"nom": it["nom"][:60], "asin": r[0], "cat": it.get("cat", "lumieres"),
                         "prix": it.get("prix", "≈ 20 €"), "desc": it.get("desc", "")})
            added += 1
            print("deco +", it["nom"])
        dpath.write_text(json.dumps(deco, ensure_ascii=False, indent=2))
    except Exception as e:
        print("deco fail", e)

# ---------- LOOKBOOK ----------
lpath = ROOT / "src/data/lookbook.json"
lb = json.loads(lpath.read_text())
if len(lb) < 12:
    titres = [a["titre"] for a in lb]
    try:
        res = ask(f"""Invente UN nouveau thème de setup de stream cozy (PAS dans : {titres}).
Exemples styles : bureau bohème, setup cottagecore, bureau cyberpunk pastel, setup scandinave.
Réponds JSON : {{"titre": str, "description": str, "produits": [{{"nom": str, "query": str}}]}} avec 4-5 produits.""")
        t = res
        prods = []
        for p in t.get("produits", [])[:5]:
            r = asin_for(p.get("query", p["nom"]))
            if r:
                prods.append({"nom": r[1] or p["nom"], "asin": r[0]})
        if len(prods) >= 3:
            slug = re.sub(r"[^a-z0-9]+", "-", t["titre"].lower()).strip("-")
            lb.append({"titre": t["titre"], "description": t["description"],
                       "produits": prods, "image": f"/images/lookbook/{slug}.webp"})
            # generate cover via Workers AI if available
            acct, tok = os.environ.get("CLOUDFLARE_ACCOUNT_ID"), (os.environ.get("CF_AI_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN"))
            if acct and tok:
                try:
                    rr = requests.post(f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/@cf/black-forest-labs/flux-1-schnell",
                        headers={"Authorization": f"Bearer {tok}"},
                        json={"prompt": f"Photorealistic cozy streaming desk setup, {t['titre']}, {t['description']}, soft light, 8k, no people, no text", "steps": 4}, timeout=60)
                    import base64 as b64
                    img = Image.open(io.BytesIO(b64.b64decode(rr.json()["result"]["image"]))).convert("RGB")
                    out = ROOT / "public/images/lookbook" / f"{slug}.webp"
                    img.save(out, "WEBP", quality=82)
                except Exception as e:
                    print("cover fail", e)
            lpath.write_text(json.dumps(lb, ensure_ascii=False, indent=2))
            print("lookbook +", t["titre"])
    except Exception as e:
        print("lookbook fail", e)

# ---------- DUPES ----------
duppath = ROOT / "src/data/dupes.json"
dupes = json.loads(duppath.read_text())
if len(dupes) < 12:
    try:
        titres = [d["titre"] for d in dupes]
        res = ask(f"""Invente UNE paire original vs dupe pour le streaming (PAS dans : {titres}).
Le dupe = alternative moins chère, esthétique si possible.
Réponds JSON : {{"titre": str, "original": {{"nom": str, "prix": "≈ X €", "query": str}}, "dupe": {{"nom": str, "prix": "≈ X €", "query": str}}, "gain": "-X €"}}""")
        o = asin_for(res["original"]["query"]); du = asin_for(res["dupe"]["query"])
        if o and du and o[0] != du[0]:
            dupes.append({"titre": res["titre"],
                          "original": {"nom": res["original"]["nom"], "prix": res["original"]["prix"], "asin": o[0]},
                          "dupe": {"nom": res["dupe"]["nom"], "prix": res["dupe"]["prix"], "asin": du[0]},
                          "gain": res["gain"]})
            duppath.write_text(json.dumps(dupes, ensure_ascii=False, indent=2))
            print("dupe +", res["titre"])
    except Exception as e:
        print("dupe fail", e)
print("done")

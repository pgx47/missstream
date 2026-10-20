#!/usr/bin/env python3
"""Nettoie les MDX existants : DeepSeek supprime les AffiliateBox spammées,
garde max 3-4 boxes placées sous le paragraphe du produit."""
import os, re, sys, json
from pathlib import Path
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com/v1")
MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")

PROMPT = """Voici un article MDX. Les composants <AffiliateBox/> sont spammés, mal placés ou trop nombreux.
1. Garde au MAXIMUM 3-4 <AffiliateBox/> — les produits phares seulement.
2. Chaque box conservée va JUSTE SOUS le paragraphe H3/### qui décrit ce produit.
3. Supprime les boxes hors contexte ou empilées. Ne modifie PAS le texte éditorial ni le frontmatter.
Renvoie UNIQUEMENT le MDX complet corrigé, sans balises code."""

for f in sorted((ROOT / "src/content/guides").glob("*.mdx")):
    txt = f.read_text(encoding="utf-8")
    if txt.count("<AffiliateBox") <= 4:
        print(f"skip {f.name} ({txt.count('<AffiliateBox')} boxes)")
        continue
    r = client.chat.completions.create(model=MODEL, messages=[
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": txt},
    ], temperature=0.2)
    out = r.choices[0].message.content.strip().strip("`")
    out = re.sub(r"^(mdx|markdown|md)\n", "", out)
    if out.startswith("---") and len(out) > len(txt) * 0.5:
        f.write_text(out, encoding="utf-8")
        print(f"clean {f.name} -> {out.count('<AffiliateBox')} boxes")
    else:
        print(f"reject {f.name}")
print("done")

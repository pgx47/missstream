#!/usr/bin/env python3
"""Wednesday: one illustrated inspiration. Sunday: up to four decor items and one alternative.

Preserve all existing entries. Only publish scraped product names/identities,
observed prices, and existing images. Repeat runs in the same ISO week are safe.
"""
import argparse
import base64
import io
import json
import os
import re
import unicodedata
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
import requests
from PIL import Image
from scraper_api import get as sget
from content_pipeline import ASIN, merge_entries, observed_price, write_json

ROOT = Path(__file__).resolve().parent.parent
CATS = ('lumieres','kawaii','rangement','gadgets-y2k')


def ask(prompt):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ['DEEPSEEK_API_KEY'],
        base_url=os.environ.get('LLM_BASE_URL') or 'https://api.deepseek.com/v1', timeout=90,max_retries=1)
    result = client.chat.completions.create(model=os.environ.get('LLM_MODEL') or 'deepseek-flash',
        messages=[{'role':'system','content':'Réponds en JSON valide uniquement. Aucun prix ni fait inventé.'},
                  {'role':'user','content':prompt}],temperature=0.5,max_tokens=3000)
    text = result.choices[0].message.content.strip()
    text = re.sub(r'^```(?:json)?\s*|\s*```$', '', text)
    return json.loads(text)


def search(query):
    response = sget('https://api.scraperapi.com/structured/amazon/search?'+urllib.parse.urlencode({
        'api_key':os.environ['SCRAPER_API_KEY'],'query':query,'country':'fr'}),timeout=30,retries=2)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data.get('results'),list):
        raise ValueError('Réponse de recherche invalide')
    return [h for h in data['results'] if isinstance(h,dict) and ASIN.fullmatch(str(h.get('asin','')))
            and h.get('name') and h.get('in_stock') is not False
            and h.get('availability') not in ('out_of_stock','unavailable')]


def product(hit, now):
    return {'nom':hit['name'][:160], 'asin':hit['asin'], 'verifiedAt':now,
            'sourceUrl':f'https://www.amazon.fr/dp/{hit["asin"]}'}


def product_image(hit):
    path = ROOT / f'public/images/products/{hit["asin"]}.webp'
    if not path.exists():
        if not hit.get('image'):
            raise ValueError('Image produit absente')
        response = requests.get(hit['image'],timeout=30)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert('RGB')
        image.thumbnail((600,600))
        path.parent.mkdir(parents=True,exist_ok=True)
        image.save(path,'WEBP',quality=82)
    return f'/images/products/{hit["asin"]}.webp'


def cover(theme, slug):
    account = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
    token = os.environ.get('CF_AI_TOKEN') or os.environ.get('CLOUDFLARE_API_TOKEN')
    if not account or not token:
        raise ValueError('Configuration image manquante : inspiration conservée hors publication')
    response = requests.post(f'https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/black-forest-labs/flux-1-schnell',
        headers={'Authorization':f'Bearer {token}'},
        json={'prompt':f'Photorealistic streaming desk inspiration, {theme}, cozy bright soft light, realistic proportions, no text, no watermark, no people','steps':4},timeout=90)
    response.raise_for_status()
    image = Image.open(io.BytesIO(base64.b64decode(response.json()['result']['image']))).convert('RGB')
    if min(image.size) < 256:
        raise ValueError('Image générée trop petite')
    path = ROOT / f'public/images/lookbook/{slug}.webp'
    path.parent.mkdir(parents=True,exist_ok=True)
    image.save(path,'WEBP',quality=85)
    return f'/images/lookbook/{slug}.webp'


def already_published(items, now):
    week = datetime.fromisoformat(now).isocalendar()[:2]
    for item in items:
        try:
            if datetime.fromisoformat(item.get('publishedAt','')).isocalendar()[:2] == week:
                return True
        except ValueError:
            continue
    return False


def inspiration(existing, now):
    if already_published(existing,now):
        return existing
    proposal = ask('Propose UNE ambiance de bureau de stream, différente de '+
        json.dumps([x['titre'] for x in existing],ensure_ascii=False)+
        '. JSON {titre,description,queries:[4 recherches produits précises]}. Description seulement esthétique, sans allégations techniques.')
    title = str(proposal['titre']).strip()[:100]
    if not title or any(x['titre'].casefold()==title.casefold() for x in existing):
        raise ValueError('Titre vide ou déjà présent')
    products, seen = [], set()
    for query in proposal['queries'][:5]:
        hits = search(query)
        hit = next((h for h in hits if h['asin'] not in seen),None)
        if hit:
            product_image(hit)
            products.append(product(hit,now))
            seen.add(hit['asin'])
    if len(products)<3:
        raise ValueError('Moins de trois produits vérifiés : pas de publication')
    slug = re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',title).encode('ascii','ignore').decode().lower()).strip('-')
    slug = f'{slug}-{now[:10]}'
    image = cover(title,slug)
    item = {'id':slug,'titre':title,'description':str(proposal['description'])[:350],
        'image':image,'produits':products,'publishedAt':now}
    return merge_entries(existing,[item],'titre',1)


def decor(existing, now):
    if already_published(existing,now):
        return existing
    proposal = ask('Propose 8 recherches Amazon pour objets déco de bureau streaming variés. Évite '+
        json.dumps([x['nom'] for x in existing],ensure_ascii=False)+
        '. JSON {items:[{query,cat,desc}]} ; cat parmi '+str(CATS)+'. Description esthétique courte, aucun prix.')
    candidates, seen = [], {x['asin'] for x in existing}
    for item in proposal['items'][:8]:
        if len(candidates)>=4:
            break
        hit = next((h for h in search(item['query']) if h['asin'] not in seen),None)
        if not hit or item.get('cat') not in CATS:
            continue
        price = observed_price(hit)
        if price is None:
            continue
        image = product_image(hit)
        candidates.append({**product(hit,now),'cat':item['cat'],'desc':str(item.get('desc',''))[:180],
            'prix':f'{price:.2f} €','image':image,'publishedAt':now})
        seen.add(hit['asin'])
    if not candidates:
        raise ValueError('Aucun nouvel objet vérifié avec prix et image')
    return merge_entries(existing,candidates,'asin',4)


def alternatives(existing, now):
    if already_published(existing,now):
        return existing
    proposal = ask('Propose UNE comparaison de deux équipements de streaming de même fonction, '+
        'premium et abordable, sans prétendre à des performances identiques. Évite '+
        json.dumps([x['titre'] for x in existing],ensure_ascii=False)+
        '. JSON {titre,originalQuery,dupeQuery}. Recherches modèles exacts.')
    hits = [search(proposal[key]) for key in ('originalQuery','dupeQuery')]
    if not all(hits):
        raise ValueError('Comparaison sans deux produits vérifiés')
    original, dupe = hits[0][0], hits[1][0]
    op, dp = observed_price(original), observed_price(dupe)
    if original['asin']==dupe['asin'] or op is None or dp is None or op<=dp:
        raise ValueError('Prix observés incompatibles avec une alternative moins chère')
    pair = {original['asin'],dupe['asin']}
    if any({d['original'].get('asin'),d['dupe'].get('asin')}==pair for d in existing):
        raise ValueError('Paire déjà présente')
    product_image(original)
    product_image(dupe)
    item = {'titre':f'{original["name"][:65]} / {dupe["name"][:65]}','publishedAt':now,
        'original':{**product(original,now),'prix':f'{op:.2f} €'},
        'dupe':{**product(dupe,now),'prix':f'{dp:.2f} €'},'gain':f'{op-dp:.2f} €'}
    return merge_entries(existing,[item],'titre',1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=('inspiration','maintenance'),required=True)
    parser.add_argument('--dry-run',action='store_true')
    args = parser.parse_args()
    jobs = [('lookbook',inspiration)] if args.mode=='inspiration' else [('deco_items',decor),('dupes',alternatives)]
    if args.dry_run:
        for name,_ in jobs:
            data = json.loads((ROOT/f'src/data/{name}.json').read_text())
            print(f'DRY RUN {name}: {len(data)} entrées préservées ; aucun appel ni écriture.')
        return 0
    for key in ('DEEPSEEK_API_KEY','SCRAPER_API_KEY'):
        if not os.environ.get(key):
            raise RuntimeError(f'{key} absent : aucune génération')
    now = datetime.now(timezone.utc).isoformat()
    results, errors = [], []
    for name,generate in jobs:
        path = ROOT/f'src/data/{name}.json'
        existing = json.loads(path.read_text())
        try:
            updated = generate(existing,now)
            write_json(path,updated)
            results.append(f'{name}: +{len(updated)-len(existing)} entrée(s), anciennes conservées')
        except Exception as error:
            # Provider exceptions can contain signed URLs/credentials; never print raw exceptions.
            errors.append(f'{name}: échec ({type(error).__name__}), données conservées')
    for line in results+errors:
        print(line)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as out:
            out.write('\n### Contenu hebdomadaire\n'+'\n'.join('- '+line for line in results+errors)+'\n')
    # Fail the job before commit if any required section failed.
    return int(bool(errors))

if __name__ == '__main__':
    raise SystemExit(main())

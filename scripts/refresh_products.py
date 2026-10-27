#!/usr/bin/env python3
"""Bounded, deduplicated product checks across every collection; failures preserve data."""
import argparse
import json
import os
import re
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
import yaml
from scraper_api import get as scraper_get
from content_pipeline import products_in, product_result, select_batch, write_json

ROOT = Path(__file__).resolve().parent.parent
COLLECTIONS = ('deals', 'deco_items', 'lookbook', 'dupes', 'packs', 'streamers')


def load_documents(root):
    documents = []
    for name in COLLECTIONS:
        path = root / f'src/data/{name}.json'
        documents.append((path, json.loads(path.read_text()), None))
    for path in sorted((root / 'src/content/guides').glob('*.mdx')):
        match = re.match(r'^---\n(.*?)\n---\n(.*)$', path.read_text(), re.S)
        if match:
            documents.append((path, yaml.safe_load(match[1]), match[2]))
    return documents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=40)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    documents = load_documents(ROOT)
    products = [p for _, data, _ in documents for p in products_in(data)]
    state_path = ROOT / 'src/data/product-health.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {'cursor':0,'products':{}}
    batch, cursor = select_batch([p['asin'] for p in products], state.get('cursor',0), max(1,args.limit))
    if args.dry_run:
        print(f'DRY RUN: {len(set(p["asin"] for p in products))} produits uniques, {len(batch)} contrôles, aucun appel ni écriture.')
        return 0
    key = os.environ.get('SCRAPER_API_KEY')
    if not key:
        raise RuntimeError('SCRAPER_API_KEY absent : aucun contrôle effectué.')
    results = {}
    valid_responses = 0
    now = datetime.now(timezone.utc).isoformat()
    for asin in batch:
        try:
            response = scraper_get('https://api.scraperapi.com/structured/amazon/search?'
                + urllib.parse.urlencode({'api_key':key,'query':asin,'country':'fr'}), timeout=30, retries=2)
            payload = response.json() if response.status_code == 200 else {}
            if isinstance(payload, dict) and isinstance(payload.get('results'), list):
                valid_responses += 1
            result = product_result(asin, payload)
        except Exception:
            result = {'status':'unknown'}
        previous = state['products'].get(asin, {})
        # On upstream failure retain the last known state and its observation date.
        if result['status'] == 'unknown':
            record = {**previous, 'status':previous.get('status','unknown'), 'lastAttemptAt':now, 'lastAttemptStatus':'unknown'}
        else:
            record = {**result, 'checkedAt':now, 'lastAttemptAt':now, 'lastAttemptStatus':result['status']}
        state['products'][asin] = record
        results[asin] = result
    if results and not valid_responses:
        raise RuntimeError('Tous les contrôles sont indéterminés : conservation des données, vérifier le fournisseur.')
    for path, data, body in documents:
        changed = False
        for product in products_in(data):
            result = results.get(product['asin'], {})
            if result.get('status') not in ('available','unavailable'):
                continue
            updates = {'productStatus':result['status']}
            if result['status'] == 'available':
                updates.update({k:result[k] for k in ('stars','avis') if result.get(k) is not None})
            for key, value in updates.items():
                if product.get(key) != value:
                    product[key] = value
                    changed = True
        if changed:
            if body is None:
                write_json(path, data)
            else:
                path.write_text('---\n'+yaml.safe_dump(data, allow_unicode=True,sort_keys=False)+'---\n'+body)
    state['cursor'] = cursor
    write_json(state_path, state)
    counts = {status:sum(r['status']==status for r in results.values()) for status in ('available','unavailable','unknown')}
    print('Product checks:', json.dumps(counts))
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a') as out:
            out.write(f'\n### Contrôle produits\n{len(batch)} références : {counts}\n')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

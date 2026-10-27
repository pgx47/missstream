#!/usr/bin/env python3
"""Maintain packs without replacing curated lookbook/dupe collections or inventing budgets."""
import json
from pathlib import Path
from content_pipeline import write_json
ROOT = Path(__file__).resolve().parent.parent


def maintain_packs(packs, health):
    """Keep identities and content stable; unavailable references remain explicitly marked.

    Replacing a component without verified compatibility and a real total budget
    would silently change a pack's promise. Hide it in the UI until revalidated.
    """
    for pack in packs:
        for item in pack.get('items', []):
            record = health.get(item.get('asin'), {})
            if record.get('status') in ('available','unavailable'):
                item['productStatus'] = record['status']
    return packs


def main():
    path = ROOT / 'src/data/packs.json'
    health = json.loads((ROOT/'src/data/product-health.json').read_text())['products']
    packs = json.loads(path.read_text())
    updated = maintain_packs(packs,health)
    write_json(path, updated)
    print('Packs conservés et statuts actualisés ; lookbook et alternatives préservés.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

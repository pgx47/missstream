#!/usr/bin/env python3
"""Read-only checks for weekly collections. Never delete or auto-rewrite content."""
import json
from pathlib import Path
from content_pipeline import ASIN
ROOT = Path(__file__).resolve().parent.parent


def validate(root=ROOT):
    errors=[]
    for name, identity in (('lookbook','titre'),('deco_items','asin'),('dupes','titre'),('packs','id')):
        path=root/f'src/data/{name}.json'
        items=json.loads(path.read_text())
        if not isinstance(items,list) or not items:
            errors.append(f'{name}: collection vide ou invalide')
            continue
        # Existing catalog may contain historical duplicates: reject new dated duplicates only.
        seen=set()
        for item in items:
            key=str(item.get(identity,'')).casefold()
            if not key or (key in seen and item.get('publishedAt')):
                errors.append(f'{name}: identité vide ou doublon récent')
            seen.add(key)
            if name=='lookbook':
                image=item.get('image','')
                if not image.startswith('/') or not (root/'public'/image.lstrip('/')).is_file():
                    errors.append(f'{name}: image locale manquante {image}')
                refs=item.get('produits',[])
            elif name=='dupes':
                refs=[item.get('original',{}),item.get('dupe',{})]
                if refs[0].get('asin')==refs[1].get('asin'):
                    errors.append('dupes: même produit des deux côtés')
            elif name=='packs':
                refs=item.get('items',[])
            else:
                refs=[item]
            if not refs or any(not ASIN.fullmatch(str(p.get('asin',''))) for p in refs):
                errors.append(f'{name}: référence produit invalide')
            if item.get('publishedAt') and len({p['asin'] for p in refs})!=len(refs):
                errors.append(f'{name}: doublons dans une nouvelle sélection')
    return errors

if __name__=='__main__':
    errors=validate()
    for error in errors:
        print(error)
    print(f'Validation : {len(errors)} erreur(s)')
    raise SystemExit(bool(errors))

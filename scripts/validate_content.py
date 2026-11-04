#!/usr/bin/env python3
"""Read-only checks for weekly collections. Never delete or auto-rewrite content."""
import json
import re
from pathlib import Path
import yaml
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

BOX_RE = re.compile(r"<AffiliateBox\b[^>]*/>")
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n-{3,}\r?\n(.*)$", re.S)


def image_missing(root, asin):
    return not (root / 'public' / 'images/products' / f'{asin}.webp').is_file()


def guide_errors(root=ROOT):
    """Bloque un guide dont une carte produit serait cassée.

    Un produit sans ASIN n'a ni photo ni lien direct, et un ASIN mort
    (page Amazon inexistante) n'a jamais d'image locale : les deux doivent
    empêcher la mise en ligne plutôt que d'afficher une carte vide.
    """
    errors = []
    for path in sorted((root / 'src/content/guides').glob('*.mdx')):
        match = FRONTMATTER_RE.match(path.read_text(encoding='utf-8'))
        if not match:
            errors.append(f'{path.name}: frontmatter illisible')
            continue
        try:
            frontmatter = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            errors.append(f'{path.name}: frontmatter YAML invalide')
            continue
        for product in frontmatter.get('products') or []:
            asin = str(product.get('asin', ''))
            if not ASIN.fullmatch(asin):
                errors.append(f'{path.name}: produit sans ASIN -> {product.get("nom")}')
            elif image_missing(root, asin):
                errors.append(f'{path.name}: image produit absente -> {asin}.webp ({product.get("nom")})')
        for tag in BOX_RE.findall(match.group(2)):
            if 'image=' in tag:
                continue
            found = re.search(r'asin="([^"]+)"', tag)
            if not found:
                errors.append(f'{path.name}: encart sans ASIN -> {tag[:80]}')
            elif image_missing(root, found.group(1)):
                errors.append(f'{path.name}: image produit absente -> {found.group(1)}.webp')
    return errors

if __name__=='__main__':
    errors=validate()+guide_errors()
    for error in errors:
        print(error)
    print(f'Validation : {len(errors)} erreur(s)')
    raise SystemExit(bool(errors))

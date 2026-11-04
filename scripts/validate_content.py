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


def guide_warnings(root=ROOT):
    """Signale les produits de guides sans ASIN ou sans image locale (non bloquant).

    Un encart sans ASIN n'affiche ni photo produit ni lien direct : c'est le
    symptôme d'un enrichissement Amazon raté à la génération.
    """
    warnings = []
    for path in sorted((root / 'src/content/guides').glob('*.mdx')):
        match = FRONTMATTER_RE.match(path.read_text(encoding='utf-8'))
        if not match:
            warnings.append(f'{path.name}: frontmatter illisible')
            continue
        try:
            frontmatter = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            warnings.append(f'{path.name}: frontmatter YAML invalide')
            continue
        body = match.group(2)
        for product in frontmatter.get('products') or []:
            if not ASIN.fullmatch(str(product.get('asin', ''))):
                warnings.append(f'{path.name}: produit sans ASIN -> {product.get("nom")}')
        for tag in BOX_RE.findall(body):
            if 'asin=' not in tag and 'image=' not in tag:
                warnings.append(f'{path.name}: encart sans ASIN -> {tag[:80]}')
                continue
            asin = re.search(r'asin="([^"]+)"', tag)
            if asin and not (root / 'public' / 'images/products' / f'{asin.group(1)}.webp').is_file():
                warnings.append(f'{path.name}: image produit absente -> {asin.group(1)}.webp')
    return warnings

if __name__=='__main__':
    errors=validate()
    for error in errors:
        print(error)
    for warning in guide_warnings():
        print(f'AVERTISSEMENT: {warning}')
    print(f'Validation : {len(errors)} erreur(s)')
    raise SystemExit(bool(errors))

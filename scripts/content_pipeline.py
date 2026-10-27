"""Pure validation helpers shared by weekly content and product maintenance."""
import json
import math
import re
from pathlib import Path

ASIN = re.compile(r'^[A-Z0-9]{10}$')


def write_json(path, data):
    path = Path(path)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def merge_entries(existing, candidates, identity, limit):
    result = list(existing)
    seen = {str(x.get(identity, '')).strip().casefold() for x in existing}
    for item in candidates:
        key = str(item.get(identity, '')).strip().casefold()
        if key and key not in seen:
            result.append(item)
            seen.add(key)
            if len(result) - len(existing) >= limit:
                break
    return result


def observed_price(hit):
    raw = hit.get('price')
    if isinstance(raw, dict):
        if raw.get('currency', 'EUR') != 'EUR':
            return None
        raw = raw.get('value')
    if isinstance(raw, str):
        raw = raw.replace('€', '').replace('EUR', '').strip().replace(',', '.')
        if not re.fullmatch(r'\d+(?:\.\d{1,2})?', raw):
            return None
    try:
        value = float(raw)
        return value if math.isfinite(value) and value > 0 else None
    except (ValueError, TypeError):
        return None


def product_result(asin, payload):
    if not isinstance(payload, dict) or not isinstance(payload.get('results'), list):
        return {'status': 'unknown'}
    for hit in payload['results']:
        if isinstance(hit, dict) and hit.get('asin') == asin:
            if hit.get('in_stock') is False or hit.get('availability') in ('out_of_stock', 'unavailable'):
                return {'status': 'unavailable'}
            return {k: v for k, v in {
                'status':'available', 'nom':hit.get('name'), 'stars':hit.get('stars'),
                'avis':hit.get('total_reviews'), 'price':observed_price(hit),
            }.items() if v is not None}
    # A search miss (including a valid empty search) is not proof of removal.
    return {'status': 'unknown'}


def valid_selection(items, catalog, minimum=3, maximum=5):
    if not isinstance(items, list) or not minimum <= len(items) <= maximum:
        return None
    ids = [p.get('asin') if isinstance(p, dict) else None for p in items]
    if len(set(ids)) != len(ids) or any(a not in catalog for a in ids):
        return None
    return [dict(catalog[a]) for a in ids]


def select_batch(ids, cursor, limit):
    ids = sorted(set(ids))
    if not ids:
        return [], 0
    start = cursor % len(ids)
    size = min(limit, len(ids))
    return [ids[(start+i) % len(ids)] for i in range(size)], (start+size) % len(ids)


def products_in(value):
    if isinstance(value, dict):
        if ASIN.fullmatch(str(value.get('asin', ''))):
            yield value
        for child in value.values():
            yield from products_in(child)
    elif isinstance(value, list):
        for child in value:
            yield from products_in(child)

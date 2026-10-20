#!/usr/bin/env python3
"""Rotation des clés ScraperAPI : tente chaque clé en cas de 429/403/limite."""
import os
import requests

_KEYS = [
    "6ae36b5bcb717498cc5b835e4735073f",
    "38f912ba7c85def9ea6cf788d1b6209f",
    "3eeb5968efac670766bcaeda563b2a0a",
]
if os.environ.get("SCRAPER_API_KEY"):
    _KEYS.append(os.environ["SCRAPER_API_KEY"])
_idx = 0


def _next_key():
    global _idx
    _idx += 1
    return _KEYS[_idx % len(_KEYS)]


def key():
    return _KEYS[_idx % len(_KEYS)]


def get(url: str, timeout: int = 60, retries: int = None, **kw):
    """GET ScraperAPI avec rotation auto sur 429/403/limite dépassée.
    L'URL doit contenir 'api_key=' — la clé est remplacée à chaque essai."""
    retries = retries or len(_KEYS) * 2
    import re as _re
    last = None
    for _ in range(retries):
        k = _next_key()
        u = _re.sub(r"api_key=[^&]*", f"api_key={k}", url)
        try:
            r = requests.get(u, timeout=timeout, **kw)
            last = r
            if r.status_code in (429, 403) or '"maximum"' in r.text[:500] or 'limit' in r.text[:500].lower():
                continue
            return r
        except requests.RequestException as e:
            last = e
            continue
    if last is None or isinstance(last, Exception):
        raise last or RuntimeError("scraperapi: all keys exhausted")
    return last

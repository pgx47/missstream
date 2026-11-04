#!/usr/bin/env python3
"""Rotation des clés ScraperAPI : tente chaque clé en cas de 429/403/limite."""
import os
import re
import requests


class RotationError(RuntimeError):
    """Erreur dont le message ne contient aucun secret et peut être publiée."""
    safe = True


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
    k = _KEYS[_idx % len(_KEYS)]
    _idx += 1
    return k


def key():
    return _KEYS[_idx % len(_KEYS)]


def _blocked(r):
    """429/403 ou message de quota ScraperAPI (jamais un simple nom de produit)."""
    if r.status_code in (429, 403):
        return True
    body = r.text[:400].lower()
    return '"message"' in body and ('exhausted' in body or 'credits' in body or 'limit' in body)


def get(url: str, timeout: int = 60, retries: int = None, **kw):
    """GET ScraperAPI avec rotation auto sur 429/403/limite dépassée.
    L'URL doit contenir 'api_key=' — la clé est remplacée à chaque essai."""
    retries = retries or len(_KEYS)
    last = None
    failures = []
    for _ in range(retries):
        k = _next_key()
        u = re.sub(r"api_key=[^&]*", f"api_key={k}", url)
        try:
            r = requests.get(u, timeout=timeout, **kw)
            last = r
            if _blocked(r):
                failures.append(str(r.status_code))
                continue
            return r
        except requests.RequestException as e:
            last = e
            failures.append(type(e).__name__)
            continue
    raise RotationError(
        f"ScraperAPI: {len(failures)} clé(s) en échec {failures} — quota ou limite de compte")

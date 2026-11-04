#!/usr/bin/env python3
"""Rotation des clés ScraperAPI : tente chaque clé en cas de 429/403/limite,
puis réessaie les échecs transitoires (499, 5xx) avec un délai croissant."""
import os
import re
import time
import requests

# Statuts qui méritent un nouvel essai : quota/limite ou cible temporairement KO.
# ScraperAPI renvoie 499 quand le scraping de la cible expire.
RETRYABLE = (403, 429, 499, 500, 502, 503, 504)


class RotationError(RuntimeError):
    """Erreur dont le message ne contient aucun secret et peut être publiée."""
    safe = True


_KEYS = [
    "6ae36b5bcb717498cc5b835e4735073f",
    "38f912ba7c85def9ea6cf788d1b6209f",
    "3eeb5968efac670766bcaeda563b2a0a",
]
if os.environ.get("SCRAPER_API_KEY") and os.environ["SCRAPER_API_KEY"] not in _KEYS:
    _KEYS.append(os.environ["SCRAPER_API_KEY"])
_idx = 0
_dead = set()  # clés dont le quota mensuel est épuisé pour de bon


def _pick():
    """Prochaine clé vivante ; None si toutes sont épuisées."""
    global _idx
    for _ in range(len(_KEYS)):
        i = _idx % len(_KEYS)
        _idx += 1
        if i not in _dead:
            return i, _KEYS[i]
    return None, None


def key():
    return _KEYS[_idx % len(_KEYS)]


def _quota_exhausted(r):
    body = r.text[:400].lower()
    return r.status_code == 403 and '"message"' in body and 'exhausted' in body


def _blocked(r):
    """Statut à réessayer (jamais un simple nom de produit dans le corps)."""
    if r.status_code in RETRYABLE:
        return True
    body = r.text[:400].lower()
    return '"message"' in body and ('exhausted' in body or 'credits' in body)


def get(url: str, timeout: int = 60, retries: int = None, **kw):
    """GET ScraperAPI avec rotation auto.
    L'URL doit contenir 'api_key=' — la clé est remplacée à chaque essai."""
    retries = retries or len(_KEYS) * 3
    failures, delay, last = [], 2.0, None
    for attempt in range(retries):
        i, k = _pick()
        if k is None:
            raise RotationError(
                f"ScraperAPI: quota épuisé sur {len(_KEYS)} clés (codes {failures[-len(_KEYS):]})")
        u = re.sub(r"api_key=[^&]*", f"api_key={k}", url)
        try:
            r = requests.get(u, timeout=timeout, **kw)
            last = r
            if not _blocked(r):
                return r
            if _quota_exhausted(r):
                _dead.add(i)
            failures.append(str(r.status_code))
        except requests.RequestException as error:
            last = error
            failures.append(type(error).__name__)
        # Nouvelle salve après avoir fait le tour des clés.
        if attempt and (attempt + 1) % len(_KEYS) == 0:
            time.sleep(delay)
            delay = min(delay * 2, 15.0)
    detail = failures[-1] if failures else 'aucun essai'
    raise RotationError(
        f"ScraperAPI: {retries} tentatives en échec (dernier code {detail}) sur {len(_KEYS)-len(_dead)} clé(s)")

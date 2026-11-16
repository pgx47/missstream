"""Normalisation de texte pour les URLs et la déduplication de contenu.

Isolé de `fetch_news.py` pour être testable sans dépendances LLM.
"""

import re
import unicodedata

SLUG_MAX = 60


def _ascii(value: str) -> str:
    """Translittère les accents au lieu de les supprimer."""
    normalized = unicodedata.normalize("NFKD", str(value))
    return "".join(c for c in normalized if not unicodedata.combining(c))


def slugify(value: str) -> str:
    """Slug lisible, jamais coupé au milieu d'un mot.

    Une troncature brutale produisait des URLs comme `...-graphite-a-`,
    ce qui crée des doublons instables d'un passage à l'autre.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", _ascii(value).lower()).strip("-")
    if len(slug) <= SLUG_MAX:
        return slug
    parts = slug[:SLUG_MAX].rsplit("-", 1)[0].strip("-").split("-")
    # Une troncature tombe parfois juste après un mot d'une lettre ("...-graphite-a").
    while len(parts) > 1 and len(parts[-1]) == 1:
        parts.pop()
    return "-".join(parts) or slug[:SLUG_MAX].strip("-")


def title_key(value: str) -> str:
    """Clé de comparaison tolérante : casse, accents et ponctuation ignorés."""
    return re.sub(r"[^a-z0-9]+", " ", _ascii(value).lower()).strip()


def is_article_url(url: str) -> bool:
    """Vrai si l'URL pointe un article précis (pas une simple page d'accueil)."""
    from urllib.parse import urlparse

    path = urlparse(str(url)).path.strip("/")
    return len(path) > 0

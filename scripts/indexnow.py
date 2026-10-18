#!/usr/bin/env python3
"""Ping IndexNow avec les URLs du sitemap (Bing, Yandex, Ecosia...)."""
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = os.environ.get("INDEXNOW_KEY", "")
HOST = "missstream.xyz"


def urls_from_sitemap() -> list[str]:
    xml = (ROOT / "public" / "sitemap-latest.xml")
    if not xml.exists():
        # fallback : reconstruit depuis les fichiers
        base = f"https://{HOST}"
        urls = [base + "/", base + "/articles/", base + "/actualites/", base + "/bons-plans/"]
        for d, p in [("guides", "/articles/"), ("news", "/actualites/")]:
            for f in (ROOT / f"src/content/{d}").glob("*.mdx"):
                urls.append(base + p + f.stem + "/")
        return urls
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in ET.parse(xml).getroot().findall("s:url/s:loc", ns)]


def main() -> int:
    if not KEY:
        print("INDEXNOW_KEY absent : skip.")
        return 0
    urls = urls_from_sitemap()
    import json

    payload = json.dumps(
        {
            "host": HOST,
            "key": KEY,
            "keyLocation": f"https://{HOST}/{KEY}.txt",
            "urlList": urls,
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=20)
        print(f"IndexNow: {len(urls)} URLs pingées")
    except Exception as e:
        print(f"IndexNow KO (non-bloquant) : {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

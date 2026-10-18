#!/usr/bin/env python3
"""Ping Google Indexing API pour les URLs récentes (guides/news modifiés).
Requiert : GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN.
Sans les secrets : exit 0 silencieux."""
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "https://missstream.xyz"
CID = os.environ.get("GOOGLE_CLIENT_ID")
CS = os.environ.get("GOOGLE_CLIENT_SECRET")
RT = os.environ.get("GOOGLE_REFRESH_TOKEN")


def access_token() -> str | None:
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=urllib.parse.urlencode({
            "client_id": CID, "client_secret": CS,
            "refresh_token": RT, "grant_type": "refresh_token",
        }).encode(),
    )
    try:
        return json.load(urllib.request.urlopen(req, timeout=20))["access_token"]
    except Exception as e:
        print(f"token KO : {e}")
        return None


def recent_urls() -> list[str]:
    """MDX touchés par le dernier commit (ou tout le sitemap en fallback)."""
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            cwd=ROOT, capture_output=True, text=True, timeout=15,
        ).stdout
        urls = []
        for line in out.splitlines():
            m = re.match(r"src/content/(guides|news)/(.+)\.mdx", line)
            if m:
                base = "/articles/" if m.group(1) == "guides" else "/actualites/"
                urls.append(HOST + base + m.group(2) + "/")
        return urls
    except Exception:
        return []


def ping(url: str, tok: str) -> bool:
    req = urllib.request.Request(
        "https://indexing.googleapis.com/v3/urlNotifications:publish",
        data=json.dumps({"url": url, "type": "URL_UPDATED"}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {tok}"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=15)
        return True
    except Exception as e:
        print(f"  ping KO {url} : {e}")
        return False


def main() -> int:
    if not (CID and CS and RT):
        print("Secrets Google manquants : skip.")
        return 0
    tok = access_token()
    if not tok:
        return 0
    urls = recent_urls() or [HOST + "/"]
    ok = sum(ping(u, tok) for u in urls)
    print(f"Google Indexing : {ok}/{len(urls)} URLs notifiées")
    return 0


if __name__ == "__main__":
    sys.exit(main())

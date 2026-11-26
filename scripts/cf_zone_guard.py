#!/usr/bin/env python3
"""Petites opérations d'assainissement sur la zone Cloudflare missstream.xyz.

Utilise CLOUDFLARE_API_TOKEN (secret GitHub) ou CF_TOKEN.
Actions :
  read              affiche les réglages utiles + les règles WAF custom
  block-junk-bots   bloque les User-Agents « early hints » qui génèrent des 504
  early-hints-off   désactive la fonctionnalité Early Hints de la zone
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

ZONE_ID = os.environ.get("CF_ZONE_ID", "972c53b0f759ce08c9b4f1917365fa07")
TOKEN = os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN", "")
API = "https://api.cloudflare.com/client/v4"
RULE_DESC = "[missstream] junk early-hints bots"
JUNK_AGENTS = ("nginx-ssl early hints", "fl2 early hints")


def api(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.load(resp)
    except urllib.error.HTTPError as err:
        try:
            return err.code, json.load(err)
        except Exception:
            return err.code, {"errors": [{"message": err.reason}]}


def require_token() -> None:
    if not TOKEN:
        print("CLOUDFLARE_API_TOKEN / CF_TOKEN absent")
        raise SystemExit(2)


def read() -> int:
    require_token()
    for setting in ("early_hints", "security_level", "browser_check", "hotlink_protection", "cache_level"):
        status, payload = api("GET", f"/zones/{ZONE_ID}/settings/{setting}")
        value = payload.get("result", {}).get("value") if payload.get("success") else payload.get("errors")
        print(f"{setting:20} {status} {value}")

    status, payload = api("GET", f"/zones/{ZONE_ID}/rulesets/phases/http_request_firewall_custom/entrypoint")
    if status == 200 and payload.get("success"):
        rules = payload["result"].get("rules", [])
        print(f"\nWAF custom rules ({len(rules)}) :")
        for rule in rules:
            print(f"  - {rule.get('action'):9} {rule.get('description') or rule.get('id')}")
            print(f"    {rule.get('expression')}")
    else:
        print(f"\nWAF custom rules : {status} {payload.get('errors')}")
    return 0


def block_junk_bots() -> int:
    require_token()
    path = f"/zones/{ZONE_ID}/rulesets/phases/http_request_firewall_custom/entrypoint"
    status, payload = api("GET", path)
    rules: list[dict] = []
    if status == 200 and payload.get("success"):
        rules = payload["result"].get("rules", [])
    elif status != 404:
        print(f"Lecture WAF impossible : {status} {payload.get('errors')}")
        return 1

    rules = [r for r in rules if r.get("description") != RULE_DESC]
    expression = " or ".join(f'(http.user_agent eq "{ua}")' for ua in JUNK_AGENTS)
    rules.append(
        {
            "action": "block",
            "expression": expression,
            "description": RULE_DESC,
            "enabled": True,
        }
    )

    status, payload = api("PUT", path, {"rules": rules})
    if status in (200, 201) and payload.get("success"):
        print(f"OK — règle WAF active ({len(rules)} règle(s) au total) : {expression}")
        return 0
    print(f"Échec WAF : {status} {payload.get('errors')}")
    return 1


def early_hints_off() -> int:
    require_token()
    status, payload = api(
        "PATCH", f"/zones/{ZONE_ID}/settings/early_hints", {"value": "off"}
    )
    if status == 200 and payload.get("success"):
        print(f"OK — early_hints = {payload['result'].get('value')}")
        return 0
    print(f"Échec early_hints : {status} {payload.get('errors')}")
    return 1


ACTIONS = {
    "read": read,
    "block-junk-bots": block_junk_bots,
    "early-hints-off": early_hints_off,
}

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "read"
    if action not in ACTIONS:
        print(f"Action inconnue : {action} (choix : {', '.join(ACTIONS)})")
        raise SystemExit(2)
    sys.exit(ACTIONS[action]())

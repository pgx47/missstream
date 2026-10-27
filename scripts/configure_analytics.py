#!/usr/bin/env python3
"""Enable cookie-free Cloudflare Web Analytics for the existing Miss Stream zone."""
import os
import requests

ACCOUNT='d0573de28c843425f94eb430fc7a226a'
ZONE='972c53b0f759ce08c9b4f1917365fa07'
BASE=f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/rum/site_info'
s=requests.Session()
s.headers['Authorization']='Bearer '+os.environ['CLOUDFLARE_API_TOKEN']

def call(method,url,**kwargs):
    response=s.request(method,url,timeout=30,**kwargs)
    payload=response.json()
    if not payload.get('success'):
        raise RuntimeError('Cloudflare Web Analytics : accès refusé ou erreur fournisseur ; aucune statistique inventée.')
    return payload.get('result')

sites=call('GET',BASE+'/list',params={'per_page':100})
site=next((site for site in sites if site.get('ruleset',{}).get('zone_tag')==ZONE or any(rule.get('host')=='missstream.xyz' for rule in site.get('rules',[]))),None)
if site:
    if not site.get('auto_install'):
        site=call('PUT',BASE+'/'+site['site_tag'],json={'auto_install':True,'enabled':True})
else:
    site=call('POST',BASE,json={'auto_install':True,'zone_tag':ZONE})
assert site.get('auto_install'), 'Installation automatique non confirmée'
print('Cloudflare Web Analytics activé pour Miss Stream, installation automatique confirmée.')

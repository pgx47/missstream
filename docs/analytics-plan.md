# Mesure — Miss Stream

> Skills utilisées : `analytics` et `conversion-tracking` (volet mesure). Le site n'a ni
> compte ni panier : **la conversion, c'est le clic sortant vers Amazon**.

## 1. Ce qui est mesuré aujourd'hui

| Donnée | Outil | État |
|---|---|---|
| Pages vues, sources, pays | Cloudflare Web Analytics (beacon, sans cookie) | ✅ actif |
| Clics affiliés (total) | visites de `/go/` — la page attend 250 ms avant la redirection pour laisser partir le beacon | ✅ depuis 2026-11-06 |
| Clic affilié par produit (ASIN) | `window.dataLayer.push({event:'affiliate_click'})` | 🟡 prêt, aucun collecteur branché |
| Requêtes, impressions, positions | Google Search Console | ❌ non branché |
| Revenu | Amazon Associates | ❌ non rapproché |

## 2. Définitions

- **Clic affilié** = visite de `/go/` (une par clic sortant, y compris les liens du corps d'article).
- **CTR affilié** = sessions `/go/` ÷ sessions des pages de contenu, sur la même période.
- **EPC** = commissions ÷ clics affiliés. Le seul indicateur qui dit si une page rapporte.
- **Clic par page** = à obtenir via `dataLayer` quand un collecteur sera branché.

## 3. Limite connue (à corriger plus tard)

Cloudflare Web Analytics agrège par chemin : les visites de `/go/` sont comptées, mais le
paramètre `?a=ASIN` n'apparaît pas dans les rapports. On mesure donc **le volume de clics**,
pas **quel produit** déclenche le clic.

Trois options, par ordre de coût :

1. **GA4 + GTM** (gratuit, 30 min) : brancher le `dataLayer` déjà en place, deux balises
   (`affiliate_click`, `affiliate_redirect`). Consentement à gérer (bandeau cookies).
2. **Cloudflare Analytics Engine + Pages Function** : première partie, sans cookie, mais
   demande un binding et un déploiement de fonction.
3. **Rien** : rester sur le volume de clics `/go/` tant que le trafic est faible.

Recommandation : option 1 dès que le site dépasse ~1 000 sessions/mois.

## 4. Search Console — à brancher (priorité 1)

1. Ajouter `missstream.xyz` comme propriété « domaine » (vérification DNS, automatique via
   Cloudflare).
2. Soumettre `https://missstream.xyz/sitemap-index.xml`.
3. Après 7 jours, exporter : requêtes, pages, pays, appareils, Core Web Vitals.
4. Cible de travail : pages en **position 8-20** avec des impressions — c'est là que le
   prochain gain est le moins coûteux (voir `docs/content-strategy.md`).

## 5. Tableau de bord minimal (mensuel)

| Indicateur | Source | Seuil d'alerte |
|---|---|---|
| Sessions organiques | GSC | baisse > 20 % sur 28 jours |
| Pages indexées | GSC > Couverture | < 90 % des pages du sitemap |
| Clics `/go/` | Cloudflare | baisse > 30 % sans baisse de trafic |
| Pages sans image produit | `python scripts/validate_content.py` | > 0 (bloque le déploiement) |
| Erreurs 5xx / 404 anormaux | Cloudflare | pic soudain |

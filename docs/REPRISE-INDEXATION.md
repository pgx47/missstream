# Reprise d'indexation — missstream.xyz

État au 26/11/2026, d'après l'export Search Console « Indexation des pages ».

## Constat

| Indicateur | Valeur |
|---|---|
| Pages indexées | **1** (1 332 le 28/08/2026) |
| Pages non indexées | **35 723** |
| Explorée, non indexée | 23 641 |
| Erreur serveur (5xx) | 10 962 |
| Impressions | 0 à 5 / jour |

Le site actuel ne compte que **95 URLs**. Les dizaines de milliers d'URLs
connues de Google proviennent de l'ancien site hébergé sur le domaine :
une plateforme de streaming (`/movie/*`, `/tv/*`, `/actor/*`), visible dans
Wayback Machine en janvier 2026 et dans les logs Cloudflare. Google a purgé
le domaine entre août et octobre 2026, puis refuse d'indexer les pages du
nouveau site (« Détectée, actuellement non indexée » = 88, soit l'essentiel
du sitemap).

**Ce n'est pas un problème on-page.** Vérifié le 26/11 :

- 95/95 URLs du sitemap en 200, titres et descriptions uniques ;
- canonical self-référent sur toutes les pages, aucun `noindex` ;
- robots.txt correct, Googlebot reçoit des 200 (aucun 5xx actuel) ;
- les 5xx et les doublons du rapport sont des URLs de l'ancien site.

Bing n'indexe pas non plus le site (`site:missstream.xyz` → aucun résultat).

## Phase 0 — vérifications Search Console (propriétaire)

1. **Sécurité et actions manuelles** : une action « Spam pur » ou
   « Contenu trompeur » changerait tout le plan (il faudrait une demande de
   reconsidération après nettoyage).
2. **Indexation → Sitemaps** : `sitemap-index.xml` doit être soumis et en
   succès.
3. **Ne pas lancer « Valider la correction » sur les 5xx** : ces URLs ne
   sont plus servies, la validation échouera. Elles disparaîtront seules.

## Phase 1 — nettoyage technique (fait)

- `functions/` : réponse **410 Gone** sur les anciens espaces d'URL
  (`/movie/`, `/tv/`, `/actor/`, `/news/`, `/privacy/`, `/disclaimer/`,
  `/ads/`, `/_next/`). 410 = suppression définitive, sortie d'index plus
  rapide qu'un 404 et économie de budget de crawl.
- Le reste du site continue d'être servi statiquement, sans surcoût.

## Phase 2 — réduction du volume (à valider)

Le site publie du contenu généré automatiquement à un rythme industriel :
3 guides/semaine, 3 brèves/semaine, 3 fiches streamers/semaine. C'est
exactement le signal « scaled content abuse » que Google sanctionne, et le
volume de pages faibles dilue les 32 guides utiles.

| Bloc | Pages | Mots | Recommandation |
|---|---|---|---|
| Guides | 32 | 670–2 500 | **Garder**, enrichir |
| Brèves (`/actualites/`) | 26 | 300–630 | **Supprimer** (RSS + LLM, 0 impression) |
| Fiches streamers | 15 | 300–400 | **Supprimer** (bios et setups non vérifiés sur des personnes réelles) |
| Pages couleurs | 4 | 239–7 815 | Garder |
| Outils / pages fixes | 15 | 45–1 700 | Garder, enrichir le texte des outils |

Après nettoyage : ~49 pages, toutes défendables.

## Phase 3 — qualité et E-E-A-T

- **Arrêter la publication automatique** (`publish.yml`, `news.yml`,
  `streamers-refresh.yml`) ou la conditionner à une relecture humaine.
- **Auteur réel** : nom, bio, photo, profils publics, page auteur reliée
  aux guides. Aujourd'hui « Léa & l'équipe » sans identité vérifiable.
- **Honnêteté des claims** : retirer « testés en conditions réelles » si les
  produits ne sont pas testés, ou documenter un protocole réel. Le texte de
  `/a-propos/` reconnaît déjà que les avis sont « générés puis relus ».
- **Photos originales** : au moins une photo maison par guide majeur
  (aujourd'hui Unsplash / images générées).

## Phase 4 — autorité

Aucun backlink identifiable. Sans liens, même un site propre reste en
« explorée, non indexée ». Objectif : 10 à 20 mentions réelles (Pinterest,
Reddit, Discord de créatrices, presse niche), pas d'annuaires.

## Phase 5 — suivi

Revue à 30 / 60 / 90 jours : nombre de pages indexées, impressions,
« Détectée, non indexée ». Si aucune page ne passe à « indexée » après
90 jours et deux vagues de nettoyage, la migration vers un domaine neuf
redevient l'option rationnelle.

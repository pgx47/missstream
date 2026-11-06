# SEO programmatique — Miss Stream

> Skill utilisée : `programmatic-seo`. Objectif : produire des pages à l'échelle **sans**
> tomber dans le contenu de masse, sur un site qui a déjà 4 pages générées par template
> (`/couleurs/`).

## 1. Ce qui existe déjà

| Template | URLs | Source de données | Qualité actuelle |
|---|---|---|---|
| `/couleurs/{couleur}/` | 4 | `guides[].products[].couleur` | 390 mots, aucun texte unique, 0 lien entrant jusqu'au 2026-11-06 |
| `/streamers/{slug}/` | 15 | `src/data/streamers.json` | bios longues, maillage correct |
| `/dupes/` | 1 | `src/data/dupes.json` | éditorial, pas programmatique |
| `/lookbook/` | 1 | `src/data/lookbook.json` | éditorial |

Le seul vrai template à risque est `/couleurs/` : il agrège des `AffiliateBox` sans
introduction propre. Quatre pages de 390 mots passent ; cinquante seraient un signal de
contenu généré sans valeur.

## 2. Matrice d'opportunités

| Famille | Motif d'URL | Volume estimé | Valeur | Verdict |
|---|---|---|---|---|
| Couleur | `/couleurs/{couleur}/` | 6-8 | Moyenne | **à enrichir**, pas à multiplier |
| Produit vs produit | `/comparer/{a}-vs-{b}/` | 15-25 | Forte (intention d'achat) | **prioritaire** |
| Setup par budget | `/setup/{150|400|900}-euros/` | 3 | Forte | à créer, 3 pages max |
| Setup par usage | `/setup/{just-chatting|gaming|podcast}/` | 3-4 | Moyenne | après les deux précédents |
| Streamer | `/streamers/{slug}/` | 15 → 40 | Moyenne (notoriété) | **continuer**, déjà en place |

Le pSEO rentable ici n'est pas « 100 pages de couleur », c'est **la comparaison de produits
déjà testés** : on a les fiches, les images, les verdicts et les liens affiliés. Chaque page
`/comparer/` répond à une requête transactionnelle (« X vs Y ») avec un contenu qui existe
déjà dans deux guides.

## 3. Spécification du template comparaison

Généré depuis `src/data/dupes.json` (déjà structuré : `original` / `dupe`, prix, verdicts).

Une page valide doit contenir, dans cet ordre :
1. **Un H1 explicite** : « Fifine AM8 vs Shure MV7 : lequel pour un setup blanc ? »
2. **Un verdict en 2 phrases dès le premier paragraphe** (réponse directe, aussi utile aux
   moteurs de réponse IA).
3. **Un tableau** : prix indicatif, type, connectique, coloris, défaut principal.
4. **Deux sections « X gagne si… » / « Y gagne si… »** avec un exemple concret.
5. **Les deux `AffiliateBox`** avec images réelles.
6. **3 questions fréquentes** propres à la paire (pas un copier-coller).
7. **3 liens internes** vers les guides parents + 1 vers `/dupes/`.

Garde-fous (bloquants) :
- 600 mots minimum de texte **unique** par page ;
- aucun produit sans image locale (déjà vérifié par `validate_content.py`) ;
- pas de page générée si les deux produits n'ont pas de guide parent ;
- introduction écrite par LLM **avec les données réelles** (prix indicatif, notes), jamais de
  prix figé.

## 4. Feuille de route

**Phase 1 (2 semaines)** — enrichir `/couleurs/` : 150-200 mots d'intro uniques par couleur,
3 critères de choix, 2 liens internes, une question fréquente. Objectif : passer de 390 à
600+ mots utiles sur les 4 pages existantes.

**Phase 2 (3 semaines)** — `/comparer/` sur les 6 paires déjà couvertes par des guides :
Fifine vs QuadCast, Fifine vs Seiren Mini, MV7 vs SM7B, Litra Glow vs Key Light Mini,
Stream Deck Neo vs MK.2, PreSonus vs Mackie. Six pages, zéro nouvelle recherche produit.

**Phase 3** — 3 pages budget (`/setup/150-euros/`, `/400-euros/`, `/900-euros/`) construites
depuis `src/data/packs.json`, avec le configurateur en CTA.

**Phase 4 (si les phases 1-3 rankent)** — étendre `/streamers/` de 15 à 30 profils, puis
`/setup/{usage}/`.

## 5. Mesure

- Suivre l'indexation et les impressions par famille dans Search Console (dès branchement).
- Seuil d'arrêt : si une famille de pages n'obtient **aucune impression après 8 semaines**,
  on arrête la série et on renforce les pages existantes au lieu d'en ajouter.
- Ne jamais publier plus de **4 pages programmatiques par semaine** : le crawl budget d'un
  site de 80 pages est limité, et un pic de pages faibles dilue le reste.

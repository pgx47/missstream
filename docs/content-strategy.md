# Stratégie de contenu — Miss Stream

> Skill utilisée : `content-strategy`. Base : 23 guides publiés, 27 sujets en réserve,
> audit SEO du 2026-11-06.

## 1. Cartographie des clusters

| Cluster | Pages existantes | Force | Manque principal |
|---|---|---|---|
| **Audio (micros)** | comparatif 4 micros blancs/roses, Fifine vs Shure, micro cadeau Noël | Fort | interface audio, micro-cravate, Rode PodMic vs Wave:3 |
| **Éclairage** | ring light/barres LED, lampe sunset vs projecteur, Litra vs Key Light (à venir) | Fort | panneau LED doux, softbox, lampe de bureau pastel |
| **Bureau & ergonomie** | bureau assis-debout, chaise pastel, support casque | Moyen | support double écran, étagère, multiprise, repose-poignet |
| **Périphériques** | clavier compact, stream deck, stream deck Neo vs MK.2, tapis + bras | Fort | souris légère, moniteur 27", G715 vs Q1 Pro |
| **Image / capture** | webcam 4K, carte d'acquisition, (capture Switch/PS5) | Moyen | Facecam Pro vs Kiyo Pro Ultra, ZV-E10 vs webcam, PCIe vs USB |
| **Déco & ambiance** | Halloween, Y2K, lava lamps, setup cosy hiver, déco Noël | Fort (saisonnier) | fond de studio pastel, ventilateur silencieux |
| **Cadeaux** | cadeau débutante, idées Noël | Temporaire | à réactiver en novembre 2027 |
| **Casques** | oreilles de chat (comparatif) | Moyen | casque fermé confort long stream |

Lecture : le site est déjà dense sur **audio + éclairage + périphériques**, qui sont les
clusters à plus forte intention d'achat. Les manques sont sur les **périphériques de
confort** (support écran, étagère, multiprise) — faible concurrence, panier moyen correct.

## 2. Décisions prises

**Cannibalisation micro — réglée.** `meilleur-micro-usb-blanc-pour-streamer` (812 mots,
générique) et `meilleur-micro-usb-blanc-rose-pour-streamer` (2 095 mots, 4 modèles testés)
visaient la même requête. Le guide court a été supprimé, son contenu unique était déjà
couvert par le long, et une **301** redirige l'ancienne URL (`public/_redirects`). Les 9 liens
internes pointent désormais vers le guide long.

**Doublons de topics — retirés.** Deux sujets en réserve doublonnaient des pages existantes
(`Elgato Stream Deck Neo vs MK.2`, `les 5 meilleurs casques oreilles de chat`) : marqués
`done` dans `topics.json` pour que le générateur ne les publie pas.

**À surveiller** : `setup-streaming-cosy-pour-l-hiver` et `setup-bureau-ultra-cozy-streams-hiver`
se recoupent. Angle retenu : le premier = guide d'ambiance (lumière, confort, textile), le
second = équipement de bureau. Interdiction de re-cibler la même requête dans les deux ;
à fusionner si l'un stagne après 3 mois.

## 3. Plan 8 semaines (2 guides/semaine max)

| Semaine | Sujet | Cluster | Intention | Pourquoi maintenant |
|---|---|---|---|---|
| 1 | panneau LED blanc pour éclairage doux | Éclairage | Achat | complète le duo ring light / Key Light |
| 1 | support double écran blanc | Bureau | Achat | zéro concurrence FR cozy, panier ~60 € |
| 2 | souris blanche légère pour jouer et streamer | Périphériques | Achat | prolonge le cluster clavier/stream deck |
| 2 | Logitech Litra Glow vs Elgato Key Light Mini | Éclairage | Comparaison | les deux produits ont déjà des fiches et des images |
| 3 | interface audio blanche pour micro XLR | Audio | Achat | capte la montée en gamme des lectrices du guide micro |
| 3 | étagère blanche pour ranger son setup | Bureau | Achat | lien naturel avec le lookbook |
| 4 | moniteur blanc 27 pouces | Périphériques | Achat | forte demande, peu d'offre blanche |
| 4 | Razer Seiren Mini vs Fifine AM8 | Audio | Comparaison | deux produits déjà testés séparément |
| 5 | fond de studio pastel (tissu, rideau, panneau) | Déco | Inspiration + achat | sujet purement visuel, très Pinterest |
| 5 | repose-poignet + multiprise USB blanc | Bureau | Achat | petits prix, forte conversion attendue |
| 6 | Rode PodMic USB vs Elgato Wave:3 | Audio | Comparaison | élargit l'audio au-delà du blanc |
| 6 | ventilateur silencieux blanc | Déco | Achat | douleur réelle l'été, zéro contenu FR cozy |
| 7 | capture PCIe vs boîtier USB | Image | Guide | répond à une question de forum récurrente |
| 7 | caméra Sony ZV-E10 vs webcam 4K | Image | Comparaison | pont vers les créatrices qui passent au mirrorless |
| 8 | micro-cravate sans fil blanc | Audio | Achat | format mobile/TikTok, non couvert |

Règle de production : **jamais deux pages du même cluster dans la même semaine** (évite de
cannibaliser son propre trafic naissant), et chaque nouveau guide doit recevoir au moins
**3 liens internes entrants** depuis des guides existants (ajout manuel dans le même commit).

## 4. Rafraîchissement

| Page | Dernière publication | Action |
|---|---|---|
| guides du 17-18 octobre (5 pages) | ~3 semaines | vérifier ASIN et images encore valides, ajouter 1 lien interne récent |
| `black-friday-materiel-streaming-setup` | 2 novembre | réécrire en octobre 2027, pas avant |
| `decorer-setup-halloween` | 26 octobre | désindexer hors saison ? Non : le garder, il remontera en septembre |
| `idees-cadeaux-streameuse-noel` | 20 octobre | rafraîchir mi-novembre (prix, disponibilités) |

Cadence de contrôle : **un passage mensuel** sur `validate_content.py` (images produits) +
un audit des positions 8-20 dès que Search Console est branchée.

## 5. Ce qu'on ne fait pas

- Pas de liste « top 20 produits » : le format testé/verdict convertit mieux et vieillit mieux.
- Pas de page par ville, par genre ou par plateforme tant qu'il n'y a pas de données propres.
- Pas de contenu anglophone : le créneau est francophone, la traduction diluerait le signal.

# Générateur de Panneaux Twitch & Bio Setup

Page : `/outils/panneaux-twitch/` — `src/pages/outils/panneaux-twitch.astro`

Outil 100 % client-side (zéro backend) : génère des panneaux de description Twitch
et une bio "mon setup" avec liens affiliés, directement dans le navigateur.

## Fonctionnement

### 1. Panneaux (canvas → PNG → ZIP)
- Rendu sur `<canvas>` à la taille exacte Twitch : **320 × 100 px** (gérant `devicePixelRatio` pour la netteté Retina).
- 4 palettes : Pink Cozy, Lavande Lilas, Menthe Douce, Soft Minimal.
- Panneaux prédéfinis (À Propos, Règles, Planning, Discord, Setup, Dons, Réseaux, Commandes) + champs custom.
- Icônes vectorielles dessinées en canvas (cœur, manette, bulle, micro) teintées à la couleur du texte.
- Export : `JSZip` via CDN → `pack .zip` de PNG nommés `01-a-propos.png`, etc.

### 2. Générateur de bio setup
- Checkboxes de produits (micros, casques, accessoires, lumière).
- Génère du Markdown prêt à coller dans les panneaux Twitch :
  `- **Micro :** [Fifine AM8 blanc](https://www.amazon.fr/dp/ASIN?tag=missstrm-21)`
- Liens affiliés construits via `amazonUrl()` (tag `missstrm-21`, `rel="nofollow sponsored"`).
- Bouton "Copier le code" via `navigator.clipboard`.

## Stack
- Astro statique, Tailwind v4 (`card-aesthetic`, `badge-guide`, `btn-cta`).
- JS vanilla + Canvas API + `navigator.clipboard`.
- JSZip 3.10.1 chargé via CDN `jsdelivr` — aucune dépendance npm serveur.

## SEO
- Title : "Générateur de Panneaux Twitch Gratuits & Aesthetic Pastel | Miss Stream"
- Cible les requêtes "panneaux twitch gratuits / aesthetic / pastel" — fort potentiel Pinterest/Discord.

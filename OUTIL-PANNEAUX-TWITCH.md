# Générateur de Panneaux Twitch & Bio Setup

Page : `/outils/panneaux-twitch/` — `src/pages/outils/panneaux-twitch.astro`

Outil 100 % client-side (zéro backend). Point d'entrée du hub `/outils/`.

## Moteur Canvas (v3)

- Largeur fixe Twitch **320 px**, hauteur **réglable 70–140 px**.
- Netteté Retina via `devicePixelRatio`.
- Styles de fond : mesh gradient pastel, glassmorphism, washi tape, couleur unie.
- Formes : coins arrondis, pilule, carrés subtils.
- Décorations : sparkles vectorielles (toggle), ombre douce sous le texte.

## Personnalisation

- **Couleurs libres** : 4 `<input type="color">` (fond, dégradé, texte, bordure) — les presets remplissent les pickers.
- **Sliders** : hauteur, épaisseur de bordure (0–4 px), taille de texte (16–34 px), letter-spacing (0–6 px).
- **Upload** : logo/émote PNG dessiné à gauche du texte.
- **Polices** : Nunito, Fredoka, Plus Jakarta Sans, Playfair, Space Grotesk.
- **Option** : tout en majuscules.
- **Presets 1 clic** : Strawberry Milk, Lavender Lofi, Matcha Latte, Clean Studio.

## Préview & Export

- Aperçu **mode Twitch** (fond `#18181b`, header fake chaîne, grille 3 colonnes).
- Clic sur un panneau = copie PNG directe (`navigator.clipboard.write` / ClipboardItem).
- Export `.zip` global via JSZip CDN — PNG 320×H, nommés `01-a-propos.png`…

## Générateur de bio setup

- Checkboxes de produits (micros, casques, accessoires, lumière) → Markdown :
  `- **Micro :** [Fifine AM8 blanc](https://www.amazon.fr/dp/ASIN?tag=missstrm-21)`
- **Ajout libre** : catégorie + nom du produit → lien recherche Amazon tagué
  `https://www.amazon.fr/s?k={nom}&tag=missstrm-21`
- Copie en un clic via `navigator.clipboard`.

## Stack

Astro statique, Tailwind v4, JS vanilla + Canvas API, JSZip 3.10.1 (CDN jsdelivr). Aucune dépendance serveur.

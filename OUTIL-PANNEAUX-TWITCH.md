# Studio de Panneaux Twitch & Bio Setup

Page : `/outils/panneaux-twitch/` — `src/pages/outils/panneaux-twitch.astro`

Mini-SaaS 100 % client-side (Canvas API, zéro backend). Deux onglets :
**🎨 Créateur de Panneaux** et **📝 Bio Setup**.

## Moteur Canvas

- Largeur Twitch **320 px**, hauteur réglable 70–140 px, net Retina (`devicePixelRatio`).
- Fonds : mesh gradient (angle 0–360°), couleur unie, glassmorphism, washi tape, **image perso uploadée** (cover-crop).
- Textures : grid lofi, polka dots, sparkles.
- Typo : 5 polices (Nunito, Fredoka, Jakarta, Playfair, Space Grotesk), taille 16–34 px, letter-spacing, majuscules.
- Effets texte : ombre douce, sticker (contour blanc), retro shadow, néon.
- Sous-titre par panneau (position fixe H×0.72).
- Stickers vectoriels canvas : cœur, manette, étoile, nœud.
- Logo/émote uploadé : gauche/droite/haut + taille slider.

## Personnalisation

- 4 swatches couleur (Couleur 1, Couleur 2, texte, bordure) + HEX affiché.
- Toggle **couleur par panneau** (picker par tag).
- Panneaux : tags renommables + sous-titre + `×` supprimer + ajout libre.
- Presets 1 clic bicolores contrastés (Strawberry, Lavender, Matcha, Studio).
- Sliders : hauteur, bordure (effet sticker à 2px), angle dégradé.

## Preview Twitch

- Fausse interface (`#18181b`) avec pseudo + avatar éditables en direct.
- Sélecteur d'ambiance segmenté : 🌙 Sombre / ☀️ Clair / 🎨 Personnalisé (uni, dégradé C1→C2, ou **image de fond uploadée**).
- Clic sur un panneau = copie PNG directe (`ClipboardItem`).
- Sticky `lg:top-24` pendant le scroll de l'éditeur.

## Export

- **Pack complet ZIP** (JSZip CDN) : panneaux PNG + bannière 1200×480 + écran « live bientôt » 1920×1080, même charte.
- **État sauvegardé dans l'URL** (`#hash` base64) : partage/template sans compte.

## Onglet Bio Setup

- Grille de produits avec miniatures Amazon (`/images/products/{asin}.webp`) + checkbox.
- Ajout libre : catégorie + nom → lien recherche tagué `amazon.fr/s?k=…&tag=missstrm-21`.
- Éditeur Markdown style Twitch (fond `#18181b`, bouton `#9146FF`, copie clipboard).

## UX

- Bloc onboarding 3 étapes, guide d'installation Twitch en bas de page (SEO).
- Outil référencé dans le hub `/outils/` (carte avec bannière 16:9).

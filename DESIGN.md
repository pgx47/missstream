# Miss Stream — Design System

Direction artistique : **cozy tech / studio pastel chic**. Cible : créatrices
de contenu (Twitch, YouTube, TikTok) qui veulent un setup beau et performant.
Anti "blog rose bonbon années 2000" : fond neutre, accents poudrés, arrondis marqués.

## Palette (Tailwind v4 `@theme`, `src/styles/global.css`)

| Token | Hex | Usage |
|---|---|---|
| `brand-primary` | `#F472B6` | rose poudré — liens, accents, dates |
| `brand-secondary` | `#C084FC` | lavande — section actualités, dégradés |
| `brand-accent` | `#FB7185` | corail — CTA, hover |
| `surface-bg` | `#FAF7F9` | fond crème teinté |
| `surface-card` | `#FFFFFF` | cartes |
| `text-main` | `#1F2937` | titres, corps fort |
| `text-muted` | `#6B7280` | texte secondaire |

Dégradés signature : `from-pink-500 to-rose-400` (boutons),
`from-pink-400 to-purple-400` (logo, titres hero).

## Typographie

- **Nunito Variable** (`@fontsource-variable/nunito`) — ronde, friendly, auto-hébergée
- Hiérarchie : titres `font-extrabold` (800), corps `leading-relaxed`, micro-labels `text-xs uppercase tracking-widest`

## Composants

| Composant | Rôle | Pattern visuel |
|---|---|---|
| `BaseLayout` | header sticky blur + footer 3 cols + disclosure affiliation | glassmorphism `bg-white/80` |
| `ArticleLayout` | fil d'Ariane, hero image 2:1, sommaire, produits, FAQ accordéon | carte blanche `rounded-2xl` |
| `AffiliateBox` | fiche produit : badge, +/− en 2 colonnes, CTA gradient | bord `pink-100`, hover shadow |
| `DealCard` | bon plan : badge promo, zéro prix en dur (TOS) | `hover:-translate-y-0.5` |
| `SeoSchema` | JSON-LD Article/FAQ/Breadcrumb/WebSite | — |

## Pages

- `/` hero gradient pink→purple, carte "à la une" split image/texte, grille 3 cols
- `/articles/` grille cards `h-40 object-cover`
- `/actualites/` même grille, accents lavande (`purple-100/500`)
- `/bons-plans/` grille 4 cols de DealCards
- `/a-propos/` `/mentions-legales/` prose simple

## Règles composants

- Cartes : `rounded-2xl bg-white border border-pink-100 shadow-sm`, hover `shadow-md -translate-y-0.5`
- Images : **toujours** `object-cover` + hauteur fixe ou `aspect-[2/1]` — ratio source 1200×630
- CTA Amazon : gradient pink→rose, `rel="nofollow sponsored noopener"`, jamais de prix
- Badges : `rounded-full` uppercase `text-xs`, rose (guides) / lavande (news) / gradient (deals)
- Zéro emoji dans le contenu et le design

## Images

- Ratio unique **1200×630** (Open Graph safe)
- Pipeline `generate_article.py` : Unsplash (vraies photos) → Pollinations/FLUX → `public/images/fallbacks/`
- Upload R2 `images-missstream` → `images.missstream.xyz` sinon `public/images/guides/`
- Frontmatter `image:` validé par Zod (`src/content.config.ts`)

## Ton éditorial

Informatif, direct, bienveillant, retour d'expérience. Interdit : clichés IA
("Plongeons dans l'univers", "En conclusion"), jargon tech-bro, prix figés,
promesses vides. Chaque produit a des défauts listés.

## SEO / Perf

- Astro 100 % statique, zéro JS côté client
- JSON-LD Article + FAQ + Breadcrumb par page
- Sitemap auto (`@astrojs/sitemap`), canonical, OG/Twitter cards
- Disclosure affiliation en footer + bas d'article (conformité Amazon)

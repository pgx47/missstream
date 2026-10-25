# Miss Stream — Architecture

Site de niche affilié Amazon, 100 % statique, contenu généré automatiquement.

- **Domaine** : missstream.xyz (Pages `missstream.pages.dev`)
- **Stack** : Astro 7 + @astrojs/mdx + Tailwind v4 + @astrojs/sitemap + content collections Zod
- **Hébergement** : Cloudflare Pages (deploy via Wrangler en CI)
- **Images** : Cloudflare R2 (`images.missstream.xyz`) + fallbacks locaux `public/images/`
- **Tag Amazon** : `streamlibfr0f-21` (`src/site.config.ts`) — injecté dans les pages via `SITE.amazonTag`, jamais hardcodé
- **LLM** : DeepSeek (`deepseek-flash`), chaîne de secours OpenRouter → Anthropic

## Secrets GitHub configurés

| Secret | Rôle |
|---|---|
| `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` | Deploy Pages |
| `R2_ACCESS_KEY_ID` + `R2_SECRET_ACCESS_KEY` + `R2_BUCKET`/`R2_PUBLIC_URL` | Upload images R2 |
| `SCRAPER_API_KEY` | Scraping Amazon (ASINs, images, notes, og:image) |
| `DEEPSEEK_API_KEY` | Génération articles/news/bios |
| `INDEXNOW_KEY` | Ping Bing/Yandex (clé fichier `public/`) |
| `GOOGLE_SA_JSON` | Google Indexing API (service account) |
| `UNSPLASH_ACCESS_KEY` | Photos fallback |
| `PINTEREST_ACCESS_TOKEN` + `PINTEREST_BOARD_ID` | Autopost épingles (❌ en attente) |

## Workflows (`.github/workflows/`)

| Workflow | Cron | Action |
|---|---|---|
| `deploy.yml` | push `main` | Build → `wrangler pages deploy dist` (~30s) |
| `publish.yml` | lun/mer/ven 08:00 UTC | `generate_article.py` : 1 guide MDX + image + pin + pings index |
| `news.yml` | mar/jeu/sam 10:00 UTC | `fetch_news.py` : 1 brève RSS + image + pings |
| `deals.yml` | lun/mer/ven 06:00 UTC | `fetch_deals.py` : refresh `deals.json` (garde-fou anti-[]) |
| `maintenance.yml` | dimanche | `refresh_products.py` (ASINs/notes) + `expand_streamers.py` + `build_feature_pages.py` |

Tous les `contents: write`, déclenchables `workflow_dispatch`, jamais de `[skip ci]`.

## Pipeline de contenu

- **Guides** : sujets de `scripts/topics.json` (pending→done), auto-refill 15 sujets si ≤2.
  Maillage interne sur slugs réels, FAQ schema, produits `<AffiliateBox/>` enrichis
  ScraperAPI (ASIN + image + note). Duel `vs` : tableau comparatif + verdict.
- **News** : RSS Google News (Elgato, Razer, Logitech, Twitch, TikTok), image :
  og:image ScraperAPI → Unsplash → pool local.
- **Images articles** : Unsplash → Pollinations/FLUX → fallbacks locaux, prompts
  pastel/bright verrouillés.
- **Streamers** : `expand_streamers.py` hebdo — DeepSeek propose profils, avatars
  Twitch, bios 300 mots, produits ASINs enrichis.
- **Épingles** : `make_pin.py` 1000×1500 → `public/images/pins/` (supporte URLs R2).

## Pages & outils

`/articles/`, `/actualites/`, `/bons-plans/`, `/streamers/` (+7 profils),
`/configurateur/` (packs 150/400/900), `/lookbook/`, `/dupes/`, `/quiz/`,
`/checklist/`, `/glossaire/`, `/couleurs/*`, `/avant-apres/`, `/streamers/[slug]/`
(bios, tableau récap, FAQ JSON-LD), hub `/outils/` + `/outils/panneaux-twitch/`
(mini-SaaS canvas 100% client — cf. OUTIL-PANNEAUX-TWITCH.md).

## SEO

Sitemap-index, robots, IndexNow + Google Indexing API à chaque publication,
Product/Review/FAQPage JSON-LD, E-E-A-T (à propos, contact, confidentialité).

## Commandes

```bash
npm run dev / npm run build
python3 scripts/generate_article.py   # 1 guide
python3 scripts/fetch_news.py         # 1 news
python3 scripts/fetch_deals.py        # refresh deals
python3 scripts/expand_streamers.py   # +3 profils streamers
python3 scripts/make_pin.py <slug>    # épingle Pinterest
```

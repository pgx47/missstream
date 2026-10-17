# Miss Stream — Architecture

Site de niche affilié Amazon, 100 % statique, contenu généré automatiquement.

- **Domaine** : missstream.xyz
- **Stack** : Astro 7 + @astrojs/mdx + Tailwind CSS v4 + @astrojs/sitemap
- **Hébergement** : Cloudflare Pages (projet `missstream`, déploiement via Wrangler en CI)
- **Tag Amazon** : `duckurbate-21` (configuré dans `src/site.config.ts`)
- **LLM** : DeepSeek (`api.deepseek.com`, modèle `deepseek-chat` par défaut, compatible OpenRouter via variables)

## Secrets GitHub à créer (Settings → Secrets and variables → Actions)

| Secret | Rôle | Statut |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | Déploiement Pages | ✅ configuré |
| `CLOUDFLARE_ACCOUNT_ID` | Compte Cloudflare | ✅ configuré |
| `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` | Stockage images R2 | ✅ configuré |
| `SCRAPER_API_KEY` | Scraping Amazon (deals) + og:image news | ✅ configuré |
| `INDEXNOW_KEY` | Ping IndexNow (fichier clé dans `public/`) | ✅ configuré |
| `DEEPSEEK_API_KEY` | Génération articles + news | ❌ à renseigner |
| `OPENROUTER_API_KEY` / `ANTHROPIC_API_KEY` | LLM de secours | ❌ optionnel |
| `UNSPLASH_ACCESS_KEY` | Fallback images niveau 2 | ❌ optionnel |

Variables (onglet *Variables*) : `AMAZON_TAG` ✅, `R2_BUCKET` ✅ (`images-missstream`),
`R2_PUBLIC_URL` ❌ (URL publique du bucket à activer), `LLM_BASE_URL`, `LLM_MODEL`.

Le LLM suit la chaîne DeepSeek → OpenRouter → Anthropic : un seul des trois
suffit pour faire tourner la génération.

## Workflows

| Workflow | Cron | Action |
|---|---|---|
| `deploy.yml` | push `main` | Build Astro → `wrangler pages deploy dist` |
| `publish.yml` | lun & jeu 08:00 UTC | `generate_article.py` → commit guide + image + topics.json |
| `deals.yml` | quotidien 06:00 UTC | `fetch_deals.py` → commit `src/data/deals.json` |
| `news.yml` | mar & ven 10:00 UTC | `fetch_news.py` → commit brève MDX |

Tous les workflows sont déclenchables à la main (`workflow_dispatch`).

## Pipeline de contenu

- **Guides** (`src/content/guides/*.mdx`) : sujets tirés de `scripts/topics.json`
  (statut `pending` → `done`). Si ≤ 2 sujets restants, le script en régénère 15
  via LLM — le backlog ne s'épuise jamais. Maillage interne obligatoire (2 liens).
- **News** (`src/content/news/*.mdx`) : flux RSS Google News filtré (Elgato, Razer,
  Logitech, Twitch, TikTok, setup streaming), 1 brève max par run.
- **Images** : Pollinations/FLUX → Unsplash → `public/images/fallbacks/*.webp`.
- **Deals** (`src/data/deals.json`) : scraping Amazon via ScraperAPI. Aucun prix
  figé — conformité TOS Amazon (badges "Promo en cours" uniquement).

## Validation frontmatter

Schémas Zod dans `src/content.config.ts` (Astro ≥5 : ce fichier remplace
l'ancien `src/content/config.ts`). ASIN validé en 10 car. alphanumériques ;
si absent, les liens d'affiliation basculent sur une recherche Amazon taguée.

## Mise en production (première fois)

1. `gh repo create missstream --private --source=. --push`
2. DNS : domaine sur Cloudflare, créer le projet Pages `missstream` ou laisser
   le premier `wrangler pages deploy` le créer.
3. Brancher `missstream.xyz` en custom domain dans Pages.
4. Injecter les secrets ci-dessus, lancer `Publish guide` manuellement pour tester.
5. Google Search Console : TXT DNS dans Cloudflare, soumettre `sitemap-index.xml`.

## Commandes

```bash
npm run dev      # dev local
npm run build    # build statique → dist/
python3 scripts/generate_article.py   # générer un guide en local (env vars requises)
python3 scripts/fetch_news.py
python3 scripts/fetch_deals.py
```

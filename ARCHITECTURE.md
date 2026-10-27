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


## Rendez-vous des rubriques (27 octobre 2026)

- **Mercredi, 08:00 UTC** : `inspiration.yml` ajoute au plus une ambiance illustrée au lookbook. L’accueil reprend les dernières inspirations datées. Horaire Paris : 09h hiver / 10h été ; GitHub peut retarder le cron.
- **Dimanche, 06:00 UTC** : `maintenance.yml` contrôle 40 ASINs uniques en rotation parmi guides, bons plans, déco, lookbook, packs, alternatives et streamers ; ajoute jusqu’à 4 objets déco et une paire d’alternatives avec prix observés. Paris : 07h hiver / 08h été.
- Les anciennes sélections restent conservées : suppression des régénérations complètes concurrentes. Plus de plafond de 80 objets / 12 ambiances bloquant les ajouts.
- `build_feature_pages.py` conserve les packs et actualise leurs statuts ; aucun remplacement automatique sans budget/compatibilité vérifiés. Le quiz utilise les catalogues plutôt qu’une liste indépendante figée.
- `product-health.json` conserve le curseur, la dernière observation et la dernière tentative. Une réponse vide, un quota ou une erreur réseau restent indéterminés et ne prouvent pas une indisponibilité. Seule une indisponibilité explicite du produit exact masque sa recommandation. Le contrôle complet tourne sur plusieurs semaines, pas à chaque passage.
- Les nouveautés utilisent les noms et ASINs réellement renvoyés par le fournisseur. Un lookbook exige trois produits distincts et une couverture locale valide. Les nouvelles alternatives exigent deux prix observés et une économie positive ; pas de promesse de performances identiques.
- Chaque section ne publie qu’une fois par semaine ISO ; les relances sans nouveauté sont sans effet. En cas d’échec, pas de commit de contenu. Résumé dans GitHub Actions ; échec visible si toutes les vérifications sont indéterminées.
- Tests Python/Node, validation non destructive et build avant publication. Les deux workflows proposent un mode manuel `dry_run` sans appel fournisseur, modification ou publication.
- Rotation hebdomadaire des profils mis en avant ; fiches présentées comme inspirations et non comme inventaire officiel. L’ajout automatique de nouvelles personnes n’est plus couplé à la maintenance : il attend des sources fiables avant reprise. Les profils existants et leur actualisation trimestrielle sont conservés.
- Bannière liée à un guide existant adapté à la saison ; thème mensuel du générateur de panneaux si disponible. Guides/actus/bons plans conservent leurs crons existants. Aucune publication LinkedIn.

Vérification locale : `python -m unittest discover -s scripts/tests -v`, `node --test src/lib/content-selection.test.mjs`, `python scripts/validate_content.py`, `npm run build`.

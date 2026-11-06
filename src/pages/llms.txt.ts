import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { SITE } from '../site.config';

export const GET: APIRoute = async () => {
  const guides = (await getCollection('guides', ({ data }) => !data.draft)).sort(
    (a, b) => b.data.publishDate.getTime() - a.data.publishDate.getTime(),
  );
  const news = (await getCollection('news', ({ data }) => !data.draft)).sort(
    (a, b) => b.data.publishDate.getTime() - a.data.publishDate.getTime(),
  );

  const link = (title: string, path: string, description?: string) =>
    `- [${title.replace(/[[\]]/g, '')}](${new URL(path, SITE.url).href})${description ? ` — ${description}` : ''}`;

  const lines = [
    `# ${SITE.name}`,
    `> ${SITE.description}`,
    '',
    `Site éditorial francophone (${SITE.url}) : guides d'achat testés, comparatifs, dupes et inspirations de setups de streaming pastel et cozy. Les liens produits renvoient vers Amazon France via des liens affiliés (rel="sponsored nofollow").`,
    '',
    `Contenu éditorial intégral en un seul fichier : ${new URL('/llms-full.txt', SITE.url).href}`,
    '',
    '## Pages clés',
    link('Guides et tests', '/articles/'),
    link('Bons plans', '/bons-plans/'),
    link('Lookbook', '/lookbook/'),
    link('Déco', '/deco/'),
    link('Inspirations streamers', '/streamers/'),
    link('Dupes et alternatives', '/dupes/'),
    link('Outils gratuits', '/outils/'),
    link('Configurateur de setup', '/configurateur/'),
    link('Glossaire du streaming', '/glossaire/'),
    link('Actualités', '/actualites/'),
    '',
    '## Guides et comparatifs',
    ...guides.map((g) => link(g.data.title, `/articles/${g.id}/`, g.data.description)),
    '',
    '## Actualités',
    ...news.map((n) => link(n.data.title, `/actualites/${n.id}/`, n.data.description)),
    '',
    '## À propos',
    `Miss Stream est un guide indépendant : chaque produit recommandé est choisi pour son rendu en caméra et son intégration dans un espace de vie, pas seulement pour sa fiche technique. Contact : ${SITE.email}.`,
    `Dernière mise à jour : ${new Date().toISOString().slice(0, 10)}.`,
    '',
  ];

  return new Response(lines.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};

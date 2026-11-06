import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { SITE } from '../site.config';

/** Version texte intégrale du site, pour les moteurs de réponse et les agents.
 *  Convention llms-full.txt : tout le contenu éditorial en un seul fichier. */
function toPlain(body: string): string {
  return body
    .replace(/<AffiliateBox[^>]*\/>/g, '')
    .replace(/<[^>]+>/g, '')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1 ($2)')
    .replace(/^#{1,6}\s*/gm, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

export const GET: APIRoute = async () => {
  const guides = (await getCollection('guides', ({ data }) => !data.draft)).sort(
    (a, b) => b.data.publishDate.getTime() - a.data.publishDate.getTime(),
  );
  const news = (await getCollection('news', ({ data }) => !data.draft)).sort(
    (a, b) => b.data.publishDate.getTime() - a.data.publishDate.getTime(),
  );

  const parts: string[] = [
    `# ${SITE.name} — contenu complet`,
    `> ${SITE.description}`,
    '',
    `Contact : ${SITE.email}`,
    `Date de génération : ${new Date().toISOString().slice(0, 10)}`,
    '',
  ];

  for (const entry of guides) {
    parts.push(
      `---`,
      `## ${entry.data.title}`,
      `URL : ${new URL(`/articles/${entry.id}/`, SITE.url).href}`,
      `Publié le : ${entry.data.publishDate.toISOString().slice(0, 10)}`,
      entry.data.description,
      '',
      toPlain(entry.body ?? ''),
      '',
    );
  }

  for (const entry of news) {
    parts.push(
      `---`,
      `## ${entry.data.title}`,
      `URL : ${new URL(`/actualites/${entry.id}/`, SITE.url).href}`,
      `Publié le : ${entry.data.publishDate.toISOString().slice(0, 10)}`,
      entry.data.description,
      '',
      toPlain(entry.body ?? ''),
      '',
    );
  }

  return new Response(parts.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};

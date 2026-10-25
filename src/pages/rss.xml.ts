import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { SITE } from '../site.config';

const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export const GET: APIRoute = async () => {
  const [guides, news] = await Promise.all([
    getCollection('guides', ({ data }) => !data.draft),
    getCollection('news', ({ data }) => !data.draft),
  ]);

  const items = [
    ...guides.map((g) => ({
      title: g.data.title,
      link: `${SITE.url}/articles/${g.id}/`,
      date: g.data.publishDate,
      description: g.data.description,
    })),
    ...news.map((n) => ({
      title: n.data.title,
      link: `${SITE.url}/actualites/${n.id}/`,
      date: n.data.publishDate,
      description: n.data.description,
    })),
  ].sort((a, b) => b.date.getTime() - a.date.getTime());

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>${esc(SITE.name)}</title>
<link>${SITE.url}</link>
<description>${esc(SITE.description)}</description>
<language>fr-FR</language>
<lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
<atom:link href="${SITE.url}/rss.xml" rel="self" type="application/rss+xml" />
${items
  .map(
    (i) => `<item>
<title>${esc(i.title)}</title>
<link>${i.link}</link>
<guid isPermaLink="true">${i.link}</guid>
<pubDate>${i.date.toUTCString()}</pubDate>
<description>${esc(i.description)}</description>
</item>`,
  )
  .join('\n')}
</channel>
</rss>`;

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
};

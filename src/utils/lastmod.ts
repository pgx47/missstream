import { execFileSync } from 'node:child_process';

const cache = new Map<string, Date | null>();

function gitLastCommit(collection: 'guides' | 'news', id: string): Date | null {
  const key = `${collection}/${id}`;
  if (cache.has(key)) return cache.get(key) ?? null;
  let date: Date | null = null;
  try {
    const out = execFileSync(
      'git',
      ['log', '-1', '--format=%cI', '--', `src/content/${collection}/${id}.mdx`],
      { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] },
    ).trim();
    if (out) {
      const d = new Date(out);
      if (!Number.isNaN(d.getTime())) date = d;
    }
  } catch {
    date = null;
  }
  cache.set(key, date);
  return date;
}

/**
 * dateModified fiable : frontmatter prioritaire, sinon date du dernier commit git
 * si (et seulement si) elle est postérieure à la publication.
 */
export function resolveUpdatedDate(
  collection: 'guides' | 'news',
  id: string,
  publishDate: Date,
  frontmatterUpdated?: Date,
): Date | undefined {
  if (frontmatterUpdated && frontmatterUpdated.getTime() > publishDate.getTime()) return frontmatterUpdated;
  const git = gitLastCommit(collection, id);
  if (git && git.getTime() > publishDate.getTime() + 24 * 3600 * 1000) return git;
  return undefined;
}

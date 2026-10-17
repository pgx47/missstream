export const SITE = {
  name: 'Miss Stream',
  domain: 'missstream.xyz',
  url: 'https://missstream.xyz',
  tagline: 'Setups streaming cozy & pastel',
  description:
    "Guides d'achat, comparatifs et bons plans pour un setup de streaming esthétique : micros, casques, chaises, LED pastel et accessoires cozy pour créatrices de contenu.",
  amazonTag: 'missstrm-21',
  locale: 'fr_FR',
  lang: 'fr',
  email: 'contact@missstream.xyz',
  affiliationDisclosure:
    "Miss Stream participe au Programme Partenaires d'Amazon EU. En tant que Partenaire Amazon, nous percevons une commission sur les achats qualifiés, sans surcoût pour vous.",
} as const;

export function amazonUrl({ asin, query }: { asin?: string; query?: string }): string {
  if (asin) {
    return `https://www.amazon.fr/dp/${asin}?tag=${SITE.amazonTag}`;
  }
  const q = encodeURIComponent(query ?? 'setup streaming');
  return `https://www.amazon.fr/s?k=${q}&tag=${SITE.amazonTag}`;
}

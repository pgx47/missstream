import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const faqItem = z.object({
  question: z.string(),
  answer: z.string(),
});

const product = z.object({
  nom: z.string(),
  asin: z
    .string()
    .regex(/^[A-Z0-9]{10}$/i, 'ASIN Amazon invalide')
    .optional(),
  couleur: z.string().optional(),
  badge: z.string().optional(),
  pointsForts: z.array(z.string()).min(1),
  pointsFaibles: z.array(z.string()).min(1),
});

const guides = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/guides' }),
  schema: z.object({
    title: z.string(),
    description: z.string().max(170),
    publishDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    image: z.string(),
    category: z.string().default('guides'),
    faq: z.array(faqItem).default([]),
    products: z.array(product).default([]),
    draft: z.boolean().default(false),
  }),
});

const news = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/news' }),
  schema: z.object({
    title: z.string(),
    description: z.string().max(170),
    publishDate: z.coerce.date(),
    category: z.string().default('news'),
    image: z.string(),
    sourceUrl: z.string().url().optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { guides, news };

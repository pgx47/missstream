import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://missstream.xyz',
  integrations: [
    mdx(),
    sitemap({
      filter: (page) => !page.includes('/go/'),
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});

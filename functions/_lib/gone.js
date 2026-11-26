// Réponse 410 pour les espaces d'URL de l'ancien site (ferme de contenu /
// streaming) qui ne doivent jamais revenir. 410 indique à Google une
// suppression définitive : l'URL sort de l'index plus vite qu'avec un 404.
export function gone(request) {
  return new Response(
    '410 Gone — cette adresse appartenait à une ancienne version du site et a été définitivement supprimée.\n' +
      'Le site actuel : https://missstream.xyz/\n',
    {
      status: 410,
      headers: {
        'content-type': 'text/plain; charset=utf-8',
        'cache-control': 'public, max-age=86400',
        'x-robots-tag': 'noindex',
      },
    },
  );
}

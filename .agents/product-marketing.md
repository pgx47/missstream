# Miss Stream — contexte marketing

> Document de référence lu par les skills marketing avant toute action.
> Dernière mise à jour : 2026-11-06.

## Le produit

**Miss Stream** (`https://missstream.xyz`) est un média éditorial indépendant francophone
consacré aux **setups de streaming esthétiques, pastel et cozy**, pour les créatrices de
contenu (Twitch, YouTube, TikTok) et les personnes qui débutent.

Ce n'est pas un SaaS ni une boutique : le site ne vend rien. Il publie des guides d'achat
testés, des comparatifs, des dupes et des outils gratuits, et monétise via le **Programme
Partenaires Amazon** (tag `4751233-21`).

- Modèle : affiliation Amazon, liens `rel="sponsored nofollow"` via la redirection interne `/go/`.
- Pas de compte utilisateur, pas de panier, pas d'email list pour l'instant.
- Publication automatisée : guides et brèves générés par LLM, enrichis par scraping Amazon
  (ASIN, visuels, notes), puis validés par un garde-fou (aucune carte produit sans image).
- Rythme : 1 guide lundi/mercredi/vendredi, 1 brève d'actualité par jour, deals quotidiens.

## Audience

**Cœur de cible** : femme de 18-30 ans, francophone, qui streame ou veut se lancer, avec un
budget contraint (souvent 150-400 € pour démarrer) et une contrainte forte : son bureau est
dans une **pièce de vie** (chambre, salon), pas un studio.

Ce qu'elle cherche, dans l'ordre :
1. un rendu propre à la caméra sans matériel de pro ;
2. des objets qui ne jurent pas avec un intérieur clair (blanc, pastel, bois clair) ;
3. des recommandations honnêtes, y compris sur les défauts ;
4. un budget maîtrisé, avec des alternatives moins chères.

Ce qu'elle fuit : le vocabulaire « gamer » agressif, le RGB criard, les comparatifs qui
récitent des fiches techniques, les listes de 20 produits sans verdict.

## Positionnement

**« Le guide indépendant du setup qui rend bien à l'image. »**

Différenciation : le site juge les produits sur leur **rendu en caméra et leur intégration
dans un espace de vie**, pas seulement sur la fiche technique. Chaque guide assume un
défaut, donne un verdict par profil et propose une alternative petit budget.

Concurrents éditoriaux : les médias tech généralistes (Les Numériques, Clubic) qui couvrent
le matériel gaming sans l'angle déco, et les blogs setup anglophones. Le créneau
« cozy/pastel francophone avec verdict honnête » est peu occupé.

## Ton et voix

- Français direct, tutoiement, phrases courtes.
- On parle à une personne (« tu »), jamais « nos chers utilisateurs ».
- Un avis assumé par guide, avec le défaut dit franchement.
- Zéro emoji dans le corps, zéro « plongeons dans l'univers », zéro « il est important de noter ».
- Les prix sont donnés en ordre de grandeur (« autour de 100 € »), jamais figés dans le temps.

## Ce qui compte (KPI)

| Objectif | Indicateur | État |
|---|---|---|
| Trafic organique | sessions Search Console | ❌ non branché |
| Clics affiliés | visites de `/go/` (Cloudflare Web Analytics) | ✅ mesurable depuis 2026-11 |
| Revenu | commissions Amazon | ❌ à rapprocher du nombre de clics |
| Contenu | guides publiés / sujets en réserve | 23 / 30 |

## Contraintes techniques utiles aux skills

- Site 100 % statique (Astro), déployé sur Cloudflare Pages : pas de backend, pas de test A/B
  serveur, pas de personnalisation.
- Les liens produits passent tous par `/go/?a=ASIN` ou `/go/?q=requête`.
- Le contenu est dans `src/content/guides/*.mdx` (frontmatter + corps MDX) ; les données
  produits dans `src/data/*.json`.
- Toute carte produit sans ASIN **ou** sans image locale bloque le déploiement
  (`validate_content.py`).

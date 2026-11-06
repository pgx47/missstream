# Acquisition de liens — Miss Stream

> Skill utilisée : `link-building`. Constat d'audit : aucun profil de backlinks mesuré
> (pas d'Ahrefs/Semrush), site de 80 pages lancé en octobre 2026. L'autorité est le vrai
> plafond, pas le contenu.

## 1. Les actifs déjà linkables

| Actif | URL | Pourquoi quelqu'un le linkerait |
|---|---|---|
| Générateur de panneaux Twitch | `/outils/panneaux-twitch/` | outil gratuit, résultat immédiat, se partage dans les Discord de créateurs |
| Configurateur de budget | `/configurateur/` | « quel setup pour 400 € » est une question récurrente |
| Checklist avant-live | `/checklist/` | ressource à épingler dans un serveur |
| Glossaire du streaming | `/glossaire/` | ressource de référence pour expliquer le jargon |
| Comparatifs « X vs Y » | `/articles/…` | réponse sourçable pour un forum |

Le générateur de panneaux est le seul actif réellement **unique et partageable** : c'est lui
qui doit porter la campagne de liens.

## 2. Cibles (par ordre de rendement attendu)

1. **Discord et subreddits de créateurs francophones** — partage du générateur, pas du site
   en général. Lien souvent en `nofollow`, mais trafic qualifié et premières citations.
2. **Blogs et médias « setup / déco / cozy »** — demandes de mention dans les roundups
   « 10 outils pour streamer », « ressources créateurs ».
3. **Chaînes YouTube FR (5k-50k abonnés)** — description de vidéo « mon setup » : proposer
   une sélection de produits blancs/pastel à créditer, sans demander de lien en retour.
4. **Annuaires spécialisés** (via la skill `directory-submissions`) : annuaires d'outils
   gratuits, listes « llms.txt », répertoires de ressources créateurs. Liens faciles, valeur
   faible mais réelle pour la découverte.
5. **Pinterest** — déjà automatisé (épingles générées par `make_pin.py`), à traiter comme un
   canal de trafic, pas de link building.

À éviter : fermes de liens, échanges « je te linke tu me linkes », annuaires généralistes
payants, articles sponsorisés sans `rel="sponsored"`.

## 3. Sprint de 4 semaines

| Semaine | Action | Volume |
|---|---|---|
| 1 | nettoyer le profil existant : vérifier les liens des 3 sites du réseau (streamlib.fr, streamgen.fr), ajouter les liens croisés pertinents | 3 |
| 1 | lister 40 cibles : Discord/Reddit FR, 15 blogs setup, 10 YouTube FR, 15 annuaires | 40 |
| 2 | 15 contacts : partage du générateur de panneaux avec un angle utile | 15 |
| 3 | 10 propositions de roundup + 5 demandes de correction de mentions | 15 |
| 4 | 10 soumissions d'annuaires + relance des non-réponses | 10 |

Objectif réaliste sur 4 semaines : **5 à 10 domaines référents**, dont 2 éditoriaux.

## 4. Modèles de messages (FR)

**Partage d'outil (Discord/Reddit)**

> Salut — j'ai fait un générateur de panneaux Twitch gratuit (export PNG, palette pastel) :
> https://missstream.xyz/outils/panneaux-twitch/
> Si ça sert à quelqu'un ici, servez-vous. Je prends les retours sur les tailles d'export.

**Proposition de roundup**

> Bonjour [prénom], votre article « [titre] » liste des ressources pour créateurs.
> J'ai un générateur de panneaux Twitch gratuit et sans compte, en français, qui pourrait
> compléter la section [X] : [URL]. Je peux vous envoyer une capture ou un jeu de panneaux
> déjà exportés si vous voulez tester avant de l'ajouter.

**Mention non liée**

> Bonjour, merci pour la mention de Miss Stream dans [article].
> Le lien pointe vers l'accueil ; la page la plus utile pour vos lecteurs serait plutôt
> [URL précise]. Aucun problème si vous préférez laisser tel quel, je voulais juste signaler.

Règles : un message par cible, personnalisé, jamais de relance avant 7 jours, et on arrête
tout dès qu'une personne répond « non ».

## 5. Mesure

Sans Ahrefs : suivre dans Search Console > Liens (dès branchement), et tenir un tableau
`docs/link-prospects.csv` (cible, type, contact, statut, date, URL du lien). Objectif
trimestriel : 15 domaines référents, dont 5 avec un trafic réel.

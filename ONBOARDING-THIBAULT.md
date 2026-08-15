# moncrg-site — onboarding Thibault

> Le site vitrine/funnel de MonCRG. Statique, déployé via **GitHub Pages** : tout push sur
> `main` est mis en ligne sur moncrg.fr (domaine dans `CNAME`). Pas de build, pas de CI.

## Contexte produit
Le POURQUOI du projet, la stratégie, l'audit concurrentiel et le backlog de build sont dans
l'autre repo : **Wasslamenace/alfred-brain**, branche `claude/mon-cgr-status-xl2avb`. Lis
d'abord `ONBOARDING-THIBAULT.md` (racine) et `moncrg/product-backlog.md` là-bas.

## Structure du site
- `index.html` — page principale / funnel (précommande fondateur).
- `conseils/` — 6 guides SEO (l'actif d'acquisition ; ils rankent, on n'y touche pas sans raison).
- `guide.html`, `cgv.html`, `confidentialite.html`, `mentions-legales.html` — pages légales/aide.
- `assets/`, `logo/`, favicons — statique.
- `BRAND.md` — **charte graphique à respecter** (palette « notaire moderne », serif Georgia,
  corps ≥ 18 px, cible 50-75 ans). Lis-la avant de toucher au CSS.
- `CNAME` — domaine. Ne pas modifier.

## Règles de contribution
- Cible = tuteurs familiaux 50-75 ans : gros caractères, fort contraste, zéro jargon startup.
- Respecter `BRAND.md` (couleurs, typos, logo).
- Statique uniquement (HTML/CSS/JS vanilla) — pas de framework, pas de build step.
- ⚠️ CHANTIER EN COURS (décision Wassim 15/08) : bascule du positionnement de
  « logiciel 79 €/an, ouverture mars 2027 » vers **« compte de gestion vérifié et garanti par
  IA »** (offre à l'acte). Le copy actuel (précommande 79 €) est en cours de refonte —
  coordonne-toi avec Wassim/Alfred avant de réécrire la home, la stratégie de prix se décide.
- Tout changement de contenu public = validation Wassim (le site est en ligne en prod).

## Déploiement
Push sur `main` → live sur moncrg.fr en ~1 min. Pas d'étape manuelle. Vérifier le rendu réel
après push.

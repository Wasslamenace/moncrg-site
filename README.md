# moncrg.fr — site MonCRG

Site statique du projet MonCRG (compte de gestion pour tuteurs familiaux).

## ⚠️ RÈGLE N°1 — DÉPLOIEMENT

**`main` = production.** Ce repo est servi par GitHub Pages : tout push sur `main` est **en
ligne sur moncrg.fr dans la minute**, sans étape intermédiaire. Pour toute modification non
triviale : branche + Pull Request, et on merge après relecture.

## Structure

- `index.html` — page d'accueil / offre
- `guide.html` + `guide-decouverte.pdf` — lead magnet (capture email)
- `conseils/` — les guides SEO (le canal d'acquisition n°1 : ne pas casser les URLs)
- `merci.html`, `cgv.html`, `confidentialite.html`, `mentions-legales.html`
- `assets/`, `logo/`, favicons, `CNAME` (domaine — ne pas toucher)
- `BRAND.md` — charte (ton, couleurs, logo)

## Conventions non négociables

1. **Chiffres légaux vérifiés aux sources primaires** (Légifrance, justice.gouv) avant toute
   publication — barèmes, articles de loi, dates limites. Incident passé documenté : un barème
   inventé a dû être corrigé en urgence. En cas de doute : ne pas publier, demander.
2. **JSON-LD** (schema.org) présent sur les pages : le maintenir à jour si le contenu change.
3. **Ton de la marque** : français clair, zéro jargon, pédagogie d'abord, transparence
   (renvoi systématique vers les sources officielles et les ISTF). Voir `BRAND.md`.
4. **Ne pas casser les URL
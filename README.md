# CAP GRANGENT — suivi du lac V1.1

## Ce qui fonctionne
- Interface web responsive, courbe, historique, saisie manuelle, export XLSX et CSV.
- Hébergement statique possible sur GitHub Pages.
- Synchronisation des relevés hébergés depuis `data/releves.json` vers le navigateur.
- Workflow quotidien GitHub Actions, **inactif tant qu'une source de cote NGF n'est pas validée et configurée**.

## Déploiement GitHub Pages
1. Créer un dépôt GitHub et y placer le contenu de ce dossier (y compris `.github`).
2. Settings → Pages → Build and deployment → Deploy from a branch → `main` / `(root)`.
3. Settings → Actions → General → Workflow permissions : Read and write permissions.
4. Après validation technique et juridique d'une API renvoyant la **cote du plan d'eau en m NGF**, créer les secrets Actions `GRANGENT_SOURCE_URL` (URL HTTPS JSON) et `GRANGENT_JSON_LEVEL_KEY` (chemin pointé, p.ex. `niveau_ngf`).
5. Tester manuellement le workflow `Releve quotidien Grangent` et vérifier la mesure par comparaison avec la source officielle.

## Limites importantes
- Le suivi n'est **pas encore autonome** : aucune source JSON NGF certifiée n'est branchée.
- Les saisies manuelles restent **locales au navigateur** ; elles ne sont pas partagées entre appareils.
- Le workflow s'exécute à 08:00 UTC, soit 09:00 l'hiver / 10:00 l'été ; GitHub peut retarder une exécution.
- La récupération automatique depuis une source ne doit pas être activée sur une simple hauteur d'eau hydrométrique non convertie en cote NGF.
- Le seuil 417,50 m est un repère indicatif configurable, pas une décision réglementaire automatisée.

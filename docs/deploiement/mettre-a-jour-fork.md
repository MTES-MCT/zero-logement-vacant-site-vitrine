# Mettre à jour son fork — 🔵 Confirmé

Si votre site tourne sur un fork qui contient ses propres ajouts (une
configuration de déploiement, par exemple), le bouton GitHub « Sync fork »
ne fonctionnera plus : il n'avance votre branche que si elle n'a aucun
commit que le dépôt officiel n'a pas. Il faut alors fusionner à la main.

## Ajouter le dépôt officiel comme remote

Une seule fois :

```sh
git remote add upstream https://github.com/numerique-gouv/sites-conformes.git
```

## Récupérer et fusionner

```sh
git fetch upstream
git checkout main
git merge upstream/main
```

Un fichier que vous êtes seul·e à avoir ne peut pas entrer en conflit. Un
conflit survient seulement si vous avez modifié un fichier que le dépôt
officiel a aussi touché, comme `config/settings.py` ou le `Procfile`. Git
s'arrête alors et vous demande de choisir, fichier par fichier, quelle
version garder avant de commiter.

```sh
git push origin main
```

## Propager sur `production`

Si le déploiement suit la branche `production`, la mise à jour ne s'y
propage pas d'elle-même :

```sh
git checkout production
git merge main
git push origin production
```

Ce push déclenche le déploiement si l'auto-déploiement est configuré sur
`production`.

Pour limiter les conflits, ajoutez de préférence de nouveaux fichiers
plutôt que de modifier ceux du dépôt officiel, et fusionnez souvent plutôt
que d'attendre plusieurs mois.

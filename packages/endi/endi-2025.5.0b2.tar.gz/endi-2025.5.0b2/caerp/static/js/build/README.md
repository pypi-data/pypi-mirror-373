# endi_js_build js builds for published versions of endi

Stores js builds for published versions of endi

## Comment publier ?

- Vous devez déjà avoir une branche/tag nommée pour votre version sur [le dépôt endi/endi](https://framagit.org/endi/endi). Par exemple `1.2.3`
- Créer une branche dans *endi/endi_js_build* (le présent dépôt) du même nom (ex: `1.2.3`)
- Se placer sur cette branche
- Depuis votre copie locale de _endi/endi_ ;construire les dépendances JS : `export ENDI_JS_BUILD_PATH='../endi_js_build/ && make devjs && make prodjs`
- Placer vous dans le répertoire *endi/endi_js_build*
- Commiter et pusher, sans oublier d'ajouter (`git add`) les éventuels nouveaux fichiers js et de supprimer (`git rm`) les anciens.

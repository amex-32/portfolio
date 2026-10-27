# Portfolio

Portfolio d'Alexandre K., en français (racine) et en anglais (`en/`).

Site statique en HTML, CSS et JavaScript, sans dépendance. Les pages sont générées par un petit script Python :

```bash
python3 tools/build.py
python3 -m http.server   # puis http://localhost:8000
```

- `tools/build.py` : gabarits des pages ; `tools/content.py` : textes FR/EN, projets, icônes ; `tools/test.js` : test de la logique des jeux
- `style.css`, `js/site.js` : styles et interactions (palette ⌘K, carrousel, thème, accent)
- `src/game.*` : 2048 (`js/game.js` est généré) ; `js/games.js` : Snake, Memory, Code Breaker
- `src/trees.json` : arborescences affichées sur les pages projet
- `api/scores.js` : classements des 4 jeux, une base MySQL par jeu (`game_2048`, `game_snake`, `game_memory`, `game_code`) ; `js/scores.js` : l'interface

Pour afficher une adresse e-mail ou activer le formulaire de contact, renseigner `EMAIL` ou `FORM_ENDPOINT` en haut de `tools/build.py` puis relancer le script.

## Classements des jeux

La fonction `api/scores.js` tourne sur Vercel et se connecte à une base MySQL (TiDB Cloud). Elle crée les bases et tables au premier appel. Variables d'environnement à définir dans Vercel : `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`.

En local : `npm install`, puis `DB_HOST=… DB_USER=… DB_PASSWORD=… node tools/dev.js` (ajouter `DB_SSL=0` pour un MySQL local sans TLS). Tests : `node tools/test.js && node tools/test-api.js`.

Les scores sont envoyés par le navigateur : ils sont bornés et validés côté serveur, mais restent falsifiables.

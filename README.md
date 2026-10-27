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
- `api/leaderboard.js` : fonction serverless du classement du jeu (voir `docs/`)

Pour afficher une adresse e-mail ou activer le formulaire de contact, renseigner `EMAIL` ou `FORM_ENDPOINT` en haut de `tools/build.py` puis relancer le script.

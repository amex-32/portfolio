# Portfolio

Portfolio d'Alexandre Klotz, en français (racine) et en anglais (`en/`).

Site statique en HTML, CSS et JavaScript, sans dépendance. Les pages sont générées par un petit script Python :

```bash
python3 tools/build.py
python3 -m http.server   # puis http://localhost:8000
```

- `tools/build.py` : textes FR/EN, projets et gabarits des pages
- `style.css`, `js/site.js` : styles et interactions communes (thème, filtres, en-tête)
- `src/game.html`, `src/game.js` : mini-jeu 2048 ; `js/game.js` est généré
- `src/trees.json` : arborescences affichées sur les pages projet
- `api/leaderboard.js` : fonction serverless du classement du jeu (voir `docs/`)

Pour afficher une adresse e-mail sur la page contact, renseigner `EMAIL` en haut de `tools/build.py` puis relancer le script.

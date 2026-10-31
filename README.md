# Portfolio

Portfolio d'Alexandre K., en français (racine) et en anglais (`en/`).

Site en ligne : https://alexandre-k.vercel.app

Site statique en HTML, CSS et JavaScript, sans dépendance. Les pages sont générées par un petit script Python :

```bash
python3 tools/build.py   # sous Windows : PYTHONUTF8=1 python tools/build.py
python3 -m http.server   # puis http://localhost:8000
```

- `tools/build.py` : gabarits des pages, plus `404.html`, `robots.txt`, `sitemap.xml` et `.well-known/security.txt` ; `tools/content.py` : textes FR/EN, projets, write-ups, icônes
- `style.css`, `js/site.js` : styles et interactions (palette ⌘K, terminal `²` ou `` ` ``, carrousel, thème, accent)
- `src/psp3d.js` : console 3D de la page 404. `js/psp3d.js` en est le bundle : `NODE_PATH=<dossier avec three@0.170.0> esbuild src/psp3d.js --bundle --minify --format=iife --outfile=js/psp3d.js`. `model/psp.glb` vient de `tools/psp_model.py` (modèle d'Ilya Ostrovsky, CC BY 4.0)
- `tools/serve.py` : serveur local, renvoie `404.html` comme Vercel
- `src/game.*` : 2048 (`js/game.js` est généré) ; `js/games.js` : Memory, Code Breaker, César
- `src/trees.json` : arborescences affichées sur les pages projet
- `api/scores.js` : classements des 4 jeux, une base MySQL par jeu (`game_2048`, `game_memory`, `game_code`, `game_cipher`) ; `js/scores.js` : l'interface
- `tools/shots.py` : convertit les captures de projets `img/*.jpg` en WebP (1600 px et `-800`)
- `fonts/` : Inter, JetBrains Mono et Space Grotesk (sous-ensemble latin, servies par le site)
- `tools/images.py` : génère `og.png` (aperçu des liens partagés), `favicon.ico` et `apple-touch-icon.png` (Pillow) ; `favicon.svg` est écrit à la main
- `vercel.json` : en-têtes de sécurité (CSP, anti-clickjacking…) ; `.vercelignore` : les fichiers de travail (`tools/`, `src/`…) ne sont pas déployés
- `js/player.js` : lecteur de musique en haut à droite, qui garde le morceau et la position d'une page à l'autre ; morceaux dans `audio/`, liste dans `TRACKS` (`tools/content.py`). Ils sont masterisés à -14 LUFS (ffmpeg : passe-haut 30 Hz, compression 2:1, loudnorm, limiteur -1,5 dB, MP3 192 kbps).
- `js/gallery.js` : galerie (`galerie.html`, vues éparpillée, grille, albums) ; images dans `img/gallery/` (`<slug>.webp` jusqu'à 1800 px et `<slug>-thumb.webp` à 640 px), liste dans `GALLERY` (`tools/content.py`)

Pour afficher une adresse e-mail ou activer le formulaire de contact, renseigner `EMAIL` ou `FORM_ENDPOINT` en haut de `tools/content.py` puis relancer le script.

## Mini-CTF

Six flags sont cachés dans le site ; ils se soumettent dans le terminal (`pseudo …` puis `flag FLAG{…}`). Les flags en clair sont dans `tools/ctf.json` (non déployé) ; `api/ctf.js` ne garde que leurs empreintes SHA-256 et enregistre les flags trouvés dans la base `game_ctf`. Pour changer un flag : `tools/ctf.json`, l'empreinte dans `api/ctf.js`, et sa cachette (`vercel.json` ou `js/site.js` pour les flags 2, 4 et 5 ; commentaire JPEG de `img/gallery/clive-mugshot.jpg` pour le 6). `node tools/test.js` vérifie que chaque flag est à sa place et n'apparaît nulle part ailleurs.

## Classements des jeux

Les fonctions `api/scores.js`, `api/ctf.js` et `api/listen.js` tournent sur Vercel et se connectent à une base MySQL (TiDB Cloud) via un petit pool partagé (`api/_lib.js`, avec l'anti-spam par route). Elles créent les bases et tables au premier appel. Variables d'environnement à définir dans Vercel : `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, et `OWNER_HASH` (empreinte SHA-256 du mot de passe de la commande `login` du terminal). Après `login`, le navigateur garde un cookie de session HttpOnly signé avec cette empreinte (30 jours) ; changer `OWNER_HASH` déconnecte toutes les sessions.

En local : `npm install`, puis `DB_HOST=… DB_USER=… DB_PASSWORD=… node tools/dev.js` (ajouter `DB_SSL=0` pour un MySQL local sans TLS). Tests : `node tools/test.js && node tools/test-api.js`.

Les scores sont envoyés par le navigateur : ils sont bornés et validés côté serveur, mais restent falsifiables.

Le déploiement Vercel se fait à chaque `git push` sur `main`.

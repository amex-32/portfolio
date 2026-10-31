# Design : BLACK BOX

Console de contrôle inspirée de l'interface de Marathon (Bungie) et de Watch Dogs 2. Le site se pilote, il ne se parcourt pas.

## Couleurs

| Rôle | Valeur |
|---|---|
| Fond | `#141414` |
| Panneaux | `#1c1c1c`, `#222` |
| Accent unique | `#c6ff3d`, en aplat avec texte `#0e0e0e` |
| Texte | `#e8e8e2`, secondaire `#8c8c8c`, décor seul `#6e6e6e` |
| Alerte | aplat `#e0201b`, texte `#ff4438`, fond `#2a0606` |
| Code Breaker, mal placé | `#ffb000`, `#5ce1ff` si l'accent est déjà ambre ; toujours doublé de pointillés |

Le rouge `#e0201b` ne sert jamais pour du petit texte sur fond sombre (3,85:1). Thème clair : mode inversé sur `#e8e8e2`, accent texte `#3f6600`, aplats toujours lime.

## Typographie

Departure Mono pour le logo et les titres (tailles multiples de 11 px), JetBrains Mono en majuscules espacées pour l'interface, Inter pour le texte long, jamais en majuscules.

## Mouvement

Steppé : `steps()` ou coupe nette, jamais de rebond. Un écran se construit par couches, séquence de 1,5 s maximum. Retour d'action binaire, gris ou lime.

| Séquence | Emplacement |
|---|---|
| 1 Boot | première page de la session (`.boot`) |
| 2 ENTER PASSWORD | entrée des jeux, décor sans vrai mot de passe |
| 3 Dashboard | accueil, grilles de panneaux |
| 4 Bouton en cours | liens `.btn`, formulaire, scores |
| 5 Rectangle lime | clic sur une carte projet ; version courte pour palette, terminal, visionneuse |
| 6 Radar | À propos |
| 7 SYS BREACH | page 404 et commande `sudo` |

La page 404 montre aussi une console 3D (`model/psp.glb`, three.js dans `js/psp3d.js`) : son écran affiche le vrai lecteur et ses boutons le pilotent. Les images des projets et de la galerie sont en noir et blanc, la couleur revient au survol.

## Mise en page

Rail gauche, barre système, colonne de télémétrie à droite dès 1280 px. L'accueil tient sans scroll dès 1101 × 720 ; ses panneaux défilent en interne. En dessous, une colonne et un dock en bas.

## Code

Tout le décor vit dans `js/hud.js`, sans logique du site. Il se relance à chaque navigation douce et doit couper ses minuteries via `akHudStop`.

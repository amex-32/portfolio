# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Recruteurs et professionnels de la cybersécurité qui évaluent un étudiant pour un stage ou une alternance, et visiteurs curieux venus pour les jeux et le mini-CTF. (Déduit du contenu du site, à confirmer.)

## Product Purpose

Présenter le parcours d'Alexandre K., étudiant en cybersécurité : projets, write-ups, musique, illustrations, et un moyen de le contacter.

## Capabilities and Constraints

Site statique généré par `tools/build.py` (FR à la racine, EN dans `en/`), fonctions serveur dans `api/`, déployé sur Vercel. La CSP n'autorise que le domaine du site : pas de CDN, polices et scripts servis localement. Toute modification du script inline « boot » impose de mettre à jour son empreinte dans `vercel.json`.

## Evidence on Hand

Quatre projets, des write-ups, une galerie d'illustrations, des morceaux dans `audio/`, l'activité GitHub réelle. Ne rien inventer : pas de chiffres ou de pourcentages fictifs présentés comme des données.

## Accessibility & Inclusion

`prefers-reduced-motion` et la commande `motion` coupent les effets. Les écrans animés ne bloquent jamais l'accès au contenu.

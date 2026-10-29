#!/usr/bin/env python3
"""Contenu du site : textes FR/EN, projets, icônes. Les gabarits sont dans build.py."""
import datetime
import json
import os
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
EMAIL = ""  # renseigner pour afficher une adresse e-mail sur la page contact
FORM_ENDPOINT = "https://formspree.io/f/myeewogr"  # service de formulaire (Formspree) ; vide = pas de formulaire
GITHUB = "https://github.com/amex-32"
LINKEDIN = "https://www.linkedin.com/in/alexandre-k-801438256/"
GITHUB_USER = "amex-32"
SITE_REPO = "https://github.com/amex-32/portfolio"
SITE_URL = "https://alexandre-k.vercel.app"
CTF_FLAGS = json.loads((ROOT / "tools/ctf.json").read_text())["flags"]

TREES = json.loads((ROOT / "src/trees.json").read_text())

# ---------------------------------------------------------------- textes
UI = {
    "fr": {
        "nav": ["Accueil", "Projets", "Jeux", "À propos", "Contact", "Write-ups"],
        "avail": "Disponible",
        "status": "Disponible pour stage / alternance · Alpes-Maritimes",
        "title": "Alexandre K. — Portfolio",
        "meta": "Portfolio d'Alexandre K., étudiant en cybersécurité et développement web dans les Alpes-Maritimes.",
        "welcome": "Bienvenue",
        "h1": "Je suis <mark>Alexandre K.</mark>, étudiant en cybersécurité.",
        "bio": "Je me forme à la cybersécurité : reconnaissance et OSINT, administration Linux, pare-feu Stormshield. Je m'entraîne sous Kali Linux et je développe mes applications web en pensant sécurité dès le départ (authentification, droits minimaux, validation des entrées). Je cherche un stage ou une alternance.",
        "cta_projects": "Voir mes projets",
        "cta_contact": "Me contacter",
        "term": [("p", "nmap -sV -p 22,80,443 scanme.nmap.org"), ("c", "# exemple : cible de test officielle de Nmap"), ("", "Nmap scan report for scanme.nmap.org"), ("", "Host is up (0.17s latency)."), ("", ""), ("k", "PORT     STATE  SERVICE  VERSION"), ("", "22/tcp   open   ssh      OpenSSH 6.6.1p1"), ("", "80/tcp   open   http     Apache httpd 2.4.7"), ("", "443/tcp  closed https"), ("", ""), ("p", "")],
        "skills_label": "Compétences",
        "skills_h": "Ce que j'utilise",
        "skills_lead": "Du front au back, avec une approche sécurité dès la conception.",
        "skills": [
            ("Sécurité", ["OSINT", "Stormshield", "Authentification", "Moindre privilège"]),
            ("Systèmes", ["Debian", "Kali Linux", "macOS", "Windows 10 / 11"]),
            ("Back-end & données", ["Node.js", "Go", "API REST", "SQL"]),
            ("Front-end & outils", ["HTML", "CSS", "JavaScript", "Git & GitHub"]),
        ],
        "proj_label": "Projets",
        "proj_h": "Réalisations",
        "proj_lead": "Projets de formation, en solo ou en équipe.",
        "all_projects": "Tous les projets",
        "details": "Détails",
        "code": "Code",
        "crumb_home": "Accueil",
        "crumb_projects": "Projets",
        "list_title": "Mes <em>projets</em>",
        "list_lead": "Tout ce que j'ai construit pendant ma formation. Filtre par type pour t'y retrouver.",
        "all": "Tous",
        "kinds": {"web": "Web", "api": "API"},
        "detail_word": "DÉTAILS", "preview_h": "Aperçu",
        "description": "Description",
        "tech": "Technologies",
        "features": "Fonctionnalités",
        "repo_tree": "Structure du dépôt",
        "facts": "En bref",
        "f_type": "Type",
        "f_context": "Contexte",
        "f_lang": "Langage",
        "f_repo": "Dépôt",
        "context": "Projet de formation",
        "view_code": "Voir le code", "view_demo": "Démo en ligne", "demo_note": "Hébergement gratuit : le premier chargement peut prendre une minute.",
        "similar_small": "Projets similaires",
        "similar_h": "Ça peut <em>t'intéresser</em>",
        "contact_label": "Contact",
        "contact_h": "Travaillons <em>ensemble</em>",
        "contact_lead": "Ouvert aux stages, aux alternances et aux collaborations. Le plus simple : un message sur LinkedIn.",
        "contact_cta_h": "Un message ?",
        "contact_cta_p": "Je réponds sur LinkedIn. Pour un stage ou une alternance, précise les dates et le type de mission.",
        "channels_h": "Où me trouver",
        "looking_h": "Ce que je cherche",
        "looking": ["Un stage ou une alternance en développement web ou en cybersécurité", "Un environnement où l'on apprend en travaillant en équipe", "Alpes-Maritimes, ou à distance"],
        "profile_h": "Profil",
        "profile": [("Zone", "Alpes-Maritimes"), ("Formation", "Ynov, cybersécurité"), ("Langues", "Français, anglais B2"), ("Statut", "Disponible")],
        "write": "Écrire",
        "footer_tag": "Étudiant en cybersécurité et développement web. Merci de votre visite.",
        "f_general": "Général",
        "f_elsewhere": "Ailleurs",
        "source": "Code source du site",
        "rights": "© 2026 Alexandre K.",
        "game_title": "Mini-jeu — 2048",
        "about_title": "À <em>propos</em>",
        "about_lead": "Mon parcours, mon activité sur GitHub, mes outils, et ce que je fais en dehors du code.",
        "gh_small": "Aperçu développeur", "gh_h": "Activité <em>GitHub</em>",
        "gh_total": "contributions sur l'année écoulée", "gh_less": "Moins", "gh_more": "Plus",
        "hw_h": "Matériel", "sw_h": "Logiciels et outils",
        "hardware": [("PC fixe", "Windows 11", "desktop"), ("MacBook Pro 16\"", "Puce M3 Pro", "laptop"), ("NAS", "Stockage réseau", "nas")],
        "months": ["Janv", "Févr", "Mars", "Avr", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"],
        "days": ["", "Lun", "", "Mer", "", "Ven", ""],
        "game_page": "Mini-<em>jeu</em>",
        "game_lead": "Une pause : le 2048, avec un classement partagé.",
        "form_h": "Écrire un message",
        "form_name": "Nom", "form_email": "Votre e-mail", "form_msg": "Message", "form_send": "Envoyer",
        "form_ok": "Message envoyé, merci !", "form_err": "Échec de l'envoi. Réessayez ou écrivez-moi sur LinkedIn.", "form_sending": "Envoi…",
        "home_name": "Accueil",
    },
    "en": {
        "nav": ["Home", "Projects", "Games", "About", "Contact", "Write-ups"],
        "avail": "Available",
        "status": "Available for an internship / work-study · Alpes-Maritimes, France",
        "title": "Alexandre K. — Portfolio",
        "meta": "Portfolio of Alexandre K., cybersecurity and web development student in the Alpes-Maritimes, France.",
        "welcome": "Welcome",
        "h1": "I'm <mark>Alexandre K.</mark>, a cybersecurity student.",
        "bio": "I'm training in cybersecurity: reconnaissance and OSINT, Linux administration, Stormshield firewalls. I practise on Kali Linux and build my web apps with security in mind from the start (authentication, least privilege, input validation). I'm looking for an internship or a work-study position.",
        "cta_projects": "See my projects",
        "cta_contact": "Get in touch",
        "term": [("p", "nmap -sV -p 22,80,443 scanme.nmap.org"), ("c", "# example: Nmap's official test target"), ("", "Nmap scan report for scanme.nmap.org"), ("", "Host is up (0.17s latency)."), ("", ""), ("k", "PORT     STATE  SERVICE  VERSION"), ("", "22/tcp   open   ssh      OpenSSH 6.6.1p1"), ("", "80/tcp   open   http     Apache httpd 2.4.7"), ("", "443/tcp  closed https"), ("", ""), ("p", "")],
        "skills_label": "Skills",
        "skills_h": "What I use",
        "skills_lead": "From front to back, with security in mind from the design stage.",
        "skills": [
            ("Security", ["OSINT", "Stormshield", "Authentication", "Least privilege"]),
            ("Systems", ["Debian", "Kali Linux", "macOS", "Windows 10 / 11"]),
            ("Back-end & data", ["Node.js", "Go", "REST API", "SQL"]),
            ("Front-end & tools", ["HTML", "CSS", "JavaScript", "Git & GitHub"]),
        ],
        "proj_label": "Projects",
        "proj_h": "Selected work",
        "proj_lead": "School projects, solo or in a team.",
        "all_projects": "All projects",
        "details": "Details",
        "code": "Code",
        "crumb_home": "Home",
        "crumb_projects": "Projects",
        "list_title": "My <em>projects</em>",
        "list_lead": "Everything I built during my studies. Filter by type to find your way around.",
        "all": "All",
        "kinds": {"web": "Web", "api": "API"},
        "detail_word": "DETAILS", "preview_h": "Preview",
        "description": "Description",
        "tech": "Technologies",
        "features": "Features",
        "repo_tree": "Repository structure",
        "facts": "At a glance",
        "f_type": "Type",
        "f_context": "Context",
        "f_lang": "Language",
        "f_repo": "Repository",
        "context": "School project",
        "view_code": "View the code", "view_demo": "Live demo", "demo_note": "Free hosting: the first load can take a minute.",
        "similar_small": "Similar projects",
        "similar_h": "You may also <em>like</em>",
        "contact_label": "Contact",
        "contact_h": "Let's work <em>together</em>",
        "contact_lead": "Open to internships, work-study positions and collaborations. The easiest way: a message on LinkedIn.",
        "contact_cta_h": "A message?",
        "contact_cta_p": "I answer on LinkedIn. For an internship or work-study, mention the dates and the type of role.",
        "channels_h": "Where to find me",
        "looking_h": "What I'm looking for",
        "looking": ["An internship or work-study in web development or cybersecurity", "A team where I can learn by working with others", "Alpes-Maritimes area, or remote"],
        "profile_h": "Profile",
        "profile": [("Area", "Alpes-Maritimes, France"), ("Studies", "Ynov, cybersecurity"), ("Languages", "French, English B2"), ("Status", "Available")],
        "write": "Write",
        "footer_tag": "Cybersecurity and web development student. Thanks for stopping by.",
        "f_general": "General",
        "f_elsewhere": "Elsewhere",
        "source": "Site source code",
        "rights": "© 2026 Alexandre K.",
        "game_title": "Mini-game — 2048",
        "about_title": "About <em>me</em>",
        "about_lead": "My background, my GitHub activity, my tools, and what I do away from the code.",
        "gh_small": "Developer insights", "gh_h": "GitHub <em>activity</em>",
        "gh_total": "contributions in the last year", "gh_less": "Less", "gh_more": "More",
        "hw_h": "Hardware", "sw_h": "Software & tools",
        "hardware": [("Desktop PC", "Windows 11", "desktop"), ("MacBook Pro 16\"", "M3 Pro chip", "laptop"), ("NAS", "Network storage", "nas")],
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "days": ["", "Mon", "", "Wed", "", "Fri", ""],
        "game_page": "Mini-<em>game</em>",
        "game_lead": "A short break: 2048, with a shared leaderboard.",
        "form_h": "Send a message",
        "form_name": "Name", "form_email": "Your e-mail", "form_msg": "Message", "form_send": "Send",
        "form_ok": "Message sent, thank you!", "form_err": "Sending failed. Try again or write to me on LinkedIn.", "form_sending": "Sending…",
        "home_name": "Home",
    },
}

PROJECTS = [
    {
        "slug": "boutique-cyberpunk", "demo": "https://boutique-js.onrender.com", "hue": 320, "glyph": "JS", "kind": "web", "lang": "JavaScript", "code": "https://github.com/amex-32/boutique-js",
        "tech": ["JavaScript", "Node.js", "Express", "MySQL", "HTML/CSS"],
        "fr": {
            "title": "Boutique Cyberpunk",
            "short": "Boutique de véhicules à l'univers cyberpunk : catalogue, variantes de couleur, commandes et comptes utilisateurs.",
            "long": ["Site de vente de véhicules dans un univers cyberpunk. Le front est en HTML et JavaScript, l'API en Node.js avec Express, et les données sont dans une base MySQL. Chaque véhicule existe en plusieurs variantes de couleur, avec ses propres visuels.",
                     "L'API expose le catalogue (liste et fiche d'un véhicule), la création de commandes ainsi que l'inscription et la connexion. Le schéma SQL, les migrations et les jeux de données sont versionnés avec le code."],
            "features": ["Catalogue et fiche détaillée de chaque véhicule", "Variantes de couleur avec leurs visuels", "Panier et création de commandes", "Inscription et connexion des utilisateurs", "Migrations SQL et jeux de données fournis", "Visuel de repli quand une image est introuvable"],
        },
        "en": {
            "title": "Cyberpunk Shop",
            "short": "A cyberpunk-themed vehicle shop: catalogue, colour variants, orders and user accounts.",
            "long": ["A vehicle shop set in a cyberpunk universe. The front end is plain HTML and JavaScript, the API runs on Node.js with Express, and the data lives in a MySQL database. Each vehicle comes in several colour variants, each with its own visuals.",
                     "The API serves the catalogue (vehicle list and detail), order creation, and sign-up / login. The SQL schema, migrations and seed data are versioned alongside the code."],
            "features": ["Catalogue and detail page for each vehicle", "Colour variants with their own visuals", "Cart and order creation", "User sign-up and login", "SQL migrations and seed data included", "Fallback visual when an image is missing"],
        },
    },
    {
        "slug": "pokedex-interactive", "demo": "https://choubigroup-groupie-tracker-psi.vercel.app", "hue": 38, "glyph": "GO", "kind": "api", "lang": "Go", "code": "https://github.com/amex-32/choubigroup-groupie-tracker",
        "tech": ["Go", "net/http", "html/template", "Tyradex API", "HTML/CSS"],
        "fr": {
            "title": "Pokédex Interactif",
            "short": "Application en Go qui exploite l'API Tyradex : recherche, filtres, fiches détaillées et favoris.",
            "long": ["Application web écrite en Go qui consomme l'API Tyradex pour afficher les Pokémon. Le serveur récupère les données, les range dans des structures Go dédiées, puis rend des pages HTML à partir de templates.",
                     "Le projet met l'accent sur le lien entre le backend Go et l'interface : routes, mapping des données de l'API et rendu côté serveur, sans framework JavaScript."],
            "features": ["Accueil avec un Pokémon tiré au hasard", "Collection avec recherche par nom", "Filtres par type, génération (1 à 9) et formes spéciales", "Fiche détaillée : stats, talents, résistances, évolutions, sprites", "Favoris ajoutés ou retirés depuis les fiches", "Pages rendues côté serveur avec html/template"],
        },
        "en": {
            "title": "Interactive Pokédex",
            "short": "A Go app built on the Tyradex API: search, filters, detail pages and favourites.",
            "long": ["A web app written in Go that consumes the Tyradex API to display Pokémon. The server fetches the data, maps it into dedicated Go structs, then renders HTML pages from templates.",
                     "The project focuses on how a Go backend talks to the interface: routing, mapping API data and server-side rendering, with no JavaScript framework."],
            "features": ["Home page with a random Pokémon", "Collection with search by name", "Filters by type, generation (1 to 9) and special forms", "Detail page: stats, abilities, resistances, evolutions, sprites", "Favourites toggled from the detail pages", "Server-side rendering with html/template"],
        },
    },
    {
        "slug": "forum-musical", "demo": "https://forum-team-xxl-frontend.vercel.app", "hue": 268, "glyph": "JWT", "kind": "web", "lang": "JavaScript", "code": "https://github.com/amex-32/forum-team-xxl",
        "tech": ["Node.js", "Express", "MySQL", "JWT", "HTML/JS"],
        "fr": {
            "title": "Forum Musical",
            "short": "Forum autour de la musique : sujets, réponses, votes, comptes et espace d'administration.",
            "long": ["Forum consacré à la musique, réalisé en binôme avec Omrane Riahi. L'API est en Node.js avec Express et MySQL, l'authentification repose sur des jetons JWT, et le front est en HTML et JavaScript.",
                     "Les utilisateurs créent des sujets, y répondent et votent. Un espace d'administration permet de modérer : bannir un utilisateur, changer le statut d'un sujet ou supprimer un contenu."],
            "features": ["Inscription et connexion avec JWT", "Création, modification et suppression de sujets", "Tags pour classer les sujets", "Réponses et votes sur les messages", "Profil utilisateur", "Tableau de bord d'administration : bannissement, statut des sujets, suppression"],
        },
        "en": {
            "title": "Music Forum",
            "short": "A music forum: topics, replies, votes, accounts and an admin area.",
            "long": ["A forum about music, built as a pair with Omrane Riahi. The API runs on Node.js with Express and MySQL, authentication relies on JWT tokens, and the front end is HTML and JavaScript.",
                     "Users create topics, reply and vote. An admin area handles moderation: banning a user, changing a topic's status or deleting content."],
            "features": ["Sign-up and login with JWT", "Create, edit and delete topics", "Tags to organise topics", "Replies and votes on messages", "User profile", "Admin dashboard: bans, topic status, content removal"],
        },
    },
    {
        "slug": "pixelworld", "demo": "https://pixelworld-em8r.onrender.com", "hue": 160, "glyph": "WS", "kind": "web", "lang": "JavaScript", "code": "https://github.com/amex-32/pixelworld",
        "tech": ["Node.js", "Express", "Socket.IO", "Canvas", "JavaScript"],
        "fr": {
            "title": "PixelWorld",
            "short": "Toile collaborative en temps réel, dans l'esprit de r/place, sur une grille de 1000 × 1000.",
            "long": ["Application web collaborative inspirée de r/place : plusieurs joueurs posent des pixels sur une même toile de 1000 × 1000. Le serveur Node.js garde l'état de la grille et le diffuse aux joueurs par WebSocket avec Socket.IO, le rendu se fait dans un Canvas.",
                     "Le projet a été cadré par un cahier des charges et une décision d'architecture écrite (ADR) : pas de base de données, la grille est gardée en mémoire et sauvegardée sur disque."],
            "features": ["Toile partagée de 1000 × 1000 pixels", "Mises à jour en temps réel par WebSocket, à l'unité ou par lot", "Zoom et déplacement de la caméra", "Pseudos des joueurs et scores", "Modération : bannissement d'un joueur", "Sauvegarde de la grille et des scores sur disque", "Cahier des charges et ADR dans le dossier docs"],
        },
        "en": {
            "title": "PixelWorld",
            "short": "A real-time collaborative canvas in the spirit of r/place, on a 1000 × 1000 grid.",
            "long": ["A collaborative web app inspired by r/place: several players place pixels on the same 1000 × 1000 canvas. The Node.js server keeps the grid state and broadcasts it to players over WebSocket with Socket.IO, and rendering happens in a Canvas.",
                     "The project was framed by a specification and a written architecture decision record (ADR): no database, the grid is kept in memory and saved to disk."],
            "features": ["Shared 1000 × 1000 pixel canvas", "Real-time updates over WebSocket, single or batched", "Camera zoom and pan", "Player nicknames and scores", "Moderation: banning a player", "Grid and scores saved to disk", "Specification and ADR in the docs folder"],
        },
    },
]


# Études de cas affichées sur chaque fiche projet : problème, ce que j'ai fait, difficulté technique, résultat
CASES = {
    "boutique-cyberpunk": {
        "fr": ["Vendre des véhicules en ligne, avec plusieurs variantes de couleur, sans mélanger catalogue, commandes et comptes.",
               "Réalisation de l'API Node.js / Express, du schéma MySQL et du front en HTML et JavaScript.",
               "Associer chaque variante de couleur à ses propres visuels, avec un visuel de repli quand une image est introuvable.",
               "Une boutique fonctionnelle en démo publique : catalogue, commandes, inscription et connexion, migrations et jeux de données versionnés."],
        "en": ["Selling vehicles online, with several colour variants, without mixing up the catalogue, orders and accounts.",
               "Built the Node.js / Express API, the MySQL schema and the HTML / JavaScript front end.",
               "Tying each colour variant to its own visuals, with a fallback visual when an image is missing.",
               "A working shop with a public demo: catalogue, orders, sign-up and login, with migrations and seed data versioned."],
    },
    "pokedex-interactive": {
        "fr": ["Exploiter une API externe sans framework JavaScript, tout en gardant une interface rapide à parcourir (recherche, filtres).",
               "Écriture du serveur Go : routes, mapping des données de l'API Tyradex, templates HTML.",
               "Ranger les données de l'API dans des structures Go dédiées, puis les rendre côté serveur avec html/template.",
               "Une application déployée en démo : recherche, filtres par type et génération, fiches détaillées et favoris."],
        "en": ["Using an external API without a JavaScript framework, while keeping an interface that is quick to browse (search, filters).",
               "Wrote the Go server: routes, mapping of the Tyradex API data, HTML templates.",
               "Mapping the API data into dedicated Go structs, then rendering it server-side with html/template.",
               "A deployed demo app: search, filters by type and generation, detail pages and favourites."],
    },
    "forum-musical": {
        "fr": ["Permettre à une communauté d'échanger sur la musique tout en gardant la main sur la modération.",
               "Projet en binôme avec Omrane Riahi : API Node.js / Express / MySQL, authentification JWT, front HTML et JavaScript.",
               "Sécuriser les accès : jetons JWT, droits d'administration, bannissement et suppression de contenus.",
               "Un forum complet (sujets, réponses, votes, profils) avec un espace d'administration, en démo publique."],
        "en": ["Letting a community talk about music while keeping control over moderation.",
               "Pair project with Omrane Riahi: Node.js / Express / MySQL API, JWT authentication, HTML and JavaScript front end.",
               "Securing access: JWT tokens, admin rights, banning users and removing content.",
               "A complete forum (topics, replies, votes, profiles) with an admin area, as a public demo."],
    },
    "pixelworld": {
        "fr": ["Faire partager une même toile de 1000 × 1000 pixels à plusieurs joueurs, en temps réel.",
               "Serveur Node.js avec Socket.IO, rendu dans un Canvas, cahier des charges et décision d'architecture (ADR).",
               "Diffuser les mises à jour de la grille à tous les joueurs, à l'unité ou par lot, sans base de données : état en mémoire, sauvegarde sur disque.",
               "Une toile collaborative jouable en ligne, avec zoom, pseudos, scores et modération."],
        "en": ["Letting several players share the same 1000 × 1000 pixel canvas, in real time.",
               "Node.js server with Socket.IO, Canvas rendering, a specification and an architecture decision record (ADR).",
               "Broadcasting grid updates to every player, one by one or in batches, without a database: state in memory, saved to disk.",
               "A collaborative canvas playable online, with zoom, nicknames, scores and moderation."],
    },
}
for _p in PROJECTS:
    for _l in ("fr", "en"):
        _p[_l]["case"] = CASES[_p["slug"]][_l]

def brand_icon(name):
    d = re.search(r' d="([^"]+)"', (ROOT / f"src/icons/{name}.svg").read_text()).group(1)
    return f'<svg viewBox="0 0 24 24" width="42" height="42" fill="currentColor" aria-hidden="true"><path d="{d}"/></svg>'


# (nom, icône Simple Icons, site officiel, couleur de marque ou "" pour la couleur du texte)
SOFTWARE = [("Notion", "notion", "https://www.notion.com", ""),
            ("JetBrains Toolbox", "jetbrains", "https://www.jetbrains.com/toolbox-app/", ""),
            ("Discord", "discord", "https://discord.com", "#5865f2"),
            ("Docker", "docker", "https://www.docker.com", "#2496ed")]
ICON_NAS = '<svg viewBox="0 0 48 48" width="44" height="44" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="8" y="8" width="32" height="14" rx="3"/><rect x="8" y="26" width="32" height="14" rx="3"/><path d="M14 15h6M14 33h6"/><circle cx="34" cy="15" r="1.5"/><circle cx="34" cy="33" r="1.5"/></svg>'
ICON_DESKTOP = '<svg viewBox="0 0 48 48" width="44" height="44" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="12" y="6" width="24" height="36" rx="3"/><path d="M18 14h12M18 20h12"/><circle cx="24" cy="34" r="2"/></svg>'
ICON_LAPTOP = '<svg viewBox="0 0 48 48" width="44" height="44" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="10" width="30" height="21" rx="2"/><path d="M4 38h40l-3-7H7z"/></svg>'
ICONS_HW = {"desktop": ICON_DESKTOP, "laptop": ICON_LAPTOP, "nas": ICON_NAS}
ICON_GH = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.21 11.39.6.11.79-.26.79-.58v-2.23c-3.34.73-4.03-1.42-4.03-1.42-.55-1.39-1.33-1.76-1.33-1.76-1.09-.74.08-.73.08-.73 1.2.08 1.84 1.24 1.84 1.24 1.07 1.83 2.81 1.3 3.5 1 .11-.78.42-1.3.76-1.6-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.12-.3-.54-1.52.12-3.18 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 0 1 6 0c2.28-1.55 3.29-1.23 3.29-1.23.66 1.66.24 2.88.12 3.18.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.63-5.48 5.92.43.37.81 1.1.81 2.22v3.29c0 .32.19.7.8.58A12 12 0 0 0 24 12c0-6.63-5.37-12-12-12Z"/></svg>'
ICON_LI = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29ZM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12ZM7.12 20.45H3.56V9h3.56v11.45ZM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0Z"/></svg>'
ICON_MAIL = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@700&display=swap" rel="stylesheet">')
THEME_JS = ("<script>try{var t=localStorage.getItem('theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');"
            "document.documentElement.dataset.theme=t}catch(e){}</script>")



# ---------------------------------------------------------------- icônes de l'interface (tracés Lucide-like)
_P = {
    "home": '<path d="M3 11 12 3l9 8v9a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/>',
    "folder": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    "game": '<path d="M7 8h10a5 5 0 0 1 4.9 6l-.7 3.2a2.4 2.4 0 0 1-4.1 1.1L15 16H9l-2.1 2.3a2.4 2.4 0 0 1-4.1-1.1L2.1 14A5 5 0 0 1 7 8z"/><path d="M8 11v3M6.5 12.5h3M15.5 12h.01M17.5 14h.01"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M20 21a8 8 0 1 0-16 0"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    "bell": '<path d="M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9M10.3 21a2 2 0 0 0 3.4 0"/>',
    "moon": '<path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z"/>',
    "cmd": '<path d="M9 6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3z"/>',
    "left": '<path d="m15 18-6-6 6-6"/>',
    "right": '<path d="m9 18 6-6-6-6"/>',
    "down": '<path d="m6 9 6 6 6-6"/>',
    "code": '<path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/>',
    "out": '<path d="M7 17 17 7M8 7h9v9"/>',
    "play": '<path d="M8 5v14l11-7z" fill="currentColor"/>',
    "dots": '<path d="M5 12h.01M12 12h.01M19 12h.01"/>',
}


def ico(name, size=20):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="1.9" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_P[name]}</svg>')


ACCENTS = ["blue", "violet", "green", "orange"]

# ---------------------------------------------------------------- textes de la nouvelle interface
UI2 = {
    "fr": {
        "search_ph": "Rechercher…", "pal_ph": "Une page, un projet, une action…", "pal_empty": "Aucun résultat",
        "pal_pages": "Pages", "pal_projects": "Projets", "pal_actions": "Actions", "pal_links": "Liens",
        "pal_theme": "Changer de thème", "pal_lang": "Passer en anglais", "pal_accent": "Couleur d'accent",
        "pal_hint": "↑↓ naviguer · ↵ ouvrir · échap fermer",
        "accent_names": {"blue": "Bleu", "violet": "Violet", "green": "Vert", "orange": "Orange"},
        "notif_h": "Notifications",
        "notifs": [("Disponible", "Pour un stage ou une alternance, dans les Alpes-Maritimes"), ("Nouveau", "6 flags sont cachés sur le site : à toi de les trouver"), ("Contact", "Le formulaire de contact est actif")],
        "handle": "@amex-32", "who_tag": "Étudiant en cybersécurité",
        "featured": "À la une", "see": "Voir le projet", "intro_slide": "Profil",
        "profile_card": "Profil", "stack_card": "Compétences",
        "discover": "À découvrir", "see_all": "Voir tout",
        "back": "Retour", "forward": "Suivant",
        "games_title": "Salle de <em>jeux</em>",
        "games_lead": "Cinq mini-jeux pour faire une pause, et un CTF caché dans le site. Chaque jeu a son classement, partagé entre tous les visiteurs.",
        "games_tabs": ["2048", "Snake", "Memory", "Code Breaker", "César", "CTF"],
        "konami": "Konami code ! Mode Matrix activé.",
        "kb_hint": "Astuce : ⌘K ou Ctrl+K ouvre la recherche, ² ou ` ouvre le terminal.",
        "pal_term": "Ouvrir le terminal",
        "pal_motion": "Animations : activer / désactiver", "pal_music": "Musique : lecture / pause",
        "case_h": "Étude de cas", "case_k": ["Problème", "Ce que j'ai fait", "Difficulté technique", "Résultat"],
        "cv_ask": "Demander mon CV", "cv_msg": "Bonjour, pourriez-vous m'envoyer votre CV ? Merci.",
        "now_label": "En ce moment", "now_h": "Ce que je fais <em>maintenant</em>", "now_listen": "J'écoute", "now_idle": "Rien en lecture — lance un morceau",
        "now_gh": "contributions GitHub sur 30 jours", "now_ctf": "Flags du mini-CTF", "now_study": "Études",
        "nf_term": "Ouvrir le terminal", "nf_game": "Jouer à 2048",
        "og_locale": "fr_FR",
        "wu_title": "<em>Write-ups</em>",
        "wu_lead": "Mes démarches de sécurité, expliquées étape par étape.",
        "nf_title": "Erreur <em>404</em>",
        "nf_lead": "Cette page n'existe pas, ou plus. Vérifie l'adresse ou repars de l'accueil.",
        "nf_home": "Retour à l'accueil",
        "ci_help": "Fais tourner l'alphabet avec ◀ ▶ (ou les flèches) jusqu'à lire un mot, puis valide. 60 secondes, −5 s par erreur.",
        "ci_shift": "Décalage", "ci_ok": "Valider",
        "ctf_h": "Mini-CTF",
        "ctf_p": "Six flags au format FLAG{…} sont cachés dans ce site. Trouve-les, puis soumets-les dans le terminal : tape <code>pseudo ton_pseudo</code>, puis <code>flag FLAG{…}</code>.",
        "ctf_hints": ["Le code source de l'accueil a un secret.", "Les en-têtes HTTP parlent plus qu'on ne croit.", "Les robots savent des choses (et le base64 aussi).", "La console du navigateur, en ROT13.", "↑ ↑ ↓ ↓ ← → ← → B A", "Une œuvre de la galerie en dit plus qu'elle n'en montre (métadonnées)."],
        "ctf_open": "Ouvrir le terminal",
        "ext_h": "En dehors du code",
        "ext_lead": "Quand je ne suis pas devant un terminal, qu'est-ce que je fais ?",
        "ext_music_h": "Musique",
        "ext_music": "Je produis des instrus sur FL Studio : breakcore, jungle, UK garage, trap, un peu de jazz. Quelques morceaux sont en écoute dans le lecteur en haut à droite.",
        "ext_art_h": "Dessin et visuels",
        "ext_art": "Je dessine sur iPad avec Procreate, souvent Clive, un personnage à tête de lune qui revient d'un dessin à l'autre. Je monte aussi des pochettes sous Photoshop et je fais un peu de 3D avec Blender.",
        "ext_listen": "Écouter", "ext_gallery": "Voir la galerie",
        "gal_title": "Ma <em>galerie</em>",
        "gal_lead": "Dessins, pochettes, rendus 3D et photos. Clique sur une œuvre pour l'agrandir.",
        "gal_works": "œuvres", "gal_series_h": "Séries", "gal_view_h": "Affichage", "gal_all": "Tout",
        "gal_views": {"scatter": "Éparpillé", "grid": "Grille", "albums": "Albums"},
        "series": {"clive": "Clive", "covers": "Pochettes et affiches", "illus": "Illustrations", "3d": "3D", "photos": "Photos"},
        "pl_label": "Lecteur de musique", "pl_play": "Lecture", "pl_pause": "Pause", "pl_prev": "Morceau précédent", "pl_next": "Morceau suivant",
        "pl_list": "Liste des morceaux", "pl_seek": "Position dans le morceau", "pl_volume": "Volume",
        "pl_shuffle": "Lecture aléatoire", "pl_like": "J'aime ce morceau", "pl_unlike": "Je n'aime plus ce morceau",
    },
    "en": {
        "search_ph": "Search…", "pal_ph": "A page, a project, an action…", "pal_empty": "No results",
        "pal_pages": "Pages", "pal_projects": "Projects", "pal_actions": "Actions", "pal_links": "Links",
        "pal_theme": "Switch theme", "pal_lang": "Switch to French", "pal_accent": "Accent colour",
        "pal_hint": "↑↓ navigate · ↵ open · esc close",
        "accent_names": {"blue": "Blue", "violet": "Violet", "green": "Green", "orange": "Orange"},
        "notif_h": "Notifications",
        "notifs": [("Available", "For an internship or work-study, in the Alpes-Maritimes"), ("New", "6 flags are hidden on this site: go find them"), ("Contact", "The contact form is live")],
        "handle": "@amex-32", "who_tag": "Cybersecurity student",
        "featured": "Featured", "see": "View project", "intro_slide": "Profile",
        "profile_card": "Profile", "stack_card": "Skills",
        "discover": "Discover", "see_all": "See all",
        "back": "Back", "forward": "Forward",
        "games_title": "Game <em>room</em>",
        "games_lead": "Five mini-games for a break, and a CTF hidden in the site. Each game has its own leaderboard, shared between all visitors.",
        "games_tabs": ["2048", "Snake", "Memory", "Code Breaker", "Caesar", "CTF"],
        "konami": "Konami code! Matrix mode on.",
        "kb_hint": "Tip: ⌘K or Ctrl+K opens search, ` opens the terminal.",
        "pal_term": "Open the terminal",
        "pal_motion": "Animations: on / off", "pal_music": "Music: play / pause",
        "case_h": "Case study", "case_k": ["Problem", "What I did", "Technical challenge", "Outcome"],
        "cv_ask": "Request my CV", "cv_msg": "Hello, could you send me your CV? Thank you.",
        "now_label": "Right now", "now_h": "What I'm doing <em>now</em>", "now_listen": "Listening to", "now_idle": "Nothing playing — start a track",
        "now_gh": "GitHub contributions over 30 days", "now_ctf": "Mini-CTF flags", "now_study": "Studies",
        "nf_term": "Open the terminal", "nf_game": "Play 2048",
        "og_locale": "en_US",
        "wu_title": "<em>Write-ups</em>",
        "wu_lead": "My security work, explained step by step.",
        "nf_title": "Error <em>404</em>",
        "nf_lead": "This page doesn't exist, or no longer does. Check the address or start again from the home page.",
        "nf_home": "Back to home",
        "ci_help": "Rotate the alphabet with ◀ ▶ (or the arrow keys) until you can read a word, then submit. 60 seconds, −5 s per mistake.",
        "ci_shift": "Shift", "ci_ok": "Submit",
        "ctf_h": "Mini-CTF",
        "ctf_p": "Six flags in the FLAG{…} format are hidden in this site. Find them, then submit them in the terminal: type <code>pseudo your_name</code>, then <code>flag FLAG{…}</code>.",
        "ctf_hints": ["The home page source code has a secret.", "HTTP headers say more than you think.", "Robots know things (and so does base64).", "The browser console, in ROT13.", "↑ ↑ ↓ ↓ ← → ← → B A", "One artwork in the gallery says more than it shows (metadata)."],
        "ctf_open": "Open the terminal",
        "ext_h": "Away from the code",
        "ext_lead": "When I'm not in front of a terminal, what do I do?",
        "ext_music_h": "Music",
        "ext_music": "I produce beats in FL Studio: breakcore, jungle, UK garage, trap, a bit of jazz. A few tracks are playing in the player at the top right.",
        "ext_art_h": "Drawing and visuals",
        "ext_art": "I draw on iPad with Procreate, often Clive, a moon-headed character who keeps coming back from one drawing to the next. I also design covers in Photoshop and do a bit of 3D in Blender.",
        "ext_listen": "Listen", "ext_gallery": "See the gallery",
        "gal_title": "My <em>gallery</em>",
        "gal_lead": "Drawings, covers, 3D renders and photos. Click an artwork to enlarge it.",
        "gal_works": "artworks", "gal_series_h": "Series", "gal_view_h": "View", "gal_all": "All",
        "gal_views": {"scatter": "Scattered", "grid": "Grid", "albums": "Albums"},
        "series": {"clive": "Clive", "covers": "Covers and posters", "illus": "Illustrations", "3d": "3D", "photos": "Photos"},
        "pl_label": "Music player", "pl_play": "Play", "pl_pause": "Pause", "pl_prev": "Previous track", "pl_next": "Next track",
        "pl_list": "Track list", "pl_seek": "Position in the track", "pl_volume": "Volume",
        "pl_shuffle": "Shuffle", "pl_like": "Like this track", "pl_unlike": "Unlike this track",
    },
}
for _l in UI:
    UI[_l].update(UI2[_l])


# ---------------------------------------------------------------- éléments du CV
CV = {
    "fr": {
        "hl_h": "Parcours cyber", "edu_h": "Formation actuelle", "lang_h": "Langues", "more_h": "Autres projets",
        "highlights": [
            ("Labo cybersécurité", "En cours · projet Ynov / Yboost",
             "Infrastructure d'une PME fictive isolée et segmentée (DMZ, LAN, postes) avec SIEM, déployée en automatisé. Cycle prévu : pentest, rapport de vulnérabilités CVSS, correctifs et règles de détection.",
             ["Proxmox", "pfSense", "Active Directory", "Wazuh", "Terraform", "Ansible"]),
            ("Challenge 48h Cybersécurité", "Niveau national, Ynov · 30–31 mars 2026",
             "CTF en équipe de 4 : OSINT, recherche d'images, forensic et reconnaissance réseau. Trois CTF de 48 h au total.",
             ["OSINT", "Forensic", "Nmap", "CTF"]),
        ],
        "edu": [("Bachelor Informatique, spécialité Cybersécurité", "Ynov Campus Sophia Antipolis · 2025 – 2028 (Bachelor 2)"),
                ("HTB CJCA", "Certified Junior Cybersecurity Associate · en préparation")],
        "langs": [("Français", "langue maternelle"), ("Anglais", "B2"), ("Espagnol", "compréhension")],
        "more": [("Application de gestion d'inventaire", "Projet d'équipe, Ynov, 1ère année",
                  "Création de la landing page qui redirige vers les app stores et de petites fonctionnalités de l'application.", ["Landing page", "Équipe"])],
    },
    "en": {
        "hl_h": "Cyber highlights", "edu_h": "Current studies", "lang_h": "Languages", "more_h": "Other projects",
        "highlights": [
            ("Cybersecurity lab", "In progress · Ynov / Yboost project",
             "Infrastructure of a fictional small company, isolated and segmented (DMZ, LAN, workstations) with a SIEM, deployed automatically. Planned cycle: pentest, CVSS vulnerability report, fixes and detection rules.",
             ["Proxmox", "pfSense", "Active Directory", "Wazuh", "Terraform", "Ansible"]),
            ("48h Cybersecurity Challenge", "National level, Ynov · 30–31 March 2026",
             "Team CTF of 4: OSINT, image search, forensics and network reconnaissance. Three 48-hour CTFs in total.",
             ["OSINT", "Forensics", "Nmap", "CTF"]),
        ],
        "edu": [("Bachelor in Computer Science, Cybersecurity track", "Ynov Campus Sophia Antipolis · 2025 – 2028 (Bachelor 2)"),
                ("HTB CJCA", "Certified Junior Cybersecurity Associate · in preparation")],
        "langs": [("French", "native"), ("English", "B2"), ("Spanish", "comprehension")],
        "more": [("Inventory management app", "Team project, Ynov, first year",
                  "Built the landing page that redirects to the app stores and a few small features of the app.", ["Landing page", "Team"])],
    },
}


# ---------------------------------------------------------------- musique et galerie
# Accueil, carrousel « À la une » : projets montrés (les autres restent sur la page Projets, et dans « À découvrir ») et œuvres du diaporama de la galerie
HOME_PROJECTS = ("boutique-cyberpunk", "pixelworld")
HOME_GALLERY = ("clive-neon", "flame-radio", "knight")

# Morceaux du lecteur : (fichier dans audio/ sans .mp3, titre)
# Masterisés par un script ffmpeg ponctuel : passe-haut 30 Hz, compression 2:1, -14 LUFS, limiteur -1,5 dB, MP3 192 kbps.
TRACKS = [("jolagreen-type-beat", "Jolagreen Type Beat"), ("post-punk", "Post Punk"), ("trap-star", "Trap Star"), ("hip-hop", "Hip Hop"),
          ("ivory", "Ivory"), ("night-shift", "Night Shift"), ("marseille", "Marseille 01.06.2026"), ("batman", "Batman"),
          ("lost-and-found", "Lost & Found"), ("low-tide", "Low Tide"), ("spiderman-ost", "Spider-Man OST")]

# Œuvres de la galerie, dans img/gallery/ : <slug>.webp (ou .jpg) et <slug>-thumb.webp. Date au format AAAA-MM, "" si inconnue.
GALLERY = [
    {"slug": "clive", "series": "clive", "date": "2025-02", "fr": "Clive", "en": "Clive"},
    {"slug": "clive-what-have-i-done", "series": "clive", "date": "2025-02", "fr": "What Have I Done???", "en": "What Have I Done???"},
    {"slug": "clive-again", "series": "clive", "date": "2025-02", "fr": "Again???", "en": "Again???"},
    {"slug": "clive-tag", "series": "clive", "date": "2025-02", "fr": "Clive, en grand", "en": "Clive, big"},
    {"slug": "clive-mugshot", "series": "clive", "date": "2025-02", "fr": "Photo d'identité judiciaire", "en": "Mugshot", "ext": "jpg"},
    {"slug": "clive-neon", "series": "clive", "date": "2025-02", "fr": "Néons", "en": "Neon"},
    {"slug": "clive-comic", "series": "clive", "date": "2025-02", "fr": "Case de BD", "en": "Comic panel"},
    {"slug": "clive-store", "series": "clive", "date": "", "fr": "Dans le magasin", "en": "In the store"},
    {"slug": "clive-glow", "series": "clive", "date": "", "fr": "Le regard", "en": "The glare"},
    {"slug": "clive-full", "series": "clive", "date": "", "fr": "Clive, en pied", "en": "Clive, full length"},
    {"slug": "clive-sheet", "series": "clive", "date": "", "fr": "Fiche personnage", "en": "Character sheet"},
    {"slug": "flame-radio", "series": "covers", "date": "2025-09", "fr": "Flame Radio Vol. 07", "en": "Flame Radio Vol. 07"},
    {"slug": "flame-radio-inverse", "series": "covers", "date": "2025-09", "fr": "Flame Radio Vol. 07, inversé", "en": "Flame Radio Vol. 07, inverted"},
    {"slug": "kvrt-cooking", "series": "covers", "date": "2025-10", "fr": "KVRT C00K1N3", "en": "KVRT C00K1N3"},
    {"slug": "knight", "series": "covers", "date": "", "fr": "Knight", "en": "Knight"},
    {"slug": "mf-doom", "series": "covers", "date": "2024-11", "fr": "MF DOOM", "en": "MF DOOM"},
    {"slug": "hooded-cat", "series": "illus", "date": "2025-02", "fr": "Chat à capuche", "en": "Hooded cat"},
    {"slug": "illu-cats", "series": "illus", "date": "", "fr": "Chats", "en": "Cats"},
    {"slug": "illu-hat-cat", "series": "illus", "date": "", "fr": "Chat au bonnet", "en": "Cat in a hat"},
    {"slug": "illu-tank", "series": "illus", "date": "", "fr": "Le char", "en": "The tank"},
    {"slug": "studio-3d", "series": "3d", "date": "2025-07", "fr": "Studio de nuit", "en": "Studio at night"},
    {"slug": "building-3d", "series": "3d", "date": "2024-11", "fr": "Outside home", "en": "Outside home"},
    {"slug": "fisheye-3d", "series": "3d", "date": "2024-11", "fr": "Fisheye", "en": "Fisheye"},
    {"slug": "setup-3d", "series": "3d", "date": "2024-11", "fr": "Setup", "en": "Setup"},
    {"slug": "pool-room", "series": "3d", "date": "", "fr": "Pool Room", "en": "Pool Room"},
    # photos : rangées par thème (nature, aquarium, voitures, ville, ambiances), sans sous-série ; métadonnées (GPS, appareil) retirées à l'export
    {"slug": "photo-nature-1", "series": "photos", "date": "", "fr": "Chemin en forêt", "en": "Forest path"},
    {"slug": "photo-nature-2", "series": "photos", "date": "", "fr": "Coucher de soleil", "en": "Sunset"},
    {"slug": "photo-nature-3", "series": "photos", "date": "2020-07", "fr": "Herbes hautes", "en": "Tall grass"},
    {"slug": "photo-nature-4", "series": "photos", "date": "", "fr": "Montagne", "en": "Mountain"},
    {"slug": "photo-aquarium-1", "series": "photos", "date": "2025-11", "fr": "Aquarium", "en": "Aquarium"},
    {"slug": "photo-aquarium-2", "series": "photos", "date": "2025-11", "fr": "Coraux", "en": "Coral"},
    {"slug": "photo-aquarium-3", "series": "photos", "date": "2025-11", "fr": "Contre-jour", "en": "Backlit"},
    {"slug": "photo-aquarium-4", "series": "photos", "date": "2025-11", "fr": "Méduse", "en": "Jellyfish"},
    {"slug": "photo-aquarium-5", "series": "photos", "date": "2025-11", "fr": "Méduses", "en": "Jellyfish"},
    {"slug": "photo-aquarium-6", "series": "photos", "date": "2025-11", "fr": "Requin", "en": "Shark"},
    {"slug": "photo-aquarium-7", "series": "photos", "date": "2025-11", "fr": "Vitre bleue", "en": "Blue glass"},
    {"slug": "photo-cars-1", "series": "photos", "date": "2026-01", "fr": "Mazda 787B", "en": "Mazda 787B"},
    {"slug": "photo-cars-2", "series": "photos", "date": "2026-01", "fr": "Ferrari", "en": "Ferrari"},
    {"slug": "photo-cars-3", "series": "photos", "date": "", "fr": "Porsche", "en": "Porsche"},
    {"slug": "photo-cars-4", "series": "photos", "date": "2026-01", "fr": "Hypercar blanche", "en": "White hypercar"},
    {"slug": "photo-cars-5", "series": "photos", "date": "", "fr": "Twingo", "en": "Twingo"},
    {"slug": "photo-cars-6", "series": "photos", "date": "2026-05", "fr": "Twingo blanche", "en": "White Twingo"},
    {"slug": "photo-city-1", "series": "photos", "date": "2024-10", "fr": "Immeuble", "en": "Building"},
    {"slug": "photo-city-2", "series": "photos", "date": "2025-11", "fr": "Tour Eiffel", "en": "Eiffel Tower"},
    {"slug": "photo-city-3", "series": "photos", "date": "2024-10", "fr": "Néons rouges", "en": "Red lights"},
    {"slug": "photo-mood-1", "series": "photos", "date": "", "fr": "Concert", "en": "Concert"},
    {"slug": "photo-mood-2", "series": "photos", "date": "", "fr": "Silhouette violette", "en": "Purple silhouette"},
    {"slug": "photo-mood-3", "series": "photos", "date": "2024-10", "fr": "Lumière bleue", "en": "Blue light"},
    {"slug": "photo-mood-4", "series": "photos", "date": "2024-10", "fr": "Discussion", "en": "Chat"},
    {"slug": "photo-mood-5", "series": "photos", "date": "2024-10", "fr": "Ambiance", "en": "Mood"},
    {"slug": "photo-mood-6", "series": "photos", "date": "2026-09", "fr": "Miroir", "en": "Mirror"},
    {"slug": "photo-mood-7", "series": "photos", "date": "2024-10", "fr": "Dos au public", "en": "Back to the crowd"},
    {"slug": "photo-mood-8", "series": "photos", "date": "2024-10", "fr": "Collier", "en": "Chain"},
    {"slug": "photo-rock", "series": "photos", "date": "2024-09", "fr": "Rock", "en": "Rock"},
    {"slug": "photo-foosball", "series": "photos", "date": "2024-10", "fr": "Baby-foot", "en": "Foosball"},
]


# ---------------------------------------------------------------- write-ups
# Chaque section : (titre, [paragraphes]) ; les paragraphes peuvent contenir du HTML simple (<code>, <b>).
WRITEUPS = [
    {
        "slug": "securiser-ce-portfolio", "date": "2026-10", "tags": ["CSP", "HTTP headers", "API", "SQL"],
        "fr": {
            "title": "Sécuriser ce portfolio",
            "summary": "Comment j'ai audité puis durci ce site : surface d'attaque, en-têtes HTTP, CSP stricte, validation côté serveur et fuites de fichiers.",
            "sections": [
                ("Contexte", [
                    "Ce site est statique (HTML, CSS, JavaScript générés par un script Python) et hébergé sur Vercel. Une seule partie tourne côté serveur : les fonctions <code>/api/scores</code> et <code>/api/ctf</code>, qui enregistrent les classements dans une base MySQL.",
                    "Objectif : réduire au maximum ce qu'un attaquant peut exploiter, sans casser le site."]),
                ("1. Cartographier la surface d'attaque", [
                    "J'ai listé tout ce qui reçoit des données de l'extérieur : les deux API (paramètres de requête et corps JSON), le formulaire de contact (envoyé à un service tiers) et ce que le navigateur charge (scripts, polices, images).",
                    "J'ai aussi regardé ce que le serveur renvoie sans qu'on le lui demande : les en-têtes HTTP et les fichiers accessibles publiquement."]),
                ("2. Constats", [
                    "<b>En-têtes absents :</b> à part HSTS, aucun en-tête de sécurité. Rien n'empêchait d'afficher le site dans une iframe (clickjacking), ni d'exécuter un script injecté.",
                    "<b>Fichiers sources exposés :</b> les scripts de génération et les fichiers de travail étaient servis comme des pages, alors que le dépôt est privé. Une fuite d'information classique.",
                    "<b>Côté API, c'était déjà sain :</b> requêtes SQL paramétrées, noms de bases tirés d'une liste fixe, pseudo validé par une expression régulière stricte, scores bornés, limite de débit par IP. Les données affichées sont insérées avec <code>textContent</code>, jamais interprétées comme du HTML."]),
                ("3. Correctifs", [
                    "<b>Content-Security-Policy stricte :</b> les scripts ne peuvent venir que du site lui-même. Le seul script inline (choix du thème avant l'affichage) est autorisé par son empreinte SHA-256, sans <code>unsafe-inline</code>. Plugins interdits, <code>base-uri</code> et <code>form-action</code> verrouillés.",
                    "<b>Autres en-têtes :</b> <code>frame-ancestors 'none'</code> et <code>X-Frame-Options: DENY</code> contre le clickjacking, <code>nosniff</code>, une <code>Referrer-Policy</code> qui ne transmet que l'origine aux autres sites, et une <code>Permissions-Policy</code> qui coupe caméra, micro, géolocalisation et paiement.",
                    "<b>Fichiers internes :</b> exclus du déploiement, ils ne sont plus servis du tout.",
                    "<b>Non-régression :</b> un test vérifie à chaque modification que l'empreinte de chaque script inline figure bien dans la CSP. Sans ça, changer une ligne du script casserait le thème sans prévenir."]),
                ("4. Ce qui reste", [
                    "Les scores des jeux sont calculés dans le navigateur : ils restent falsifiables à l'intérieur des bornes. Les empêcher vraiment demanderait de rejouer la partie côté serveur, ce qui est disproportionné pour un portfolio.",
                    "La limite de débit est propre à chaque instance serverless. Elle suffit contre le spam simple ; au-delà, il faudrait une règle dans le pare-feu de l'hébergeur."]),
                ("5. Vérifier", [
                    "<code>curl -I</code> sur la page d'accueil affiche tous les en-têtes. En parcourant le site, la console du navigateur ne doit montrer aucune violation de CSP.",
                    "Et pour t'entraîner : six flags sont cachés dans ce site. L'onglet CTF de la page Jeux donne les indices."]),
            ],
        },
        "en": {
            "title": "Securing this portfolio",
            "summary": "How I audited and hardened this site: attack surface, HTTP headers, a strict CSP, server-side validation and leaked files.",
            "sections": [
                ("Context", [
                    "This site is static (HTML, CSS and JavaScript generated by a Python script) and hosted on Vercel. Only one part runs on a server: the <code>/api/scores</code> and <code>/api/ctf</code> functions, which store the leaderboards in a MySQL database.",
                    "Goal: shrink what an attacker can exploit as much as possible, without breaking the site."]),
                ("1. Mapping the attack surface", [
                    "I listed everything that receives outside data: the two APIs (query parameters and JSON body), the contact form (sent to a third-party service) and what the browser loads (scripts, fonts, images).",
                    "I also looked at what the server returns unasked: the HTTP headers and the publicly reachable files."]),
                ("2. Findings", [
                    "<b>Missing headers:</b> apart from HSTS, no security headers at all. Nothing stopped the site from being framed (clickjacking) or an injected script from running.",
                    "<b>Exposed source files:</b> the build scripts and working files were served like pages, even though the repository is private. A classic information leak.",
                    "<b>The API was already sound:</b> parameterised SQL queries, database names taken from a fixed list, nicknames checked by a strict regular expression, bounded scores, per-IP rate limiting. Displayed data is inserted with <code>textContent</code>, never parsed as HTML."]),
                ("3. Fixes", [
                    "<b>Strict Content-Security-Policy:</b> scripts can only come from the site itself. The single inline script (picking the theme before first paint) is allowed by its SHA-256 hash, without <code>unsafe-inline</code>. Plugins are blocked, <code>base-uri</code> and <code>form-action</code> are locked down.",
                    "<b>Other headers:</b> <code>frame-ancestors 'none'</code> and <code>X-Frame-Options: DENY</code> against clickjacking, <code>nosniff</code>, a <code>Referrer-Policy</code> that only sends the origin to other sites, and a <code>Permissions-Policy</code> that turns off camera, microphone, geolocation and payment.",
                    "<b>Internal files:</b> excluded from the deployment, they are no longer served at all.",
                    "<b>Regression test:</b> on every change, a test checks that the hash of each inline script is in the CSP. Without it, editing one line of that script would silently break the theme."]),
                ("4. What remains", [
                    "Game scores are computed in the browser, so they can still be faked within the bounds. Truly preventing it would mean replaying the game on the server, which is overkill for a portfolio.",
                    "Rate limiting is per serverless instance. It is enough against simple spam; beyond that, it would take a rule in the host's firewall."]),
                ("5. Checking", [
                    "<code>curl -I</code> on the home page shows every header. While browsing the site, the browser console should show no CSP violation.",
                    "And to practise: six flags are hidden in this site. The CTF tab on the Games page gives the hints."]),
            ],
        },
    },
]

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

TREES = json.loads((ROOT / "src/trees.json").read_text())

# ---------------------------------------------------------------- textes
UI = {
    "fr": {
        "nav": ["Accueil", "Projets", "Jeux", "À propos", "Contact"],
        "avail": "Disponible",
        "status": "Disponible pour stage / alternance · Marseille, France",
        "title": "Alexandre Klotz — Portfolio",
        "meta": "Portfolio d'Alexandre Klotz, étudiant en cybersécurité et développement web à Marseille.",
        "welcome": "Bienvenue",
        "h1": "Je suis <mark>Alexandre Klotz</mark>, étudiant en cybersécurité.",
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
        "detail_word": "DÉTAILS",
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
        "view_code": "Voir le code",
        "similar_small": "Projets similaires",
        "similar_h": "Ça peut <em>t'intéresser</em>",
        "contact_label": "Contact",
        "contact_h": "Travaillons <em>ensemble</em>",
        "contact_lead": "Ouvert aux stages, aux alternances et aux collaborations. Le plus simple : un message sur LinkedIn.",
        "contact_cta_h": "Un message ?",
        "contact_cta_p": "Je réponds sur LinkedIn. Pour un stage ou une alternance, précise les dates et le type de mission.",
        "channels_h": "Où me trouver",
        "looking_h": "Ce que je cherche",
        "looking": ["Un stage ou une alternance en développement web ou en cybersécurité", "Un environnement où l'on apprend en travaillant en équipe", "Marseille et alentours, ou à distance"],
        "profile_h": "Profil",
        "profile": [("Ville", "Marseille, France"), ("Formation", "Cybersécurité"), ("Langues", "Français, anglais"), ("Statut", "Disponible")],
        "write": "Écrire",
        "footer_tag": "Étudiant en cybersécurité et développement web. Merci de votre visite.",
        "f_general": "Général",
        "f_elsewhere": "Ailleurs",
        "source": "Code source du site",
        "rights": "© 2026 Alexandre Klotz",
        "game_title": "Mini-jeu — 2048",
        "about_title": "À <em>propos</em>",
        "about_lead": "Mon activité sur GitHub et les outils que j'utilise au quotidien.",
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
        "nav": ["Home", "Projects", "Games", "About", "Contact"],
        "avail": "Available",
        "status": "Available for an internship / work-study · Marseille, France",
        "title": "Alexandre Klotz — Portfolio",
        "meta": "Portfolio of Alexandre Klotz, cybersecurity and web development student in Marseille, France.",
        "welcome": "Welcome",
        "h1": "I'm <mark>Alexandre Klotz</mark>, a cybersecurity student.",
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
        "detail_word": "DETAILS",
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
        "view_code": "View the code",
        "similar_small": "Similar projects",
        "similar_h": "You may also <em>like</em>",
        "contact_label": "Contact",
        "contact_h": "Let's work <em>together</em>",
        "contact_lead": "Open to internships, work-study positions and collaborations. The easiest way: a message on LinkedIn.",
        "contact_cta_h": "A message?",
        "contact_cta_p": "I answer on LinkedIn. For an internship or work-study, mention the dates and the type of role.",
        "channels_h": "Where to find me",
        "looking_h": "What I'm looking for",
        "looking": ["An internship or work-study in web development or cybersecurity", "A team where I can learn by working with others", "Marseille area, or remote"],
        "profile_h": "Profile",
        "profile": [("City", "Marseille, France"), ("Studies", "Cybersecurity"), ("Languages", "French, English"), ("Status", "Available")],
        "write": "Write",
        "footer_tag": "Cybersecurity and web development student. Thanks for stopping by.",
        "f_general": "General",
        "f_elsewhere": "Elsewhere",
        "source": "Site source code",
        "rights": "© 2026 Alexandre Klotz",
        "game_title": "Mini-game — 2048",
        "about_title": "About <em>me</em>",
        "about_lead": "My GitHub activity and the tools I use every day.",
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
        "slug": "boutique-cyberpunk", "hue": 320, "glyph": "JS", "kind": "web", "lang": "JavaScript", "code": "https://github.com/amex-32/boutique-js",
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
        "slug": "pokedex-interactive", "hue": 38, "glyph": "GO", "kind": "api", "lang": "Go", "code": "https://github.com/amex-32/choubigroup-groupie-tracker",
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
        "slug": "forum-musical", "hue": 268, "glyph": "JWT", "kind": "web", "lang": "JavaScript", "code": "https://github.com/amex-32/forum-team-xxl",
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
        "slug": "pixelworld", "hue": 160, "glyph": "WS", "kind": "web", "lang": "JavaScript", "code": "https://github.com/amex-32/pixelworld",
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
        "notifs": [("Disponible", "Pour un stage ou une alternance, à Marseille"), ("Nouveau", "4 mini-jeux dans l'onglet Jeux"), ("Contact", "Le formulaire de contact est actif")],
        "handle": "@amex-32", "who_tag": "Étudiant en cybersécurité",
        "featured": "À la une", "see": "Voir le projet", "intro_slide": "Profil",
        "profile_card": "Profil", "stack_card": "Compétences",
        "discover": "À découvrir", "see_all": "Voir tout",
        "back": "Retour", "forward": "Suivant",
        "games_title": "Salle de <em>jeux</em>",
        "games_lead": "Quatre mini-jeux pour faire une pause. Les meilleurs scores sont gardés dans ton navigateur.",
        "games_tabs": ["2048", "Snake", "Memory", "Code Breaker"],
        "konami": "Konami code ! Mode Matrix activé.",
        "kb_hint": "Astuce : ⌘K ou Ctrl+K ouvre la recherche.",
    },
    "en": {
        "search_ph": "Search…", "pal_ph": "A page, a project, an action…", "pal_empty": "No results",
        "pal_pages": "Pages", "pal_projects": "Projects", "pal_actions": "Actions", "pal_links": "Links",
        "pal_theme": "Switch theme", "pal_lang": "Switch to French", "pal_accent": "Accent colour",
        "pal_hint": "↑↓ navigate · ↵ open · esc close",
        "accent_names": {"blue": "Blue", "violet": "Violet", "green": "Green", "orange": "Orange"},
        "notif_h": "Notifications",
        "notifs": [("Available", "For an internship or work-study, in Marseille"), ("New", "4 mini-games in the Games tab"), ("Contact", "The contact form is live")],
        "handle": "@amex-32", "who_tag": "Cybersecurity student",
        "featured": "Featured", "see": "View project", "intro_slide": "Profile",
        "profile_card": "Profile", "stack_card": "Skills",
        "discover": "Discover", "see_all": "See all",
        "back": "Back", "forward": "Forward",
        "games_title": "Game <em>room</em>",
        "games_lead": "Four mini-games for a break. Best scores are kept in your browser.",
        "games_tabs": ["2048", "Snake", "Memory", "Code Breaker"],
        "konami": "Konami code! Matrix mode on.",
        "kb_hint": "Tip: ⌘K or Ctrl+K opens search.",
    },
}
for _l in UI:
    UI[_l].update(UI2[_l])

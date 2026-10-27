#!/usr/bin/env python3
"""Génère le site (FR à la racine, EN dans en/) : python3 tools/build.py

Contenu et textes : ce fichier. Jeu 2048 : src/game.html et src/game.js.
"""
import datetime
import json
import os
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
EMAIL = ""  # renseigner pour afficher une adresse e-mail sur la page contact
FORM_ENDPOINT = ""  # URL d'un service de formulaire (ex. https://formspree.io/f/xxxx) ; vide = pas de formulaire
GITHUB = "https://github.com/amex-32"
LINKEDIN = "https://www.linkedin.com/in/alexandre-k-801438256/"
GITHUB_USER = "amex-32"
SITE_REPO = "https://github.com/amex-32/portfolio"

TREES = json.loads((ROOT / "src/trees.json").read_text())

# ---------------------------------------------------------------- textes
UI = {
    "fr": {
        "nav": ["Accueil", "Projets", "Jeu", "À propos", "Contact"],
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
        "gh_note": "Compte amex-32. Mis à jour automatiquement chaque jour.",
        "hw_h": "Matériel", "sw_h": "Logiciels et outils",
        "hardware": [("PC fixe", "Windows 11", "desktop"), ("MacBook Pro 16\"", "Puce M3 Pro", "laptop")],
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
        "nav": ["Home", "Projects", "Game", "About", "Contact"],
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
        "gh_note": "Account amex-32. Updated automatically every day.",
        "hw_h": "Hardware", "sw_h": "Software & tools",
        "hardware": [("Desktop PC", "Windows 11", "desktop"), ("MacBook Pro 16\"", "M3 Pro chip", "laptop")],
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
        "slug": "boutique-cyberpunk", "kind": "web", "lang": "JavaScript", "code": "https://github.com/amex-32/boutique-js",
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
        "slug": "pokedex-interactive", "kind": "api", "lang": "Go", "code": "https://github.com/amex-32/choubigroup-groupie-tracker",
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
        "slug": "forum-musical", "kind": "web", "lang": "JavaScript", "code": "https://github.com/amex-32/forum-team-xxl",
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
        "slug": "pixelworld", "kind": "web", "lang": "JavaScript", "code": "https://github.com/amex-32/pixelworld",
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

SOFTWARE = [("Notion", "N", "#111827"), ("JetBrains Toolbox", "JB", "#e6317d"), ("Discord", "D", "#5865f2"), ("Docker", "Dk", "#1d63ed")]
ICON_DESKTOP = '<svg viewBox="0 0 48 48" width="44" height="44" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="12" y="6" width="24" height="36" rx="3"/><path d="M18 14h12M18 20h12"/><circle cx="24" cy="34" r="2"/></svg>'
ICON_LAPTOP = '<svg viewBox="0 0 48 48" width="44" height="44" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="10" width="30" height="21" rx="2"/><path d="M4 38h40l-3-7H7z"/></svg>'
ICON_GH = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.21 11.39.6.11.79-.26.79-.58v-2.23c-3.34.73-4.03-1.42-4.03-1.42-.55-1.39-1.33-1.76-1.33-1.76-1.09-.74.08-.73.08-.73 1.2.08 1.84 1.24 1.84 1.24 1.07 1.83 2.81 1.3 3.5 1 .11-.78.42-1.3.76-1.6-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.12-.3-.54-1.52.12-3.18 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 0 1 6 0c2.28-1.55 3.29-1.23 3.29-1.23.66 1.66.24 2.88.12 3.18.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.63-5.48 5.92.43.37.81 1.1.81 2.22v3.29c0 .32.19.7.8.58A12 12 0 0 0 24 12c0-6.63-5.37-12-12-12Z"/></svg>'
ICON_LI = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29ZM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12ZM7.12 20.45H3.56V9h3.56v11.45ZM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0Z"/></svg>'
ICON_MAIL = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@700&display=swap" rel="stylesheet">')
THEME_JS = ("<script>try{var t=localStorage.getItem('theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');"
            "document.documentElement.dataset.theme=t}catch(e){}</script>")


# ---------------------------------------------------------------- chemins
def out_path(lang, page, slug=None):
    pre = "en/" if lang == "en" else ""
    names = {
        "home": "index.html",
        "list": "projects.html" if lang == "en" else "projets.html",
        "game": "game.html" if lang == "en" else "jeu.html",
        "about": "about.html" if lang == "en" else "a-propos.html",
        "contact": "contact.html",
        "detail": f"projects/{slug}.html",
    }
    return pre + names[page]


def rel(src, dst):
    """Lien relatif de la page src vers dst (chemins depuis la racine du site)."""
    anchor = ""
    if "#" in dst:
        dst, anchor = dst.split("#")
        anchor = "#" + anchor
    r = os.path.relpath(dst, os.path.dirname(src) or ".")
    return r + anchor


def github_activity():
    """Contributions de l'année : API publique, sinon dernier cache (src/github.json)."""
    cache = ROOT / "src/github.json"
    try:
        url = f"https://github-contributions-api.jogruber.de/v4/{GITHUB_USER}?y=last"
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.load(r)
        assert data["contributions"]
        cache.write_text(json.dumps(data))
    except Exception as e:
        print("activité GitHub : cache utilisé (", e, ")")
        data = json.loads(cache.read_text())
    return data


def heatmap(lang, data):
    t = UI[lang]
    days = data["contributions"]
    first = datetime.date.fromisoformat(days[0]["date"])
    cells = [None] * ((first.weekday() + 1) % 7) + days  # semaines du dimanche au samedi
    weeks = [cells[i:i + 7] for i in range(0, len(cells), 7)]
    cols = ""
    for w in weeks:
        # le mois s'affiche sur la semaine qui contient son 1er jour
        month = next((int(c["date"][5:7]) - 1 for c in w if c and c["date"].endswith("-01")), None)
        label = t["months"][month] if month is not None else ""
        sq = "".join(
            '<i class="sq"></i>' if c is None else
            f'<i class="sq l{c["level"]}" title="{c["date"]} : {c["count"]}"></i>' for c in w)
        cols += f'<div class="wk"><b>{label}</b>{sq}</div>'
    dl = "".join(f"<span>{d}</span>" for d in t["days"])
    total = data["total"]["lastYear"]
    legend = "".join(f'<i class="sq l{n}"></i>' for n in range(5))
    return f'''<div class="heat"><div class="heat-days"><b></b>{dl}</div><div class="heat-scroll">{cols}</div></div>
<div class="heat-foot"><span>{total} {t["gh_total"]}</span><span class="legend">{t["gh_less"]} {legend} {t["gh_more"]}</span></div>'''


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- briques
def hud(lang, page, slug, me):
    t = UI[lang]
    items = [("home", "00", t["nav"][0], out_path(lang, "home")),
             ("list", "01", t["nav"][1], out_path(lang, "list")),
             ("game", "02", t["nav"][2], out_path(lang, "game")),
             ("about", "03", t["nav"][3], out_path(lang, "about")),
             ("contact", "04", t["nav"][4], out_path(lang, "contact"))]
    cur = {"home": "home", "list": "list", "detail": "list", "game": "game", "about": "about", "contact": "contact"}[page]
    nav = "".join(
        f'<a href="{rel(me, href)}"{" aria-current=\"page\"" if key == cur else ""}><i>{n}</i>{label}</a>'
        for key, n, label, href in items)
    num = {"home": "00", "list": "01", "detail": "01", "game": "02", "about": "03", "contact": "04"}[page]
    fr_href, en_href = (rel(me, out_path("fr", page, slug)), rel(me, out_path("en", page, slug)))
    cur_fr = ' aria-current="true"' if lang == "fr" else ""
    cur_en = ' aria-current="true"' if lang == "en" else ""
    return f'''<header class="hud">
  <a class="hud-id" href="{rel(me, out_path(lang, "home"))}"><b>ALEXANDRE KLOTZ</b><span>/ {num}</span></a>
  <nav aria-label="Navigation">{nav}</nav>
  <div class="hud-meta"><span data-clock>00:00:00</span><span data-view>L0H0</span></div>
  <div class="hud-right">
    <div class="lang" role="group" aria-label="Langue / Language"><a href="{fr_href}" hreflang="fr" lang="fr"{cur_fr}>FR</a><a href="{en_href}" hreflang="en" lang="en"{cur_en}>EN</a></div>
    <button id="theme-toggle" type="button" aria-label="Thème / Theme">◐</button>
  </div>
</header>

<div id="taskbar">
  <a class="start-btn" href="{rel(me, out_path(lang, "home"))}" style="text-decoration:none">
    <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="4" cy="4" r="3.5" fill="#ff4444"/><circle cx="12" cy="4" r="3.5" fill="#44cc44"/><circle cx="4" cy="12" r="3.5" fill="#4444ff"/><circle cx="12" cy="12" r="3.5" fill="#ffcc00"/></svg>
    {"démarrer" if lang == "fr" else "start"}
  </a>
  <a class="taskbar-btn" href="{rel(me, out_path(lang, "list"))}">{t["nav"][1]}</a>
  <a class="taskbar-btn" href="{rel(me, out_path(lang, "contact"))}">{t["nav"][4]}</a>
  <div class="taskbar-tray"><span class="dot"></span><span>{t["avail"]}</span><span id="tray-clock">00:00</span></div>
</div>'''


def footer(lang, me):
    t = UI[lang]
    return f'''<footer class="site-footer">
  <div class="foot-box">
    <div class="foot-top">
      <div><div class="foot-logo">A<em>K</em></div><p>{t["footer_tag"]}</p></div>
      <div class="foot-col"><h4>{t["f_general"]}</h4>
        <a href="{rel(me, out_path(lang, "home"))}">{t["nav"][0]}</a>
        <a href="{rel(me, out_path(lang, "list"))}">{t["nav"][1]}</a>
        <a href="{rel(me, out_path(lang, "game"))}">{t["nav"][2]}</a>
        <a href="{rel(me, out_path(lang, "about"))}">{t["nav"][3]}</a>
        <a href="{rel(me, out_path(lang, "contact"))}">{t["nav"][4]}</a></div>
      <div class="foot-col"><h4>{t["f_elsewhere"]}</h4>
        <a href="{GITHUB}" target="_blank" rel="noopener">GitHub</a>
        <a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a>
        <a href="{SITE_REPO}" target="_blank" rel="noopener">{t["source"]}</a></div>
    </div>
    <div class="foot-bottom"><span>{t["rights"]}</span>
      <div class="socials"><a href="{LINKEDIN}" target="_blank" rel="noopener" aria-label="LinkedIn">{ICON_LI}</a><a href="{GITHUB}" target="_blank" rel="noopener" aria-label="GitHub">{ICON_GH}</a></div>
    </div>
  </div>
</footer>'''


def win(title, inner, extra_id="", status=""):
    idattr = f' id="{extra_id}"' if extra_id else ""
    st = f'<div class="status-bar">{status}</div>' if status else ""
    return (f'<section{idattr} class="win fadein"><div class="win-title">{title}<div class="win-controls"><i></i><i></i><i></i></div></div>'
            f'<div class="win-body">{inner}</div>{st}</section>')


def card(lang, p, me):
    d, t = p[lang], UI[lang]
    tags = "".join(f"<span>{x}</span>" for x in p["tech"][:4])
    href = rel(me, out_path(lang, "detail", p["slug"]))
    return f'''
        <a class="proj" href="{href}" data-kind="{p["kind"]}">
          <div class="proj-bar">{p["slug"]}</div>
          <div class="proj-body"><div class="proj-num">{t["kinds"][p["kind"]]}</div><h3>{d["title"]}</h3><p>{d["short"]}</p><div class="tags">{tags}</div></div>
          <div class="proj-foot"><span class="proj-more">{t["details"]} →</span><span class="kind">{p["lang"]}</span></div>
        </a>'''


def page(lang, kind, slug, title, desc, body, me):
    root = "../" * me.count("/")
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{rel(me, out_path(l, kind, slug))}">' for l in ("fr", "en"))
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  {alts}
  {FONTS}
  <link rel="stylesheet" href="{root}style.css">
  {THEME_JS}
</head>
<body>
{hud(lang, kind, slug, me)}
<main>
{body}
</main>
{footer(lang, me)}
<script src="{root}js/site.js"></script>
{extra_scripts(kind, root)}
</body>
</html>
'''


def extra_scripts(kind, root):
    return f'<script src="{root}js/game.js"></script>' if kind == "game" else ""


# ---------------------------------------------------------------- pages
def build_home(lang):
    t, me = UI[lang], out_path(lang, "home")
    lines = ""
    for n, (cls, txt) in enumerate(t["term"]):
        if cls == "p":
            txt = f'<span class="p">$</span> {esc(txt)}'
        elif cls:
            txt = f'<span class="{cls}">{esc(txt)}</span>'
        else:
            txt = esc(txt)
        tail = '<span class="cursor"></span>' if n == len(t["term"]) - 1 else ""
        lines += f'<span class="line" style="animation-delay:{.3 + n * .35:.2f}s">{txt}{tail}</span>\n'

    hero = win("Profil.exe", f'''
      <div class="hero-grid">
        <div>
          <span class="label"><b>00</b> / {t["welcome"]}</span>
          <h1>{t["h1"]}</h1>
          <p class="hero-bio">{t["bio"]}</p>
          <div class="btn-row">
            <a class="btn btn-primary" href="{rel(me, out_path(lang, "list"))}">{t["cta_projects"]}</a>
            <a class="btn" href="{rel(me, out_path(lang, "contact"))}">{t["cta_contact"]}</a>
            <a class="btn" href="{GITHUB}" target="_blank" rel="noopener">{ICON_GH} GitHub</a>
          </div>
        </div>
        <div class="term" aria-hidden="true">
          <div class="term-bar"><span></span><span></span><span></span><em>alexandre@marseille: ~</em></div>
          <pre>{lines}</pre>
        </div>
      </div>''', "profil", f'<span class="dot"></span>{t["status"]}')

    boxes = "".join(f'<div class="skill-box"><h3>{h}</h3><div class="tags">{"".join(f"<span>{x}</span>" for x in items)}</div></div>' for h, items in t["skills"])
    skills = win(t["skills_label"], f'''
      <span class="label"><b>01</b> / {t["skills_label"]}</span>
      <h2>{t["skills_h"]}</h2><p class="lead">{t["skills_lead"]}</p>
      <div class="skills">{boxes}</div>''', "competences")

    contact = win(t["contact_label"], f'''
      <span class="label"><b>02</b> / {t["contact_label"]}</span>
      <h2>{t["contact_h"]}</h2><p class="lead">{t["contact_lead"]}</p>
      <div class="btn-row"><a class="btn btn-primary" href="{rel(me, out_path(lang, "contact"))}">{t["cta_contact"]}</a>
      <a class="btn" href="{LINKEDIN}" target="_blank" rel="noopener">{ICON_LI} LinkedIn</a></div>''', "contact")
    return page(lang, "home", None, t["title"], t["meta"], "\n".join([hero, skills, contact]), me)


GAME_EN = {
    "Mini-jeu — 2048": "Mini-game — 2048", "Nouvelle partie": "New game", "Score :": "Score:", "Meilleur :": "Best:",
    "Classement global": "Global leaderboard", "Chargement…": "Loading…", "Votre pseudo": "Your nickname",
    "Soumettre score": "Submit score", "Flèches clavier ou swipe mobile": "Arrow keys or swipe on mobile",
    "Un score par pseudo — seul le meilleur est conservé.": "One score per nickname, only the best is kept.",
    "Classement partagé entre tous les visiteurs.": "Leaderboard shared between all visitors.",
}


def game_block(lang):
    g = (ROOT / "src/game.html").read_text()
    g = re.sub(r'\s*<!-- .*? -->', '', g)
    g = g.replace('<div id="jeu" class="win fadein">', '<section id="jeu" class="win fadein">')
    g = re.sub(r'\n  </div>\s*$', '\n  </section>', g)
    g = g.replace("Mini-jeu — 2048", UI[lang]["game_title"])
    if lang == "en":
        for fr, en in GAME_EN.items():
            g = g.replace(fr, en)
    return g.strip()


GAME_JS_EN = {
    "2048 atteint ! Continuez…": "2048 reached! Keep going…",
    "Game over !": "Game over!",
    "Classement local (API indisponible)": "Local leaderboard (API unavailable)",
    "Entrez un pseudo avant de soumettre.": "Enter a nickname before submitting.",
    "Score soumis au classement global !": "Score submitted to the global leaderboard!",
    "Score sauvegardé localement (API non disponible).": "Score saved locally (API unavailable).",
    "Chargement…": "Loading…",
    "Aucun score": "No score yet",
    "Classement global": "Global leaderboard",
    "Soumettre score": "Submit score",
}


def build_game_js():
    js = (ROOT / "src/game.js").read_text()
    for fr in GAME_JS_EN:
        js = js.replace(f"'{fr}'", f"T('{fr}')")
        js = js.replace(f">{fr}</div>", f">'+T('{fr}')+'</div>")
    js = js.replace("alert('Votre score est 0 — jouez d\\'abord !')", "alert(T('Votre score est 0 — jouez d\\'abord !'))")
    en = dict(GAME_JS_EN)
    en["Votre score est 0 — jouez d'abord !"] = "Your score is 0, play first!"
    head = ("// Traductions : la page porte la langue dans <html lang>.\n"
            f"var TR_EN = {json.dumps(en, ensure_ascii=False)};\n"
            "function T(s){ return document.documentElement.lang === 'en' && TR_EN[s] || s; }\n")
    (ROOT / "js/game.js").write_text(head + js)


def build_game(lang):
    t, me = UI[lang], out_path(lang, "game")
    body = f'''<div class="crumbs"><a href="{rel(me, out_path(lang, "home"))}">{t["crumb_home"]}</a><span>/</span><span>{t["nav"][2]}</span></div>
<h1 class="page-title">{t["game_page"]}</h1>
<p class="lead">{t["game_lead"]}</p>
{game_block(lang)}'''
    return page(lang, "game", None, f'{t["game_title"]} — Alexandre Klotz', t["game_lead"], body, me)


def build_about(lang, data):
    t, me = UI[lang], out_path(lang, "about")
    hw = "".join(
        f'<div class="tile"><div class="tile-ico">{ICON_DESKTOP if k == "desktop" else ICON_LAPTOP}</div><b>{name}</b><small>{sub}</small></div>'
        for name, sub, k in t["hardware"])
    sw = "".join(f'<div class="tile"><div class="tile-ico mono" style="--c:{c}">{m}</div><b>{n}</b></div>' for n, m, c in SOFTWARE)
    body = f'''<div class="crumbs"><a href="{rel(me, out_path(lang, "home"))}">{t["crumb_home"]}</a><span>/</span><span>{t["nav"][3]}</span></div>
<h1 class="page-title">{t["about_title"]}</h1>
<p class="lead">{t["about_lead"]}</p>
<section class="win fadein"><div class="win-title">github.exe<div class="win-controls"><i></i><i></i><i></i></div></div>
<div class="win-body"><div class="similar" style="margin-top:0"><div class="head"><small>{t["gh_small"]}</small><h2>{t["gh_h"]}</h2></div></div>
{heatmap(lang, data)}
<p class="lead" style="margin:14px 0 0;font-size:13px">{t["gh_note"]} <a href="{GITHUB}" target="_blank" rel="noopener">github.com/{GITHUB_USER} ↗</a></p></div></section>
<section class="win fadein"><div class="win-title">setup.exe<div class="win-controls"><i></i><i></i><i></i></div></div>
<div class="win-body"><div class="block"><h3>{t["hw_h"]}</h3><div class="tiles">{hw}</div></div>
<div class="block" style="margin-bottom:0"><h3>{t["sw_h"]}</h3><div class="tiles">{sw}</div></div></div></section>'''
    return page(lang, "about", None, f'{t["nav"][3]} — Alexandre Klotz', t["about_lead"], body, me)


def build_list(lang):
    t, me = UI[lang], out_path(lang, "list")
    kinds = sorted({p["kind"] for p in PROJECTS})
    btns = f'<button type="button" data-f="all" aria-pressed="true">{t["all"]}</button>' + "".join(
        f'<button type="button" data-f="{k}" aria-pressed="false">{t["kinds"][k]}</button>' for k in kinds)
    cards = "".join(card(lang, p, me) for p in PROJECTS)
    body = f'''<div class="crumbs"><a href="{rel(me, out_path(lang, "home"))}">{t["crumb_home"]}</a><span>/</span><span>{t["crumb_projects"]}</span></div>
<h1 class="page-title">{t["list_title"]}</h1>
<p class="lead">{t["list_lead"]}</p>
<div class="filters" role="group">{btns}</div>
<div class="proj-grid">{cards}</div>'''
    return page(lang, "list", None, f'{t["crumb_projects"]} — Alexandre Klotz', t["list_lead"], body, me)


def build_detail(lang, p):
    t, d, me = UI[lang], p[lang], out_path(lang, "detail", p["slug"])
    chips = "".join(f"<span>{x}</span>" for x in p["tech"])
    feats = "".join(f"<li>{x}</li>" for x in d["features"])
    longp = "".join(f"<p>{x}</p>" for x in d["long"])
    tree = esc("\n".join(TREES[p["slug"]]))
    others = [q for q in PROJECTS if q["slug"] != p["slug"] and q["kind"] == p["kind"]]
    others += [q for q in PROJECTS if q["slug"] != p["slug"] and q not in others]
    sim = "".join(card(lang, q, me) for q in others[:3])
    body = f'''<div class="crumbs"><a href="{rel(me, out_path(lang, "home"))}">{t["crumb_home"]}</a><span>/</span><a href="{rel(me, out_path(lang, "list"))}">{t["crumb_projects"]}</a><span>/</span><span>{d["title"]}</span></div>
<div class="page-head">
  <h1 class="page-title">{d["title"]} <em>{t["detail_word"]}</em></h1>
  <a class="btn btn-primary" href="{p["code"]}" target="_blank" rel="noopener">{ICON_GH} {t["view_code"]}</a>
</div>
<div class="meta-line"><span>{t["kinds"][p["kind"]]}</span><span>{t["context"]}</span><span>{p["lang"]}</span></div>
<div class="detail-grid" style="margin-top:26px">
  <div>
    <div class="block"><h3>{t["description"]}</h3>{longp}</div>
    <div class="block"><h3>{t["tech"]}</h3><div class="chips">{chips}</div></div>
    <div class="block"><h3>{t["features"]}</h3><ul class="feat">{feats}</ul></div>
  </div>
  <aside class="side">
    <div class="term"><div class="term-bar"><span></span><span></span><span></span><em>{p["slug"]} ~ {t["repo_tree"].lower()}</em></div><pre class="tree">{tree}</pre></div>
    <dl class="facts">
      <div><dt>{t["f_type"]}</dt><dd>{t["kinds"][p["kind"]]}</dd></div>
      <div><dt>{t["f_context"]}</dt><dd>{t["context"]}</dd></div>
      <div><dt>{t["f_lang"]}</dt><dd>{p["lang"]}</dd></div>
      <div><dt>{t["f_repo"]}</dt><dd><a href="{p["code"]}" target="_blank" rel="noopener">GitHub ↗</a></dd></div>
    </dl>
  </aside>
</div>
<div class="similar"><div class="head"><small>{t["similar_small"]}</small><h2>{t["similar_h"]}</h2></div><div class="proj-grid">{sim}</div></div>'''
    return page(lang, "detail", p["slug"], f'{d["title"]} — Alexandre Klotz', d["short"], body, me)


def build_contact(lang):
    t, me = UI[lang], out_path(lang, "contact")
    mail = (f'<a class="channel" href="mailto:{EMAIL}"><div class="contact-icon ci-mail">{ICON_MAIL}</div><div><b>E-mail</b><small>{EMAIL}</small></div><span class="go">→</span></a>' if EMAIL else "")
    form = ""
    if FORM_ENDPOINT:
        form = f'''<div class="block"><h3>{t["form_h"]}</h3>
      <form id="contact-form" class="form" action="{FORM_ENDPOINT}" method="post" data-ok="{t["form_ok"]}" data-err="{t["form_err"]}" data-sending="{t["form_sending"]}">
        <label>{t["form_name"]}<input name="name" required maxlength="80" autocomplete="name"></label>
        <label>{t["form_email"]}<input name="email" type="email" required maxlength="120" autocomplete="email"></label>
        <label>{t["form_msg"]}<textarea name="message" required rows="6" maxlength="3000"></textarea></label>
        <input name="_gotcha" tabindex="-1" autocomplete="off" class="trap" aria-hidden="true">
        <button class="btn btn-primary" type="submit">{t["form_send"]}</button>
        <p class="form-msg" role="status"></p>
      </form></div>'''
    looking = "".join(f"<li>{x}</li>" for x in t["looking"])
    profile = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in t["profile"])
    body = f'''<div class="crumbs"><a href="{rel(me, out_path(lang, "home"))}">{t["crumb_home"]}</a><span>/</span><span>{t["contact_label"]}</span></div>
<h1 class="page-title">{t["contact_h"]}</h1>
<p class="lead">{t["contact_lead"]}</p>
<div class="contact-wrap">
  <div>
    <div class="block"><h3>{t["channels_h"]}</h3>
      <a class="channel" href="{LINKEDIN}" target="_blank" rel="noopener"><div class="contact-icon ci-li">{ICON_LI}</div><div><b>LinkedIn</b><small>alexandre-k-801438256</small></div><span class="go">↗</span></a>
      <a class="channel" href="{GITHUB}" target="_blank" rel="noopener"><div class="contact-icon ci-gh">{ICON_GH}</div><div><b>GitHub</b><small>github.com/amex-32</small></div><span class="go">↗</span></a>
      {mail}
    </div>
    {form}
    <div class="block"><h3>{t["looking_h"]}</h3><ul class="feat">{looking}</ul></div>
  </div>
  <aside class="side">
    <div class="win"><div class="win-title">{t["contact_cta_h"]}<div class="win-controls"><i></i><i></i><i></i></div></div>
      <div class="win-body"><p style="color:var(--text2);margin-bottom:16px">{t["contact_cta_p"]}</p>
      <a class="btn btn-primary" href="{LINKEDIN}" target="_blank" rel="noopener">{ICON_LI} {t["write"]}</a></div>
      <div class="status-bar"><span class="dot"></span>{t["status"]}</div></div>
    <dl class="facts">{profile}</dl>
  </aside>
</div>'''
    return page(lang, "contact", None, f'{t["contact_label"]} — Alexandre Klotz', t["contact_lead"], body, me)


def write(rel_path, html):
    f = ROOT / rel_path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html)


if __name__ == "__main__":
    for old in [*(ROOT / "projects").glob("*.html"), *(ROOT / "en/projects").glob("*.html")]:
        old.unlink()
    build_game_js()
    activity = github_activity()
    for lang in ("fr", "en"):
        write(out_path(lang, "home"), build_home(lang))
        write(out_path(lang, "list"), build_list(lang))
        write(out_path(lang, "game"), build_game(lang))
        write(out_path(lang, "about"), build_about(lang, activity))
        write(out_path(lang, "contact"), build_contact(lang))
        for p in PROJECTS:
            write(out_path(lang, "detail", p["slug"]), build_detail(lang, p))
    print("ok")

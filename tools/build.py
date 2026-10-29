#!/usr/bin/env python3
"""Génère le site (FR à la racine, EN dans en/) : python3 tools/build.py

Textes, projets et icônes : tools/content.py. Jeu 2048 : src/game.html et src/game.js.
"""
import base64
import datetime
import json
import os
import posixpath
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from content import *  # noqa: E402,F401,F403
from content import _P  # noqa: E402

_P.update({
    "shield": '<path d="M12 3 4 6v6c0 5 3.5 8.5 8 9 4.5-.5 8-4 8-9V6z"/>',
    "terminal": '<path d="m4 17 6-6-6-6M12 19h8"/>',
    "server": '<rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 7.5h.01M7 16.5h.01"/>',
    "layout": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M3 9h18M9 21V9"/>',
    "pause": '<path d="M7 5h3v14H7zM14 5h3v14h-3z" fill="currentColor"/>',
    "prev": '<path d="M18 6v12L9 12zM6 6v12" fill="currentColor"/>',
    "next": '<path d="M6 6v12l9-6zM18 6v12" fill="currentColor"/>',
    "shuffle": '<path d="M16 3h5v5M4 20 21 3M21 16v5h-5M15 15l6 6M4 4l5 5"/>',
    "heart": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    "volume": '<path d="M4 9v6h4l5 4V5L8 9zM16.5 8.5a5 5 0 0 1 0 7"/>',
})

PAGE_NUM = {"home": "00", "list": "01", "detail": "01", "game": "02", "about": "03", "gallery": "03", "contact": "04", "writeups": "05"}
PATH = {"home": "", "list": "/projets", "game": "/jeux", "about": "/a-propos", "gallery": "/a-propos/galerie", "contact": "/contact", "writeups": "/write-ups", "notfound": "/404"}
# noms acceptés par les commandes cd / cat du terminal
TERM_NAMES = {"home": ["accueil", "home"], "list": ["projets", "projects"], "game": ["jeux", "games"],
              "writeups": ["write-ups", "writeups"], "about": ["a-propos", "about"], "gallery": ["galerie", "gallery"], "contact": ["contact"]}
SKILL_ICONS = ["shield", "terminal", "server", "layout"]


# ---------------------------------------------------------------- chemins
def out_path(lang, page, slug=None):
    pre = "en/" if lang == "en" else ""
    names = {
        "home": "index.html",
        "list": "projects.html" if lang == "en" else "projets.html",
        "game": "games.html" if lang == "en" else "jeux.html",
        "about": "about.html" if lang == "en" else "a-propos.html",
        "contact": "contact.html",
        "writeups": "write-ups.html",
        "gallery": "gallery.html" if lang == "en" else "galerie.html",
        "notfound": "404.html",
        "detail": f"projects/{slug}.html",
    }
    return pre + names[page]


def abs_url(path):
    return SITE_URL + "/" + (path[:-len("index.html")] if path.endswith("index.html") else path)


def rel(src, dst):
    # posixpath : des liens en "/" même quand le site est généré sous Windows
    return posixpath.relpath(dst, posixpath.dirname(src) or ".")


def webp_size(path):
    """Largeur et hauteur d'une image WebP (VP8, VP8L ou VP8X), sans dépendance."""
    b = open(path, "rb").read(30)
    kind = b[12:16]
    if kind == b"VP8X":
        return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
    if kind == b"VP8L":
        v = int.from_bytes(b[21:25], "little")
        return 1 + (v & 0x3FFF), 1 + ((v >> 14) & 0x3FFF)
    return int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF


def dims(path):
    """Attributs width et height d'une image du site, pour réserver sa place avant le chargement."""
    return 'width="{}" height="{}"'.format(*webp_size(ROOT / path))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- activité GitHub
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
    """Grille unique : 1 colonne de libellés + 1 colonne par semaine, qui s'adapte à la largeur (pas de défilement)."""
    t = UI[lang]
    days = data["contributions"]
    first = datetime.date.fromisoformat(days[0]["date"])
    cells = [None] * ((first.weekday() + 1) % 7) + days  # semaines du dimanche au samedi
    weeks = [cells[i:i + 7] for i in range(0, len(cells), 7)]
    out = "<b></b>" + "".join(f"<span>{d}</span>" for d in t["days"])
    for w in weeks:
        month = next((int(c["date"][5:7]) - 1 for c in w if c and c["date"].endswith("-01")), None)
        out += f'<b>{t["months"][month] if month is not None else ""}</b>'
        out += "".join(
            '<i class="sq"></i>' if c is None else
            f'<i class="sq l{c["level"]}" title="{c["date"]} : {c["count"]}"></i>' for c in w + [None] * (7 - len(w)))
    legend = "".join(f'<i class="sq l{n}"></i>' for n in range(5))
    return (f'<div class="heat" style="--weeks:{len(weeks)}">{out}</div>'
            f'<div class="heat-foot"><span>{data["total"]["lastYear"]} {t["gh_total"]}</span>'
            f'<span class="legend">{t["gh_less"]} {legend} {t["gh_more"]}</span></div>')


# ---------------------------------------------------------------- jeux
GAME_EN = {
    "Nouvelle partie": "New game", "Score :": "Score:", "Meilleur :": "Best:", "Classement global": "Global leaderboard",
    "Chargement…": "Loading…", "Votre pseudo": "Your nickname", "Soumettre score": "Submit score",
    "Flèches clavier ou swipe mobile": "Arrow keys or swipe on mobile",
    "Un score par pseudo — seul le meilleur est conservé.": "One score per nickname, only the best is kept.",
    "Classement partagé entre tous les visiteurs.": "Leaderboard shared between all visitors.",
}
GAME_JS_EN = {
    "2048 atteint ! Continuez…": "2048 reached! Keep going…", "Game over !": "Game over!",
    "Classement local (API indisponible)": "Local leaderboard (API unavailable)",
    "Entrez un pseudo avant de soumettre.": "Enter a nickname before submitting.",
    "Score soumis au classement global !": "Score submitted to the global leaderboard!",
    "Score sauvegardé localement (API non disponible).": "Score saved locally (API unavailable).",
    "Chargement…": "Loading…", "Aucun score": "No score yet", "Classement global": "Global leaderboard",
    "Soumettre score": "Submit score",
}
GT = {
    "fr": {"score": "Score", "best": "Meilleur", "moves": "Coups", "time": "Temps", "left": "Essais restants"},
    "en": {"score": "Score", "best": "Best", "moves": "Moves", "time": "Time", "left": "Tries left"},
}


def build_game_js():
    js = (ROOT / "src/game.js").read_text()
    for fr in GAME_JS_EN:
        js = js.replace(f"'{fr}'", f"T('{fr}')").replace(f">{fr}</div>", f">'+T('{fr}')+'</div>")
    js = js.replace("alert('Votre score est 0 — jouez d\\'abord !')", "alert(T('Votre score est 0 — jouez d\\'abord !'))")
    gate = "document.addEventListener('keydown', e=>{\n"
    assert gate in js
    # les flèches ne pilotent le 2048 que quand son onglet est affiché
    js = js.replace(gate, gate + "      if(!document.getElementById('g-2048').classList.contains('on')) return;\n", 1)
    en = dict(GAME_JS_EN)
    en["Votre score est 0 — jouez d'abord !"] = "Your score is 0, play first!"
    head = ("// Traductions : la langue est portée par <html lang>.\n"
            f"var TR_EN = {json.dumps(en, ensure_ascii=False)};\n"
            "function T(s){ return document.documentElement.lang === 'en' && TR_EN[s] || s; }\n")
    (ROOT / "js/game.js").write_text(head + js)


def games_panels(lang):
    g = (ROOT / "src/game.html").read_text()
    inner = re.search(r'<div class="win-body">(.*)</div>\s*</div>\s*$', g, re.S).group(1)
    inner = re.sub(r'\s*<!-- .*? -->', '', inner)
    if lang == "en":
        for fr, en in GAME_EN.items():
            inner = inner.replace(fr, en)
    t, u = GT[lang], UI[lang]
    return f'''
<div class="gp" id="g-2048"><div class="cols"><div>{inner}</div><aside class="sb" data-game="2048"></aside></div></div>
<div class="gp" id="g-snake"><div class="cols"><div class="play">
  <div class="gbar"><span>{t["score"]} <b id="sn-score">0</b></span><span>{t["best"]} <b id="sn-best">0</b></span><span class="msg" id="sn-msg"></span><button class="xp-btn" id="sn-btn" type="button"></button></div>
  <canvas id="snake" width="360" height="360"></canvas><p class="lead help" id="snake-help"></p></div><aside class="sb" data-game="snake"></aside></div></div>
<div class="gp" id="g-memory"><div class="cols"><div class="play">
  <div class="gbar"><span>{t["moves"]} <b id="mem-moves">0</b></span><span>{t["time"]} <b id="mem-time">0s</b></span><span>{t["best"]} <b id="mem-best">–</b></span><span class="msg" id="mem-msg"></span><button class="xp-btn" id="mem-btn" type="button"></button></div>
  <div class="mem" id="mem"></div><p class="lead help" id="mem-help"></p></div><aside class="sb" data-game="memory"></aside></div></div>
<div class="gp" id="g-code"><div class="cols"><div class="play"><div class="cb">
  <div class="gbar"><span>{t["left"]} <b id="cb-left">8</b></span><span class="msg" id="cb-msg"></span><button class="xp-btn" id="cb-btn" type="button"></button></div>
  <div class="cb-rows" id="cb-rows"></div><div class="pad" id="cb-pad"></div><p class="lead help" id="cb-help"></p></div></div><aside class="sb" data-game="code"></aside></div></div>
<div class="gp" id="g-cipher"><div class="cols"><div class="play"><div class="ci">
  <div class="gbar"><span>{t["score"]} <b id="ci-score">0</b></span><span>{t["time"]} <b id="ci-time">60s</b></span><span>{t["best"]} <b id="ci-best">0</b></span><span class="msg" id="ci-msg"></span><button class="xp-btn" id="ci-btn" type="button"></button></div>
  <p class="ci-text" id="ci-cipher">· · ·</p><p class="ci-text ci-plain" id="ci-plain" aria-live="polite">· · ·</p>
  <div class="ci-ctl"><button class="round" id="ci-down" type="button" aria-label="−1">◀</button><span>{u["ci_shift"]} <b id="ci-shift">0</b></span><button class="round" id="ci-up" type="button" aria-label="+1">▶</button><button class="xp-btn" id="ci-ok" type="button">{u["ci_ok"]}</button></div>
  <p class="lead help">{u["ci_help"]}</p></div></div><aside class="sb" data-game="cipher"></aside></div></div>
<div class="gp" id="g-ctf"><div class="cols"><div class="play ctf"><h3>{u["ctf_h"]}</h3><p>{u["ctf_p"]}</p>
  <ol>{"".join(f"<li>{esc(h)}</li>" for h in u["ctf_hints"])}</ol><button class="btn btn-primary" type="button" data-act="term">{u["ctf_open"]}</button></div><aside class="sb" data-ctf></aside></div></div>'''


# ---------------------------------------------------------------- briques
def poster(p, vt=False):
    name = f";view-transition-name:p-{p['slug']}" if vt else ""  # nom unique par page : la vignette devient la bannière au clic
    return f'<div class="poster" data-p="{p["slug"]}" style="--h:{p["hue"]}{name}"><span class="glyph">{p["glyph"]}</span></div><div class="shade"></div>'


def proj_card(lang, p, me, vt=False):
    d, t = p[lang], UI[lang]
    return (f'<a class="proj" href="{rel(me, out_path(lang, "detail", p["slug"]))}" data-kind="{p["kind"]}">{poster(p, vt)}'
            f'<span class="pill">{t["kinds"][p["kind"]]}</span>'
            f'<div class="meta"><h3>{d["title"]}</h3><p>{d["short"]}</p></div><span class="go">{ico("right", 20)}</span></a>')


# mesuré avec Lighthouse sur le site en ligne ; à mettre à jour après un gros changement
NOW_FLAGS = 5  # flags du mini-CTF trouvés par moi (affiché dans « En ce moment »)
LIGHTHOUSE = "Performance 88 · Accessibilité 98 · Bonnes pratiques 100 · SEO 100"
LIGHTHOUSE_EN = "Performance 88 · Accessibility 98 · Best practices 100 · SEO 100"


def og_url(lang, page, slug, title):
    """Aperçu de lien propre à la page (img/og/…), généré une fois avec Pillow et versionné ; sinon l'aperçu général."""
    if page == "home":
        return f"{SITE_URL}/og.png"
    rel_path = f"img/og/{lang}-{slug or page}.png"
    if not (ROOT / rel_path).exists():
        try:
            sys.path.insert(0, str(ROOT / "tools"))
            from images import og_card
            (ROOT / rel_path).parent.mkdir(exist_ok=True)
            og_card(re.sub(r"<[^>]+>", "", title.split(" — ")[0])).save(ROOT / rel_path, optimize=True)
        except Exception as e:  # Pillow ou polices absents (CI) : aperçu général
            print("aperçu de lien :", rel_path, "non généré (", e, ")")
            return f"{SITE_URL}/og.png"
    return f"{SITE_URL}/{rel_path}"


def chrome(lang, page, slug, me, title, desc, body, extra_js=""):
    t, other = UI[lang], ("en" if lang == "fr" else "fr")
    root = "../" * me.count("/")
    r = lambda p, s=None: rel(me, out_path(lang, p, s))
    # la page 404 n'existe qu'à la racine : ses liens de langue mènent aux accueils
    lp = "home" if page == "notfound" else page
    nav = [("home", t["nav"][0], "home"), ("list", t["nav"][1], "folder"), ("game", t["nav"][2], "game"),
           ("writeups", t["nav"][5], "shield"), ("about", t["nav"][3], "user"), ("contact", t["nav"][4], "mail")]
    cur = {"detail": "list", "gallery": "about"}.get(page, page)
    here = ' aria-current="page"'
    tabs = "".join(f'<a href="{r(k)}"{here if k == cur else ""}>{label}</a>' for k, label, _ in nav)
    dock = "".join(f'<a href="{r(k)}" data-tip="{label}" aria-label="{label}"{here if k == cur else ""}>{ico(ic)}</a>' for k, label, ic in nav)
    dock += (f'<button type="button" data-act="palette" data-tip="⌘K" aria-label="{t["pal_ph"]}">{ico("cmd")}</button>'
             f'<button type="button" data-act="theme" data-tip="{t["pal_theme"]}" aria-label="{t["pal_theme"]}">{ico("moon")}</button>')
    path = "~/amex" + (PATH[page] if page != "detail" else f"/projets/{slug}")
    on = ' aria-current="true"'
    notifs = "".join(f'<li><b>{a}</b><span>{b}</span></li>' for a, b in t["notifs"])
    descs = {"home": t["meta"], "list": t["list_lead"], "game": t["games_lead"], "writeups": t["wu_lead"], "about": t["about_lead"],
             "gallery": t["gal_lead"], "contact": t["contact_lead"]}
    # la galerie n'est pas dans la navigation (sous-page d'À propos) mais la palette et le terminal la connaissent
    pages = nav[:5] + [("gallery", re.sub(r"<[^>]+>", "", t["gal_title"]), "")] + nav[5:]
    cmd = {
        "pages": [{"t": label, "u": r(k), "i": PAGE_NUM[k], "k": TERM_NAMES[k], "d": descs[k]} for k, label, _ in pages],
        "projects": [{"t": p[lang]["title"], "u": r("detail", p["slug"]), "k": t["kinds"][p["kind"]], "s": p["slug"], "d": p[lang]["short"]} for p in PROJECTS],
        "links": [{"t": "GitHub", "u": GITHUB}, {"t": "LinkedIn", "u": LINKEDIN}, {"t": t["source"], "u": SITE_REPO}],
        "langUrl": rel(me, out_path(other, lp, slug)), "cvUrl": rel(me, out_path(lang, "contact")) + "?cv=1#contact-form",
        "l": {"pages": t["pal_pages"], "projects": t["pal_projects"], "actions": t["pal_actions"], "links": t["pal_links"],
              "theme": t["pal_theme"], "lang": t["pal_lang"], "accent": t["pal_accent"], "accents": t["accent_names"], "empty": t["pal_empty"],
              "term": t["pal_term"], "motion": t["pal_motion"], "music": t["pal_music"], "cv": t["cv_ask"]},
    }
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{abs_url(out_path(l, lp, slug))}">' for l in ("fr", "en"))
    alts += f'<link rel="alternate" hreflang="x-default" href="{abs_url(out_path("fr", lp, slug))}">'
    boot = ("<script>try{var d=document.documentElement,t=localStorage.getItem('theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');"
            "d.dataset.theme=t;var a=localStorage.getItem('accent');if(a)d.dataset.accent=a}catch(e){}</script>")
    plain = lambda s: esc(re.sub(r"<[^>]+>", "", s)).replace('"', "&quot;")
    if page == "notfound":
        # servie à n'importe quelle adresse : <base> pour que les liens relatifs partent de la racine
        seo = '<base href="/"><meta name="robots" content="noindex">'
    else:
        url = abs_url(me)
        seo = (f'<link rel="canonical" href="{url}">{alts}'
               f'<meta property="og:type" content="website"><meta property="og:site_name" content="Alexandre K.">'
               f'<meta property="og:title" content="{plain(title)}"><meta property="og:description" content="{plain(desc)}">'
               f'<meta property="og:url" content="{url}"><meta property="og:image" content="{og_url(lang, page, slug, title)}">'
               f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
               f'<meta property="og:locale" content="{t["og_locale"]}"><meta name="twitter:card" content="summary_large_image">')
        if page in ("home", "about"):
            # données structurées : qui je suis, pour les moteurs de recherche (un bloc de données, non exécuté : hors CSP)
            person = {"@context": "https://schema.org", "@type": "Person", "name": "Alexandre K.", "jobTitle": t["who_tag"],
                      "url": abs_url(out_path(lang, "home")), "image": f"{SITE_URL}/img/avatar.webp", "sameAs": [GITHUB, LINKEDIN],
                      "affiliation": {"@type": "EducationalOrganization", "name": "Ynov Campus Sophia Antipolis"},
                      "address": {"@type": "PostalAddress", "addressRegion": "Alpes-Maritimes", "addressCountry": "FR"},
                      "knowsLanguage": ["fr", "en"]}
            seo += f'<script type="application/ld+json">{json.dumps(person, ensure_ascii=False)}</script>'

    icons = (f'<link rel="icon" href="{root}favicon.svg" type="image/svg+xml"><link rel="icon" href="{root}favicon.ico" sizes="32x32">'
             f'<link rel="apple-touch-icon" href="{root}apple-touch-icon.png">')
    flag = f"\n  <!-- {CTF_FLAGS[0]} : 1/6, le code source ne ment jamais. -->" if page == "home" else ""
    pl_items = "".join(f'<li><button type="button" data-i="{i}">{esc(name)}</button></li>' for i, (_, name) in enumerate(TRACKS))
    tracks = json.dumps([{"t": name, "u": f"{root}audio/{s}.mp3"} for s, name in TRACKS], ensure_ascii=False).replace("</", "<\\/")
    return f'''<!DOCTYPE html>
<html lang="{lang}" data-konami="{t["konami"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#0b1220" media="(prefers-color-scheme: dark)"><meta name="theme-color" content="#8fb4d8" media="(prefers-color-scheme: light)">
  {seo}
  {icons}
  {FONTS.format(root=root)}
  <link rel="stylesheet" href="{root}style.css">
  {boot}{flag}
</head>
<body>
<button class="tty-fab" type="button" data-act="term" aria-label="{t["ctf_open"]}" title="{t["ctf_open"]}">{ico("terminal", 20)}</button>
<div class="urlbar">
  <button class="round" type="button" data-act="back" aria-label="{t["back"]}">{ico("left", 18)}</button>
  <button class="round" type="button" data-act="forward" aria-label="{t["forward"]}">{ico("right", 18)}</button>
  <div class="path"><b>{path}</b></div>
  <div class="lang" role="group" aria-label="Langue / Language"><a href="{rel(me, out_path("fr", lp, slug))}" hreflang="fr" lang="fr"{on if lang == "fr" else ""}>FR</a><a href="{rel(me, out_path("en", lp, slug))}" hreflang="en" lang="en"{on if lang == "en" else ""}>EN</a></div>
</div>
<div class="dock" role="navigation" aria-label="Dock">{dock}</div>
<div class="shell">
  <header class="topbar">
    <button class="search" type="button" data-act="palette">{ico("search", 18)}<span>{t["search_ph"]}</span><kbd>⌘K</kbd></button>
    <nav class="tabs" aria-label="Navigation">{tabs}</nav>
    <div class="top-right">
      <button class="round bell" type="button" data-act="bell" aria-label="{t["notif_h"]}">{ico("bell", 19)}<i></i></button>
      <a class="profile" href="{r("about")}"><img class="avatar" src="{root}img/avatar.webp" width="256" height="256" alt=""><div><b>Alexandre K.</b><small>{t["handle"]}</small></div></a>
      <div class="drop" id="notifs"><h4>{t["notif_h"]}</h4><ul>{notifs}</ul></div>
    </div>
  </header>
  <main class="page">
{body}
  </main>
</div>
<div class="foot">
  <a href="{GITHUB}" target="_blank" rel="noopener">GitHub</a><a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a><a href="{SITE_REPO}" target="_blank" rel="noopener">{t["source"]}</a>
  <div class="mt-8">{t["rights"]} · {t["kb_hint"]}</div>
  <div class="mt-4">Lighthouse (mobile, 29/10/2026) : {LIGHTHOUSE if lang == "fr" else LIGHTHOUSE_EN}</div>
</div>
<div class="pal-bg" role="dialog" aria-modal="true" aria-label="{t["search_ph"]}"><div class="pal"><input type="text" placeholder="{t["pal_ph"]}" aria-label="{t["search_ph"]}" autocomplete="off"><ul></ul><footer>{t["pal_hint"]}</footer></div></div>
<div class="tty-bg" role="dialog" aria-modal="true" aria-label="Terminal"><div class="term tty"><div class="term-bar"><button class="tty-x" type="button" aria-label="{t["tty_close"]}">✕</button><span></span><span></span><em>amex@portfolio: ~</em></div><div class="tty-out" aria-live="polite"></div><label class="tty-in"><span class="p">$</span><input type="text" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Terminal"></label></div></div>
<div class="toast" role="status"></div>
<div class="player" role="region" aria-label="{t["pl_label"]}">
  <div class="pl-pill"><button class="pl-toggle" type="button" aria-expanded="false" aria-label="{t["pl_list"]}"><i></i><i></i><i></i><i></i></button><span class="pl-now"></span>
    <button class="round pl-play" type="button" aria-label="{t["pl_play"]}" data-play="{t["pl_play"]}" data-pause="{t["pl_pause"]}">{ico("play", 16)}{ico("pause", 16)}</button></div>
  <div class="pl-panel"><b class="pl-title"></b><small>amex · FL Studio</small>
    <input class="pl-seek" type="range" min="0" max="1000" value="0" aria-label="{t["pl_seek"]}"><div class="pl-time"><span>0:00</span><span>0:00</span></div>
    <div class="pl-ctl"><button class="round pl-shuffle" type="button" aria-pressed="false" aria-label="{t["pl_shuffle"]}">{ico("shuffle", 16)}</button><button class="round pl-prev" type="button" aria-label="{t["pl_prev"]}">{ico("prev", 16)}</button><button class="round pl-play" type="button" aria-label="{t["pl_play"]}" data-play="{t["pl_play"]}" data-pause="{t["pl_pause"]}">{ico("play", 16)}{ico("pause", 16)}</button><button class="round pl-next" type="button" aria-label="{t["pl_next"]}">{ico("next", 16)}</button><button class="round pl-like" type="button" aria-pressed="false" data-like="{t["pl_like"]}" data-unlike="{t["pl_unlike"]}" aria-label="{t["pl_like"]}">{ico("heart", 16)}</button></div>
    <label class="pl-vol">{ico("volume", 16)}<input class="pl-volume" type="range" min="0" max="100" value="35" aria-label="{t["pl_volume"]}"></label>
    <ol class="pl-list" aria-label="{t["pl_list"]}">{pl_items}</ol></div>
</div>
<script type="application/json" id="tracks">{tracks}</script>
<script src="{root}js/nav.js"></script>
<script src="{root}js/player.js"></script>
<script type="application/json" id="cmd-data">{json.dumps(cmd, ensure_ascii=False).replace("</", "<\\/")}</script>
<script src="{root}js/site.js"></script>
{extra_js.replace("ROOT/", root)}
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
'''


def cv_cards(lang, detailed):
    """Éléments du CV : parcours cyber, formation, langues (+ autres projets en version détaillée)."""
    c = CV[lang]
    chips = lambda xs: '<div class="tags">' + "".join(f"<span>{x}</span>" for x in xs) + '</div>'
    hl = "".join(
        f'<div class="hl"><b>{n}</b><small>{sub}</small>' + (f'<p>{d}</p>' if detailed else "") + chips(tg if detailed else tg[:4]) + '</div>'
        for n, sub, d, tg in c["highlights"])
    edu = "".join(f'<div class="hl"><b>{n}</b><small>{s}</small></div>' for n, s in c["edu"])
    langs = "".join(f'<div class="lg"><b>{n}</b><span>{lv}</span></div>' for n, lv in c["langs"])
    out = [card(f'<div class="card-h"><h3>{c["hl_h"]}</h3></div>{hl}'), card(f'<div class="card-h"><h3>{c["edu_h"]}</h3></div>{edu}'),
           card(f'<div class="card-h"><h3>{c["lang_h"]}</h3></div><div class="langs">{langs}</div>')]
    if detailed:
        more = "".join(f'<div class="hl"><b>{n}</b><small>{sub}</small><p>{d}</p>{chips(tg)}</div>' for n, sub, d, tg in c["more"])
        out.append(card(f'<div class="card-h"><h3>{c["more_h"]}</h3></div>{more}'))
    return out


def skills_card(lang):
    t = UI[lang]
    rows = "".join(
        f'<div class="row"><div class="ic">{ico(SKILL_ICONS[i])}</div><div><b>{h}</b><small>{" · ".join(items)}</small></div></div>'
        for i, (h, items) in enumerate(t["skills"]))
    return card(f'<div class="card-h"><h3>{t["stack_card"]}</h3></div><div class="rows">{rows}</div>')


def card(inner, cls="", extra=""):
    return f'<section class="card fadein {cls}"{extra}>{inner}</section>'


def head_c(lang, me, crumb_last, title, lead, extra=""):
    t = UI[lang]
    return (f'<div class="head-c"><div class="crumbs"><a href="{rel(me, out_path(lang, "home"))}">{t["crumb_home"]}</a><span>/</span><span>{crumb_last}</span></div>'
            f'<h1 class="page-title">{title}</h1><p class="lead">{lead}</p>{extra}</div>')


# ---------------------------------------------------------------- pages
def build_home(lang):
    t, me = UI[lang], out_path(lang, "home")
    r = lambda p, s=None: rel(me, out_path(lang, p, s))
    lines = ""
    for n, (cls, txt) in enumerate(t["term"]):
        txt = f'<span class="p">$</span> {esc(txt)}' if cls == "p" else (f'<span class="{cls}">{esc(txt)}</span>' if cls else esc(txt))
        tail = '<span class="cursor"></span>' if n == len(t["term"]) - 1 else ""
        lines += f'<span class="line" style="animation-delay:{.3 + n * .35:.2f}s">{txt}{tail}</span>\n'
    intro = f'''<div class="slide intro on">
      <div><span class="label"><b>00</b> / {t["welcome"]}</span><h1>{t["h1"]}</h1><p>{t["bio"]}</p>
        <div class="btn-row"><a class="btn btn-primary" href="{r("list")}">{t["cta_projects"]}</a><a class="btn" href="{r("contact")}">{t["cta_contact"]}</a></div></div>
      <div class="term" aria-hidden="true"><div class="term-bar"><span></span><span></span><span></span><em>amex@kali: ~</em></div><pre>{lines}</pre></div>
    </div>'''
    # carrousel : présentation, galerie, puis les projets choisis dans HOME_PROJECTS (les autres restent sur la page Projets)
    shown = [p for p in PROJECTS if p["slug"] in HOME_PROJECTS]
    slides = "".join(
        f'''<div class="slide pj" aria-hidden="true">{poster(p)}<div class="inner">
      <span class="pill">{t["featured"]} · {t["kinds"][p["kind"]]}</span><h2>{p[lang]["title"]}</h2>
      <div class="tags">{"".join(f"<span>{x}</span>" for x in p["tech"][:3])}</div><p>{p[lang]["short"]}</p>
      <div class="btn-row"><a class="btn btn-primary" href="{r("detail", p["slug"])}">{ico("play", 16)} {t["see"]}</a><a class="btn" href="{p["code"]}" target="_blank" rel="noopener">{ico("code", 16)} {t["code"]}</a></div></div></div>'''
        for p in shown)
    work = {w["slug"]: w for w in GALLERY}
    gtiles = "".join(f'<img src="{rel(me, f"img/gallery/{s}-thumb.webp")}" {dims(f"img/gallery/{s}-thumb.webp")} alt="{esc(work[s][lang])}" loading="lazy" decoding="async">' for s in HOME_GALLERY)
    gtags = "".join(f"<span>{x}</span>" for x in t["series"].values())
    gallery_slide = f'''<div class="slide pj gl" aria-hidden="true"><div class="gl-bg" style="background-image:url('{rel(me, f"img/gallery/{HOME_GALLERY[0]}-thumb.webp")}')"></div><div class="shade"></div><div class="gl-tiles" aria-hidden="true">{gtiles}</div><div class="inner">
      <span class="pill">{t["featured"]} · {re.sub(r"<[^>]+>", "", t["gal_title"])}</span><h2>{t["gal_title"].replace("<em>", "").replace("</em>", "")}</h2>
      <div class="tags">{gtags}</div><p>{t["gal_lead"]}</p>
      <div class="btn-row"><a class="btn btn-primary" href="{r("gallery")}">{ico("play", 16)} {t["ext_gallery"]}</a></div></div></div>'''
    slides = gallery_slide + slides
    n_slides = len(shown) + 2
    dots = "".join(f'<button type="button" aria-label="{t["slide_n"].format(n=i + 1, total=n_slides)}"></button>' for i in range(n_slides))
    nav = (f'<div class="hero-nav"><button class="round" type="button" data-act="pause" aria-pressed="false" aria-label="{t["slide_pause"]}" data-pause="{t["slide_pause"]}" data-play="{t["slide_play"]}">{ico("pause", 16)}{ico("play", 16)}</button>'
           f'<button class="round" type="button" data-act="prev" aria-label="{t["slide_prev"]}">{ico("left", 18)}</button>'
           f'<button class="round" type="button" data-act="next" aria-label="{t["slide_next"]}">{ico("right", 18)}</button></div>')
    hero = card(f'{intro}{slides}<div class="dots">{dots}</div>{nav}', "hero")
    who = card(f'''<div class="who"><img class="avatar" src="{rel(me, "img/avatar.webp")}" width="256" height="256" alt=""><h3>Alexandre K.</h3><p>{t["who_tag"]}</p>
      <div class="btn-row"><a class="btn small" href="{GITHUB}" target="_blank" rel="noopener">{ICON_GH} GitHub</a><a class="btn small" href="{LINKEDIN}" target="_blank" rel="noopener">{ICON_LI} LinkedIn</a></div>
      <div class="status"><span class="dot"></span>{t["status"]}</div></div>''')
    skills = skills_card(lang)
    cards = "".join(proj_card(lang, p, me) for p in PROJECTS)
    discover = card(f'<div class="card-h"><h3>{t["discover"]}</h3><a href="{r("list")}">{t["see_all"]}</a></div><div class="proj-grid">{cards}</div>')
    contact = card(f'<div class="head-c tight"><span class="label">{t["contact_label"]}</span><h2>{t["contact_h"]}</h2><p class="lead">{t["contact_lead"]}</p>'
                   f'<div class="btn-row center"><a class="btn btn-primary" href="{r("contact")}">{t["cta_contact"]}</a><a class="btn" href="{LINKEDIN}" target="_blank" rel="noopener">{ICON_LI} LinkedIn</a></div></div>')
    body = f'<div class="home"><div class="stack aside">{who}{skills}{"".join(cv_cards(lang, False))}</div><div class="stack">{hero}{discover}</div></div>\n{contact}'
    return chrome(lang, "home", None, me, t["title"], t["meta"], body)


def build_list(lang):
    t, me = UI[lang], out_path(lang, "list")
    kinds = sorted({p["kind"] for p in PROJECTS})
    btns = f'<button type="button" data-f="all" aria-pressed="true">{t["all"]}</button>' + "".join(
        f'<button type="button" data-f="{k}" aria-pressed="false">{t["kinds"][k]}</button>' for k in kinds)
    cards = "".join(proj_card(lang, p, me, True) for p in PROJECTS)
    body = (head_c(lang, me, t["crumb_projects"], t["list_title"], t["list_lead"], f'<div class="filters" role="group">{btns}</div>')
            + f'<div class="proj-grid fadein">{cards}</div>')
    return chrome(lang, "list", None, me, f'{t["crumb_projects"]} — Alexandre K.', t["list_lead"], body)


def build_detail(lang, p):
    t, d, me = UI[lang], p[lang], out_path(lang, "detail", p["slug"])
    r = lambda pg, s=None: rel(me, out_path(lang, pg, s))
    tags = "".join(f"<span>{x}</span>" for x in p["tech"][:4])
    demo_btn = f'<a class="btn btn-primary" href="{p["demo"]}" target="_blank" rel="noopener">{ico("play", 16)} {t["view_demo"]}</a>' if p.get("demo") else ""
    demo_note = f'<p class="demo-note">{t["demo_note"]}</p>' if p.get("demo") else ""
    banner = (f'<section class="card banner fadein">{poster(p, True)}<div class="inner">'
              f'<div class="crumbs"><a href="{r("home")}">{t["crumb_home"]}</a><span>/</span><a href="{r("list")}">{t["crumb_projects"]}</a><span>/</span><span>{d["title"]}</span></div>'
              f'<h1>{d["title"]} <em>{t["detail_word"]}</em></h1><div class="tags">{tags}</div>'
              f'<div class="btn-row">{demo_btn}<a class="btn {"" if demo_btn else "btn-primary"}" href="{p["code"]}" target="_blank" rel="noopener">{ICON_GH} {t["view_code"]}</a><a class="btn" href="{r("list")}">{t["all_projects"]}</a></div>{demo_note}</div></section>')
    study = card('<div class="card-h"><h3>' + t["case_h"] + '</h3></div><div class="case">' + "".join(
        f'<div><small>{k}</small><p>{v}</p></div>' for k, v in zip(t["case_k"], d["case"])) + '</div>')
    longp = "".join(f"<p>{x}</p>" for x in d["long"])
    chips = "".join(f"<span>{x}</span>" for x in p["tech"])
    feats = "".join(f"<li>{x}</li>" for x in d["features"])
    main = card(f'<div class="block"><h3>{t["description"]}</h3>{longp}</div><div class="block"><h3>{t["tech"]}</h3><div class="chips">{chips}</div></div>'
                f'<div class="block"><h3>{t["features"]}</h3><ul class="feat">{feats}</ul></div>')
    tree = esc("\n".join(TREES[p["slug"]]))
    facts = (f'<dl class="facts"><div><dt>{t["f_type"]}</dt><dd>{t["kinds"][p["kind"]]}</dd></div><div><dt>{t["f_context"]}</dt><dd>{t["context"]}</dd></div>'
             f'<div><dt>{t["f_lang"]}</dt><dd>{p["lang"]}</dd></div><div><dt>{t["f_repo"]}</dt><dd><a href="{p["code"]}" target="_blank" rel="noopener">GitHub ↗</a></dd></div>'
             + (f'<div><dt>Demo</dt><dd><a href="{p["demo"]}" target="_blank" rel="noopener">{t["view_demo"]} ↗</a></dd></div>' if p.get("demo") else "") + '</dl>')
    shots = sorted(f for f in (ROOT / "img").glob(f'{p["slug"]}-*.webp') if not f.stem.endswith("-800"))  # captures : tools/shots.py

    def shot(f):
        w, h = webp_size(f)
        full, small = rel(me, "img/" + f.name), rel(me, f"img/{f.stem}-800.webp")
        return (f'<a href="{full}" target="_blank" rel="noopener"><img src="{small}" srcset="{small} 800w, {full} {w}w" '
                f'sizes="(max-width: 700px) 100vw, 50vw" width="{w}" height="{h}" alt="{d["title"]}" loading="lazy" decoding="async"></a>')
    gallery = card(f'<div class="card-h"><h3>{t["preview_h"]}</h3></div><div class="shots">' + "".join(map(shot, shots)) + '</div>') if shots else ""
    side = (f'<aside class="side"><div class="term fadein"><div class="term-bar"><span></span><span></span><span></span><em>{p["slug"]} ~ {t["repo_tree"].lower()}</em></div><pre class="tree">{tree}</pre></div>'
            + card(facts) + '</aside>')
    others = sorted((q for q in PROJECTS if q["slug"] != p["slug"]), key=lambda q: q["kind"] != p["kind"])
    sim = card(f'<div class="card-h"><h3>{t["similar_small"]}</h3></div><div class="proj-grid">{"".join(proj_card(lang, q, me, True) for q in others[:3])}</div>')
    return chrome(lang, "detail", p["slug"], me, f'{d["title"]} — Alexandre K.', d["short"], f'{banner}{study}<div class="detail-grid">{main}{side}</div>{gallery}{sim}')


def build_game(lang):
    t, me = UI[lang], out_path(lang, "game")
    tabs = "".join(f'<button type="button" role="tab" data-g="{g}" aria-selected="false">{n}</button>'
                   for g, n in zip(["g-2048", "g-snake", "g-memory", "g-code", "g-cipher", "g-ctf"], t["games_tabs"]))
    body = head_c(lang, me, t["nav"][2], t["games_title"], t["games_lead"]) + card(f'<div class="seg" role="tablist">{tabs}</div>{games_panels(lang)}')
    return chrome(lang, "game", None, me, f'{t["nav"][2]} — Alexandre K.', t["games_lead"], body,
                  '<script src="ROOT/js/game.js"></script><script src="ROOT/js/games.js"></script><script src="ROOT/js/scores.js"></script>')


def build_about(lang, data):
    t, me = UI[lang], out_path(lang, "about")
    hw = "".join(f'<div class="tile"><div class="tile-ico">{ICONS_HW[k]}</div><b>{name}</b><small>{sub}</small></div>' for name, sub, k in t["hardware"])
    sw = "".join(
        f'<a class="tile" href="{url}" target="_blank" rel="noopener"><div class="tile-ico"{f" style=color:{c}" if c else ""}>{brand_icon(ic)}</div><b>{n}</b></a>'
        for n, ic, url, c in SOFTWARE)
    gh = card(f'<div class="head-c flush"><span class="label">{t["gh_small"]}</span><h2>{t["gh_h"]}</h2></div>{heatmap(lang, data)}')
    setup = card(f'<div class="block"><h3>{t["hw_h"]}</h3><div class="tiles">{hw}</div></div><div class="block"><h3>{t["sw_h"]}</h3><div class="tiles">{sw}</div></div>')
    left = f'<div class="stack">{skills_card(lang)}{"".join(cv_cards(lang, True))}</div>'
    tags = lambda xs: '<div class="tags">' + "".join(f"<span>{x}</span>" for x in xs) + '</div>'
    peek = "".join(f'<img src="{rel(me, "img/gallery/" + s + "-thumb.webp")}" {dims("img/gallery/" + s + "-thumb.webp")} alt="" loading="lazy" decoding="async">' for s in ("clive-neon", "flame-radio", "knight"))
    ext = card(f'''<div class="head-c flush"><span class="label">{t["ext_h"]}</span><h2>{t["ext_lead"]}</h2></div>
      <div class="ext"><div class="block"><h3>{t["ext_music_h"]}</h3><p>{t["ext_music"]}</p>{tags(["FL Studio", "Breakcore", "Jungle", "UK garage", "Trap"])}
        <div class="btn-row mt-14"><button class="btn btn-primary" type="button" data-act="music">{ico("play", 16)} {t["ext_listen"]}</button></div></div>
      <div class="block"><h3>{t["ext_art_h"]}</h3><p>{t["ext_art"]}</p>{tags(["Procreate", "Photoshop", "Blender"])}
        <a class="ext-peek" href="{rel(me, out_path(lang, "gallery"))}">{peek}<span class="btn">{t["ext_gallery"]} {ico("right", 16)}</span></a></div></div>''', "ext-card")
    last30 = sum(c["count"] for c in data["contributions"][-30:])
    now = card(f'<div class="head-c flush"><span class="label">{t["now_label"]}</span><h2>{t["now_h"]}</h2></div><ul class="now">'
               f'<li><span>{t["now_study"]}</span><b>{t["who_tag"]}</b><small>{t["status"]}</small></li>'
               f'<li><span>{t["now_last"]}</span><b data-now="last" data-none="{t["now_none"]}">…</b></li>'
               f'<li><span>{t["now_top"]}</span><b data-now="top">…</b></li>'
               f'<li><span>GitHub</span><b>{last30} <small>{t["now_gh"]}</small></b></li>'
               f'<li><span>{t["now_ctf"]}</span><b>{NOW_FLAGS} / {len(CTF_FLAGS)}</b></li></ul>', "now-card")
    body = head_c(lang, me, t["nav"][3], t["about_title"], t["about_lead"]) + f'<div class="about-grid">{left}<div class="stack">{now}{ext}{gh}{setup}</div></div>'
    return chrome(lang, "about", None, me, f'{t["nav"][3]} — Alexandre K.', t["about_lead"], body)


def build_gallery(lang):
    t, me = UI[lang], out_path(lang, "gallery")
    img = lambda f: rel(me, "img/gallery/" + f)
    when = lambda d: f'{t["months"][int(d[5:7]) - 1]} {d[:4]}' if d else ""
    series = list(dict.fromkeys(w["series"] for w in GALLERY))
    count = {s: sum(w["series"] == s for w in GALLERY) for s in series}
    items = "".join(
        f'<button class="gal-item" type="button" data-i="{i}" data-s="{w["series"]}" data-full="{img(w["slug"] + "." + w.get("ext", "webp"))}">'
        f'<img src="{img(w["slug"] + "-thumb.webp")}" {dims("img/gallery/" + w["slug"] + "-thumb.webp")} alt="{esc(w[lang])}" loading="lazy" decoding="async"><span><b>{esc(w[lang])}</b><small>{when(w["date"])}</small></span></button>'
        for i, w in enumerate(GALLERY))
    albums = "".join(
        f'<button class="gal-album" type="button" data-s="{s}"><span class="gal-mosaic">'
        + "".join(f'<img src="{img(w["slug"] + "-thumb.webp")}" {dims("img/gallery/" + w["slug"] + "-thumb.webp")} alt="" loading="lazy" decoding="async">' for w in [w for w in GALLERY if w["series"] == s][:4])
        + f'</span><b>{t["series"][s]}</b><small>{count[s]} {t["gal_works"]}</small></button>' for s in series)
    time = "".join(f'<button type="button" role="tab" data-s="{s}" aria-selected="false">{t["series"][s]} <small>{count[s]}</small></button>' for s in series)
    views = "".join(f'<button type="button" data-view="{v}" aria-pressed="false">{label}</button>' for v, label in t["gal_views"].items())
    crumbs = f'<a href="{rel(me, out_path(lang, "about"))}">{t["nav"][3]}</a></span><span>/</span><span>{re.sub(r"<[^>]+>", "", t["gal_title"])}'
    body = head_c(lang, me, crumbs, t["gal_title"], t["gal_lead"]) + card(f'''<div class="gal-bg" aria-hidden="true"></div><div class="gal-bg" aria-hidden="true"></div>
      <aside class="gal-side"><div class="gal-stat"><b>{len(GALLERY)}</b><span>{t["gal_works"]}</span></div><div class="gal-stat"><b>{len(series)}</b><span>{t["gal_series_h"]}</span></div>
        <h4>{t["gal_view_h"]}</h4><div class="gal-views" role="group" aria-label="{t["gal_view_h"]}">{views}</div></aside>
      <div class="gal-main"><div class="gal-head"><h2 class="gal-name"></h2><small class="gal-count" data-unit="{t["gal_works"]}"></small></div>
        <div class="gal-stage" data-view="scatter">{items}</div><div class="gal-albums">{albums}</div>
        <div class="gal-pager" hidden><button class="round gal-prev" type="button" aria-label="{t["page_prev"]}">{ico("left", 16)}</button><span class="gal-page" aria-live="polite"></span><button class="round gal-next" type="button" aria-label="{t["page_next"]}">{ico("right", 16)}</button></div></div>
      <nav class="gal-time" role="tablist" aria-label="{t["gal_series_h"]}">{time}</nav>''', "gal")
    return chrome(lang, "gallery", None, me, f'{re.sub(r"<[^>]+>", "", t["gal_title"])} — Alexandre K.', t["gal_lead"], body,
                  '<script src="ROOT/js/gallery.js"></script>')


def build_contact(lang):
    t, me = UI[lang], out_path(lang, "contact")
    form = ""
    if FORM_ENDPOINT:
        form = f'''<div class="block"><h3>{t["form_h"]}</h3>
      <form id="contact-form" class="form" data-cv="{esc(t["cv_msg"])}" action="{FORM_ENDPOINT}" method="post" data-ok="{t["form_ok"]}" data-err="{t["form_err"]}" data-sending="{t["form_sending"]}">
        <label>{t["form_name"]}<input name="name" required maxlength="80" autocomplete="name"></label>
        <label>{t["form_email"]}<input name="email" type="email" required maxlength="120" autocomplete="email"></label>
        <label>{t["form_msg"]}<textarea name="message" required rows="6" maxlength="3000"></textarea></label>
        <input name="_gotcha" tabindex="-1" autocomplete="off" class="trap" aria-hidden="true">
        <button class="btn btn-primary" type="submit">{t["form_send"]}</button>
        <p class="form-msg" role="status"></p>
      </form></div>'''
    mail = (f'<a class="channel" href="mailto:{EMAIL}"><div class="contact-icon ci-mail">{ICON_MAIL}</div><div><b>E-mail</b><small>{EMAIL}</small></div><span class="go">→</span></a>' if EMAIL else "")
    looking = "".join(f"<li>{x}</li>" for x in t["looking"])
    profile = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in t["profile"])
    left = card(f'''<div class="block"><h3>{t["channels_h"]}</h3>
      <a class="channel" href="{LINKEDIN}" target="_blank" rel="noopener"><div class="contact-icon ci-li">{ICON_LI}</div><div><b>LinkedIn</b><small>alexandre-k-801438256</small></div><span class="go">↗</span></a>
      <a class="channel" href="{GITHUB}" target="_blank" rel="noopener"><div class="contact-icon ci-gh">{ICON_GH}</div><div><b>GitHub</b><small>github.com/amex-32</small></div><span class="go">↗</span></a>{mail}</div>
      {form}<div class="block"><h3>{t["looking_h"]}</h3><ul class="feat">{looking}</ul></div>''')
    cta = card(f'<div class="block"><h3>{t["contact_cta_h"]}</h3><p>{t["contact_cta_p"]}</p><div class="btn-row"><a class="btn btn-primary" href="{LINKEDIN}" target="_blank" rel="noopener">{ICON_LI} {t["write"]}</a>'
               f'<a class="btn" href="{posixpath.basename(me)}?cv=1#contact-form">{t["cv_ask"]}</a></div>'
               f'<p class="mt-14"><span class="dot"></span> {t["status"]}</p></div>')
    right = f'<aside class="side">{cta}{card(f"<dl class=facts>{profile}</dl>")}</aside>'
    body = head_c(lang, me, t["contact_label"], t["contact_h"], t["contact_lead"]) + f'<div class="contact-wrap">{left}{right}</div>'
    return chrome(lang, "contact", None, me, f'{t["contact_label"]} — Alexandre K.', t["contact_lead"], body)


def build_writeups(lang):
    t, me = UI[lang], out_path(lang, "writeups")
    arts = ""
    for w in WRITEUPS:
        d = w[lang]
        secs = "".join(f'<div class="block"><h3>{h}</h3>{"".join(f"<p>{x}</p>" for x in ps)}</div>' for h, ps in d["sections"])
        tags = "".join(f"<span>{x}</span>" for x in w["tags"])
        arts += card(f'<article class="wu" id="{w["slug"]}"><div class="card-h"><h2>{d["title"]}</h2><small>{w["date"]}</small></div>'
                     f'<p class="lead">{d["summary"]}</p><div class="tags">{tags}</div>{secs}</article>')
    body = head_c(lang, me, t["nav"][5], t["wu_title"], t["wu_lead"]) + arts
    return chrome(lang, "writeups", None, me, f'Write-ups — Alexandre K.', t["wu_lead"], body)


def build_404():
    t, me = UI["fr"], out_path("fr", "notfound")
    en = UI["en"]
    body = card(f'<div class="head-c nf"><span class="label"><b>404</b> / not found</span><h1 class="page-title">{t["nf_title"]}</h1>'
                f'<p class="lead">{t["nf_lead"]}</p><p class="lead" lang="en">{en["nf_lead"]}</p>'
                f'<div class="btn-row center"><a class="btn btn-primary" href="index.html">{t["nf_home"]}</a>'
                f'<a class="btn" href="en/index.html" lang="en">{en["nf_home"]}</a>'
                f'<button class="btn" type="button" data-act="term">{t["nf_term"]}</button><a class="btn" href="jeux.html">{t["nf_game"]}</a></div></div>')
    return chrome("fr", "notfound", None, me, "404 — Alexandre K.", t["nf_lead"], body)


def seo_files(pages):
    """robots.txt, sitemap.xml et security.txt (RFC 9116)."""
    b64 = base64.b64encode(CTF_FLAGS[2].encode()).decode()
    robots = f"User-agent: *\nAllow: /\n\n# Rien à cacher ici... ou presque : {b64}\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    urls = ""
    for page, slug in pages:
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{abs_url(out_path(l, page, slug))}"/>' for l in ("fr", "en"))
        alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{abs_url(out_path("fr", page, slug))}"/>'
        urls += "".join(f"<url><loc>{abs_url(out_path(l, page, slug))}</loc>{alts}</url>\n" for l in ("fr", "en"))
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
               f'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n{urls}</urlset>\n')
    # Expires fixé à la fin de l'année suivante : le fichier ne change qu'une fois par an (pas de commit quotidien)
    expires = f"{datetime.date.today().year + 1}-12-31T23:59:59Z"
    security = (f"Contact: {SITE_URL}/contact.html\nContact: {LINKEDIN}\nExpires: {expires}\n"
                f"Preferred-Languages: fr, en\nCanonical: {SITE_URL}/.well-known/security.txt\n")
    write("robots.txt", robots)
    write("sitemap.xml", sitemap)
    write(".well-known/security.txt", security)


def write(path, html):
    f = ROOT / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    for old in [*ROOT.glob("*.html"), *ROOT.glob("projects/*.html"), *ROOT.glob("en/*.html"), *ROOT.glob("en/projects/*.html")]:
        old.unlink()
    build_game_js()
    activity = github_activity()
    for lang in ("fr", "en"):
        write(out_path(lang, "home"), build_home(lang))
        write(out_path(lang, "list"), build_list(lang))
        write(out_path(lang, "game"), build_game(lang))
        write(out_path(lang, "about"), build_about(lang, activity))
        write(out_path(lang, "contact"), build_contact(lang))
        write(out_path(lang, "writeups"), build_writeups(lang))
        write(out_path(lang, "gallery"), build_gallery(lang))
        for p in PROJECTS:
            write(out_path(lang, "detail", p["slug"]), build_detail(lang, p))
    write(out_path("fr", "notfound"), build_404())
    seo_files([(k, None) for k in ("home", "list", "game", "writeups", "about", "gallery", "contact")] + [("detail", p["slug"]) for p in PROJECTS])
    print("ok")

#!/usr/bin/env python3
"""Génère le site (FR à la racine, EN dans en/) : python3 tools/build.py

Textes, projets et icônes : tools/content.py. Jeu 2048 : src/game.html et src/game.js.
"""
import datetime
import json
import os
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
})

PAGE_NUM = {"home": "00", "list": "01", "detail": "01", "game": "02", "about": "03", "contact": "04"}
PATH = {"home": "", "list": "/projets", "game": "/jeux", "about": "/a-propos", "contact": "/contact"}
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
        "detail": f"projects/{slug}.html",
    }
    return pre + names[page]


def rel(src, dst):
    return os.path.relpath(dst, os.path.dirname(src) or ".")


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
    t = UI[lang]
    days = data["contributions"]
    first = datetime.date.fromisoformat(days[0]["date"])
    cells = [None] * ((first.weekday() + 1) % 7) + days  # semaines du dimanche au samedi
    cols = ""
    for i in range(0, len(cells), 7):
        w = cells[i:i + 7]
        month = next((int(c["date"][5:7]) - 1 for c in w if c and c["date"].endswith("-01")), None)
        label = t["months"][month] if month is not None else ""
        sq = "".join(
            '<i class="sq"></i>' if c is None else
            f'<i class="sq l{c["level"]}" title="{c["date"]} : {c["count"]}"></i>' for c in w)
        cols += f'<div class="wk"><b>{label}</b>{sq}</div>'
    dl = "".join(f"<span>{d}</span>" for d in t["days"])
    legend = "".join(f'<i class="sq l{n}"></i>' for n in range(5))
    return (f'<div class="heat"><div class="heat-days"><b></b>{dl}</div><div class="heat-scroll">{cols}</div></div>'
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
    t = GT[lang]
    return f'''
<div class="gp" id="g-2048">{inner}</div>
<div class="gp" id="g-snake"><div class="play">
  <div class="gbar"><span>{t["score"]} <b id="sn-score">0</b></span><span>{t["best"]} <b id="sn-best">0</b></span><span class="msg" id="sn-msg"></span><button class="xp-btn" id="sn-btn" type="button"></button></div>
  <canvas id="snake" width="360" height="360"></canvas><p class="lead" id="snake-help" style="margin:0;font-size:13px"></p></div></div>
<div class="gp" id="g-memory"><div class="play">
  <div class="gbar"><span>{t["moves"]} <b id="mem-moves">0</b></span><span>{t["time"]} <b id="mem-time">0s</b></span><span>{t["best"]} <b id="mem-best">–</b></span><span class="msg" id="mem-msg"></span><button class="xp-btn" id="mem-btn" type="button"></button></div>
  <div class="mem" id="mem"></div><p class="lead" id="mem-help" style="margin:0;font-size:13px"></p></div></div>
<div class="gp" id="g-code"><div class="play"><div class="cb">
  <div class="gbar"><span>{t["left"]} <b id="cb-left">8</b></span><span class="msg" id="cb-msg"></span><button class="xp-btn" id="cb-btn" type="button"></button></div>
  <div class="cb-rows" id="cb-rows"></div><div class="pad" id="cb-pad"></div><p class="lead" id="cb-help" style="margin:0;font-size:13px"></p></div></div></div>'''


# ---------------------------------------------------------------- briques
def poster(p):
    return f'<div class="poster" data-p="{p["slug"]}" style="--h:{p["hue"]}"><span class="glyph">{p["glyph"]}</span></div><div class="shade"></div>'


def proj_card(lang, p, me):
    d, t = p[lang], UI[lang]
    return (f'<a class="proj" href="{rel(me, out_path(lang, "detail", p["slug"]))}" data-kind="{p["kind"]}">{poster(p)}'
            f'<span class="pill">{t["kinds"][p["kind"]]}</span>'
            f'<div class="meta"><h3>{d["title"]}</h3><p>{d["short"]}</p></div><span class="go">{ico("right", 20)}</span></a>')


def chrome(lang, page, slug, me, title, desc, body, extra_js=""):
    t, other = UI[lang], ("en" if lang == "fr" else "fr")
    root = "../" * me.count("/")
    r = lambda p, s=None: rel(me, out_path(lang, p, s))
    nav = [("home", t["nav"][0], "home"), ("list", t["nav"][1], "folder"), ("game", t["nav"][2], "game"),
           ("about", t["nav"][3], "user"), ("contact", t["nav"][4], "mail")]
    cur = "list" if page == "detail" else page
    here = ' aria-current="page"'
    tabs = "".join(f'<a href="{r(k)}"{here if k == cur else ""}>{label}</a>' for k, label, _ in nav)
    dock = "".join(f'<a href="{r(k)}" data-tip="{label}" aria-label="{label}"{here if k == cur else ""}>{ico(ic)}</a>' for k, label, ic in nav)
    dock += (f'<button type="button" data-act="palette" data-tip="⌘K" aria-label="{t["pal_ph"]}">{ico("cmd")}</button>'
             f'<button type="button" data-act="theme" data-tip="{t["pal_theme"]}" aria-label="{t["pal_theme"]}">{ico("moon")}</button>')
    path = "~/amex" + (PATH[page] if page != "detail" else f"/projets/{slug}")
    on = ' aria-current="true"'
    notifs = "".join(f'<li><b>{a}</b><span>{b}</span></li>' for a, b in t["notifs"])
    cmd = {
        "pages": [{"t": label, "u": r(k), "i": PAGE_NUM[k]} for k, label, _ in nav],
        "projects": [{"t": p[lang]["title"], "u": r("detail", p["slug"]), "k": t["kinds"][p["kind"]]} for p in PROJECTS],
        "links": [{"t": "GitHub", "u": GITHUB}, {"t": "LinkedIn", "u": LINKEDIN}, {"t": t["source"], "u": SITE_REPO}],
        "langUrl": rel(me, out_path(other, page, slug)),
        "l": {"pages": t["pal_pages"], "projects": t["pal_projects"], "actions": t["pal_actions"], "links": t["pal_links"],
              "theme": t["pal_theme"], "lang": t["pal_lang"], "accent": t["pal_accent"], "accents": t["accent_names"], "empty": t["pal_empty"]},
    }
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{rel(me, out_path(l, page, slug))}">' for l in ("fr", "en"))
    boot = ("<script>try{var d=document.documentElement,t=localStorage.getItem('theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');"
            "d.dataset.theme=t;var a=localStorage.getItem('accent');if(a)d.dataset.accent=a}catch(e){}</script>")
    return f'''<!DOCTYPE html>
<html lang="{lang}" data-konami="{t["konami"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  {alts}
  {FONTS}
  <link rel="stylesheet" href="{root}style.css">
  {boot}
</head>
<body>
<div class="urlbar">
  <button class="round" type="button" data-act="back" aria-label="{t["back"]}">{ico("left", 18)}</button>
  <button class="round" type="button" data-act="forward" aria-label="{t["forward"]}">{ico("right", 18)}</button>
  <div class="path"><b>{path}</b></div>
  <div class="lang" role="group" aria-label="Langue / Language"><a href="{rel(me, out_path("fr", page, slug))}" hreflang="fr" lang="fr"{on if lang == "fr" else ""}>FR</a><a href="{rel(me, out_path("en", page, slug))}" hreflang="en" lang="en"{on if lang == "en" else ""}>EN</a></div>
</div>
<div class="dock" role="navigation" aria-label="Dock">{dock}</div>
<div class="shell">
  <header class="topbar">
    <button class="search" type="button" data-act="palette">{ico("search", 18)}<span>{t["search_ph"]}</span><kbd>⌘K</kbd></button>
    <nav class="tabs" aria-label="Navigation">{tabs}</nav>
    <div class="top-right">
      <button class="round bell" type="button" data-act="bell" aria-label="{t["notif_h"]}">{ico("bell", 19)}<i></i></button>
      <a class="profile" href="{r("about")}"><span class="avatar">AK</span><div><b>Alexandre K.</b><small>{t["handle"]}</small></div></a>
      <div class="drop" id="notifs"><h4>{t["notif_h"]}</h4><ul>{notifs}</ul></div>
    </div>
  </header>
  <main class="page">
{body}
  </main>
</div>
<div class="foot">
  <a href="{GITHUB}" target="_blank" rel="noopener">GitHub</a><a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a><a href="{SITE_REPO}" target="_blank" rel="noopener">{t["source"]}</a>
  <div style="margin-top:8px">{t["rights"]} · {t["kb_hint"]}</div>
</div>
<div class="pal-bg" role="dialog" aria-modal="true" aria-label="{t["search_ph"]}"><div class="pal"><input type="text" placeholder="{t["pal_ph"]}" aria-label="{t["search_ph"]}" autocomplete="off"><ul></ul><footer>{t["pal_hint"]}</footer></div></div>
<div class="toast" role="status"></div>
<script type="application/json" id="cmd-data">{json.dumps(cmd, ensure_ascii=False)}</script>
<script src="{root}js/site.js"></script>
{extra_js.replace("ROOT/", root)}
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
    slides = "".join(
        f'''<div class="slide pj" aria-hidden="true">{poster(p)}<div class="inner">
      <span class="pill">{t["featured"]} · {t["kinds"][p["kind"]]}</span><h2>{p[lang]["title"]}</h2>
      <div class="tags">{"".join(f"<span>{x}</span>" for x in p["tech"][:3])}</div><p>{p[lang]["short"]}</p>
      <div class="btn-row"><a class="btn btn-primary" href="{r("detail", p["slug"])}">{ico("play", 16)} {t["see"]}</a><a class="btn" href="{p["code"]}" target="_blank" rel="noopener">{ico("code", 16)} {t["code"]}</a></div></div></div>'''
        for p in PROJECTS)
    dots = "".join(f'<button type="button" aria-label="{i + 1}"></button>' for i in range(len(PROJECTS) + 1))
    nav = (f'<div class="hero-nav"><button class="round" type="button" data-act="prev" aria-label="{t["back"]}">{ico("left", 18)}</button>'
           f'<button class="round" type="button" data-act="next" aria-label="{t["forward"]}">{ico("right", 18)}</button></div>')
    hero = card(f'{intro}{slides}<div class="dots">{dots}</div>{nav}', "hero")
    who = card(f'''<div class="who"><div class="avatar">AK</div><h3>Alexandre K.</h3><p>{t["who_tag"]}</p>
      <div class="btn-row"><a class="btn small" href="{GITHUB}" target="_blank" rel="noopener">{ICON_GH} GitHub</a><a class="btn small" href="{LINKEDIN}" target="_blank" rel="noopener">{ICON_LI} LinkedIn</a></div>
      <div class="status"><span class="dot"></span>{t["status"]}</div></div>''')
    skills = skills_card(lang)
    cards = "".join(proj_card(lang, p, me) for p in PROJECTS)
    discover = card(f'<div class="card-h"><h3>{t["discover"]}</h3><a href="{r("list")}">{t["see_all"]}</a></div><div class="proj-grid">{cards}</div>')
    contact = card(f'<div class="head-c" style="padding:6px 0"><span class="label"><b>04</b> / {t["contact_label"]}</span><h2>{t["contact_h"]}</h2><p class="lead">{t["contact_lead"]}</p>'
                   f'<div class="btn-row" style="justify-content:center"><a class="btn btn-primary" href="{r("contact")}">{t["cta_contact"]}</a><a class="btn" href="{LINKEDIN}" target="_blank" rel="noopener">{ICON_LI} LinkedIn</a></div></div>')
    body = f'<div class="home"><div class="stack aside">{who}{skills}{"".join(cv_cards(lang, False))}</div><div class="stack">{hero}{discover}</div></div>\n{contact}'
    return chrome(lang, "home", None, me, t["title"], t["meta"], body)


def build_list(lang):
    t, me = UI[lang], out_path(lang, "list")
    kinds = sorted({p["kind"] for p in PROJECTS})
    btns = f'<button type="button" data-f="all" aria-pressed="true">{t["all"]}</button>' + "".join(
        f'<button type="button" data-f="{k}" aria-pressed="false">{t["kinds"][k]}</button>' for k in kinds)
    cards = "".join(proj_card(lang, p, me) for p in PROJECTS)
    body = (head_c(lang, me, t["crumb_projects"], t["list_title"], t["list_lead"], f'<div class="filters" role="group">{btns}</div>')
            + f'<div class="proj-grid fadein">{cards}</div>')
    return chrome(lang, "list", None, me, f'{t["crumb_projects"]} — Alexandre K.', t["list_lead"], body)


def build_detail(lang, p):
    t, d, me = UI[lang], p[lang], out_path(lang, "detail", p["slug"])
    r = lambda pg, s=None: rel(me, out_path(lang, pg, s))
    tags = "".join(f"<span>{x}</span>" for x in p["tech"][:4])
    banner = (f'<section class="card banner fadein">{poster(p)}<div class="inner">'
              f'<div class="crumbs"><a href="{r("home")}">{t["crumb_home"]}</a><span>/</span><a href="{r("list")}">{t["crumb_projects"]}</a><span>/</span><span>{d["title"]}</span></div>'
              f'<h1>{d["title"]} <em>{t["detail_word"]}</em></h1><div class="tags">{tags}</div>'
              f'<div class="btn-row"><a class="btn btn-primary" href="{p["code"]}" target="_blank" rel="noopener">{ICON_GH} {t["view_code"]}</a><a class="btn" href="{r("list")}">{t["all_projects"]}</a></div></div></section>')
    longp = "".join(f"<p>{x}</p>" for x in d["long"])
    chips = "".join(f"<span>{x}</span>" for x in p["tech"])
    feats = "".join(f"<li>{x}</li>" for x in d["features"])
    main = card(f'<div class="block"><h3>{t["description"]}</h3>{longp}</div><div class="block"><h3>{t["tech"]}</h3><div class="chips">{chips}</div></div>'
                f'<div class="block"><h3>{t["features"]}</h3><ul class="feat">{feats}</ul></div>')
    tree = esc("\n".join(TREES[p["slug"]]))
    facts = (f'<dl class="facts"><div><dt>{t["f_type"]}</dt><dd>{t["kinds"][p["kind"]]}</dd></div><div><dt>{t["f_context"]}</dt><dd>{t["context"]}</dd></div>'
             f'<div><dt>{t["f_lang"]}</dt><dd>{p["lang"]}</dd></div><div><dt>{t["f_repo"]}</dt><dd><a href="{p["code"]}" target="_blank" rel="noopener">GitHub ↗</a></dd></div></dl>')
    shots = sorted((ROOT / "img").glob(f'{p["slug"]}-*.jpg'))
    gallery = card(f'<div class="card-h"><h3>{t["preview_h"]}</h3></div><div class="shots">' + "".join(
        f'<a href="{rel(me, "img/" + f.name)}" target="_blank" rel="noopener"><img src="{rel(me, "img/" + f.name)}" alt="{d["title"]}" loading="lazy"></a>' for f in shots) + '</div>') if shots else ""
    side = (f'<aside class="side"><div class="term fadein"><div class="term-bar"><span></span><span></span><span></span><em>{p["slug"]} ~ {t["repo_tree"].lower()}</em></div><pre class="tree">{tree}</pre></div>'
            + card(facts) + '</aside>')
    others = sorted((q for q in PROJECTS if q["slug"] != p["slug"]), key=lambda q: q["kind"] != p["kind"])
    sim = card(f'<div class="card-h"><h3>{t["similar_small"]}</h3></div><div class="proj-grid">{"".join(proj_card(lang, q, me) for q in others[:3])}</div>')
    return chrome(lang, "detail", p["slug"], me, f'{d["title"]} — Alexandre K.', d["short"], f'{banner}<div class="detail-grid">{main}{side}</div>{gallery}{sim}')


def build_game(lang):
    t, me = UI[lang], out_path(lang, "game")
    tabs = "".join(f'<button type="button" role="tab" data-g="{g}" aria-selected="false">{n}</button>'
                   for g, n in zip(["g-2048", "g-snake", "g-memory", "g-code"], t["games_tabs"]))
    body = head_c(lang, me, t["nav"][2], t["games_title"], t["games_lead"]) + card(f'<div class="seg" role="tablist">{tabs}</div>{games_panels(lang)}')
    return chrome(lang, "game", None, me, f'{t["nav"][2]} — Alexandre K.', t["games_lead"], body,
                  '<script src="ROOT/js/game.js"></script><script src="ROOT/js/games.js"></script>')


def build_about(lang, data):
    t, me = UI[lang], out_path(lang, "about")
    hw = "".join(f'<div class="tile"><div class="tile-ico">{ICONS_HW[k]}</div><b>{name}</b><small>{sub}</small></div>' for name, sub, k in t["hardware"])
    sw = "".join(
        f'<a class="tile" href="{url}" target="_blank" rel="noopener"><div class="tile-ico"{f" style=color:{c}" if c else ""}>{brand_icon(ic)}</div><b>{n}</b></a>'
        for n, ic, url, c in SOFTWARE)
    gh = card(f'<div class="head-c" style="padding-top:0"><span class="label">{t["gh_small"]}</span><h2>{t["gh_h"]}</h2></div>{heatmap(lang, data)}')
    setup = card(f'<div class="block"><h3>{t["hw_h"]}</h3><div class="tiles">{hw}</div></div><div class="block"><h3>{t["sw_h"]}</h3><div class="tiles">{sw}</div></div>')
    left = f'<div class="stack">{skills_card(lang)}{"".join(cv_cards(lang, True))}</div>'
    body = head_c(lang, me, t["nav"][3], t["about_title"], t["about_lead"]) + f'<div class="about-grid">{left}<div class="stack">{gh}{setup}</div></div>'
    return chrome(lang, "about", None, me, f'{t["nav"][3]} — Alexandre K.', t["about_lead"], body)


def build_contact(lang):
    t, me = UI[lang], out_path(lang, "contact")
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
    mail = (f'<a class="channel" href="mailto:{EMAIL}"><div class="contact-icon ci-mail">{ICON_MAIL}</div><div><b>E-mail</b><small>{EMAIL}</small></div><span class="go">→</span></a>' if EMAIL else "")
    looking = "".join(f"<li>{x}</li>" for x in t["looking"])
    profile = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in t["profile"])
    left = card(f'''<div class="block"><h3>{t["channels_h"]}</h3>
      <a class="channel" href="{LINKEDIN}" target="_blank" rel="noopener"><div class="contact-icon ci-li">{ICON_LI}</div><div><b>LinkedIn</b><small>alexandre-k-801438256</small></div><span class="go">↗</span></a>
      <a class="channel" href="{GITHUB}" target="_blank" rel="noopener"><div class="contact-icon ci-gh">{ICON_GH}</div><div><b>GitHub</b><small>github.com/amex-32</small></div><span class="go">↗</span></a>{mail}</div>
      {form}<div class="block"><h3>{t["looking_h"]}</h3><ul class="feat">{looking}</ul></div>''')
    cta = card(f'<div class="block"><h3>{t["contact_cta_h"]}</h3><p>{t["contact_cta_p"]}</p><a class="btn btn-primary" href="{LINKEDIN}" target="_blank" rel="noopener">{ICON_LI} {t["write"]}</a>'
               f'<p style="margin-top:14px"><span class="dot"></span> {t["status"]}</p></div>')
    right = f'<aside class="side">{cta}{card(f"<dl class=facts>{profile}</dl>")}</aside>'
    body = head_c(lang, me, t["contact_label"], t["contact_h"], t["contact_lead"]) + f'<div class="contact-wrap">{left}{right}</div>'
    return chrome(lang, "contact", None, me, f'{t["contact_label"]} — Alexandre K.', t["contact_lead"], body)


def write(path, html):
    f = ROOT / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html)


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
        for p in PROJECTS:
            write(out_path(lang, "detail", p["slug"]), build_detail(lang, p))
    print("ok")

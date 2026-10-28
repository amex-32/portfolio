(function () {
  'use strict';
  var root = document.documentElement;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  function save(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  // ---------- toast ----------
  var toastEl = $('.toast'), toastT;
  function toast(msg, ms) {
    toastEl.textContent = msg; toastEl.classList.add('on');
    clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove('on'); }, ms || 2600);
  }
  window.toast = toast;

  // ---------- thème et accent ----------
  function setTheme(t) { root.dataset.theme = t; save('theme', t); }
  function toggleTheme() { setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark'); }
  function setAccent(a) { root.dataset.accent = a; save('accent', a); }
  $$('[data-act="theme"]').forEach(function (b) { b.addEventListener('click', toggleTheme); });

  // ---------- historique (barre d'adresse) ----------
  $$('[data-act="back"]').forEach(function (b) { b.addEventListener('click', function () { history.back(); }); });
  $$('[data-act="forward"]').forEach(function (b) { b.addEventListener('click', function () { history.forward(); }); });

  // ---------- apparition, halo des cartes ----------
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('show'); io.unobserve(e.target); } });
  }, { threshold: 0.05 });
  $$('.fadein').forEach(function (el) { io.observe(el); });
  document.addEventListener('pointermove', function (e) {
    var el = e.target.closest && e.target.closest('.card, .proj');
    if (!el) return;
    var r = el.getBoundingClientRect();
    el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
    el.style.setProperty('--my', (e.clientY - r.top) + 'px');
  });

  // ---------- notifications ----------
  var bell = $('[data-act="bell"]'), drop = $('#notifs');
  if (bell) {
    bell.addEventListener('click', function (e) { e.stopPropagation(); drop.classList.toggle('open'); var d = $('i', bell); if (d) d.remove(); });
    document.addEventListener('click', function (e) { if (!drop.contains(e.target)) drop.classList.remove('open'); });
  }

  // ---------- carrousel de la page d'accueil ----------
  var hero = $('.hero');
  if (hero) {
    var slides = $$('.slide', hero), dots = $$('.dots button', hero), cur = 0, timer;
    var show = function (n) {
      cur = (n + slides.length) % slides.length;
      slides.forEach(function (s, i) { s.classList.toggle('on', i === cur); s.setAttribute('aria-hidden', i === cur ? 'false' : 'true'); });
      dots.forEach(function (d, i) { d.classList.toggle('on', i === cur); });
    };
    var play = function () { clearInterval(timer); if (!reduce) timer = setInterval(function () { show(cur + 1); }, 8000); };
    $('[data-act="prev"]', hero).addEventListener('click', function () { show(cur - 1); play(); });
    $('[data-act="next"]', hero).addEventListener('click', function () { show(cur + 1); play(); });
    dots.forEach(function (d, i) { d.addEventListener('click', function () { show(i); play(); }); });
    hero.addEventListener('pointerenter', function () { clearInterval(timer); });
    hero.addEventListener('pointerleave', play);
    show(0); play();
  }

  // ---------- filtres de la liste de projets ----------
  var filters = $$('.filters button');
  filters.forEach(function (b) {
    b.addEventListener('click', function () {
      filters.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      $$('.proj[data-kind]').forEach(function (p) { p.hidden = b.dataset.f !== 'all' && p.dataset.kind !== b.dataset.f; });
    });
  });

  // ---------- palette de commandes ----------
  var bg = $('.pal-bg'), data = JSON.parse(($('#cmd-data') || {}).textContent || 'null');
  if (bg && data) {
    var input = $('input', bg), list = $('ul', bg), items = [], sel = 0;
    var accents = ['blue', 'violet', 'green', 'orange'];
    var all = [];
    data.pages.forEach(function (p) { all.push({ g: data.l.pages, t: p.t, h: p.i, run: function () { location.href = p.u; } }); });
    data.projects.forEach(function (p) { all.push({ g: data.l.projects, t: p.t, h: p.k, run: function () { location.href = p.u; } }); });
    all.push({ g: data.l.actions, t: data.l.theme, h: '◐', run: toggleTheme });
    all.push({ g: data.l.actions, t: data.l.lang, h: 'FR / EN', run: function () { location.href = data.langUrl; } });
    accents.forEach(function (a) { all.push({ g: data.l.actions, t: data.l.accent + ' — ' + data.l.accents[a], h: '●', run: function () { setAccent(a); } }); });
    all.push({ g: data.l.actions, t: data.l.term, h: '>_', run: function () { openTty(); } });
    data.links.forEach(function (p) { all.push({ g: data.l.links, t: p.t, h: '↗', run: function () { window.open(p.u, '_blank', 'noopener'); } }); });
    var render = function () {
      var q = input.value.trim().toLowerCase(), last = '', html = '';
      items = all.filter(function (x) { return !q || (x.t + ' ' + x.h).toLowerCase().indexOf(q) > -1; });
      if (sel >= items.length) sel = 0;
      items.forEach(function (x, i) {
        if (x.g !== last) { html += '<h5>' + x.g + '</h5>'; last = x.g; }
        html += '<li data-i="' + i + '"' + (i === sel ? ' class="sel"' : '') + '>' + x.t.replace(/[<&]/g, '') + '<span>' + x.h + '</span></li>';
      });
      list.innerHTML = html || '<li>' + data.l.empty + '</li>';
      var s = $('.sel', list); if (s) s.scrollIntoView({ block: 'nearest' });
    };
    var open = function () { bg.classList.add('open'); input.value = ''; sel = 0; render(); input.focus(); };
    var close = function () { bg.classList.remove('open'); };
    var run = function (i) { var x = items[i]; if (x) { close(); x.run(); } };
    $$('[data-act="palette"]').forEach(function (b) { b.addEventListener('click', open); });
    bg.addEventListener('click', function (e) { if (e.target === bg) close(); });
    list.addEventListener('click', function (e) { var li = e.target.closest('li[data-i]'); if (li) run(+li.dataset.i); });
    input.addEventListener('input', function () { sel = 0; render(); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { sel = (sel + 1) % items.length; render(); e.preventDefault(); }
      else if (e.key === 'ArrowUp') { sel = (sel - 1 + items.length) % items.length; render(); e.preventDefault(); }
      else if (e.key === 'Enter') run(sel);
    });
    document.addEventListener('keydown', function (e) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); bg.classList.contains('open') ? close() : open(); }
      else if (e.key === 'Escape') { close(); if (drop) drop.classList.remove('open'); }
    });
  }

  // ---------- code Konami : pluie de caractères ----------
  var seq = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'], pos = 0;
  document.addEventListener('keydown', function (e) {
    var k = e.key.length === 1 ? e.key.toLowerCase() : e.key;
    pos = k === seq[pos] ? pos + 1 : (k === seq[0] ? 1 : 0);
    if (pos === seq.length) { pos = 0; matrix(); toast((document.documentElement.dataset.konami || 'Konami!') + ' ' + '}4b_nw0dnw0dpupu{GALF'.split('').reverse().join(''), 8000); }
  });

  // ---------- mini-CTF : un flag pour qui ouvre la console ----------
  console.log('%c amex@portfolio ', 'background:#7cc4ff;color:#0d1726;font-weight:700;border-radius:4px',
    root.lang === 'en' ? 'Curious? Good. Flag 4/6, in ROT13:' : 'Curieux ? Tant mieux. Flag 4/6, en ROT13 :', 'SYNT{e0g13_1a_gu3_p0af0y3}');

  // ---------- terminal : navigation au clavier et soumission des flags ----------
  var tty = $('.tty-bg'), openTty = function () {};
  if (tty && data) {
    var out = $('.tty-out', tty), cli = $('input', tty), hist = [], hi = 0, PSEUDO = /^[A-Za-z0-9_-]{2,16}$/;
    var en = root.lang === 'en';
    var TT = en ? {
      hello: 'Type help to see the commands.', unknown: 'command not found: ', nofile: 'no such page: ',
      help: ['help            this list', 'ls [projects]   list the pages (or the projects)', 'cd <page>       go to a page or a project', 'cat <page>      describe a page or a project',
        'whoami          who am I', 'ctf             the mini-CTF rules', 'pseudo <name>   choose your nickname', 'flag <FLAG{…}>  submit a flag (or paste it alone)', 'top             CTF leaderboard',
        'music           my tracks', 'play [n] · pause · next', 'theme · clear · exit'],
      whoami: 'Alexandre K., cybersecurity student (Ynov, Sophia Antipolis). Looking for an internship or work-study.',
      ctf: ['6 flags in the FLAG{…} format are hidden in this site.', '1. The home page source code has a secret.', '2. HTTP headers say more than you think.',
        '3. Robots know things (and so does base64).', '4. The browser console, in ROT13.', '5. ↑ ↑ ↓ ↓ ← → ← → B A', '6. One artwork in the gallery says more than it shows (metadata).',
        'Then: pseudo <name>, and flag FLAG{…}'],
      nowPlaying: 'now playing: ', paused: 'paused.', noTrack: 'no such track: ', pseudoFlag: 'nickname and flag are two commands: pseudo <name>, then flag FLAG{…}',
      pseudoIs: 'nickname: ', noPseudo: 'choose a nickname first: pseudo <name>', badPseudo: '2 to 16 characters: letters, digits, _ or -.',
      usageFlag: 'usage: flag FLAG{…}', bad: 'wrong flag, keep looking.', slow: 'too fast, try again in a few seconds.', err: 'leaderboard unavailable.',
      got: 'correct flag! ', already: 'already found. ', found: ' flags found', all: 'All flags found. Well done!', none: 'no one yet.', sudo: 'amex is not in the sudoers file. This incident will be reported.'
    } : {
      hello: 'Tape help pour voir les commandes.', unknown: 'commande introuvable : ', nofile: 'page introuvable : ',
      help: ['help            cette liste', 'ls [projets]    lister les pages (ou les projets)', 'cd <page>       aller sur une page ou un projet', 'cat <page>      décrire une page ou un projet',
        'whoami          qui suis-je', 'ctf             les règles du mini-CTF', 'pseudo <nom>    choisir ton pseudo', 'flag <FLAG{…}>  soumettre un flag (ou colle-le seul)', 'top             classement du CTF',
        'music           mes morceaux', 'play [n] · pause · next', 'theme · clear · exit'],
      whoami: 'Alexandre K., étudiant en cybersécurité (Ynov, Sophia Antipolis). Je cherche un stage ou une alternance.',
      ctf: ['6 flags au format FLAG{…} sont cachés dans ce site.', '1. Le code source de l\'accueil a un secret.', '2. Les en-têtes HTTP parlent plus qu\'on ne croit.',
        '3. Les robots savent des choses (et le base64 aussi).', '4. La console du navigateur, en ROT13.', '5. ↑ ↑ ↓ ↓ ← → ← → B A', '6. Une œuvre de la galerie en dit plus qu\'elle n\'en montre (métadonnées).',
        'Ensuite : pseudo <nom>, puis flag FLAG{…}'],
      nowPlaying: 'en lecture : ', paused: 'en pause.', noTrack: 'morceau introuvable : ', pseudoFlag: 'pseudo et flag sont deux commandes : pseudo <nom>, puis flag FLAG{…}',
      pseudoIs: 'pseudo : ', noPseudo: 'choisis d\'abord un pseudo : pseudo <nom>', badPseudo: '2 à 16 caractères : lettres, chiffres, _ ou -.',
      usageFlag: 'usage : flag FLAG{…}', bad: 'flag incorrect, continue de chercher.', slow: 'trop rapide, réessaie dans quelques secondes.', err: 'classement indisponible.',
      got: 'flag correct ! ', already: 'déjà trouvé. ', found: ' flags trouvés', all: 'Tous les flags sont trouvés. Bravo !', none: 'personne pour l\'instant.', sudo: 'amex n\'est pas dans le fichier sudoers. Cet incident sera signalé.'
    };
    var print = function (s, cls) {
      [].concat(s).forEach(function (line) { var d = document.createElement('div'); if (cls) d.className = cls; d.textContent = line; out.appendChild(d); });
      out.scrollTop = out.scrollHeight;
    };
    var name = function (p) { return en ? p.k[p.k.length - 1] : p.k[0]; };
    var find = function (x) {
      x = (x || '').toLowerCase().replace(/\/+$/, '');
      if (x === '' || x === '~' || x === '..' || x === '/') return data.pages[0];
      return data.pages.filter(function (p) { return p.k.indexOf(x) > -1; })[0] || data.projects.filter(function (p) { return p.s === x; })[0];
    };
    var pseudo = function (v) { try { if (v != null) localStorage.setItem('ak-pseudo', v); return localStorage.getItem('ak-pseudo') || ''; } catch (e) { return v || ''; } };
    var flag = function (f) {
      var who = pseudo();
      if (!f) return print(TT.usageFlag, 'err');
      if (!PSEUDO.test(who)) return print(TT.noPseudo, 'err');
      fetch('/api/ctf', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pseudo: who, flag: f }) })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (d) { return { s: r.status, d: d }; }); })
        .then(function (x) {
          if (x.s === 200) {
            print((x.d.already ? TT.already : TT.got) + x.d.found + ' / ' + x.d.total + TT.found, 'ok');
            if (x.d.found === x.d.total) print(TT.all, 'ok');
            window.dispatchEvent(new CustomEvent('ak-flag'));
          } else print(x.s === 400 ? TT.bad : x.s === 429 ? TT.slow : TT.err, 'err');
        })
        .catch(function () { print(TT.err, 'err'); });
    };
    var top = function () {
      fetch('/api/ctf', { cache: 'no-store' }).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (d) {
        if (!d.rows.length) return print(TT.none);
        print(d.rows.map(function (r, i) { return (i + 1 + '.   ').slice(0, 4) + (r.pseudo + '                ').slice(0, 17) + r.found + ' / ' + d.total; }));
      }).catch(function () { print(TT.err, 'err'); });
    };
    var CMDS = {
      help: function () { print(TT.help); },
      ls: function (a) {
        var p = find(a);
        if (a && p === data.pages[1]) return print(data.projects.map(function (q) { return q.s; }).join('  '));
        if (a && !p) return print(TT.nofile + a, 'err');
        print(data.pages.map(function (q) { return name(q) + '/'; }).join('  '));
      },
      cd: function (a) { var p = find(a); if (!p) return print(TT.nofile + a, 'err'); location.href = p.u; },
      cat: function (a) { var p = find(a); if (!p) return print(TT.nofile + a, 'err'); print(p.d); },
      whoami: function () { print(TT.whoami); },
      ctf: function () { print(TT.ctf); },
      pseudo: function (a) {
        if (!a) return print(TT.pseudoIs + (pseudo() || '–'));
        if (/FLAG\{/i.test(a)) return print(TT.pseudoFlag, 'err');
        if (!PSEUDO.test(a)) return print(TT.badPseudo, 'err');
        pseudo(a); print(TT.pseudoIs + a, 'ok');
      },
      flag: flag, top: top,
      music: function () {
        var p = window.akPlayer; if (!p) return print(TT.err, 'err');
        print(p.tracks.map(function (t, k) { return (k === p.current() && p.playing() ? '▶ ' : '  ') + (k + 1) + '. ' + t.t; }));
      },
      play: function (a) {
        var p = window.akPlayer, k = a ? parseInt(a, 10) - 1 : null; if (!p) return print(TT.err, 'err');
        if (k != null && !(k >= 0 && k < p.tracks.length)) return print(TT.noTrack + a, 'err');
        p.play(k); print(TT.nowPlaying + p.tracks[k == null ? p.current() : k].t, 'ok');
      },
      pause: function () { if (window.akPlayer) { window.akPlayer.pause(); print(TT.paused); } },
      next: function () { var p = window.akPlayer; if (p) { p.next(); print(TT.nowPlaying + p.tracks[p.current()].t, 'ok'); } },
      theme: function () { toggleTheme(); },
      clear: function () { out.textContent = ''; },
      exit: function () { closeTty(); },
      sudo: function () { print(TT.sudo, 'err'); }
    };
    var exec = function (line) {
      print('$ ' + line, 'cmd');
      var parts = line.trim().split(/\s+/), c = parts[0].toLowerCase();
      if (!c) return;
      if (/^flag\{/.test(c)) return flag(parts[0]); // un flag collé seul
      if (Object.prototype.hasOwnProperty.call(CMDS, c)) CMDS[c](parts.slice(1).join(' '));
      else print(TT.unknown + parts[0], 'err');
    };
    openTty = function () {
      if (bg) bg.classList.remove('open');
      tty.classList.add('open');
      if (!out.childNodes.length) print(TT.hello);
      cli.focus();
    };
    var closeTty = function () { tty.classList.remove('open'); cli.blur(); };
    cli.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { var v = cli.value; cli.value = ''; if (v.trim()) { hist.push(v); hi = hist.length; } exec(v); }
      else if (e.key === 'ArrowUp' && hi > 0) { cli.value = hist[--hi]; e.preventDefault(); }
      else if (e.key === 'ArrowDown') { hi = Math.min(hist.length, hi + 1); cli.value = hist[hi] || ''; e.preventDefault(); }
      else if (e.key === 'Escape') closeTty();
    });
    $('.tty-x', tty).addEventListener('click', closeTty);
    tty.addEventListener('click', function (e) { if (e.target === tty) closeTty(); });
    $$('[data-act="term"]').forEach(function (b) { b.addEventListener('click', openTty); });
    document.addEventListener('keydown', function (e) {
      if ((e.key === '²' || e.key === '`') && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { e.preventDefault(); tty.classList.contains('open') ? closeTty() : openTty(); }
    });
  }
  function matrix() {
    if (reduce || $('#matrix')) return;
    var c = document.createElement('canvas'), g = c.getContext('2d');
    c.id = 'matrix'; c.width = innerWidth; c.height = innerHeight; document.body.appendChild(c);
    var cols = Math.floor(c.width / 16), y = [], chars = '01アイウエオカキクケコ$#<>/{}';
    for (var i = 0; i < cols; i++) y[i] = Math.random() * -40;
    var t = setInterval(function () {
      g.fillStyle = 'rgba(0,0,0,.08)'; g.fillRect(0, 0, c.width, c.height);
      g.fillStyle = '#3ddc84'; g.font = '15px monospace';
      for (var i = 0; i < cols; i++) {
        g.fillText(chars[Math.floor(Math.random() * chars.length)], i * 16, y[i] * 16);
        y[i] = y[i] * 16 > c.height && Math.random() > .975 ? 0 : y[i] + 1;
      }
    }, 50);
    setTimeout(function () { clearInterval(t); c.remove(); }, 9000);
  }

  // ---------- visionneuse d'images (aperçus des projets) ----------
  var shots = $$('.shots a');
  if (shots.length) {
    var lb = document.createElement('div'), img = document.createElement('img'), count = document.createElement('span'), at = 0;
    lb.className = 'lb'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true');
    count.className = 'count';
    lb.innerHTML = '<button class="round x" type="button" aria-label="Fermer">✕</button><button class="round prev" type="button" aria-label="Précédent">‹</button><button class="round next" type="button" aria-label="Suivant">›</button>';
    lb.appendChild(img); lb.appendChild(count); document.body.appendChild(lb);
    var go = function (n) { at = (n + shots.length) % shots.length; img.src = shots[at].href; img.alt = $('img', shots[at]).alt; count.textContent = (at + 1) + ' / ' + shots.length; };
    var shut = function () { lb.classList.remove('open'); };
    shots.forEach(function (a, i) { a.addEventListener('click', function (e) { e.preventDefault(); go(i); lb.classList.add('open'); }); });
    $('.x', lb).addEventListener('click', shut);
    $('.prev', lb).addEventListener('click', function () { go(at - 1); });
    $('.next', lb).addEventListener('click', function () { go(at + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) shut(); });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') shut(); else if (e.key === 'ArrowLeft') go(at - 1); else if (e.key === 'ArrowRight') go(at + 1);
    });
    var x0; lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', function (e) { var d = e.changedTouches[0].clientX - x0; if (Math.abs(d) > 40) go(at + (d < 0 ? 1 : -1)); });
  }

  // ---------- formulaire de contact ----------
  var f = document.getElementById('contact-form');
  if (f) {
    var msg = $('.form-msg', f), btn = $('button', f);
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      btn.disabled = true; msg.textContent = f.dataset.sending;
      fetch(f.action, { method: 'POST', headers: { Accept: 'application/json' }, body: new FormData(f) })
        .then(function (r) { if (!r.ok) throw 0; msg.textContent = f.dataset.ok; f.reset(); })
        .catch(function () { msg.textContent = f.dataset.err; })
        .then(function () { btn.disabled = false; });
    });
  }
})();

(function () {
  'use strict';
  var root = document.documentElement;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  function save(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  // ---------- toast ----------
  var toastEl = $('.toast'), toastT;
  function toast(msg) {
    toastEl.textContent = msg; toastEl.classList.add('on');
    clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove('on'); }, 2600);
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
    if (pos === seq.length) { pos = 0; matrix(); toast(document.documentElement.dataset.konami || 'Konami!'); }
  });
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

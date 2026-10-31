// Effets visuels du HUD : décor et séquences animées, sans aucune logique du site.
// Rejoué à chaque page (la navigation douce relance les scripts) : les minuteries de la page précédente sont d'abord coupées.
(function () {
  'use strict';
  if (window.akHudStop) window.akHudStop();
  var root = document.documentElement, g = window.gsap, en = root.lang === 'en', timers = [];
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var calm = function () { return !g || matchMedia('(prefers-reduced-motion: reduce)').matches || root.dataset.motion === 'off'; };
  var once = function (k) { try { if (sessionStorage.getItem(k)) return false; sessionStorage.setItem(k, '1'); } catch (e) {} return true; };
  var pick = function (s) { return s[Math.floor(Math.random() * s.length)]; };
  var every = function (fn, ms) { timers.push(setInterval(function () { if (!document.hidden) fn(); }, ms)); };
  window.akHudStop = function () { timers.forEach(clearInterval); theme.disconnect(); };
  var el = function (tag, cls, html) { var n = document.createElement(tag); n.className = cls || ''; if (html) n.innerHTML = html; n.setAttribute('aria-hidden', 'true'); return n; };
  // glyphes en gros pixels : une chaîne par ligne
  var AK = ['0111000010001', '1000100010010', '1000100010100', '1111100011000', '1000100010100', '1000100010010', '1000100010001'];
  var CHECK = ['00000001', '00000011', '10000110', '11001100', '01111000', '00110000'];
  var SIGNAL = ['101101101', '011111110', '110010011', '011111110', '101101101', '010010010', '110111011'];
  function pixels(rows, cls) {
    var r = '';
    rows.forEach(function (row, y) { row.split('').forEach(function (c, x) { if (c === '1') r += '<rect x="' + x + '" y="' + y + '" width="1" height="1"/>'; }); });
    return '<svg class="' + (cls || '') + '" viewBox="0 0 ' + rows[0].length + ' ' + rows.length + '" fill="currentColor">' + r + '</svg>';
  }

  // curseur à la couleur de l'accent : un SVG ne lit pas les variables CSS, on le redessine quand le thème change
  function cursor() {
    var c = getComputedStyle(root).getPropertyValue('--accent').trim();
    var dot = function (s, r, hot, end) {
      var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + s + '" height="' + s + '"><circle cx="' + s / 2 + '" cy="' + s / 2 + '" r="' + r + '" fill="' + c + '" stroke="#0e0e0e" stroke-width="1.4"/></svg>';
      return 'url("data:image/svg+xml,' + encodeURIComponent(svg) + '") ' + hot + ' ' + hot + ', ' + end;
    };
    root.style.setProperty('--cur', dot(12, 4.2, 6, 'auto'));
    root.style.setProperty('--cur-on', dot(18, 6.6, 9, 'pointer'));
  }
  var theme = new MutationObserver(cursor);
  theme.observe(root, { attributes: true, attributeFilter: ['data-theme', 'data-accent'] });
  cursor();

  // ---------- texte qui se décode caractère par caractère ----------
  var NOISE = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789/+#';
  function scramble(node, ms) {
    if (calm() || node.dataset.sc) return;
    node.dataset.sc = '1';
    var walk = document.createTreeWalker(node, NodeFilter.SHOW_TEXT), texts = [], t;
    while ((t = walk.nextNode())) if (t.nodeValue.trim()) texts.push({ n: t, v: t.nodeValue });
    var start = performance.now(), dur = ms || 420;
    var id = setInterval(function () {
      var p = Math.min(1, (performance.now() - start) / dur);
      texts.forEach(function (x) {
        var keep = Math.floor(x.v.length * p), s = x.v.slice(0, keep);
        for (var i = keep; i < x.v.length; i++) s += /\s/.test(x.v[i]) ? x.v[i] : pick(NOISE);
        x.n.nodeValue = s;
      });
      if (p === 1) { clearInterval(id); texts.forEach(function (x) { x.n.nodeValue = x.v; }); delete node.dataset.sc; }
    }, 40);
    timers.push(id);
  }
  var seen = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { seen.unobserve(e.target); scramble(e.target); } }); });
  $$('.page-title, .slide.intro h1, .card-h h3, .label, .block h3, .gal-stat b').forEach(function (n) { seen.observe(n); });

  // ---------- séquence 1 : boot ----------
  var ready = [];
  function booted(fn) { root.classList.contains('booting') ? ready.push(fn) : fn(); }
  function boot() {
    var box = $('.boot');
    if (!root.classList.contains('booting')) return;
    var finish = function () { root.classList.remove('booting'); ready.splice(0).forEach(function (f) { f(); }); };
    setTimeout(finish, 2000); // onglet en arrière-plan : l'horloge de GSAP dort, la page ne reste pas voilée
    if (!box || calm()) return finish();
    box.innerHTML = '<div class="boot-in">' + pixels(AK) + '<div class="boot-bar"><i></i></div><span class="boot-txt">BOOT // AMEX.SYS</span></div>';
    var rects = $$('rect', box).sort(function () { return Math.random() - .5; }), tl = g.timeline({ onComplete: finish });
    rects.forEach(function (r, i) { tl.set(r, { opacity: 1 }, i * .014); });
    [.25, .55, .8, 1].forEach(function (v, i) { tl.set($('.boot-bar i', box), { scaleX: v }, .42 + i * .14); });
    tl.to({}, { duration: .14 });
    var skip = function () { removeEventListener('keydown', skip); removeEventListener('pointerdown', skip); tl.progress(1); };
    addEventListener('keydown', skip); addEventListener('pointerdown', skip);
  }

  // ---------- séquence 2 : ENTER PASSWORD, à l'entrée des jeux (décor : rien n'est demandé) ----------
  function gate() {
    if (!$('.seg') || calm() || !once('ak-gate')) return;
    var o = el('div', 'hud-layer hud-gate', '<div class="in"><span>ENTER PASSWORD</span><div class="pw"><b></b></div></div>' + pixels(CHECK));
    document.body.appendChild(o);
    var pw = $('.pw', o), cur = $('b', pw), tl = g.timeline({ onComplete: function () { o.remove(); } });
    for (var i = 0; i < 8; i++) tl.call(function () { pw.insertBefore(document.createElement('i'), cur); }, null, .12 + i * .07);
    tl.call(function () { o.classList.add('ok'); }, null, .76).to({}, { duration: .2 }, .76);
    var skip = function () { removeEventListener('keydown', skip); o.removeEventListener('pointerdown', skip); tl.progress(1); };
    addEventListener('keydown', skip); o.addEventListener('pointerdown', skip);
  }

  // ---------- séquence 3 : instruments de l'accueil ----------
  function draw(tl, paths, at, gap) {
    paths.forEach(function (p, i) {
      g.set(p, { attr: { pathLength: 1 }, strokeDasharray: 1, strokeDashoffset: 1 });
      tl.to(p, { strokeDashoffset: 0, duration: .18, ease: 'steps(6)' }, at + i * gap);
    });
  }
  function rack() {
    var host = $('.slide.intro');
    if (!host) return;
    var cells = '';
    for (var i = 0; i < 36; i++) cells += '<i></i>';
    var r = el('div', 'hud-rack', '<span class="hud-micro">SIGNAL ARRAY / <b>ONLINE</b></span>' +
      '<svg viewBox="0 0 300 64"><path d="M0 52H60V24H118V52H176V12H300"/><path d="M60 24V8H96"/><path d="M176 52H236V34H270"/><rect x="58" y="22" width="4" height="4"/><rect x="174" y="50" width="4" height="4"/><rect x="268" y="32" width="4" height="4"/></svg>' +
      '<div class="hud-lamps">' + cells + '</div>');
    host.appendChild(r);
    var lamps = $$('i', r), flip = function () { pick(lamps).classList.toggle('on'); };
    if (calm()) { lamps.forEach(function (l, k) { l.classList.toggle('on', k % 3 === 0); }); return; }
    booted(function () {
      var tl = g.timeline({ delay: .3 });
      draw(tl, $$('path', r), 0, .08);
      lamps.slice().sort(function () { return Math.random() - .5; }).slice(0, 14).forEach(function (l, k) { tl.call(function () { l.classList.add('on'); }, null, .3 + k * .03); });
      tl.call(function () { every(flip, 260); });
    });
  }

  // colonnes de caractères qui changent en permanence
  function tele() {
    if (innerWidth < 1280) return;
    var rows = function () { var s = ''; for (var i = 0; i < 7; i++) s += pick(NOISE) + pick(NOISE) + pick(NOISE) + '\n'; return s; };
    var box = el('div', 'hud-tele', '<b>SYS</b><div></div><span class="hot">P01</span><div></div><span class="hot">L03</span><div></div><span class="hot">C20</span><div></div><b>LIVE</b>');
    document.body.appendChild(box);
    var cols = $$('div', box);
    cols.forEach(function (c) { c.textContent = rows(); });
    if (!calm()) every(function () { pick(cols).textContent = rows(); }, 320);
  }

  // ---------- séquence 4 : état de chargement des boutons ----------
  var WAIT = en ? '… IN PROGRESS' : '… EN COURS';
  $$('.form button').forEach(function (b) { b.dataset.busy = WAIT; });
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('a.btn, .sb-form button');
    if (!b || calm()) return;
    b.dataset.busy = WAIT; b.classList.add('busy');
    timers.push(setTimeout(function () { b.classList.add('idle'); }, 200));
    timers.push(setTimeout(function () { b.classList.remove('busy', 'idle'); }, 900));
  });

  // ---------- séquence 5 : le rectangle lime qui ouvre un projet ----------
  var pass = false;
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a.proj');
    if (!a || pass || calm() || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault(); e.stopPropagation();
    var lines = (a.dataset.tech || '').split('|').filter(Boolean).slice(0, 8).map(function (t, i) {
      return '<li><span>ALGN 0' + (i + 1) + '</span><span>' + t + '</span><i></i></li>';
    }).join('');
    var o = el('div', 'hud-layer hud-modal', '<div class="box"><div class="txt"><small>' + (en ? 'Project alignment initiating' : 'Alignement du projet') + '</small><h4></h4><ol>' + lines + '</ol></div></div>');
    document.body.appendChild(o);
    var box = $('.box', o), txt = $('.txt', o), bars = $$('li', o), title = $('h4', o);
    title.textContent = $('h3', a).textContent;
    var tl = g.timeline({ onComplete: function () { o.remove(); pass = true; a.click(); pass = false; } });
    g.set(txt, { visibility: 'hidden' }); g.set(bars, { visibility: 'hidden' });
    tl.fromTo(box, { clipPath: 'inset(49% 50%)' }, { clipPath: 'inset(49% 0%)', duration: .12, ease: 'steps(5)' })
      .to(box, { clipPath: 'inset(0% 0%)', duration: .14, ease: 'steps(5)' })
      .set(txt, { visibility: 'visible' }).call(function () { scramble(title, 200); });
    bars.forEach(function (li, i) {
      tl.set(li, { visibility: 'visible' }, .3 + i * .045);
      tl.fromTo($('i', li), { '--p': 0 }, { '--p': 1, duration: .16, ease: 'steps(6)' }, .32 + i * .045);
    });
    tl.set(txt, { visibility: 'hidden' }, '+=.1').to(box, { clipPath: 'inset(49% 0%)', duration: .1, ease: 'steps(4)' });
  }, true);

  // ---------- séquence 6 : radar d'À propos ----------
  function radar() {
    var host = $('.now-card');
    if (!host) return;
    var arcs = '';
    for (var r = 50; r <= 170; r += 40) arcs += '<path class="r a" d="M' + (200 - r) + ' 190A' + r + ' ' + r + ' 0 0 1 ' + (200 + r) + ' 190"/>';
    var ticks = '';
    for (var x = 20; x <= 380; x += 20) ticks += 'M' + x + ' 190v' + (x % 100 ? -4 : -8);
    var c = el('section', 'card hud-radar', '<div class="card-h"><h3>DEEP-SPACE RADAR ARRAY</h3></div><svg viewBox="0 0 400 200">' +
      '<path class="r" d="M200 190V10"/><path class="r" d="M20 190H380' + ticks + '"/><path class="r" d="M200 190L80 30"/><path class="r" d="M200 190L320 30"/>' + arcs +
      '<circle class="red" cx="262" cy="96" r="3"/><g class="sig-g" transform="translate(286 34) scale(5)"><g class="sig">' + pixels(SIGNAL).replace(/^<svg[^>]*>|<\/svg>$/g, '') + '</g></g>' +
      '<text class="sig-t" x="284" y="82">SIGNAL DETECTED</text></svg><div class="hud-ticker"><span></span></div>');
    host.parentNode.insertBefore(c, host);
    var msg = (en ? 'SIGNAL DETECTED // STACK ONLINE // SCANNING SECTORS // ' : 'SIGNAL DÉTECTÉ // STACK EN LIGNE // BALAYAGE DES SECTEURS // ');
    $('.hud-ticker span', c).textContent = msg + msg + msg + msg;
    if (calm()) return;
    var paths = $$('.r', c), late = $$('.red, .sig-g, .sig-t, .hud-ticker', c);
    g.set(late, { autoAlpha: 0 });
    paths.forEach(function (p) { g.set(p, { attr: { pathLength: 1 }, strokeDasharray: 1, strokeDashoffset: 1 }); });
    var io = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return;
      io.disconnect();
      var tl = g.timeline();
      draw(tl, paths.slice(0, 4), 0, .1);
      draw(tl, paths.slice(4), .42, .1);
      late.forEach(function (n, i) { tl.set(n, { autoAlpha: 1 }, .86 + i * .12); });
    }, { threshold: .3 });
    io.observe(c);
  }

  // ---------- séquence 7 : SYS BREACH, dissolution en bruit de pixels rouges ----------
  function breach() {
    if (calm() || $('.hud-breach')) return;
    var word = '<span>⚠ SYS BREACH ⚠ SYS BREACH ⚠ SYS BREACH ⚠</span>';
    var o = el('div', 'hud-layer hud-breach', pixels(SIGNAL) + '<div class="band">' + word + word + '</div><canvas></canvas>');
    document.body.appendChild(o);
    var mark = $('svg', o), band = $('.band', o), cv = $('canvas', o), c = cv.getContext('2d');
    var w = cv.width = Math.ceil(innerWidth / 8), h = cv.height = Math.ceil(innerHeight / 8);
    band.style.top = '62%'; band.style.visibility = 'hidden';
    g.set(o, { background: '#141414' }); g.set(mark, { color: '#c6ff3d' });
    var noise = { v: 0 }, tl = g.timeline({ onComplete: function () { o.remove(); } });
    tl.set(mark, { color: '#ff4438' }, .16).set(o, { background: '#2a0606' }, .16).set(band, { visibility: 'visible' }, .22)
      .to(noise, { v: 1, duration: .46, ease: 'steps(14)', onUpdate: function () {
        c.fillStyle = '#e0201b';
        for (var i = 0, n = w * h * .09; i < n; i++) c.fillRect(Math.random() * w | 0, Math.random() * h | 0, 1, 1);
        if (noise.v > .7) { c.fillStyle = '#2a0606'; c.fillRect(0, 0, w * Math.random(), 1); }
      } }, .78)
      .to(o, { autoAlpha: 0, duration: .1, ease: 'steps(2)' });
  }
  var out = $('.tty-out');
  if (out) new MutationObserver(function (ms) { // la commande sudo annonce déjà un incident : on le met en scène
    ms.forEach(function (m) { m.addedNodes.forEach(function (n) { if (n.className === 'err' && /sudoers/.test(n.textContent)) { $('.tty-x').click(); breach(); } }); });
  }).observe(out, { childList: true });

  // ---------- navigation vivante : les lettres se décodent, cassent, se reconstruisent ----------
  function letters() {
    if (calm()) return;
    $$('.tabs a').forEach(function (a) {
      var text = a.textContent, hits = 0;
      a.setAttribute('aria-label', text);
      a.innerHTML = text.split('').map(function (ch) { return '<span class="ch" aria-hidden="true">' + ch + '</span>'; }).join('');
      var chars = $$('.ch', a);
      a.addEventListener('pointerenter', function () {
        scramble(a, 220);
        if (++hits < 6) return; // shortcut: seuil fixe de 6 survols, à rendre réglable si un autre élément reprend l'effet
        hits = 0;
        g.timeline().to(chars, { x: function () { return (Math.random() * 60 - 30) | 0; }, y: function () { return (Math.random() * 30 - 15) | 0; }, rotation: function () { return (Math.random() * 90 - 45) | 0; }, autoAlpha: 0, duration: .16, ease: 'steps(3)' })
          .to(chars, { x: 0, y: 0, rotation: 0, autoAlpha: 1, duration: .1, ease: 'steps(3)', stagger: .025 });
      });
    });
  }

  // ---------- images au survol : boîtes de détection et CRT ----------
  var hash = function (s) { for (var i = 0, h = 7; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0; return h; };
  function blob(host) {
    var img = $('img', host), p = $('.poster', host), name = (p ? p.dataset.p : (img && img.src.split('/').pop().split('.')[0])) || 'frame';
    var h = hash(name), boxes = [], line = '', html = '';
    for (var i = 0; i < 3; i++) {
      var n = (h >> (i * 7)) & 127, b = { x: 8 + (n % 5) * 14 + i * 4, y: 12 + ((n >> 2) % 4) * 13 + i * 9, w: 18 + (n % 3) * 7, h: 14 + (n % 4) * 5 };
      boxes.push(b);
      var label = i === 0 ? (b.x + 20.7814) .toFixed(4) + '.' + (b.y * 19) : i === 1 ? name + '.jpg' : 'ID ' + (n + 100);
      html += '<i style="left:' + b.x + '%;top:' + b.y + '%;width:' + b.w + '%;height:' + b.h + '%;animation-delay:' + (i * 70) + 'ms"><b>' + label + '</b></i>';
    }
    boxes.forEach(function (b, i) { if (i) { var a = boxes[i - 1]; line += 'M' + (a.x + a.w) + ' ' + (a.y + a.h / 2) + 'H' + (b.x + b.w / 2) + 'V' + b.y; } });
    var o = el('div', 'hud-blob', '<svg viewBox="0 0 100 100" preserveAspectRatio="none"><path d="' + line + '"/></svg>' + html);
    host.appendChild(o);
    return o;
  }
  var VS = 'attribute vec2 a;varying vec2 u;void main(){u=a*.5+.5;u.y=1.-u.y;gl_Position=vec4(a,0.,1.);}';
  var FS = 'precision mediump float;varying vec2 u;uniform sampler2D t;uniform float s;uniform vec2 k;' +
    'float r(float x){return fract(sin(x*91.7)*437.5);}' +
    'void main(){vec2 v=u;float b=floor(v.y*18.);float g=step(.93,r(b+floor(s*9.)));v.x+=g*.035*(r(b)-.5)*2.;' + // bandes décalées par moments
    'v=(v-.5)*k+.5;float c=.0028;' +
    'vec3 o=vec3(texture2D(t,v+vec2(c,0.)).r,texture2D(t,v).g,texture2D(t,v-vec2(c,0.)).b);' + // décalage RGB
    'o*=.84+.16*step(.5,fract(u.y*190.));o+=o*o*.18;gl_FragColor=vec4(o,1.);}';
  var crt = (function () { // un seul canvas WebGL, déplacé sous la souris ; sans WebGL il reste les scanlines du CSS
    var cv = el('canvas', 'hud-crt'), gl = cv.getContext('webgl', { antialias: false }), raf = 0, go = false, ready2 = false;
    if (!gl) return null;
    var prog = gl.createProgram();
    [[gl.VERTEX_SHADER, VS], [gl.FRAGMENT_SHADER, FS]].forEach(function (x) { var sh = gl.createShader(x[0]); gl.shaderSource(sh, x[1]); gl.compileShader(sh); gl.attachShader(prog, sh); });
    gl.linkProgram(prog); gl.useProgram(prog);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0); gl.bindAttribLocation(prog, 0, 'a'); gl.linkProgram(prog); gl.useProgram(prog);
    gl.vertexAttribPointer(gl.getAttribLocation(prog, 'a'), 2, gl.FLOAT, false, 0, 0);
    gl.bindTexture(gl.TEXTURE_2D, gl.createTexture());
    [gl.TEXTURE_WRAP_S, gl.TEXTURE_WRAP_T].forEach(function (p) { gl.texParameteri(gl.TEXTURE_2D, p, gl.CLAMP_TO_EDGE); });
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    var uS = gl.getUniformLocation(prog, 's'), uK = gl.getUniformLocation(prog, 'k');
    var frame = function (t) { if (!go) return; gl.uniform1f(uS, t / 1000); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); raf = requestAnimationFrame(frame); };
    return {
      on: function (host, url) {
        var im = new Image();
        im.onload = function () {
          if (!go || cv.dataset.url !== url) return;
          var r = host.getBoundingClientRect(), box = r.width / Math.max(1, r.height), pic = im.width / im.height;
          cv.width = Math.min(800, r.width | 0); cv.height = Math.min(800, r.height | 0);
          gl.viewport(0, 0, cv.width, cv.height);
          gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, im);
          gl.uniform2f(uK, box < pic ? box / pic : 1, box < pic ? 1 : pic / box); // recadrage « cover »
          host.appendChild(cv); cancelAnimationFrame(raf); raf = requestAnimationFrame(frame);
        };
        go = true; cv.dataset.url = url; im.src = url;
      },
      off: function () { go = false; cancelAnimationFrame(raf); cv.remove(); }
    };
  })();
  function hover() {
    if (calm() || !matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    var cur = null, mark = null, tag = null;
    document.addEventListener('pointerover', function (e) {
      var t = e.target.closest && e.target.closest('.proj, .shots a, .gal-item');
      if (t === cur) return;
      if (cur) { mark.remove(); tag.remove(); if (crt) crt.off(); }
      cur = t;
      if (!t) return;
      mark = blob(t);
      tag = el('span', 'hud-tag', 'P01 L0' + ((hash(t.textContent) % 8) + 1) + ' C' + (10 + hash(t.textContent) % 80));
      t.appendChild(tag);
      if (t.matches('.proj')) scramble($('h3', t), 240);
      var p = $('.poster', t), img = $('img', t), bg = p && getComputedStyle(p, '::after').backgroundImage;
      if (!bg || bg === 'none') bg = p && getComputedStyle(p).backgroundImage;
      var url = img ? img.currentSrc || img.src : ((bg || '').match(/url\("?(.+?)"?\)/) || [])[1];
      if (crt && url) crt.on(p || t, url);
    });
  }

  // halftone : nuage de points dont la taille suit une tache, à droite des en-têtes
  function halftone() {
    if (innerWidth < 760) return;
    $$('.head-c').forEach(function (h) {
      if (h.closest('.card')) return;
      var cv = el('canvas', 'hud-halftone'), w = cv.width = 420, H = cv.height = 150, c = cv.getContext('2d'), seed = hash(h.textContent);
      c.fillStyle = getComputedStyle(root).getPropertyValue('--accent').trim();
      for (var y = 0; y < H; y += 6) for (var x = 0; x < w; x += 6) {
        var dx = (x - w * (.55 + (seed % 30) / 100)) / 170, dy = (y - H / 2) / 80, v = 1 - dx * dx - dy * dy;
        var off = (y / 6) % 2 ? 3 : 0;
        if (v > 0) c.fillRect(x + off, y, Math.ceil(v * 3.4), Math.ceil(v * 3.4));
      }
      h.insertBefore(cv, h.firstChild);
    });
  }

  // ---------- 404 : journal de la requête, console 3D qui pilote le lecteur ----------
  function lost() {
    var log = $('.nf-log'), stage = $('.psp-stage');
    if (!log) return;
    var at = calm() ? 0 : 1.5; // après SYS BREACH
    ['GET ' + location.pathname, 'ROUTE ' + '.'.repeat(12) + ' <b>NOT FOUND</b>', '> ' + (en ? 'SIGNAL LOST, RETURN ADVISED' : 'SIGNAL PERDU, RETOUR CONSEILLÉ')].forEach(function (line, i) {
      var d = document.createElement('div');
      if (i) d.innerHTML = line; else d.textContent = line;
      log.appendChild(d);
      if (at) g.from(d, { autoAlpha: 0, duration: .01, delay: at + .3 + i * .24 });
    });
    var act = function (sel) { var real = $(sel); if (real) real.click(); };
    $('.psp-keys').addEventListener('click', function (e) { var b = e.target.closest('[data-do]'); if (b) act(b.dataset.do); });
    var go = function () { window.akPsp(stage, { url: 'model/psp.glb', at: at, calm: calm(), act: act }); };
    if (window.akPsp) return go();
    var s = document.createElement('script'); s.src = 'js/psp3d.js'; s.onload = go; document.body.appendChild(s); // 500 Ko : seulement ici
  }

  document.body.appendChild(el('div', 'hud-logo', pixels(AK)));
  $$('.heat').forEach(function (h) { h.scrollLeft = h.scrollWidth; }); // sur téléphone : ouvert sur les semaines récentes
  tele(); rack(); radar(); letters(); hover(); halftone(); lost();
  booted(gate);
  if ($('.nf')) booted(breach);
  boot();
})();

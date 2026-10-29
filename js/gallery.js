// Galerie : tirages éparpillés (par pages de 8, avec fondu glissé au changement de page) sur un fond flouté, grille ou albums ; frise des séries en bas ; visionneuse.
(function () {
  'use strict';
  var gal = document.querySelector('.gal');
  if (!gal) return;
  var $ = function (s, c) { return (c || gal).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || gal).querySelectorAll(s)); };
  var items = $$('.gal-item'), bgs = $$('.gal-bg'), front = 0, name = $('.gal-name'), count = $('.gal-count');
  var tabs = $$('.gal-time button'), views = $$('.gal-views button');
  var pager = $('.gal-pager'), pageEl = $('.gal-page');
  var stage = $('.gal-stage'), PER = 8, cur = '', page = 0, pref = 'scatter', busy = false;

  // Placement aléatoire des tirages (nouveau à chaque affichage), sous contraintes : tout reste dans la scène, rotation et échelle bornées,
  // et deux tirages ne se recouvrent que d'environ 30 % au plus (meilleur de 60 essais par tirage ; au pire le moins mauvais).
  // shortcut: pas de garantie absolue si la scène est très étroite, les tirages se chevauchent alors un peu plus.
  function scatter(want) {
    var r = stage.getBoundingClientRect(), W = r.width || 800, H = r.height || 520;
    var cw = Math.min(235, Math.max(150, W * .21)) * 1.1, ch = cw * 1.2; // taille d'un tirage, échelle maximale comprise
    var mx = Math.min(cw / 2 + 8, W / 2), my = Math.min(ch / 2 + 6, H / 2), placed = [];
    var order = want.map(function (_, k) { return k; }).sort(function () { return Math.random() - .5; }); // ordre d'empilement
    want.forEach(function (it, k) {
      var best = null, bestSep = -1;
      for (var t = 0; t < 60 && bestSep < 1; t++) {
        var x = mx + Math.random() * (W - 2 * mx), y = my + Math.random() * (H - 2 * my), sep = Infinity;
        placed.forEach(function (q) { sep = Math.min(sep, Math.max(Math.abs(x - q[0]) / (cw * .72), Math.abs(y - q[1]) / (ch * .72))); });
        if (sep > bestSep) { bestSep = sep; best = [x, y]; }
      }
      placed.push(best);
      it.style.setProperty('--x', (best[0] / W * 100).toFixed(1) + '%'); it.style.setProperty('--y', (best[1] / H * 100).toFixed(1) + '%');
      it.style.setProperty('--r', ((Math.random() * 16 - 8)).toFixed(1) + 'deg'); it.style.setProperty('--k', (.88 + Math.random() * .2).toFixed(2));
      it.style.setProperty('--z', order[k] + 1);
    });
  }

  var inSeries = function () { return items.filter(function (it) { return it.dataset.s === cur; }); };
  var visible = function () { return items.filter(function (it) { return !it.hidden; }); };
  // deux calques de fond : le nouveau apparaît pendant que l'ancien s'efface (fondu enchaîné)
  var setBg = function (it) {
    if (!it) return;
    var url = 'url("' + it.dataset.bg + '")';
    if (bgs[front].style.backgroundImage === url) return;
    front = 1 - front;
    bgs[front].style.backgroundImage = url;
    bgs[front].classList.add('on'); bgs[1 - front].classList.remove('on');
  };

  // affiche la page courante : tous les tirages de la série en grille, PER tirages par page en vue éparpillée
  function render() {
    var all = inSeries(), grid = gal.dataset.view === 'grid', n = Math.max(1, Math.ceil(all.length / PER));
    if (page >= n) page = 0;
    var want = grid ? all : all.slice(page * PER, page * PER + PER);
    // un tirage de plus à placer, ou jamais placé (premier affichage) : on redistribue toute la page
    var fresh = want.some(function (it) { return it.hidden || !it.style.getPropertyValue('--x'); });
    items.forEach(function (it) { it.classList.remove('out'); it.hidden = want.indexOf(it) < 0; });
    if (!grid && fresh) scatter(want);
    pager.hidden = grid || n < 2;
    pageEl.textContent = (page + 1) + ' / ' + n;
    setBg(want[0]);
  }
  // change de page : fondu + léger glissement dans le sens de la navigation, la nouvelle page arrive du côté opposé
  function turn(dir) {
    var n = Math.ceil(inSeries().length / PER);
    if (busy || n < 2) return;
    busy = true;
    var slide = function (from, to, ms, ease) {
      return stage.animate([{ opacity: from[0], transform: 'translateX(' + from[1] + 'px)' }, { opacity: to[0], transform: 'translateX(' + to[1] + 'px)' }], { duration: ms, easing: ease, fill: 'forwards' });
    };
    slide([1, 0], [0, -28 * dir], 300, 'ease-in').finished.then(function () {
      page = (page + dir + n) % n; render();
      var inn = slide([0, 28 * dir], [1, 0], 420, 'cubic-bezier(.22,.61,.36,1)');
      stage.getAnimations().forEach(function (a) { if (a !== inn) a.cancel(); });
      return inn.finished;
    }).then(function () { stage.getAnimations().forEach(function (a) { a.cancel(); }); busy = false; }, function () { busy = false; });
  }

  function series(s) {
    cur = s; page = 0;
    tabs.forEach(function (b) { b.setAttribute('aria-selected', b.dataset.s === s ? 'true' : 'false'); });
    var tab = tabs.filter(function (b) { return b.dataset.s === s; })[0];
    name.textContent = tab.firstChild.textContent.trim();
    count.textContent = inSeries().length + ' ' + count.dataset.unit;
    if (gal.dataset.view !== 'albums') setView(pref); else render();
    if (history.replaceState) history.replaceState(null, '', '#' + s);
  }
  function setView(v) {
    gal.dataset.view = v;
    views.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.view === v ? 'true' : 'false'); });
    render();
  }

  tabs.forEach(function (b) { b.addEventListener('click', function () { if (gal.dataset.view === 'albums') setView(pref); series(b.dataset.s); }); });
  views.forEach(function (b) { b.addEventListener('click', function () { if (b.dataset.view !== 'albums') pref = b.dataset.view; setView(b.dataset.view); }); });
  $$('.gal-album').forEach(function (b) { b.addEventListener('click', function () { setView(pref); series(b.dataset.s); }); });
  // glisser vers la gauche / la droite change de page (écran tactile)
  var sx = null;
  stage.addEventListener('touchstart', function (e) { sx = e.touches[0].clientX; }, { passive: true });
  stage.addEventListener('touchend', function (e) {
    if (sx == null) return;
    var dx = e.changedTouches[0].clientX - sx; sx = null;
    if (Math.abs(dx) > 60 && gal.dataset.view !== 'grid') turn(dx < 0 ? 1 : -1);
  });
  $('.gal-prev').addEventListener('click', function () { turn(-1); });
  $('.gal-next').addEventListener('click', function () { turn(1); });
  items.forEach(function (it) {
    it.addEventListener('pointerenter', function () { setBg(it); });
    it.addEventListener('focus', function () { setBg(it); });
    it.addEventListener('click', function () { show(inSeries().indexOf(it)); });
  });

  // ---------- visionneuse (parcourt toute la série, pas seulement la page affichée) ----------
  var lb = document.createElement('div'), img = document.createElement('img'), cap = document.createElement('span'), at = 0, list = [];
  lb.className = 'lb'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); cap.className = 'count';
  [['x', '✕'], ['prev', '‹'], ['next', '›']].forEach(function (b) {
    var e = document.createElement('button'); e.type = 'button'; e.className = 'round ' + b[0]; e.textContent = b[1]; lb.appendChild(e);
  });
  lb.appendChild(img); lb.appendChild(cap); document.body.appendChild(lb);
  function go(n) {
    at = (n + list.length) % list.length;
    var it = list[at], t = $('b', it).textContent, d = $('small', it).textContent;
    img.src = it.dataset.full; img.alt = t;
    cap.textContent = t + (d ? ' · ' + d : '') + '  ' + (at + 1) + ' / ' + list.length;
    // la page affichée derrière suit l'œuvre ouverte
    if (it.hidden && gal.dataset.view !== 'grid') { page = Math.floor(at / PER); render(); }
  }
  function show(n) { list = inSeries(); go(n); lb.classList.add('open'); $('.x', lb).focus(); }
  function shut() { lb.classList.remove('open'); if (list[at]) list[at].focus(); }
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

  var h = location.hash.replace('#', '');
  series(tabs.some(function (b) { return b.dataset.s === h; }) ? h : tabs[0].dataset.s);
})();

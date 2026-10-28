// Galerie : tirages éparpillés sur un fond flouté, grille ou albums ; frise des séries en bas ; visionneuse.
(function () {
  'use strict';
  var gal = document.querySelector('.gal');
  if (!gal) return;
  var $ = function (s, c) { return (c || gal).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || gal).querySelectorAll(s)); };
  var items = $$('.gal-item'), stage = $('.gal-stage'), bgs = $$('.gal-bg'), front = 0, name = $('.gal-name'), count = $('.gal-count');
  var tabs = $$('.gal-time button'), views = $$('.gal-views button');
  // emplacements des tirages en vue éparpillée : x %, y %, rotation, échelle (le premier est au centre, au premier plan)
  var SLOTS = [[50, 47, -3, 1.12], [21, 28, -7, .95], [79, 27, 6, .95], [17, 73, 5, .9], [42, 79, -4, .88], [64, 76, 4, .9], [85, 66, -6, .88], [33, 50, 8, .82]];

  var shown = function () { return items.filter(function (it) { return !it.hidden; }); };
  // deux calques de fond : le nouveau apparaît pendant que l'ancien s'efface (fondu enchaîné)
  var setBg = function (it) {
    if (!it) return;
    var url = 'url("' + $('img', it).src + '")';
    if (bgs[front].style.backgroundImage === url) return;
    front = 1 - front;
    bgs[front].style.backgroundImage = url;
    bgs[front].classList.add('on'); bgs[1 - front].classList.remove('on');
  };

  function series(s) {
    var k = 0;
    tabs.forEach(function (b) { b.setAttribute('aria-selected', b.dataset.s === s ? 'true' : 'false'); });
    items.forEach(function (it) {
      it.hidden = it.dataset.s !== s;
      if (it.hidden) return;
      var p = SLOTS[k % SLOTS.length];
      it.style.setProperty('--x', p[0] + '%'); it.style.setProperty('--y', p[1] + '%');
      it.style.setProperty('--r', p[2] + 'deg'); it.style.setProperty('--k', p[3]); it.style.setProperty('--z', SLOTS.length - k);
      k++;
    });
    var tab = tabs.filter(function (b) { return b.dataset.s === s; })[0];
    name.textContent = tab.firstChild.textContent.trim();
    count.textContent = k + ' ' + count.dataset.unit;
    setBg(shown()[0]);
    if (history.replaceState) history.replaceState(null, '', '#' + s);
  }
  function setView(v) {
    gal.dataset.view = v;
    views.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.view === v ? 'true' : 'false'); });
  }

  tabs.forEach(function (b) { b.addEventListener('click', function () { series(b.dataset.s); if (gal.dataset.view === 'albums') setView('scatter'); }); });
  views.forEach(function (b) { b.addEventListener('click', function () { setView(b.dataset.view); }); });
  $$('.gal-album').forEach(function (b) { b.addEventListener('click', function () { series(b.dataset.s); setView('scatter'); }); });
  items.forEach(function (it) {
    it.addEventListener('pointerenter', function () { setBg(it); });
    it.addEventListener('focus', function () { setBg(it); });
    it.addEventListener('click', function () { show(shown().indexOf(it)); });
  });

  // ---------- visionneuse ----------
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
  }
  function show(n) { list = shown(); go(n); lb.classList.add('open'); $('.x', lb).focus(); }
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
  setView('scatter');
})();

(function () {
  var pad = function (n) { return String(n).padStart(2, '0'); };

  // horloge et taille de la fenêtre dans l'en-tête
  var clock = document.querySelector('[data-clock]');
  var view = document.querySelector('[data-view]');
  function tick() {
    var d = new Date();
    var t = pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
    if (clock) clock.textContent = t;
    var tray = document.getElementById('tray-clock');
    if (tray) tray.textContent = t.slice(0, 5);
    if (view) view.textContent = 'L' + innerWidth + 'H' + innerHeight;
  }
  tick(); setInterval(tick, 1000);
  addEventListener('resize', tick);

  // apparition des fenêtres
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('show'); io.unobserve(e.target); } });
  }, { threshold: 0.05 });
  document.querySelectorAll('.fadein').forEach(function (el) { io.observe(el); });

  // thème clair / sombre
  var root = document.documentElement, btn = document.getElementById('theme-toggle');
  function paint() { btn.textContent = root.dataset.theme === 'dark' ? '●' : '◐'; }
  paint();
  btn.addEventListener('click', function () {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('theme', root.dataset.theme); } catch (e) {}
    paint();
  });

  // filtres de la liste des projets
  var filters = document.querySelectorAll('.filters button');
  filters.forEach(function (b) {
    b.addEventListener('click', function () {
      filters.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      document.querySelectorAll('.proj[data-kind]').forEach(function (p) {
        p.hidden = b.dataset.f !== 'all' && p.dataset.kind !== b.dataset.f;
      });
    });
  });
})();

// formulaire de contact : envoi en JSON vers le service configuré
(function () {
  var f = document.getElementById('contact-form');
  if (!f) return;
  var msg = f.querySelector('.form-msg'), btn = f.querySelector('button');
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    btn.disabled = true; msg.textContent = f.dataset.sending;
    fetch(f.action, { method: 'POST', headers: { Accept: 'application/json' }, body: new FormData(f) })
      .then(function (r) { if (!r.ok) throw 0; msg.textContent = f.dataset.ok; f.reset(); })
      .catch(function () { msg.textContent = f.dataset.err; })
      .then(function () { btn.disabled = false; });
  });
})();

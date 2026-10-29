// Navigation douce : un clic sur un lien interne remplace le document sans recharger la fenêtre, pour que la musique ne coupe pas.
// document.open() garde l'objet window (donc l'Audio de js/player.js) ; les scripts de la nouvelle page se relancent normalement.
// En cas de problème (réseau, page absente), on retombe sur une navigation classique.
(function () {
  'use strict';
  if (!window.fetch || !history.pushState) return;
  var cur = location.pathname + location.search, busy = false;

  function soft(a) {
    return a && a.href && a.origin === location.origin && !a.target && !a.hasAttribute('download') &&
      (/\.html$/.test(a.pathname) || /\/$/.test(a.pathname)) && (a.pathname + a.search !== cur || !a.hash);
  }
  function go(url, push) {
    if (busy) return;
    busy = true;
    var bar = document.createElement('div'); bar.className = 'navbar'; document.documentElement.appendChild(bar);
    requestAnimationFrame(function () { bar.classList.add('go'); }); // barre de chargement : se remplit tant que la page arrive
    fetch(url, { credentials: 'same-origin' }).then(function (r) {
      if (!r.ok || !/text\/html/.test(r.headers.get('content-type') || '')) throw 0;
      return r.text();
    }).then(function (html) {
      // le script de mesures de Vercel reste celui de la première page : il suit déjà history.pushState
      html = html.replace(/<script[^>]*_vercel\/insights[^>]*><\/script>/, '');
      if (push) history.pushState(null, '', url);
      var done = false, swap = function () {
        if (done) return; done = true;
        document.open(); document.write(html); document.close();
        var h = new URL(url, location.href).hash, el = h && document.getElementById(h.slice(1));
        window.scrollTo(0, el ? el.getBoundingClientRect().top + scrollY - 90 : 0);
      };
      // transition entre pages : fondu, et la vignette d'un projet devient sa bannière (view-transition-name posé par le site)
      var calm = matchMedia('(prefers-reduced-motion: reduce)').matches || document.documentElement.dataset.motion === 'off';
      if (document.startViewTransition && !calm) {
        document.startViewTransition(swap).finished.catch(function () {});
        setTimeout(swap, 700); // fenêtre qui ne dessine pas (onglet en arrière-plan) : on ne reste pas bloqué
      } else swap();
    }).catch(function () { busy = false; bar.remove(); location.href = url; });
  }

  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest && e.target.closest('a');
    if (!soft(a)) return;
    e.preventDefault();
    go(a.href, true);
  });
  window.addEventListener('popstate', function () {
    if (location.pathname + location.search === cur) return; // simple changement de #ancre
    go(location.href, false);
  });
})();

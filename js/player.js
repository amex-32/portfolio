// Lecteur de musique, en haut à droite de toutes les pages.
// L'objet Audio vit sur window : la navigation douce (js/nav.js) réécrit le document sans recharger la fenêtre, donc la lecture ne coupe pas.
// Au premier chargement (ou après un rechargement complet), le morceau et la position reviennent de sessionStorage.
(function () {
  'use strict';
  var root = document.querySelector('.player'), data = document.getElementById('tracks');
  if (!root || !data) return;
  var $ = function (s) { return root.querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || root).querySelectorAll(s)); };

  // écouteurs posés sur l'Audio (qui survit aux pages) : retirés avant de se rebrancher sur la nouvelle page, sinon ils s'empilent
  (window.akOff || []).forEach(function (f) { f(); });
  var off = window.akOff = [];
  function on(target, type, fn) { target.addEventListener(type, fn); off.push(function () { target.removeEventListener(type, fn); }); }

  var tracks = JSON.parse(data.textContent), carry = !!window.akAudio, audio = window.akAudio || (window.akAudio = new Audio());
  var st = window.akState = window.akState || { i: 0, played: [] };
  var i = st.i, resumeAt = 0, lastSave = 0;
  var seek = $('.pl-seek'), times = $$('.pl-time span'), list = $$('.pl-list button'), toggle = $('.pl-toggle'), volEl = $('.pl-volume');
  var likeBtn = $('.pl-like'), shufBtn = $('.pl-shuffle');
  if (!carry) audio.preload = 'none';

  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function fetchStore(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  // ancienne version : le mot de passe était gardé ici en clair ; on l'échange une fois contre un cookie de session, puis on l'efface
  var oldTok = fetchStore('ak-owner');
  if (oldTok && oldTok !== '1') {
    try { localStorage.removeItem('ak-owner'); } catch (e) {}
    fetch('/api/listen?auth=1', { method: 'POST', headers: { 'x-owner': oldTok } }).then(function (r) { if (r.ok) store('ak-owner', '1'); }).catch(function () {});
  }

  // volume mémorisé (35 % par défaut : les morceaux sont masterisés fort), et fondu d'entrée pour ne jamais surprendre
  var vol = 0.35;
  var v0 = parseFloat(fetchStore('ak-volume')); if (v0 >= 0 && v0 <= 1) vol = v0;
  volEl.value = Math.round(vol * 100);
  function fadeIn() {
    clearInterval(window.akFade); audio.volume = 0;
    window.akFade = setInterval(function () { audio.volume = Math.min(vol, audio.volume + vol / 20); if (audio.volume >= vol) clearInterval(window.akFade); }, 40);
  }
  volEl.addEventListener('input', function () { vol = volEl.value / 100; clearInterval(window.akFade); audio.volume = vol; store('ak-volume', vol); });

  // j'aime : liste des morceaux aimés, gardée dans le navigateur (localStorage)
  var key = function (k) { return tracks[k].u.split('/').pop(); };
  function likes() { try { var a = JSON.parse(fetchStore('ak-likes')); return Array.isArray(a) ? a : []; } catch (e) { return []; } }
  var isLiked = function (k) { return likes().indexOf(key(k)) > -1; };
  function toggleLike(k) {
    var a = likes(), n = key(k), p = a.indexOf(n);
    if (p > -1) a.splice(p, 1); else a.push(n);
    store('ak-likes', JSON.stringify(a)); paint();
  }

  // lecture aléatoire : mémorisée aussi ; « précédent » revient sur les morceaux déjà joués
  var shuffle = fetchStore('ak-shuffle') === '1';
  function pick() {
    if (tracks.length < 2) return 0;
    var k; do { k = Math.floor(Math.random() * tracks.length); } while (k === i);
    return k;
  }
  function nextIndex() { return shuffle ? pick() : (i + 1) % tracks.length; }

  function fmt(s) { if (!isFinite(s)) return '–:––'; s = Math.floor(s || 0); return Math.floor(s / 60) + ':' + ('0' + s % 60).slice(-2); }
  var known = function () { return isFinite(audio.duration) && audio.duration > 0; };
  function save() { try { sessionStorage.setItem('ak-player', JSON.stringify({ i: i, t: audio.currentTime || resumeAt, on: !audio.paused })); } catch (e) {} }
  // le titre défile seulement s'il dépasse de la largeur fixe du lecteur
  var now = $('.pl-now');
  function fit() {
    var s = now.firstChild;
    if (!s) return;
    now.classList.remove('roll');
    if (s.offsetWidth <= now.clientWidth) return;
    s.dataset.t = now.dataset.t; now.style.setProperty('--roll', Math.max(6, s.offsetWidth / 24) + 's'); now.classList.add('roll');
  }
  function paint() {
    var on = !audio.paused, liked = isLiked(i);
    root.classList.toggle('playing', on);
    $$('.pl-play').forEach(function (b) { b.setAttribute('aria-label', on ? b.dataset.pause : b.dataset.play); });
    $('.pl-title').textContent = tracks[i].t;
    if (now.dataset.t !== tracks[i].t) { now.dataset.t = tracks[i].t; now.innerHTML = '<span></span>'; now.firstChild.textContent = tracks[i].t; fit(); }
    list.forEach(function (b, k) { b.setAttribute('aria-current', k === i ? 'true' : 'false'); b.dataset.liked = isLiked(k) ? 'true' : 'false'; });
    likeBtn.setAttribute('aria-pressed', liked ? 'true' : 'false');
    likeBtn.setAttribute('aria-label', liked ? likeBtn.dataset.unlike : likeBtn.dataset.like);
    shufBtn.setAttribute('aria-pressed', shuffle ? 'true' : 'false');
  }
  function load(k, t) {
    i = st.i = (k + tracks.length) % tracks.length; resumeAt = t || 0; st.counted = resumeAt >= 20;
    audio.src = tracks[i].u; seek.value = 0; times[0].textContent = fmt(resumeAt); times[1].textContent = '0:00';
    if ('mediaSession' in navigator && window.MediaMetadata) navigator.mediaSession.metadata = new MediaMetadata({ title: tracks[i].t, artist: 'amex' });
    paint();
  }
  // play() renvoie une promesse refusée si le navigateur bloque la lecture automatique : on reprend au premier clic ou à la première touche.
  function play() {
    return audio.play().then(paint, function () {
      paint();
      var resume = function (e) {
        document.removeEventListener('pointerdown', resume, true); document.removeEventListener('keydown', resume, true);
        if (audio.paused && !root.contains(e.target)) audio.play().catch(paint); // un clic dans le lecteur est géré par ses propres boutons
      };
      document.addEventListener('pointerdown', resume, true); document.addEventListener('keydown', resume, true);
    });
  }
  function pause() { audio.pause(); }
  function go(k) { st.played.push(i); if (st.played.length > 50) st.played.shift(); load(k); play(); }
  function next() { go(nextIndex()); }
  function prev() {
    if (audio.currentTime > 3) audio.currentTime = 0;
    else if (shuffle && st.played.length) { var k = st.played.pop(); load(k); play(); }
    else go(i - 1 < 0 ? tracks.length - 1 : i - 1);
  }
  function open(on) { root.classList.toggle('open', on); toggle.setAttribute('aria-expanded', on ? 'true' : 'false'); }

  on(audio, 'loadedmetadata', function () {
    if (resumeAt) { audio.currentTime = known() ? Math.min(resumeAt, audio.duration - 1) : resumeAt; resumeAt = 0; }
    times[1].textContent = fmt(audio.duration);
  });
  on(audio, 'durationchange', function () { times[1].textContent = fmt(audio.duration); });
  on(audio, 'timeupdate', function () {
    if (known()) seek.value = Math.round(audio.currentTime / audio.duration * 1000);
    times[0].textContent = fmt(audio.currentTime);
    // écoute comptée après 20 s de lecture, et seulement si je suis connecté (voir la commande login du terminal)
    if (!st.counted && !audio.paused && audio.currentTime >= 20) {
      st.counted = true;
      // la session est un cookie HttpOnly envoyé avec la requête ; si elle a expiré, on oublie qu'on était connecté
      if (fetchStore('ak-owner') === '1') fetch('/api/listen', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ track: tracks[i].t }) })
        .then(function (r) { if (r.status === 401) try { localStorage.removeItem('ak-owner'); } catch (e) {} }).catch(function () {});
    }
    if (Date.now() - lastSave > 1000) { lastSave = Date.now(); save(); }
  });
  on(audio, 'play', function () { fadeIn(); paint(); save(); });
  on(audio, 'pause', function () { paint(); save(); });
  on(audio, 'ended', next);
  seek.addEventListener('input', function () { if (known()) audio.currentTime = seek.value / 1000 * audio.duration; });
  $$('.pl-play').forEach(function (b) { b.addEventListener('click', function () { audio.paused ? play() : pause(); }); });
  $('.pl-prev').addEventListener('click', prev);
  $('.pl-next').addEventListener('click', next);
  likeBtn.addEventListener('click', function () { toggleLike(i); });
  shufBtn.addEventListener('click', function () { shuffle = !shuffle; store('ak-shuffle', shuffle ? '1' : '0'); paint(); });
  list.forEach(function (b) { b.addEventListener('click', function () { go(+b.dataset.i); }); });
  toggle.addEventListener('click', function (e) { e.stopPropagation(); open(!root.classList.contains('open')); });
  document.addEventListener('click', function (e) { if (!root.contains(e.target)) open(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') open(false); });
  $$('[data-act="music"]', document).forEach(function (b) { b.addEventListener('click', function (e) { e.stopPropagation(); open(true); if (audio.paused) play(); }); });
  window.addEventListener('pagehide', save);
  on(window, 'resize', fit);
  if (document.fonts) document.fonts.ready.then(fit); // la largeur du titre change quand la police arrive
  if ('mediaSession' in navigator) {
    navigator.mediaSession.setActionHandler('play', play);
    navigator.mediaSession.setActionHandler('pause', pause);
    navigator.mediaSession.setActionHandler('previoustrack', prev);
    navigator.mediaSession.setActionHandler('nexttrack', next);
  }

  if (carry) {
    // navigation douce : l'audio continue, on remet seulement l'affichage à jour
    if (known()) seek.value = Math.round(audio.currentTime / audio.duration * 1000);
    times[0].textContent = fmt(audio.currentTime); times[1].textContent = fmt(audio.duration);
    paint();
  } else {
    var s = null;
    try { s = JSON.parse(sessionStorage.getItem('ak-player')); } catch (e) {}
    load(s && s.i < tracks.length ? s.i : 0, s ? s.t : 0);
    if (s && s.on) play();
  }

  // utilisé par le terminal (commandes music, play, pause, next, like, shuffle)
  window.akPlayer = { tracks: tracks, current: function () { return i; }, playing: function () { return !audio.paused; },
    play: function (k) { k == null ? play() : go(k); }, pause: pause, next: next,
    like: function () { toggleLike(i); return isLiked(i); }, liked: isLiked,
    shuffle: function () { shuffle = !shuffle; store('ak-shuffle', shuffle ? '1' : '0'); paint(); return shuffle; } };
})();

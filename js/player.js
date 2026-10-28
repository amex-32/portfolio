// Lecteur de musique, en haut à droite de toutes les pages. Le morceau et la position suivent d'une page à l'autre (sessionStorage).
(function () {
  'use strict';
  var root = document.querySelector('.player'), data = document.getElementById('tracks');
  if (!root || !data) return;
  var $ = function (s) { return root.querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || root).querySelectorAll(s)); };
  var tracks = JSON.parse(data.textContent), audio = new Audio(), i = 0, resumeAt = 0, lastSave = 0;
  var seek = $('.pl-seek'), times = $$('.pl-time span'), list = $$('.pl-list button'), toggle = $('.pl-toggle'), volEl = $('.pl-volume');
  audio.preload = 'none';
  // volume mémorisé (35 % par défaut : les morceaux sont masterisés fort), et fondu d'entrée pour ne jamais surprendre
  var vol = 0.35, fade;
  try { var v = parseFloat(localStorage.getItem('ak-volume')); if (v >= 0 && v <= 1) vol = v; } catch (e) {}
  volEl.value = Math.round(vol * 100);
  function fadeIn() {
    clearInterval(fade); audio.volume = 0;
    fade = setInterval(function () { audio.volume = Math.min(vol, audio.volume + vol / 20); if (audio.volume >= vol) clearInterval(fade); }, 40);
  }
  volEl.addEventListener('input', function () {
    vol = volEl.value / 100; clearInterval(fade); audio.volume = vol;
    try { localStorage.setItem('ak-volume', vol); } catch (e) {}
  });

  function fmt(s) { if (!isFinite(s)) return '–:––'; s = Math.floor(s || 0); return Math.floor(s / 60) + ':' + ('0' + s % 60).slice(-2); }
  var known = function () { return isFinite(audio.duration) && audio.duration > 0; };
  function save() { try { sessionStorage.setItem('ak-player', JSON.stringify({ i: i, t: audio.currentTime || resumeAt, on: !audio.paused })); } catch (e) {} }
  function paint() {
    var on = !audio.paused;
    root.classList.toggle('playing', on);
    $$('.pl-play').forEach(function (b) { b.setAttribute('aria-label', on ? b.dataset.pause : b.dataset.play); });
    $('.pl-title').textContent = $('.pl-now').textContent = tracks[i].t;
    list.forEach(function (b, k) { b.setAttribute('aria-current', k === i ? 'true' : 'false'); });
  }
  function load(k, t) {
    i = (k + tracks.length) % tracks.length; resumeAt = t || 0;
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
  function go(k) { load(k); play(); }
  function prev() { if (audio.currentTime > 3) audio.currentTime = 0; else go(i - 1); }
  function open(on) { root.classList.toggle('open', on); toggle.setAttribute('aria-expanded', on ? 'true' : 'false'); }

  audio.addEventListener('loadedmetadata', function () {
    if (resumeAt) { audio.currentTime = known() ? Math.min(resumeAt, audio.duration - 1) : resumeAt; resumeAt = 0; }
    times[1].textContent = fmt(audio.duration);
  });
  audio.addEventListener('durationchange', function () { times[1].textContent = fmt(audio.duration); });
  audio.addEventListener('timeupdate', function () {
    if (known()) seek.value = Math.round(audio.currentTime / audio.duration * 1000);
    times[0].textContent = fmt(audio.currentTime);
    if (Date.now() - lastSave > 1000) { lastSave = Date.now(); save(); }
  });
  audio.addEventListener('play', function () { fadeIn(); paint(); save(); });
  audio.addEventListener('pause', function () { paint(); save(); });
  audio.addEventListener('ended', function () { go(i + 1); });
  seek.addEventListener('input', function () { if (known()) audio.currentTime = seek.value / 1000 * audio.duration; });
  $$('.pl-play').forEach(function (b) { b.addEventListener('click', function () { audio.paused ? play() : pause(); }); });
  $('.pl-prev').addEventListener('click', prev);
  $('.pl-next').addEventListener('click', function () { go(i + 1); });
  list.forEach(function (b) { b.addEventListener('click', function () { go(+b.dataset.i); }); });
  toggle.addEventListener('click', function (e) { e.stopPropagation(); open(!root.classList.contains('open')); });
  document.addEventListener('click', function (e) { if (!root.contains(e.target)) open(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') open(false); });
  $$('[data-act="music"]', document).forEach(function (b) { b.addEventListener('click', function (e) { e.stopPropagation(); open(true); if (audio.paused) play(); }); });
  window.addEventListener('pagehide', save);
  if ('mediaSession' in navigator) {
    navigator.mediaSession.setActionHandler('play', play);
    navigator.mediaSession.setActionHandler('pause', pause);
    navigator.mediaSession.setActionHandler('previoustrack', prev);
    navigator.mediaSession.setActionHandler('nexttrack', function () { go(i + 1); });
  }

  var s = null;
  try { s = JSON.parse(sessionStorage.getItem('ak-player')); } catch (e) {}
  load(s && s.i < tracks.length ? s.i : 0, s ? s.t : 0);
  if (s && s.on) play();

  // utilisé par le terminal (commandes music, play, pause, next)
  window.akPlayer = { tracks: tracks, current: function () { return i; }, playing: function () { return !audio.paused; },
    play: function (k) { k == null ? play() : go(k); }, pause: pause, next: function () { go(i + 1); } };
})();

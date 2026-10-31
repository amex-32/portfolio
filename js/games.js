// Mini-jeux : onglets, Memory, Code Breaker. (2048 est dans game.js)

// ---------- logique pure (testée par tools/test.js) ----------
// Verdict de chaque chiffre, à la Wordle (secret et essai n'ont jamais de doublon).
function marks(secret, guess) {
  return guess.split('').map(function (d, i) { return d === secret[i] ? 'hit' : secret.indexOf(d) > -1 ? 'near' : 'miss'; });
}
function shuffle(a, rnd) {
  a = a.slice();
  for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; }
  return a;
}
function secretCode(rnd) { return shuffle('0123456789'.split(''), rnd).slice(0, 4).join(''); }
// Chiffre de César sur A-Z (le reste est laissé tel quel) ; k négatif pour déchiffrer.
function caesar(s, k) {
  return s.replace(/[A-Z]/g, function (c) { return String.fromCharCode((c.charCodeAt(0) - 65 + k % 26 + 26) % 26 + 65); });
}

if (typeof module !== 'undefined') module.exports = { marks: marks, shuffle: shuffle, secretCode: secretCode, caesar: caesar };

if (typeof document !== 'undefined') (function () {
  'use strict';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var fr = document.documentElement.lang !== 'en';
  var TX = fr ? {
    start: 'Jouer', again: 'Rejouer', score: 'Score', best: 'Meilleur', moves: 'Coups', time: 'Temps', tries: 'Essais',
    win: 'Gagné !',
    cbHint: 'Trouve le code à 4 chiffres, tous différents. Plein : bien placé. Pointillés : mal placé. Gris : absent.', cbMark: { hit: 'bien placé', near: 'mal placé', miss: 'absent' }, cbLose: 'Perdu, le code était ', cbWin: 'Code craqué en ',
    memHint: 'Retrouve toutes les paires.', ok: 'Entrer', del: 'Effacer', ciWrong: 'Raté, −5 s', ciEnd: 'Temps écoulé : ',
    words: ['PARE FEU', 'MOT DE PASSE', 'CHIFFREMENT', 'HAMECONNAGE', 'PORT OUVERT', 'INJECTION SQL', 'PAQUET RESEAU', 'CLE PUBLIQUE',
      'SAUVEGARDE', 'AUTHENTIFICATION', 'JOURNAL SYSTEME', 'VULNERABILITE', 'RECONNAISSANCE', 'PORTE DEROBEE', 'RANCONGICIEL', 'DROITS MINIMAUX']
  } : {
    start: 'Play', again: 'Play again', score: 'Score', best: 'Best', moves: 'Moves', time: 'Time', tries: 'Tries',
    win: 'You win!',
    cbHint: 'Find the 4-digit code, all digits different. Solid: right place. Dotted: wrong place. Grey: not in the code.', cbMark: { hit: 'right place', near: 'wrong place', miss: 'not in the code' }, cbLose: 'You lost, the code was ', cbWin: 'Code cracked in ',
    memHint: 'Find all the pairs.', ok: 'Enter', del: 'Delete', ciWrong: 'Wrong, −5 s', ciEnd: 'Time is up: ',
    words: ['FIREWALL', 'PASSWORD', 'ENCRYPTION', 'PHISHING', 'OPEN PORT', 'SQL INJECTION', 'NETWORK PACKET', 'PUBLIC KEY',
      'BACKUP', 'AUTHENTICATION', 'SYSTEM LOG', 'VULNERABILITY', 'RECONNAISSANCE', 'BACKDOOR', 'RANSOMWARE', 'LEAST PRIVILEGE']
  };
  var announce = function (game, score) { window.dispatchEvent(new CustomEvent('ak-score', { detail: { game: game, score: score } })); };
  var best = function (k) { try { return +localStorage.getItem(k) || 0; } catch (e) { return 0; } };
  var keep = function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} };
  var active = function () { var p = $('.gp.on'); return p && p.id; };

  // ---------- onglets ----------
  var tabs = $$('.seg button');
  function select(id) {
    tabs.forEach(function (b) { b.setAttribute('aria-selected', b.dataset.g === id ? 'true' : 'false'); });
    $$('.gp').forEach(function (p) { p.classList.toggle('on', p.id === id); });
    if (history.replaceState) history.replaceState(null, '', '#' + id.replace('g-', ''));
    if (id !== 'g-cipher' && cipherGame) cipherGame.stop();
  }
  tabs.forEach(function (b) { b.addEventListener('click', function () { select(b.dataset.g); }); });

  // ---------- Memory ----------
  (function () {
    var grid = $('#mem'), movesEl = $('#mem-moves'), timeEl = $('#mem-time'), bestEl = $('#mem-best'), msg = $('#mem-msg'), btn = $('#mem-btn');
    var SYM = ['⌘', '⚡', '☢', '⚙', '✦', '♞', '⚑', '☂'], open, moves, left, t0, ti, lock;
    bestEl.textContent = best('ak-mem') || '–';
    function start() {
      var deck = shuffle(SYM.concat(SYM), Math.random);
      grid.innerHTML = ''; open = []; moves = 0; left = 8; lock = false; clearInterval(ti); t0 = 0;
      movesEl.textContent = 0; timeEl.textContent = '0s'; msg.textContent = '';
      deck.forEach(function (s) {
        var b = document.createElement('button'); b.type = 'button'; b.dataset.s = s; b.setAttribute('aria-label', '?'); b.textContent = '';
        b.addEventListener('click', function () { flip(b); }); grid.appendChild(b);
      });
    }
    function flip(b) {
      if (lock || b.classList.contains('up') || b.classList.contains('done')) return;
      if (!t0) { t0 = Date.now(); ti = setInterval(function () { timeEl.textContent = Math.round((Date.now() - t0) / 1000) + 's'; }, 500); }
      b.classList.add('up'); b.textContent = b.dataset.s; open.push(b);
      if (open.length < 2) return;
      moves++; movesEl.textContent = moves; lock = true;
      var a = open[0], c = open[1];
      setTimeout(function () {
        if (a.dataset.s === c.dataset.s) { a.className = c.className = 'done'; left--; }
        else { a.classList.remove('up'); c.classList.remove('up'); a.textContent = c.textContent = ''; }
        open = []; lock = false;
        if (!left) {
          clearInterval(ti); msg.textContent = TX.win;
          if (!best('ak-mem') || moves < best('ak-mem')) { keep('ak-mem', moves); bestEl.textContent = moves; }
          announce('memory', moves);
          if (window.toast) window.toast(TX.win + ' ' + moves + ' ' + TX.moves.toLowerCase());
        }
      }, 650);
    }
    btn.addEventListener('click', start); btn.textContent = TX.again; $('#mem-help').textContent = TX.memHint;
    start();
  })();

  // ---------- Code Breaker ----------
  (function () {
    var rows = $('#cb-rows'), pad = $('#cb-pad'), msg = $('#cb-msg'), btn = $('#cb-btn'), left = $('#cb-left');
    var MAX = 8, keys = {}, secret, cur, tries, done;
    function paint() {
      rows.innerHTML = '';
      for (var i = 0; i < MAX; i++) {
        var r = document.createElement('div'), t = tries[i];
        r.className = 'cb-row' + (!t && i === tries.length && !done ? ' cur' : '');
        var txt = t ? t.g : (i === tries.length && !done ? (cur + '····').slice(0, 4) : '····');
        r.innerHTML = txt.split('').map(function (d, k) { return '<i class="' + (t ? t.m[k] : '') + '">' + d + '</i>'; }).join('');
        if (t) { r.setAttribute('role', 'img'); r.setAttribute('aria-label', t.m.map(function (m, k) { return t.g[k] + ' ' + TX.cbMark[m]; }).join(', ')); }
        rows.appendChild(r);
      }
      left.textContent = MAX - tries.length;
      Object.keys(keys).forEach(function (d) { // le pavé garde en mémoire ce qu'on sait de chaque chiffre
        var seen = '';
        tries.forEach(function (t) { var k = t.g.indexOf(d); if (k > -1 && seen !== 'hit') seen = t.m[k]; });
        keys[d].className = seen;
      });
    }
    function submit() {
      if (done || cur.length < 4) return;
      var m = marks(secret, cur); tries.push({ g: cur, m: m });
      if (cur === secret) { done = true; announce('code', tries.length); msg.textContent = TX.cbWin + tries.length + '/' + MAX; if (window.toast) window.toast(msg.textContent); }
      else if (tries.length === MAX) { done = true; msg.textContent = TX.cbLose + secret; }
      cur = ''; paint();
    }
    function press(k) {
      if (done) return;
      if (/^\d$/.test(k) && cur.length < 4 && cur.indexOf(k) < 0) cur += k;
      else if (k === 'Backspace') cur = cur.slice(0, -1);
      else if (k === 'Enter') return submit();
      paint();
    }
    function start() { secret = secretCode(Math.random); cur = ''; tries = []; done = false; msg.textContent = ''; paint(); }
    '1234567890'.split('').forEach(function (d) { var b = document.createElement('button'); b.type = 'button'; b.textContent = d; keys[d] = b; b.addEventListener('click', function () { press(d); }); pad.appendChild(b); });
    [['⌫', 'Backspace', TX.del], ['↵', 'Enter', TX.ok]].forEach(function (a) { var b = document.createElement('button'); b.type = 'button'; b.textContent = a[0]; b.title = a[2]; b.addEventListener('click', function () { press(a[1]); }); pad.appendChild(b); });
    document.addEventListener('keydown', function (e) { if (active() === 'g-code' && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) { if (e.key === 'Enter' || e.key === 'Backspace' || /^\d$/.test(e.key)) { e.preventDefault(); press(e.key); } } });
    btn.addEventListener('click', start); btn.textContent = TX.again; $('#cb-help').textContent = TX.cbHint;
    start();
  })();

  // ---------- César : retrouver le décalage ----------
  var cipherGame = (function () {
    var cEl = $('#ci-cipher'), pEl = $('#ci-plain'), shEl = $('#ci-shift'), scEl = $('#ci-score'), tEl = $('#ci-time'), bestEl = $('#ci-best'), msg = $('#ci-msg'), btn = $('#ci-btn');
    var word, k, s, score, end, ti, run = false, last;
    bestEl.textContent = best('ak-cipher');
    function paint() { shEl.textContent = s; pEl.textContent = run ? caesar(cEl.textContent, -s) : '· · ·'; }
    function next() {
      do { word = TX.words[Math.floor(Math.random() * TX.words.length)]; } while (word === last);
      last = word; k = 1 + Math.floor(Math.random() * 25); s = 0;
      cEl.textContent = caesar(word, k); paint();
    }
    function tick() {
      var left = Math.max(0, Math.ceil((end - Date.now()) / 1000));
      tEl.textContent = left + 's';
      if (!left) stop();
    }
    function stop() {
      run = false; clearInterval(ti); msg.textContent = TX.ciEnd + score; btn.textContent = TX.again;
      if (score > best('ak-cipher')) { keep('ak-cipher', score); bestEl.textContent = score; }
      if (score > 0) announce('cipher', score);
      paint();
    }
    function start() {
      score = 0; scEl.textContent = 0; msg.textContent = ''; run = true; end = Date.now() + 60000;
      clearInterval(ti); ti = setInterval(tick, 250); tick(); btn.textContent = TX.again; next();
    }
    function turn(d) { if (run) { s = (s + d + 26) % 26; paint(); } }
    function submit() {
      if (!run) return;
      if (s === k) { score++; scEl.textContent = score; msg.textContent = ''; next(); }
      else { end -= 5000; msg.textContent = TX.ciWrong; tick(); }
    }
    $('#ci-down').addEventListener('click', function () { turn(-1); });
    $('#ci-up').addEventListener('click', function () { turn(1); });
    $('#ci-ok').addEventListener('click', submit);
    btn.addEventListener('click', start); btn.textContent = TX.start;
    document.addEventListener('keydown', function (e) {
      if (active() !== 'g-cipher' || /INPUT|TEXTAREA/.test(document.activeElement.tagName)) return;
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') { e.preventDefault(); turn(e.key === 'ArrowLeft' ? -1 : 1); }
      else if (e.key === 'Enter') { e.preventDefault(); run ? submit() : start(); }
    });
    s = 0; paint();
    return { stop: function () { if (run) stop(); } }; // quitter l'onglet termine la manche
  })();

  // ---------- onglet initial (#memory, #code, #cipher, #ctf) ----------
  var h = location.hash.replace('#', ''), map = { memory: 'g-memory', code: 'g-code', '2048': 'g-2048', cipher: 'g-cipher', ctf: 'g-ctf' };
  select(map[h] || 'g-2048');
})();

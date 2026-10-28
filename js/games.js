// Mini-jeux : onglets, Snake, Memory, Code Breaker. (2048 est dans game.js)

// ---------- logique pure (testée par tools/test.js) ----------
function feedback(secret, guess) {
  var hit = 0, near = 0;
  for (var i = 0; i < guess.length; i++) {
    if (guess[i] === secret[i]) hit++;
    else if (secret.indexOf(guess[i]) > -1) near++;
  }
  return { hit: hit, near: near };
}
function shuffle(a, rnd) {
  a = a.slice();
  for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; }
  return a;
}
function secretCode(rnd) { return shuffle('0123456789'.split(''), rnd).slice(0, 4).join(''); }
function nextHead(h, d, n) { return { x: (h.x + d.x + n) % n, y: (h.y + d.y + n) % n }; }
// Chiffre de César sur A-Z (le reste est laissé tel quel) ; k négatif pour déchiffrer.
function caesar(s, k) {
  return s.replace(/[A-Z]/g, function (c) { return String.fromCharCode((c.charCodeAt(0) - 65 + k % 26 + 26) % 26 + 65); });
}

if (typeof module !== 'undefined') module.exports = { feedback: feedback, shuffle: shuffle, secretCode: secretCode, nextHead: nextHead, caesar: caesar };

if (typeof document !== 'undefined') (function () {
  'use strict';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var fr = document.documentElement.lang !== 'en';
  var TX = fr ? {
    start: 'Jouer', again: 'Rejouer', score: 'Score', best: 'Meilleur', moves: 'Coups', time: 'Temps', tries: 'Essais',
    over: 'Perdu !', paused: 'Pause', win: 'Gagné !', hint: 'Flèches, ZQSD ou glisser. Espace pour pause.',
    cbHint: 'Trouve le code à 4 chiffres, tous différents. ● bien placé, ○ mal placé.', cbLose: 'Perdu, le code était ', cbWin: 'Code craqué en ',
    memHint: 'Retrouve toutes les paires.', ok: 'Entrer', del: 'Effacer', ciWrong: 'Raté, −5 s', ciEnd: 'Temps écoulé : ',
    words: ['PARE FEU', 'MOT DE PASSE', 'CHIFFREMENT', 'HAMECONNAGE', 'PORT OUVERT', 'INJECTION SQL', 'PAQUET RESEAU', 'CLE PUBLIQUE',
      'SAUVEGARDE', 'AUTHENTIFICATION', 'JOURNAL SYSTEME', 'VULNERABILITE', 'RECONNAISSANCE', 'PORTE DEROBEE', 'RANCONGICIEL', 'DROITS MINIMAUX']
  } : {
    start: 'Play', again: 'Play again', score: 'Score', best: 'Best', moves: 'Moves', time: 'Time', tries: 'Tries',
    over: 'Game over!', paused: 'Paused', win: 'You win!', hint: 'Arrows, WASD or swipe. Space to pause.',
    cbHint: 'Find the 4-digit code, all digits different. ● right place, ○ wrong place.', cbLose: 'You lost, the code was ', cbWin: 'Code cracked in ',
    memHint: 'Find all the pairs.', ok: 'Enter', del: 'Delete', ciWrong: 'Wrong, −5 s', ciEnd: 'Time is up: ',
    words: ['FIREWALL', 'PASSWORD', 'ENCRYPTION', 'PHISHING', 'OPEN PORT', 'SQL INJECTION', 'NETWORK PACKET', 'PUBLIC KEY',
      'BACKUP', 'AUTHENTICATION', 'SYSTEM LOG', 'VULNERABILITY', 'RECONNAISSANCE', 'BACKDOOR', 'RANSOMWARE', 'LEAST PRIVILEGE']
  };
  var announce = function (game, score) { window.dispatchEvent(new CustomEvent('ak-score', { detail: { game: game, score: score } })); };
  var best = function (k) { try { return +localStorage.getItem(k) || 0; } catch (e) { return 0; } };
  var keep = function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} };
  var active = function () { var p = $('.gp.on'); return p && p.id; };
  var accent = function () { return getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#7cc4ff'; };

  // ---------- onglets ----------
  var tabs = $$('.seg button');
  function select(id) {
    tabs.forEach(function (b) { b.setAttribute('aria-selected', b.dataset.g === id ? 'true' : 'false'); });
    $$('.gp').forEach(function (p) { p.classList.toggle('on', p.id === id); });
    if (history.replaceState) history.replaceState(null, '', '#' + id.replace('g-', ''));
    if (id !== 'g-snake') snake.pause();
    if (id !== 'g-cipher' && cipherGame) cipherGame.stop();
  }
  tabs.forEach(function (b) { b.addEventListener('click', function () { select(b.dataset.g); }); });

  // ---------- Snake ----------
  var snake = (function () {
    var cv = $('#snake'), N = 18, S = 20, g = cv.getContext('2d');
    var body, dir, qd, food, score, run, over, tm, speed;
    var bestEl = $('#sn-best'), scoreEl = $('#sn-score'), msg = $('#sn-msg'), btn = $('#sn-btn');
    bestEl.textContent = best('ak-snake');
    function put() { do { food = { x: Math.floor(Math.random() * N), y: Math.floor(Math.random() * N) }; } while (body.some(function (c) { return c.x === food.x && c.y === food.y; })); }
    function draw() {
      g.clearRect(0, 0, cv.width, cv.height);
      g.fillStyle = 'rgba(255,255,255,.05)';
      for (var i = 0; i < N; i++) for (var j = 0; j < N; j++) if ((i + j) % 2) g.fillRect(i * S, j * S, S, S);
      g.fillStyle = '#ff6b6b'; g.beginPath(); g.arc(food.x * S + S / 2, food.y * S + S / 2, S / 2 - 3, 0, 7); g.fill();
      g.fillStyle = accent();
      body.forEach(function (c, i) { g.globalAlpha = i ? .85 : 1; g.beginPath(); g.roundRect ? g.roundRect(c.x * S + 1, c.y * S + 1, S - 2, S - 2, 6) : g.rect(c.x * S + 1, c.y * S + 1, S - 2, S - 2); g.fill(); });
      g.globalAlpha = 1;
    }
    function tick() {
      dir = qd;
      var h = nextHead(body[0], dir, N);
      if (body.some(function (c) { return c.x === h.x && c.y === h.y; })) return end();
      body.unshift(h);
      if (h.x === food.x && h.y === food.y) { score++; scoreEl.textContent = score; speed = Math.max(60, speed - 3); put(); }
      else body.pop();
      draw(); schedule();
    }
    function schedule() { clearTimeout(tm); if (run) tm = setTimeout(tick, speed); }
    function end() {
      run = false; over = true; msg.textContent = TX.over; btn.textContent = TX.again;
      if (score > best('ak-snake')) { keep('ak-snake', score); bestEl.textContent = score; }
      if (score > 0) announce('snake', score);
      draw();
    }
    function reset() {
      body = [{ x: 9, y: 9 }, { x: 8, y: 9 }, { x: 7, y: 9 }]; dir = qd = { x: 1, y: 0 }; score = 0; speed = 140; over = false; run = false;
      scoreEl.textContent = 0; msg.textContent = ''; put(); draw();
    }
    function go() { if (over || !body) reset(); run = true; msg.textContent = ''; btn.textContent = TX.again; schedule(); }
    function pause() { if (run) { run = false; clearTimeout(tm); msg.textContent = TX.paused; } }
    function turn(x, y) { if (x !== -dir.x || y !== -dir.y) qd = { x: x, y: y }; if (!run && !over) go(); }
    var keys = { ArrowUp: [0, -1], w: [0, -1], z: [0, -1], ArrowDown: [0, 1], s: [0, 1], ArrowLeft: [-1, 0], a: [-1, 0], q: [-1, 0], ArrowRight: [1, 0], d: [1, 0] };
    document.addEventListener('keydown', function (e) {
      if (active() !== 'g-snake') return;
      var k = keys[e.key.length === 1 ? e.key.toLowerCase() : e.key];
      if (k) { e.preventDefault(); turn(k[0], k[1]); }
      else if (e.key === ' ') { e.preventDefault(); run ? pause() : go(); }
    });
    var t0;
    cv.addEventListener('touchstart', function (e) { t0 = e.touches[0]; e.preventDefault(); }, { passive: false });
    cv.addEventListener('touchend', function (e) {
      if (!t0) return; var t = e.changedTouches[0], dx = t.clientX - t0.clientX, dy = t.clientY - t0.clientY;
      if (Math.max(Math.abs(dx), Math.abs(dy)) < 20) return;
      Math.abs(dx) > Math.abs(dy) ? turn(dx > 0 ? 1 : -1, 0) : turn(0, dy > 0 ? 1 : -1);
    });
    btn.addEventListener('click', function () { reset(); go(); });
    $('#snake-help').textContent = TX.hint; btn.textContent = TX.start;
    reset();
    return { pause: pause };
  })();

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
    var MAX = 8, secret, cur, tries, done;
    function paint() {
      rows.innerHTML = '';
      for (var i = 0; i < MAX; i++) {
        var r = document.createElement('div'), t = tries[i];
        r.className = 'cb-row' + (!t && i === tries.length && !done ? ' cur' : '');
        var txt = t ? t.g : (i === tries.length && !done ? (cur + '····').slice(0, 4) : '····');
        r.innerHTML = '<span>' + txt + '</span><small>' + (t ? '●'.repeat(t.hit) + '○'.repeat(t.near) + (t.hit + t.near ? '' : '–') : '') + '</small>';
        rows.appendChild(r);
      }
      left.textContent = MAX - tries.length;
    }
    function submit() {
      if (done || cur.length < 4) return;
      var f = feedback(secret, cur); tries.push({ g: cur, hit: f.hit, near: f.near });
      if (f.hit === 4) { done = true; announce('code', tries.length); msg.textContent = TX.cbWin + tries.length + '/' + MAX; if (window.toast) window.toast(msg.textContent); }
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
    '1234567890'.split('').forEach(function (d) { var b = document.createElement('button'); b.type = 'button'; b.textContent = d; b.addEventListener('click', function () { press(d); }); pad.appendChild(b); });
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

  // ---------- onglet initial (#snake, #memory, #code, #cipher, #ctf) ----------
  var h = location.hash.replace('#', ''), map = { snake: 'g-snake', memory: 'g-memory', code: 'g-code', '2048': 'g-2048', cipher: 'g-cipher', ctf: 'g-ctf' };
  select(map[h] || 'g-2048');
})();

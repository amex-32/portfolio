// Classements : un par jeu, branchés sur /api/scores. Les jeux annoncent leur score avec l'événement "ak-score".
(function () {
  'use strict';
  var fr = document.documentElement.lang !== 'en';
  var TX = fr ? {
    title: 'Classement', pseudo: 'Ton pseudo', send: 'Enregistrer', none: 'Aucun score pour le moment.', loading: 'Chargement…',
    play: 'Joue une partie pour enregistrer un score.', yours: 'Ton score', saved: 'Enregistré. Ton meilleur : ', error: 'Classement indisponible.',
    rule: '2 à 16 caractères : lettres, chiffres, _ ou -.', pts: 'pts', moves: 'coups', tries: 'essais', low: 'Moins = mieux.'
  } : {
    title: 'Leaderboard', pseudo: 'Your nickname', send: 'Save', none: 'No score yet.', loading: 'Loading…',
    play: 'Play a game to save a score.', yours: 'Your score', saved: 'Saved. Your best: ', error: 'Leaderboard unavailable.',
    rule: '2 to 16 characters: letters, digits, _ or -.', pts: 'pts', moves: 'moves', tries: 'tries', low: 'Lower is better.'
  };
  var UNIT = { '2048': TX.pts, snake: TX.pts, memory: TX.moves, code: TX.tries, cipher: TX.pts };
  var LOW = ['memory', 'code'];
  var candidate = {}; // meilleur score de la session, par jeu
  var boards = {};

  function pseudoStore(v) { try { if (v != null) localStorage.setItem('ak-pseudo', v); return localStorage.getItem('ak-pseudo') || ''; } catch (e) { return ''; } }
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text) n.textContent = text; return n; }

  function build(root) {
    var game = root.dataset.game, low = LOW.indexOf(game) > -1;
    var list = el('ol', 'sb-list'), yours = el('p', 'sb-yours'), msg = el('p', 'sb-msg');
    var form = el('form', 'sb-form'), input = el('input'), btn = el('button', 'xp-btn', TX.send);
    input.type = 'text'; input.maxLength = 16; input.placeholder = TX.pseudo; input.required = true;
    input.pattern = '[A-Za-z0-9_\\-]{2,16}'; input.title = TX.rule; input.autocomplete = 'nickname'; input.value = pseudoStore();
    btn.type = 'submit'; form.appendChild(input); form.appendChild(btn);
    root.appendChild(el('h3', '', TX.title));
    if (low) root.appendChild(el('small', 'sb-hint', TX.low));
    [list, yours, form, msg].forEach(function (n) { root.appendChild(n); });

    function paintYours() {
      var s = candidate[game];
      yours.textContent = s == null ? TX.play : TX.yours + ' : ' + s + ' ' + UNIT[game];
      btn.disabled = s == null;
    }
    function load() {
      list.textContent = ''; list.appendChild(el('li', 'sb-empty', TX.loading));
      fetch('/api/scores?game=' + game, { cache: 'no-store' }).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (d) {
        list.textContent = '';
        if (!d.rows.length) { list.appendChild(el('li', 'sb-empty', TX.none)); return; }
        d.rows.forEach(function (row, i) {
          var li = el('li');
          li.appendChild(el('span', 'sb-rank', String(i + 1)));
          li.appendChild(el('b', i === 0 ? 'gold' : '', row.pseudo));
          li.appendChild(el('span', 'sb-score', row.score + ' ' + UNIT[game]));
          list.appendChild(li);
        });
      }).catch(function () { list.textContent = ''; list.appendChild(el('li', 'sb-empty', TX.error)); });
    }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (candidate[game] == null) return;
      btn.disabled = true; msg.textContent = '';
      fetch('/api/scores', { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ game: game, pseudo: input.value.trim(), score: candidate[game] }) })
        .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
        .then(function (x) {
          if (!x.ok) { msg.textContent = x.d.error || TX.error; return; }
          pseudoStore(input.value.trim()); msg.textContent = TX.saved + x.d.best + ' ' + UNIT[game]; load();
        })
        .catch(function () { msg.textContent = TX.error; })
        .then(function () { btn.disabled = candidate[game] == null; });
    });
    boards[game] = { paint: paintYours, load: load };
    paintYours(); load();
  }

  window.addEventListener('ak-score', function (e) {
    var d = e.detail, low = LOW.indexOf(d.game) > -1, c = candidate[d.game];
    if (c == null || (low ? d.score < c : d.score > c)) candidate[d.game] = d.score;
    if (boards[d.game]) boards[d.game].paint();
  });
  Array.prototype.forEach.call(document.querySelectorAll('.sb[data-game]'), build);

  // Classement du mini-CTF : lecture seule, les flags se soumettent dans le terminal (js/site.js).
  var ctf = document.querySelector('.sb[data-ctf]');
  if (ctf) {
    var list = el('ol', 'sb-list');
    ctf.appendChild(el('h3', '', TX.title)); ctf.appendChild(list);
    var loadCtf = function () {
      list.textContent = ''; list.appendChild(el('li', 'sb-empty', TX.loading));
      fetch('/api/ctf', { cache: 'no-store' }).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (d) {
        list.textContent = '';
        if (!d.rows.length) { list.appendChild(el('li', 'sb-empty', TX.none)); return; }
        d.rows.forEach(function (row, i) {
          var li = el('li');
          li.appendChild(el('span', 'sb-rank', String(i + 1)));
          li.appendChild(el('b', row.found === d.total ? 'gold' : '', row.pseudo));
          li.appendChild(el('span', 'sb-score', row.found + ' / ' + d.total));
          list.appendChild(li);
        });
      }).catch(function () { list.textContent = ''; list.appendChild(el('li', 'sb-empty', TX.error)); });
    };
    window.addEventListener('ak-flag', loadCtf);
    loadCtf();
  }
})();

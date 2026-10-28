// Vérifie la validation de l'API des classements : node tools/test-api.js
const assert = require('assert');
const { validate, GAMES } = require('../api/scores.js');

const ok = (b) => assert(!validate(b).error, JSON.stringify(b));
const ko = (b) => assert(validate(b).error, JSON.stringify(b));

ok({ game: 'snake', pseudo: 'Alex_k', score: 12 });
ok({ game: 'memory', pseudo: 'ab', score: 8 });
ok({ game: 'code', pseudo: 'a-b_c9', score: 3 });
ok({ game: '2048', pseudo: 'x'.repeat(16), score: 2048 });
ko({ game: 'nope', pseudo: 'abc', score: 1 });            // jeu inconnu
ko({ game: 'snake', pseudo: 'a', score: 5 });             // pseudo trop court
ko({ game: 'snake', pseudo: 'x'.repeat(17), score: 5 });  // pseudo trop long
ko({ game: 'snake', pseudo: 'a b', score: 5 });           // espace
ko({ game: 'snake', pseudo: "a';DROP", score: 5 });       // caractères interdits
ko({ game: 'snake', pseudo: 'abc', score: 322 });         // hors borne
ko({ game: 'snake', pseudo: 'abc', score: '12' });        // pas un entier
ko({ game: 'snake', pseudo: 'abc', score: 1.5 });
ko({ game: 'memory', pseudo: 'abc', score: 3 });          // sous le minimum de coups
ko({ game: 'code', pseudo: 'abc', score: 9 });
ko({ game: 'code', pseudo: 'abc', score: 0 });
ko(null);
ko({});
ok({ game: 'cipher', pseudo: 'abc', score: 60 });
ko({ game: 'cipher', pseudo: 'abc', score: 61 });
assert.deepStrictEqual(Object.keys(GAMES).sort(), ['2048', 'cipher', 'code', 'memory', 'snake']);
console.log('api : ok');

// CTF : chaque flag de tools/ctf.json est reconnu à sa place, le reste est refusé.
const { flagIndex, HASHES } = require('../api/ctf.js');
const { flags } = require('./ctf.json');
assert.strictEqual(HASHES.length, flags.length);
flags.forEach((f, i) => assert.strictEqual(flagIndex(f), i, f));
for (const bad of ['FLAG{nope}', 'flag{v13w_s0urc3_1s_y0ur_fr13nd}', flags[0] + ' ', '', null, 42, { a: 1 }, 'FLAG{' + 'a'.repeat(61) + '}']) assert.strictEqual(flagIndex(bad), -1, String(bad));
console.log('ctf : ok');

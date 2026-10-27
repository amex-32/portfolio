// Vérifie la logique pure des mini-jeux : node tools/test.js
const assert = require('assert');
const { feedback, shuffle, secretCode, nextHead } = require('../js/games.js');

assert.deepStrictEqual(feedback('1234', '1234'), { hit: 4, near: 0 });
assert.deepStrictEqual(feedback('1234', '4321'), { hit: 0, near: 4 });
assert.deepStrictEqual(feedback('1234', '1567'), { hit: 1, near: 0 });
assert.deepStrictEqual(feedback('1234', '5678'), { hit: 0, near: 0 });
assert.deepStrictEqual(feedback('1234', '1243'), { hit: 2, near: 2 });

const s = shuffle([1, 2, 3, 4, 5], Math.random);
assert.deepStrictEqual(s.slice().sort(), [1, 2, 3, 4, 5]);
for (let i = 0; i < 200; i++) {
  const c = secretCode(Math.random);
  assert(/^\d{4}$/.test(c) && new Set(c).size === 4, c);
}
assert.deepStrictEqual(nextHead({ x: 17, y: 0 }, { x: 1, y: 0 }, 18), { x: 0, y: 0 });
assert.deepStrictEqual(nextHead({ x: 0, y: 0 }, { x: 0, y: -1 }, 18), { x: 0, y: 17 });
console.log('jeux : ok');

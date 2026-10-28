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

// La CSP de vercel.json n'autorise que les scripts inline dont elle connaît l'empreinte : après un changement du script "boot" de build.py, recopier la nouvelle empreinte.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const root = path.join(__dirname, '..');
const csp = JSON.parse(fs.readFileSync(path.join(root, 'vercel.json'), 'utf8')).headers[0].headers.find((h) => h.key === 'Content-Security-Policy').value;
const pages = (dir) => fs.readdirSync(dir).filter((f) => f.endsWith('.html')).map((f) => path.join(dir, f));
for (const f of ['', 'en', 'projects', 'en/projects'].flatMap((d) => pages(path.join(root, d)))) {
  for (const [, js] of fs.readFileSync(f, 'utf8').matchAll(/<script>([\s\S]*?)<\/script>/g)) {
    const hash = "'sha256-" + crypto.createHash('sha256').update(js).digest('base64') + "'";
    assert(csp.includes(hash), `${f} : script inline absent de la CSP, ajouter ${hash} dans vercel.json`);
  }
}
console.log('csp : ok');

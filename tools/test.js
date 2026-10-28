// Vérifie la logique pure des mini-jeux : node tools/test.js
const assert = require('assert');
const { feedback, shuffle, secretCode, nextHead, caesar } = require('../js/games.js');

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
assert.strictEqual(caesar('PARE FEU', 3), 'SDUH IHX');
assert.strictEqual(caesar('XYZ', 3), 'ABC');
assert.strictEqual(caesar(caesar('MOT DE PASSE', 11), -11), 'MOT DE PASSE');
assert.strictEqual(caesar('ABC', 26), 'ABC');
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

// Mini-CTF : chaque flag est caché à sa place (sous la forme attendue), et n'apparaît en clair dans aucun autre fichier déployé.
const { flags } = require('./ctf.json');
const read = (f) => fs.readFileSync(path.join(root, f), 'utf8');
const rot13 = (s) => s.replace(/[a-z]/gi, (c) => String.fromCharCode((c <= 'Z' ? 65 : 97) + (c.toLowerCase().charCodeAt(0) - 97 + 13) % 26));
assert(read('index.html').includes(flags[0]) && read('en/index.html').includes(flags[0]), 'flag 1 : code source de l\'accueil');
assert(JSON.parse(read('vercel.json')).headers[0].headers.some((h) => h.key === 'X-Flag' && h.value.endsWith(flags[1])), 'flag 2 : en-tête X-Flag');
assert(read('robots.txt').includes(Buffer.from(flags[2]).toString('base64')), 'flag 3 : base64 dans robots.txt');
assert(read('js/site.js').includes(rot13(flags[3])), 'flag 4 : ROT13 dans la console');
assert(read('js/site.js').includes(flags[4].split('').reverse().join('')), 'flag 5 : code Konami');
const ignored = read('.vercelignore').split('\n').map((l) => l.trim().replace(/\/$/, '')).filter((l) => l && !l.startsWith('#'));
const deployed = (dir) => fs.readdirSync(path.join(root, dir), { withFileTypes: true }).flatMap((e) => {
  const rel = path.posix.join(dir, e.name);
  if (ignored.includes(rel) || ['.git', 'node_modules'].includes(rel)) return [];
  return e.isDirectory() ? deployed(rel) : [rel];
});
const allowed = { [flags[0]]: ['index.html', 'en/index.html'], [flags[1]]: ['vercel.json'] };
for (const f of deployed('')) {
  if (!/\.(html|js|css|json|txt|xml|svg)$/.test(f)) continue;
  const text = read(f);
  for (const flag of flags) assert(!text.includes(flag) || (allowed[flag] || []).includes(f), `${f} : contient ${flag} en clair`);
}
console.log('ctf : ok');

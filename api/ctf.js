// Mini-CTF : 6 flags cachés dans le site, un classement par nombre de flags trouvés.
// GET  /api/ctf                -> { rows: [{ pseudo, found }], total: 6 }
// POST /api/ctf {pseudo, flag} -> { ok: true, found, total, already } ou 400 { error }
const crypto = require('crypto');
const { PSEUDO, connect, tooFast } = require('./scores.js');

// Empreintes SHA-256 des flags (tools/ctf.json, vérifié par tools/test.js) : le code serveur ne contient pas les flags eux-mêmes.
const HASHES = [
  'b15268ea87ce2214e2d2cecce9ccd6e71e54e1d5bf13444ac866438a656f6305',
  'c5671714561ac187e24fa8a7acc0428c210db1f38a61fc29695c3d261b7e7394',
  '5c77c0213b21e33c09e0a6531529c553f6b8f00c72d6bbccc37c84e5ac2c48ad',
  '3ad342f577045fad64b087b49001cb0a8aa286917cf90752d8ea37d76a043cfb',
  'ea6d89dc5568005eed6e926c51d2b754f541d4d9c6584cee69f9dfd95a69891e',
  '3b0802725c9b1cfd982b0d39195b283f06ae64d525eb47bdfc56d554e4430150',
];

// Numéro du flag (0 à 5), -1 s'il est faux ou mal formé.
function flagIndex(flag) {
  if (typeof flag !== 'string' || !/^FLAG\{[A-Za-z0-9_]{1,60}\}$/.test(flag)) return -1;
  return HASHES.indexOf(crypto.createHash('sha256').update(flag).digest('hex'));
}

let ready; // table créée une fois par instance
async function db() {
  const conn = await connect();
  ready = ready || (async () => {
    await conn.query('CREATE DATABASE IF NOT EXISTS game_ctf');
    await conn.query(`CREATE TABLE IF NOT EXISTS game_ctf.found (
      pseudo VARCHAR(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
      flag TINYINT NOT NULL,
      found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (pseudo, flag))`);
  })();
  await ready;
  return conn;
}

async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  let conn;
  try {
    if (req.method === 'GET') {
      conn = await db();
      const [rows] = await conn.query(
        'SELECT pseudo, COUNT(*) AS found FROM game_ctf.found GROUP BY pseudo ORDER BY found DESC, MAX(found_at) ASC LIMIT 10');
      return res.status(200).json({ rows: rows.map((r) => ({ pseudo: r.pseudo, found: Number(r.found) })), total: HASHES.length });
    }
    if (req.method === 'POST') {
      const body = req.body || {};
      if (typeof body.pseudo !== 'string' || !PSEUDO.test(body.pseudo)) return res.status(400).json({ error: 'pseudo invalide (2 à 16 lettres, chiffres, _ ou -)' });
      if (tooFast(req)) return res.status(429).json({ error: 'trop rapide, réessaie dans quelques secondes' });
      const i = flagIndex(body.flag);
      if (i < 0) return res.status(400).json({ error: 'flag incorrect' });
      conn = await db();
      const [r] = await conn.execute('INSERT IGNORE INTO game_ctf.found (pseudo, flag) VALUES (?, ?)', [body.pseudo, i]);
      const [[row]] = await conn.execute('SELECT COUNT(*) AS n FROM game_ctf.found WHERE pseudo = ?', [body.pseudo]);
      return res.status(200).json({ ok: true, found: Number(row.n), total: HASHES.length, already: r.affectedRows === 0 });
    }
    res.setHeader('Allow', 'GET, POST');
    return res.status(405).json({ error: 'méthode non autorisée' });
  } catch (e) {
    console.error(e);
    return res.status(503).json({ error: 'classement indisponible' });
  } finally {
    if (conn) conn.end().catch(() => {});
  }
}

module.exports = handler;
module.exports.flagIndex = flagIndex;
module.exports.HASHES = HASHES;

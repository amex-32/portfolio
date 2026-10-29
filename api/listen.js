// Suivi de mes écoutes (lecteur du site) : lecture publique, écriture réservée au propriétaire.
// GET  /api/listen              -> { total, recent: [{ track, at }], top: [{ track, plays }] }   (public)
// GET  /api/listen?auth=1       -> 200 { owner: true } ou 401                                    (en-tête x-owner)
// POST /api/listen { track }    -> { ok: true }                                                  (en-tête x-owner)
// x-owner : mon mot de passe ; seul son empreinte SHA-256 (variable d'environnement OWNER_HASH) est connue du serveur.
const crypto = require('crypto');
const mysql = require('mysql2/promise');
const { tooFast } = require('./scores.js');

function isOwner(req) {
  const hash = (process.env.OWNER_HASH || '').trim().replace(/^["']|["']$/g, ''), tok = req.headers['x-owner']; // tolère espaces et guillemets collés avec la valeur
  if (!/^[0-9a-f]{64}$/i.test(hash) || typeof tok !== 'string' || !tok || tok.length > 200) return false;
  return crypto.timingSafeEqual(crypto.createHash('sha256').update(tok).digest(), Buffer.from(hash, 'hex'));
}
const TRACK = /^[\p{L}\p{N} .,'!?()&+_-]{1,60}$/u;

let ready;
async function connect() {
  const conn = await mysql.createConnection({
    host: process.env.DB_HOST, port: Number(process.env.DB_PORT) || 4000,
    user: process.env.DB_USER, password: process.env.DB_PASSWORD,
    ssl: process.env.DB_SSL === '0' ? undefined : { minVersion: 'TLSv1.2', rejectUnauthorized: true },
    connectTimeout: 8000,
  });
  ready = ready || (async () => {
    await conn.query('CREATE DATABASE IF NOT EXISTS portfolio_listen');
    await conn.query(`CREATE TABLE IF NOT EXISTS portfolio_listen.plays (
      id BIGINT AUTO_INCREMENT PRIMARY KEY,
      track VARCHAR(60) CHARACTER SET utf8mb4 NOT NULL,
      played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)`);
  })();
  await ready;
  return conn;
}

async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  let conn;
  try {
    if (req.method === 'GET' && req.query.auth) {
      if (tooFast(req)) return res.status(429).json({ error: 'trop rapide' });
      return isOwner(req) ? res.status(200).json({ owner: true }) : res.status(401).json({ error: 'refusé' });
    }
    if (req.method === 'GET') {
      conn = await connect();
      const [[{ total }]] = await conn.query('SELECT COUNT(*) AS total FROM portfolio_listen.plays');
      const [recent] = await conn.query('SELECT track, played_at AS at FROM portfolio_listen.plays ORDER BY id DESC LIMIT 5');
      const [top] = await conn.query('SELECT track, COUNT(*) AS plays FROM portfolio_listen.plays GROUP BY track ORDER BY plays DESC, MAX(id) DESC LIMIT 5');
      return res.status(200).json({ total, recent, top });
    }
    if (req.method === 'POST') {
      if (tooFast(req)) return res.status(429).json({ error: 'trop rapide' });
      if (!isOwner(req)) return res.status(401).json({ error: 'refusé' });
      const track = req.body && req.body.track;
      if (typeof track !== 'string' || !TRACK.test(track)) return res.status(400).json({ error: 'morceau invalide' });
      conn = await connect();
      await conn.execute('INSERT INTO portfolio_listen.plays (track) VALUES (?)', [track]);
      return res.status(200).json({ ok: true });
    }
    res.setHeader('Allow', 'GET, POST');
    return res.status(405).json({ error: 'méthode non autorisée' });
  } catch (e) {
    console.error(e);
    return res.status(503).json({ error: 'indisponible' });
  } finally {
    if (conn) conn.end().catch(() => {});
  }
}

module.exports = handler;
module.exports.isOwner = isOwner;
module.exports.TRACK = TRACK;

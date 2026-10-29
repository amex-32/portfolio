// Suivi de mes écoutes (lecteur du site) : lecture publique, écriture réservée au propriétaire.
// GET    /api/listen             -> { total, recent: [{ track, at }], top: [{ track, plays }] }   (public)
// POST   /api/listen?auth=1      -> 200 { owner: true } + cookie de session, ou 401              (en-tête x-owner : mon mot de passe)
// DELETE /api/listen?auth=1      -> { ok: true }, cookie effacé
// POST   /api/listen { track }   -> { ok: true }                                                  (cookie de session)
// Le serveur ne connaît que l'empreinte SHA-256 du mot de passe (variable d'environnement OWNER_HASH).
// Après le login, le navigateur garde seulement un cookie HttpOnly signé avec cette empreinte : le mot de passe n'est stocké nulle part,
// et changer OWNER_HASH déconnecte toutes les sessions.
const crypto = require('crypto');
const { db, ensure, tooFast, cookies } = require('./_lib.js');

const ownerHash = () => (process.env.OWNER_HASH || '').trim().replace(/^["']|["']$/g, ''); // tolère espaces et guillemets collés avec la valeur
const hashOk = () => /^[0-9a-f]{64}$/i.test(ownerHash());

function isOwner(req) {
  const hash = ownerHash(), tok = req.headers['x-owner'];
  if (!hashOk() || typeof tok !== 'string' || !tok || tok.length > 200) return false;
  return crypto.timingSafeEqual(crypto.createHash('sha256').update(tok).digest(), Buffer.from(hash, 'hex'));
}

// Session : "<expiration en ms>.<HMAC-SHA256(expiration) avec OWNER_HASH comme clé>", valable 30 jours.
const COOKIE = 'ak_owner', DAYS = 30;
const sign = (exp) => crypto.createHmac('sha256', Buffer.from(ownerHash(), 'hex')).update('listen:' + exp).digest('hex');
function newSession(now) {
  const exp = (now || Date.now()) + DAYS * 864e5;
  return exp + '.' + sign(exp);
}
function hasSession(req, now) {
  const v = cookies(req)[COOKIE];
  if (!hashOk() || typeof v !== 'string') return false;
  const m = /^(\d{13})\.([0-9a-f]{64})$/.exec(v);
  if (!m || Number(m[1]) < (now || Date.now())) return false;
  return crypto.timingSafeEqual(Buffer.from(m[2], 'hex'), Buffer.from(sign(m[1]), 'hex'));
}
const cookieHeader = (value, maxAge) => `${COOKIE}=${value}; Path=/api/listen; Max-Age=${maxAge}; HttpOnly; Secure; SameSite=Strict`;

const TRACK = /^[\p{L}\p{N} .,'!?()&+_-]{1,60}$/u;

const schema = () => ensure('listen', async (pool) => {
  await pool.query('CREATE DATABASE IF NOT EXISTS portfolio_listen');
  await pool.query(`CREATE TABLE IF NOT EXISTS portfolio_listen.plays (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    track VARCHAR(60) CHARACTER SET utf8mb4 NOT NULL,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)`);
});

async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  try {
    if (req.query.auth && req.method === 'POST') {
      if (!hashOk()) return res.status(503).json({ error: 'OWNER_HASH absent ou mal formé (64 caractères hexadécimaux attendus)' });
      // un essai toutes les 5 s par adresse : de quoi rendre le devinage du mot de passe très lent
      if (tooFast(req, 'login')) return res.status(429).json({ error: 'trop rapide' });
      if (!isOwner(req)) return res.status(401).json({ error: 'refusé' });
      res.setHeader('Set-Cookie', cookieHeader(newSession(), DAYS * 86400));
      return res.status(200).json({ owner: true });
    }
    if (req.query.auth && req.method === 'DELETE') {
      res.setHeader('Set-Cookie', cookieHeader('', 0));
      return res.status(200).json({ ok: true });
    }
    if (req.method === 'GET') {
      await schema();
      const pool = db();
      const [[{ total }]] = await pool.query('SELECT COUNT(*) AS total FROM portfolio_listen.plays');
      const [recent] = await pool.query('SELECT track, played_at AS at FROM portfolio_listen.plays ORDER BY id DESC LIMIT 5');
      const [top] = await pool.query('SELECT track, COUNT(*) AS plays FROM portfolio_listen.plays GROUP BY track ORDER BY plays DESC, MAX(id) DESC LIMIT 5');
      return res.status(200).json({ total, recent, top });
    }
    if (req.method === 'POST') {
      if (!hasSession(req)) return res.status(401).json({ error: 'refusé' });
      const track = req.body && req.body.track;
      if (typeof track !== 'string' || !TRACK.test(track)) return res.status(400).json({ error: 'morceau invalide' });
      await schema();
      await db().execute('INSERT INTO portfolio_listen.plays (track) VALUES (?)', [track]);
      return res.status(200).json({ ok: true });
    }
    res.setHeader('Allow', 'GET, POST, DELETE');
    return res.status(405).json({ error: 'méthode non autorisée' });
  } catch (e) {
    console.error(e);
    return res.status(503).json({ error: 'indisponible' });
  }
}

module.exports = handler;
module.exports.isOwner = isOwner;
module.exports.newSession = newSession;
module.exports.hasSession = hasSession;
module.exports.TRACK = TRACK;

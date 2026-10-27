// Classements des mini-jeux : une base MySQL (TiDB Cloud) par jeu, un score par pseudo.
// GET  /api/scores?game=snake            -> { rows: [{ pseudo, score }], best: "high" | "low" }
// POST /api/scores {game, pseudo, score}  -> { ok: true, best: <meilleur score de ce pseudo> }
const mysql = require('mysql2/promise');

// best "high" : le plus grand score gagne ; "low" : le plus petit gagne (coups, essais).
// min/max : bornes plausibles, rien d'autre n'est accepté.
const GAMES = {
  '2048': { db: 'game_2048', best: 'high', min: 4, max: 3000000 },
  snake: { db: 'game_snake', best: 'high', min: 1, max: 321 },
  memory: { db: 'game_memory', best: 'low', min: 8, max: 99 },
  code: { db: 'game_code', best: 'low', min: 1, max: 8 },
};
const PSEUDO = /^[A-Za-z0-9_-]{2,16}$/;

// shortcut: scores envoyés par le navigateur, donc falsifiables dans les bornes ; ajouter une preuve de partie si ça devient un enjeu.
function validate(body) {
  const game = GAMES[body && body.game];
  if (!game) return { error: 'jeu inconnu' };
  if (typeof body.pseudo !== 'string' || !PSEUDO.test(body.pseudo)) return { error: 'pseudo invalide (2 à 16 lettres, chiffres, _ ou -)' };
  const score = body.score;
  if (!Number.isInteger(score) || score < game.min || score > game.max) return { error: 'score invalide' };
  return { game, pseudo: body.pseudo, score };
}

let ready; // schéma créé une fois par instance
async function connect() {
  const conn = await mysql.createConnection({
    host: process.env.DB_HOST, port: Number(process.env.DB_PORT) || 4000,
    user: process.env.DB_USER, password: process.env.DB_PASSWORD,
    ssl: process.env.DB_SSL === '0' ? undefined : { minVersion: 'TLSv1.2', rejectUnauthorized: true },
    connectTimeout: 8000,
  });
  ready = ready || Promise.all(Object.values(GAMES).map(async (g) => {
    await conn.query(`CREATE DATABASE IF NOT EXISTS ${g.db}`);
    await conn.query(`CREATE TABLE IF NOT EXISTS ${g.db}.scores (
      pseudo VARCHAR(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci PRIMARY KEY,
      score INT NOT NULL,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)`);
  }));
  await ready;
  return conn;
}

// shortcut: limite par instance serverless (pas partagée entre instances), suffisante contre le spam simple.
const lastPost = new Map();
function tooFast(req) {
  const ip = String(req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').split(',')[0].trim();
  const now = Date.now();
  if (now - (lastPost.get(ip) || 0) < 5000) return true;
  lastPost.set(ip, now);
  if (lastPost.size > 5000) lastPost.clear();
  return false;
}

async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  let conn;
  try {
    if (req.method === 'GET') {
      const game = GAMES[req.query.game];
      if (!game) return res.status(400).json({ error: 'jeu inconnu' });
      conn = await connect();
      const order = game.best === 'high' ? 'DESC' : 'ASC';
      const [rows] = await conn.query(`SELECT pseudo, score FROM ${game.db}.scores ORDER BY score ${order}, updated_at ASC LIMIT 10`);
      return res.status(200).json({ rows, best: game.best });
    }
    if (req.method === 'POST') {
      const v = validate(req.body);
      if (v.error) return res.status(400).json({ error: v.error });
      if (tooFast(req)) return res.status(429).json({ error: 'trop rapide, réessaie dans quelques secondes' });
      conn = await connect();
      const better = v.game.best === 'high' ? '<' : '>'; // ancien score moins bon que le nouveau
      await conn.execute(
        `INSERT INTO ${v.game.db}.scores (pseudo, score) VALUES (?, ?)
         ON DUPLICATE KEY UPDATE score = IF(score ${better} VALUES(score), VALUES(score), score)`,
        [v.pseudo, v.score]);
      const [[row]] = await conn.execute(`SELECT score FROM ${v.game.db}.scores WHERE pseudo = ?`, [v.pseudo]);
      return res.status(200).json({ ok: true, best: row.score });
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
module.exports.validate = validate;
module.exports.GAMES = GAMES;

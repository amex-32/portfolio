// Outils communs aux fonctions de api/ (le « _ » empêche Vercel d'en faire une route).
const mysql = require('mysql2/promise');

// Un petit pool par instance serverless : les requêtes suivantes réutilisent la connexion TLS au lieu d'en rouvrir une.
// idleTimeout ferme les connexions restées inactives (instance gelée entre deux appels) avant que la base ne les coupe.
let pool;
function db() {
  pool = pool || mysql.createPool({
    host: process.env.DB_HOST, port: Number(process.env.DB_PORT) || 4000,
    user: process.env.DB_USER, password: process.env.DB_PASSWORD,
    ssl: process.env.DB_SSL === '0' ? undefined : { minVersion: 'TLSv1.2', rejectUnauthorized: true },
    connectTimeout: 8000, connectionLimit: 2, maxIdle: 1, idleTimeout: 20000, enableKeepAlive: true,
  });
  return pool;
}

// Schéma créé une fois par instance (CREATE … IF NOT EXISTS) ; en cas d'échec, on réessaiera au prochain appel.
const schemas = new Map();
function ensure(name, create) {
  if (!schemas.has(name)) schemas.set(name, create(db()).catch((e) => { schemas.delete(name); throw e; }));
  return schemas.get(name);
}

// Adresse du visiteur : Vercel fournit x-real-ip ; sinon premier élément de x-forwarded-for (serveur local).
function ip(req) {
  return String(req.headers['x-real-ip'] || req.headers['x-forwarded-for'] || (req.socket && req.socket.remoteAddress) || '').split(',')[0].trim();
}

// shortcut: limite par instance serverless (pas partagée entre instances), suffisante contre le spam simple.
// Une clé par route : un score envoyé ne bloque pas un flag, et inversement.
const last = new Map();
function tooFast(req, route, ms) {
  const key = route + ' ' + ip(req), now = Date.now();
  if (now - (last.get(key) || 0) < (ms || 5000)) return true;
  last.set(key, now);
  if (last.size > 5000) last.clear();
  return false;
}

// Cookies de la requête (Vercel remplit req.cookies ; le serveur local tools/dev.js non).
function cookies(req) {
  if (req.cookies) return req.cookies;
  return Object.fromEntries(String(req.headers.cookie || '').split(';').map((c) => c.trim().split('=')).filter((c) => c[0]).map(([k, ...v]) => [k, decodeURIComponent(v.join('='))]));
}

module.exports = { db, ensure, ip, tooFast, cookies };

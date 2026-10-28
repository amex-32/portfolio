// Serveur local : fichiers statiques + /api/scores et /api/ctf. Usage : DB_HOST=… DB_USER=… DB_PASSWORD=… node tools/dev.js [port]
const http = require('http');
const fs = require('fs');
const path = require('path');
const API = { '/api/scores': require('../api/scores.js'), '/api/ctf': require('../api/ctf.js') };

const ROOT = path.join(__dirname, '..');
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.png': 'image/png', '.json': 'application/json', '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.txt': 'text/plain; charset=utf-8', '.xml': 'application/xml' };

http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  const handler = API[url.pathname];
  if (handler) {
    req.query = Object.fromEntries(url.searchParams);
    res.status = (c) => { res.statusCode = c; return res; };
    res.json = (o) => { res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(o)); };
    let body = '';
    req.on('data', (c) => { body += c; if (body.length > 2000) req.destroy(); });
    req.on('end', () => { try { req.body = body ? JSON.parse(body) : undefined; } catch { req.body = undefined; } handler(req, res); });
    return;
  }
  let file = path.join(ROOT, decodeURIComponent(url.pathname));
  if (!file.startsWith(ROOT)) return res.writeHead(403).end();
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
  fs.readFile(file, (err, data) => {
    if (err) return res.writeHead(404).end('404');
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' }).end(data);
  });
}).listen(Number(process.argv[2]) || 8765, () => console.log('http://localhost:' + (process.argv[2] || 8765)));

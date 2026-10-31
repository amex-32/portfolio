"""Serveur local : comme Vercel, une adresse inconnue renvoie 404.html. Usage : python tools/serve.py [port]"""
import http.server
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


class Site(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".glb": "model/gltf-binary"}

    def send_error(self, code, message=None, explain=None):
        if code != 404 or self.command != "GET":
            return super().send_error(code, message, explain)
        page = (ROOT / "404.html").read_bytes()
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)


os.chdir(ROOT)
http.server.ThreadingHTTPServer(("", int(sys.argv[1]) if len(sys.argv) > 1 else 8770), Site).serve_forever()

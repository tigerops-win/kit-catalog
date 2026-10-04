#!/usr/bin/env python3
"""kit-catalog server: serves the catalog, /health, and /notify -> signups.jsonl.
Run: python3 server.py (PORT env, default 8000). Deployed on Railway."""
import json, os, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/html"):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/health":
            return self._send(200, json.dumps({"ok": True}), "application/json")
        if p in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html")) as f:
                return self._send(200, f.read())
        return self._send(404, "not found", "text/plain")
    def do_POST(self):
        if urlparse(self.path).path == "/notify":
            n = int(self.headers.get("Content-Length", 0))
            try:
                payload = json.loads(self.rfile.read(n) or b"{}")
            except Exception:
                payload = {}
            email = str(payload.get("email", "")).strip()
            kit = str(payload.get("kit", "")).strip()
            if "@" not in email or not kit:
                return self._send(400, json.dumps({"ok": False}), "application/json")
            payload["ts"] = int(time.time())
            with open(os.path.join(HERE, "signups.jsonl"), "a") as f:
                f.write(json.dumps({"ts": payload["ts"], "kit": kit, "email": email}) + "\n")
            return self._send(200, json.dumps({"ok": True}), "application/json")
        return self._send(404, "not found", "text/plain")
    def log_message(self, *a):
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(("0.0.0.0", port), H).serve_forever()

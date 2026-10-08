import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

BASE = Path(__file__).parent
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

class H(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        f = BASE / ("index.html" if self.path in ("/", "/index.html") else self.path.lstrip("/"))
        if f.exists() and f.is_file() and f.suffix in (".html", ".css", ".js"):
            body = f.read_bytes()
            mime = {"html": "text/html; charset=utf-8", "css": "text/css", "js": "text/javascript"}.get(f.suffix[1:], "text/plain")
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            # default to index
            body = (BASE / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/chat":
            return self._json({"error": "not found"}, 404)
        try:
            ln = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(ln) or b"{}")
        except Exception:
            return self._json({"error": "JSON غلط"}, 400)

        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            return self._json({"error": "حط NVIDIA_API_KEY في الـ Environment الاول"}, 500)

        body = {
            "model": payload.get("model", "deepseek-ai/deepseek-v3.1"),
            "messages": payload.get("messages", []),
            "temperature": float(payload.get("temperature", 0.6)),
            "max_tokens": 1024,
        }
        req = urllib.request.Request(
            NVIDIA_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return self._json(json.loads(r.read()))
        except Exception as e:
            return self._json({"error": f"NVIDIA error: {e}"}, 502)

if __name__ == "__main__":
    port = 8787
    print(f"Server running on http://localhost:{port}", flush=True)
    print("Set NVIDIA_API_KEY env var before running", flush=True)
    HTTPServer(("127.0.0.1", port), H).serve_forever()

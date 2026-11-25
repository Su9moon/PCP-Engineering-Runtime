"""Serve the personal Dashboard V1 over loopback HTTPS."""
import argparse
import json
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from sources import Sources

ROOT = Path(__file__).resolve().parent
STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}
CSP = "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"

class DashboardServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port, sources, context):
        self.sources = sources
        super().__init__(("127.0.0.1", port), Handler)
        self.socket = context.wrap_socket(self.socket, server_side=True, do_handshake_on_connect=False)


class Handler(BaseHTTPRequestHandler):
    server_version = "PCP-Dashboard/1"
    sys_version = ""

    def setup(self):
        self.request.settimeout(12)
        super().setup()

    def log_message(self, format, *args):
        return

    def payload(self, status, body, media_type="text/plain; charset=utf-8", headers=(), head=False):
        self.send_response(status)
        self.send_header("Content-Type", media_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        for key, value in headers:
            self.send_header(key, value)
        self.end_headers()
        if not head:
            self.wfile.write(body)
    def do_GET(self):
        self.read(False)

    def do_HEAD(self):
        self.read(True)

    def read(self, head):
        try:
            path = urlsplit(self.path).path
        except ValueError:
            self.payload(400, b"Invalid request", head=head)
            return
        if path == "/api/state":
            try:
                state = self.server.sources.snapshot()
                body = json.dumps(state, ensure_ascii=False).encode("utf-8")
            except (ValueError, OSError, TypeError, AttributeError):
                self.payload(503, b"Dashboard source snapshot unavailable", head=head)
                return
            self.payload(200, body, "application/json; charset=utf-8", head=head)
            return
        if path not in STATIC:
            self.payload(404, b"Not found", head=head)
            return
        name, media_type = STATIC[path]
        self.payload(200, (ROOT / name).read_bytes(), media_type, head=head)

    def do_POST(self):
        self.payload(405, b"Read-only dashboard", headers=[("Allow", "GET, HEAD")])

    do_PUT = do_PATCH = do_DELETE = do_POST


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    config = json.loads(parser.parse_args().config.read_text(encoding="utf-8"))
    tls = config["tls"]
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(tls["cert"], tls["key"])
    sources = Sources(config["sources"], ROOT.parent)
    with DashboardServer(config["port"], sources, context) as server:
        print(f"Dashboard V1 HTTPS listening on {server.server_address[0]}:{server.server_address[1]}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()

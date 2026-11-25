"""Serve the personal Dashboard V1 over loopback and private LAN HTTPS."""
import argparse
import ipaddress
import json
import ssl
import threading
from contextlib import ExitStack
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
PRIVATE_NETWORKS = tuple(ipaddress.IPv4Network(value) for value in (
    "127.0.0.0/8", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
))


class DashboardServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port, sources, context, *, address="127.0.0.1", clients="127.0.0.0/8"):
        self.clients = ipaddress.IPv4Network(clients)
        bind = ipaddress.IPv4Address(address)
        if bind not in self.clients or not any(self.clients.subnet_of(private) for private in PRIVATE_NETWORKS):
            raise ValueError("Listener and client network must share an explicit private IPv4 subnet")
        self.sources = sources
        super().__init__((str(bind), port), Handler)
        self.socket = context.wrap_socket(self.socket, server_side=True, do_handshake_on_connect=False)

    def verify_request(self, request, client_address):
        return ipaddress.IPv4Address(client_address[0]) in self.clients


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
    with ExitStack() as stack:
        local = stack.enter_context(DashboardServer(config["port"], sources, context))
        if lan := config.get("lan"):
            try:
                private = stack.enter_context(DashboardServer(
                    config["port"], sources, context, address=lan["address"], clients=lan["clients"],
                ))
            except OSError as exc:
                print(f"Dashboard LAN listener unavailable at {lan['address']}: {exc.strerror}", flush=True)
            else:
                print(f"Dashboard V1 HTTPS listening on {private.server_address[0]}:{private.server_address[1]}", flush=True)
                threading.Thread(target=private.serve_forever, daemon=True).start()
        print(f"Dashboard V1 HTTPS listening on {local.server_address[0]}:{local.server_address[1]}", flush=True)
        local.serve_forever()


if __name__ == "__main__":
    main()

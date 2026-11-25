"""Serve Dashboard V1 to one administrator on a private HTTPS listener."""
import argparse
import base64
import binascii
import hmac
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


def password_from(path):
    file = Path(path)
    if file.stat().st_mode & 0o077:
        raise ValueError("Dashboard password file must be private (0600)")
    value = file.read_text(encoding="utf-8").strip()
    if len(value) < 24 or not value.isascii() or any(ord(char) < 33 or ord(char) == 127 for char in value):
        raise ValueError("Dashboard password must have at least 24 printable ASCII characters")
    return value


class DashboardServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, endpoint, networks, password, sources, context):
        self.networks = networks
        self.credential = ("admin:" + password).encode("ascii")
        self.sources = sources
        super().__init__(endpoint, Handler)
        self.socket = context.wrap_socket(self.socket, server_side=True, do_handshake_on_connect=False)

    def verify_request(self, request, client_address):
        address = ipaddress.ip_address(client_address[0])
        return any(address in network for network in self.networks)


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

    def authorized(self):
        method, _, encoded = self.headers.get("Authorization", "").partition(" ")
        if method.lower() != "basic":
            return False
        try:
            given = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error):
            return False
        return hmac.compare_digest(given, self.server.credential)

    def do_GET(self):
        self.read(False)

    def do_HEAD(self):
        self.read(True)

    def read(self, head):
        if not self.authorized():
            self.payload(401, b"Dashboard authentication required",
                         headers=[("WWW-Authenticate", 'Basic realm="PCP Dashboard V1"')], head=head)
            return
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
    password = password_from(tls["password_file"])
    sources = Sources(config["sources"], ROOT.parent)
    private = [ipaddress.ip_network(value) for value in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8")]
    listeners = config["listeners"]
    if not listeners:
        raise ValueError("Configure at least one HTTPS listener")
    with ExitStack() as stack:
        servers = []
        for listener in listeners:
            address = ipaddress.ip_address(listener["address"])
            if not any(address in network for network in private):
                raise ValueError("Bind HTTPS to an explicit private IPv4 or loopback address")
            networks = [ipaddress.ip_network(value) for value in listener["allow_clients"]]
            if not networks or not all(any(network.subnet_of(net) for net in private if network.version == net.version) for network in networks):
                raise ValueError("Specify private IPv4 client networks")
            server = stack.enter_context(DashboardServer((str(address), listener["port"]), networks, password, sources, context))
            servers.append(server)
            print(f"Dashboard V1 HTTPS listening on {address}:{listener['port']}", flush=True)
        for server in servers[1:]:
            threading.Thread(target=server.serve_forever, daemon=True).start()
        servers[0].serve_forever()


if __name__ == "__main__":
    main()

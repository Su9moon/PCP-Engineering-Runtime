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

from intake import Intake, IntakeError
from operator_grant import FORMAL_ACTIONS, MODEL_ACTIONS, load_service_settings
from sources import Sources, PROJECT

ROOT = Path(__file__).resolve().parent
STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/intake.js": ("intake.js", "text/javascript; charset=utf-8"),
    "/plan.js": ("plan.js", "text/javascript; charset=utf-8"),
    "/intake.css": ("intake.css", "text/css; charset=utf-8"),
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
        if path == "/api/intake" or path.startswith("/api/intake/"):
            self.intake_request(path, head=head)
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
        path = self.path.split("?", 1)[0]
        if path == "/api/intake" or path.startswith("/api/intake/"):
            self.intake_request(path, write=True)
        else:
            self.reject_write()

    def reject_write(self):
        self.payload(405, b"Unsupported write", headers=[("Allow", "GET, HEAD")])

    do_PUT = do_PATCH = do_DELETE = reject_write

    def intake_request(self, path, *, write=False, head=False):
        try:
            result = self.intake_operation(path, write)
            status = 200
        except IntakeError as exc:
            result, status = {"error": str(exc)}, exc.status
        except (OSError, ValueError, KeyError, TypeError):
            result, status = {"error": "本机 Intake 草稿当前不可读写。"}, 503
        body = json.dumps(result, ensure_ascii=False).encode("utf-8")
        self.payload(status, body, "application/json; charset=utf-8", head=head)

    def intake_operation(self, path, write):
        if not (intake := getattr(self.server, "intake", None)):
            raise IntakeError("此部署的 Intake 草稿存储未启用或无法打开。", 503)
        address, port = self.server.server_address
        origin = self.headers.get("Origin")
        hosts = {f"{address}:{port}"}
        if address == "127.0.0.1":
            hosts.add(f"localhost:{port}")
        if self.headers.get("Host") not in hosts or (origin and origin not in {f"https://{host}" for host in hosts}):
            raise IntakeError("请使用已配置的 Dashboard HTTPS 地址。", 403)
        ident = path.removeprefix("/api/intake/") if path != "/api/intake" else None
        if ident is not None:
            intake.path(ident)
        peer = ipaddress.IPv4Address(self.client_address[0])
        local_planner = address == "127.0.0.1" and peer.is_loopback
        trusted_lan = getattr(self.server, "lan_operator", False) and peer in self.server.clients
        grant = getattr(self.server, "operator_grant", None)
        actions = grant.get("actions") if isinstance(grant, dict) and grant.get("project") == PROJECT else None
        local_actions = set(actions) if (local_planner or trusted_lan) and isinstance(actions, list) and all(isinstance(a, str) for a in actions) else set()
        generalized = grant.get("engineering") if grant else None
        legacy = ident is not None and ident == (grant or {}).get("formalDraft")

        def apply_capabilities(result):
            caps = result["capabilities"]
            caps["dialogueAvailable"] = caps["plannerAvailable"] and "ai_reply" in local_actions
            caps["plannerAvailable"] &= "plan_generate" in local_actions
            formal = bool(intake.formal and ident and (generalized or legacy)) and not (generalized and legacy)
            caps["formalActions"] = sorted(FORMAL_ACTIONS & local_actions) if formal else []
            return result

        if not write:
            return apply_capabilities(intake.read(ident))
        if self.headers.get_content_type() != "application/json":
            raise IntakeError("请使用 JSON 提交草稿。", 415)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 65536:
                raise IntakeError("草稿请求超出大小限制。", 413)
            data = json.loads(self.rfile.read(length))
        except ValueError as exc:
            raise IntakeError("草稿请求格式错误。") from exc
        if not isinstance(data, dict):
            raise IntakeError("草稿请求格式错误。")
        action = data.get("action")
        if not isinstance(action, str):
            raise IntakeError("草稿操作名称无效。")
        authorized_origin = origin == f"https://{self.headers.get('Host')}"
        if legacy and (generalized or not (local_actions and authorized_origin)):
            raise IntakeError("此历史正式草稿保留为只读记录。", 403)
        if action in FORMAL_ACTIONS | MODEL_ACTIONS:
            if action not in local_actions or not authorized_origin:
                raise IntakeError("此操作需要已配置的本机服务授权和同源请求。", 403)
            if action in FORMAL_ACTIONS and (not ident or not (generalized or legacy)):
                raise IntakeError("此草稿不在服务端正式执行授权范围内。", 403)
            data["serviceAuthority"] = {"principal": "service-owner", "listener": str(address), "peer": str(peer)}
        return apply_capabilities(intake.update(ident, data))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    config, grant = load_service_settings(parser.parse_args().config)
    tls = config["tls"]
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(tls["cert"], tls["key"])
    source_settings = dict(config["sources"])
    formal_settings = (grant or {}).get("engineering") or (grant or {}).get("formal")
    if isinstance(formal_settings, dict) and formal_settings.get("eoRepo") == source_settings.get("eo"):
        source_settings["eo_ref"] = formal_settings.get("eoRef")
    sources = Sources(source_settings, ROOT.parent)
    intake = None
    if settings := config.get("intake"):
        try:
            intake = Intake(settings, ROOT.parent, config["sources"].get("eo"), grant, config["sources"].get("es"))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"Dashboard Intake unavailable: {type(exc).__name__}", flush=True)
    with ExitStack() as stack:
        local = stack.enter_context(DashboardServer(config["port"], sources, context))
        local.intake = intake
        local.operator_grant = grant
        if lan := config.get("lan"):
            try:
                private = stack.enter_context(DashboardServer(
                    config["port"], sources, context, address=lan["address"], clients=lan["clients"],
                ))
            except OSError as exc:
                print(f"Dashboard LAN listener unavailable at {lan['address']}: {exc.strerror}", flush=True)
            else:
                print(f"Dashboard V1 HTTPS listening on {private.server_address[0]}:{private.server_address[1]}", flush=True)
                private.intake = intake
                private.operator_grant = grant
                private.lan_operator = bool(grant and grant.get("trustedLan") is True)
                threading.Thread(target=private.serve_forever, daemon=True).start()
        print(f"Dashboard V1 HTTPS listening on {local.server_address[0]}:{local.server_address[1]}", flush=True)
        local.serve_forever()


if __name__ == "__main__":
    main()

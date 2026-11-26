"""Exercise the grant boundary for local, forwarded and LAN requests."""
import json
from email.message import Message
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase

from intake import IntakeError
from operator_grant import load_service_settings
from serve import Handler
from sources import PROJECT


class OperatorGrantTests(TestCase):
    def test_only_owner_private_regular_file_grants_access(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "dashboard.json"
            path.write_text(json.dumps({"operator": {"project": PROJECT}}))
            path.chmod(0o600)
            self.assertEqual(load_service_settings(path)[1], {"project": PROJECT})
            link = path.with_name("linked.json")
            link.symlink_to(path)
            self.assertIsNone(load_service_settings(link)[1])
            path.chmod(0o640)
            self.assertIsNone(load_service_settings(path)[1])

    def call(self, action, *, bind="127.0.0.1", peer="127.0.0.1", origin=None, host=None, grant=None, draft="draft"):
        def receive(ident, payload):
            return {"capabilities": {"plannerAvailable": True}, "received": (ident, payload)}

        store = SimpleNamespace(path=lambda ident: None, update=receive, formal=True)
        server = SimpleNamespace(server_address=(bind, 8787), intake=store, operator_grant=grant)
        headers = Message()
        headers["Host"] = host or f"{bind}:8787"
        if origin is not None:
            headers["Origin"] = origin
        headers["X-Forwarded-For"] = "127.0.0.1"
        headers["Content-Type"] = "application/json"
        data = json.dumps({"action": action, "operator": "admin", "project": PROJECT}).encode()
        headers["Content-Length"] = str(len(data))
        request = SimpleNamespace(server=server, client_address=(peer, 42000), headers=headers, rfile=BytesIO(data))
        return Handler.intake_operation(request, "/api/intake/" + draft, True)

    def test_lan_can_edit_and_cannot_call_model_or_dispatch(self):
        lan = {"bind": "192.168.5.4", "peer": "192.168.5.7", "origin": "https://192.168.5.4:8787",
               "grant": {"project": PROJECT, "actions": ["ai_reply", "formal_dispatch"], "formalDraft": "draft"}}
        self.assertEqual(self.call("field", draft="ordinary", **lan)["received"][0], "ordinary")
        with self.assertRaises(IntakeError) as failure:
            self.call("field", **lan)
        self.assertEqual(failure.exception.status, 403)
        for action in ("ai_reply", "formal_dispatch"):
            with self.assertRaises(IntakeError) as failure:
                self.call(action, **lan)
            self.assertEqual(failure.exception.status, 403)

    def test_exact_origin_private_grant_and_formal_draft_are_required(self):
        allowed = {"project": PROJECT, "actions": ["plan_generate", "formal_dispatch"], "formalDraft": "draft"}
        origin = "https://127.0.0.1:8787"
        for args in ({"origin": None}, {"origin": "null"}, {"origin": "https://localhost:8787"},
                     {"origin": origin, "host": "evil.invalid"}):
            with self.assertRaises(IntakeError):
                self.call("plan_generate", grant=allowed, **args)
        with self.assertRaises(IntakeError):
            self.call("plan_generate", origin=origin)
        with self.assertRaises(IntakeError):
            self.call("formal_dispatch", origin=origin, grant=allowed, draft="other")
        self.assertEqual(self.call("formal_dispatch", origin=origin, grant=allowed)["received"][0], "draft")

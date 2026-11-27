"""Focused V1 source mapping and read-boundary regression checks."""
import ipaddress
import json
import ssl
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from urllib import error

from serve import DashboardServer, Handler
from sources import Sources, archived_hub, eo_records, es_records, hub_state, provider


OBSERVED_AT = "2026-11-27T03:00:00+00:00"


class SourceTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def write(self, relative, value):
        file = self.root / relative
        file.parent.mkdir(exist_ok=True, parents=True)
        file.write_text(value, encoding="utf-8")
        return file

    def test_eo_scope_and_draft(self):
        subprocess.run(["git", "init", "-q", self.root], check=True)
        subprocess.run(["git", "-C", self.root, "-c", "user.name=Fixture", "-c",
                        "user.email=fixture@example.invalid", "commit", "-qm", "base", "--allow-empty"], check=True)
        self.write("jobs/JOB-1/job.yaml", "job_id: JOB-1\ntitle: Local task\n")
        self.write("workorders/WO-1/workorder.yaml", "workorder_id: WO-1\njob_id: JOB-1\n"
                   "input_refs: ['Su9moon/PCP-Engineering-Runtime:README.md']\nstatus: READY\n")
        self.write("workorders/WO-2/workorder.yaml", "workorder_id: WO-2\ninput_refs: ['other/project:README.md']\n")
        self.write("results/RES-1/result.yaml", "result_id: RES-1\nworkorder_id: WO-1\nstatus: DRAFT\n")
        result = eo_records(self.root)
        self.assertEqual([(t["workorder_id"], t["title"], t["gitClean"]) for t in result["tasks"]], [("WO-1", "Local task", False)])
        self.assertEqual([row["status"] for row in result["results"]], ["DRAFT"])

    def test_es_associates_metadata_without_rewriting_provider_ref(self):
        file = self.root / "es.sqlite3"
        with sqlite3.connect(file) as conn:
            conn.executescript("""
                CREATE TABLE executions (execution_id, request_id, state, updated_at);
                CREATE TABLE requests (request_id, body_json);
                CREATE TABLE attempts (execution_id,attempt_id,invocation_id,state,runtime_ref,started_at,ended_at,created_at);
                CREATE TABLE reviews (execution_id,attempt_id,decision,resulting_state,created_at);
                INSERT INTO executions VALUES ('EXE-1','EXR-1','DONE','2026-11-25');
                INSERT INTO requests VALUES ('EXR-1','{"metadata":{"workorder_id":"WO-1","job_id":"JOB-1"}}');
                INSERT INTO attempts VALUES ('EXE-1','ATT-1','INV-1','COMPLETED','provider-placeholder',NULL,NULL,'2026-11-25');
            """)
        item = es_records(file)["executions"][0]
        self.assertEqual((item["workorder_id"], item["job_id"], item["state"]), ("WO-1", "JOB-1", "DONE"))
        self.assertEqual(item["attempts"][0]["runtime_ref"], "provider-placeholder")

    def make_hub(self):
        file = self.root / "hub.db"
        with sqlite3.connect(file) as conn:
            conn.executescript("""
                CREATE TABLE runs (id,rule,agent,state,attempts,session,created_at,claimed_at,finished_at,summary,error);
                CREATE TABLE events (id,type,source,subject,received_at);
                CREATE TABLE run_events (run_id,event_id);
                CREATE TABLE seen (kind,name,seen_at);
                INSERT INTO runs VALUES (21,'check','codex','done',1,NULL,'2026-11-25',NULL,'2026-11-25',NULL,NULL);
                INSERT INTO events VALUES (22,'event.complete','fixture','Task','2026-11-25');
                INSERT INTO run_events VALUES (21,22);
                INSERT INTO seen VALUES ('worker','worker-test','2026-11-25');
            """)
        return file

    def test_archive_keeps_event_and_run_ids_distinct(self):
        runs, workers = archived_hub(self.make_hub(), {(21, 21): {"files": ["wrong"]}, (21, 22): {"files": ["correct"]}})
        self.assertEqual((runs[0]["id"], runs[0]["events"][0]["id"]), (21, 22))
        self.assertEqual(runs[0]["delivery"]["files"], ["correct"])
        self.assertEqual(runs[0]["mode"], "history")
        self.assertNotIn("online", workers[0])

    @patch("sources.now", return_value=OBSERVED_AT)
    def test_live_worker_uses_hub_reported_assignment_and_presence(self, _clock):
        live = {"now": "2026-11-27T03:00:00.500Z", "runs": [{"id": 21, "agent": "codex", "state": "claimed"}],
                "agents": [{"id": "codex", "worker": "worker-test", "online": True, "use": "codex",
                            "seenAt": "2026-11-27T02:57:00.500Z"}]}
        config = self.write("config.json", "{}")
        with patch("sources.hub_state", return_value=live):
            hub = provider("test", config, self.make_hub())
        self.assertEqual([item["id"] for item in hub["runs"][0]["events"]], [22])
        self.assertEqual(hub["runs"][0]["worker"], "worker-test")
        self.assertEqual(hub["workers"][0]["activeRuns"], [21])
        self.assertEqual(hub["workers"][0]["availability"], "active")
        self.assertEqual(hub["workers"][0]["observedAt"], hub["health"]["observedAt"])

    @patch("sources.now", return_value=OBSERVED_AT)
    def test_hub_worker_presence_is_independent_of_agent_order(self, _clock):
        config = self.write("config.json", "{}")
        online = {"id": "a", "worker": "shared", "online": True, "seenAt": "2026-11-27T02:59:00Z"}
        offline = {"id": "b", "worker": "shared", "online": False, "seenAt": "2026-11-27T02:30:00Z"}
        for agents in ([online, offline], [offline, online]):
            with self.subTest(order=[agent["id"] for agent in agents]), patch("sources.hub_state", return_value={
                "now": "2026-11-27T03:00:00Z", "agents": agents, "runs": [],
            }):
                worker, = provider("test", config)["workers"]
                self.assertEqual(worker["availability"], "active")
                self.assertEqual(worker["seenAt"], "2026-11-27T02:59:00+00:00")

    @patch("sources.now", return_value=OBSERVED_AT)
    def test_reachable_hub_does_not_treat_expired_or_missing_evidence_as_active(self, _clock):
        config = self.write("config.json", "{}")
        expired = "2026-11-27T02:56:59.999Z"
        live = {"now": "2026-11-27T03:00:00Z", "runs": [{"id": 21, "agent": "late", "state": "claimed"}],
                "agents": [{"id": "late", "worker": "stale", "online": True, "seenAt": expired},
                           {"id": "off", "worker": "offline", "online": False, "seenAt": expired},
                           {"id": "no-heartbeat", "worker": "missing-time", "online": True},
                           {"id": "no-flag", "worker": "missing-flag", "seenAt": "2026-11-27T02:59:00Z"}]}
        with patch("sources.hub_state", return_value=live):
            hub = provider("test", config, self.make_hub())
        workers = {worker["name"]: worker for worker in hub["workers"]}
        self.assertEqual(hub["health"]["availability"], "active")
        self.assertEqual({name: worker["availability"] for name, worker in workers.items()}, {
            "stale": "unavailable", "offline": "unavailable", "missing-time": "unknown",
            "missing-flag": "unknown", "worker-test": "unknown",
        })
        self.assertNotIn("activeRuns", workers["stale"])
        self.assertEqual(workers["worker-test"]["seenAt"], "2026-11-25")
        self.assertEqual(hub["runs"][0]["state"], "claimed")

    @patch("sources.now", return_value=OBSERVED_AT)
    def test_unverifiable_hub_snapshot_cannot_report_current_worker_presence(self, _clock):
        config = self.write("config.json", "{}")
        for source_at in ("2020-01-01T00:01:00+00:00", None, "invalid", "2026-11-27T03:01:00Z"):
            snapshot = {"now": source_at, "runs": [{"id": 21, "agent": "a", "state": "claimed"}],
                        "agents": [{"id": "a", "worker": "worker-test", "online": True,
                                    "seenAt": "2020-01-01T00:00:59+00:00"},
                                   {"id": "b", "worker": "offline-test", "online": False}]}
            with self.subTest(source_at=source_at), patch("sources.hub_state", return_value=snapshot):
                hub = provider("test", config)
                self.assertEqual(hub["health"]["availability"], "unknown")
                self.assertEqual(hub["health"]["sourceAt"], source_at)
                self.assertEqual(hub["health"]["observedAt"], OBSERVED_AT)
                worker, offline = hub["workers"]
                self.assertEqual(worker["availability"], "unknown")
                self.assertEqual(worker["seenAt"], "2020-01-01T00:00:59+00:00")
                self.assertEqual(offline["availability"], "unknown")
                for record in (worker, offline):
                    self.assertNotIn("activeRuns", record)
                    self.assertNotIn("online", record)
                run, = hub["runs"]
                self.assertEqual((run["id"], run["state"], run["mode"]), (21, "claimed", "snapshot"))

    @patch("sources.now", return_value=OBSERVED_AT)
    def test_state_read_returns_unknown_for_unstamped_hub_run_with_null_events(self, _clock):
        config = self.write("config.json", "{}")
        sources = Sources({"hubs": [{"name": "test", "config_file": config}]}, self.root)
        client = Handler.__new__(Handler)
        client.path = "/api/state"
        client.server = Mock(sources=sources)
        client.payload = Mock()
        with patch.object(sources.ruflo, "refresh", return_value=sources.ruflo.snapshot), \
                patch("sources.hub_state", return_value={"runs": [{"id": 1, "events": None}], "agents": []}):
            client.do_GET()
        self.assertEqual(client.payload.call_args.args[0], 200)
        hub, = json.loads(client.payload.call_args.args[1])["hubs"]
        self.assertEqual(hub["health"]["availability"], "unknown")
        self.assertEqual(hub["health"]["observedAt"], OBSERVED_AT)
        self.assertIsNone(hub["health"]["sourceAt"])
        run, = hub["runs"]
        self.assertEqual((run["id"], run["mode"], run["events"]), (1, "snapshot", []))

    @patch("sources.now", return_value=OBSERVED_AT)
    def test_heartbeat_must_still_be_recent_when_dashboard_reads_hub(self, _clock):
        config = self.write("config.json", "{}")
        snapshot = {"now": "2026-11-27T02:58:00Z", "runs": [],
                    "agents": [{"id": "a", "worker": "worker-test", "online": True,
                                "seenAt": "2026-11-27T02:56:00Z"}]}
        with patch("sources.hub_state", return_value=snapshot):
            hub = provider("test", config)
        self.assertEqual(hub["health"]["availability"], "active")
        self.assertEqual(hub["workers"][0]["availability"], "unavailable")

    def test_disconnected_hub_still_returns_history(self):
        config = self.write("config.json", "{}")
        with patch("sources.hub_state", side_effect=error.URLError("offline")):
            hub = provider("test", config, self.make_hub())
        self.assertEqual(hub["health"]["status"], "disconnected")
        self.assertEqual(hub["health"]["availability"], "unavailable")
        self.assertEqual(hub["workers"][0]["availability"], "unknown")
        self.assertEqual(hub["workers"][0]["seenAt"], "2026-11-25")
        self.assertEqual(hub["runs"][0]["mode"], "history")

    @patch("sources.now", return_value=OBSERVED_AT)
    def test_state_reads_observe_changes_without_writing_run_or_event_records(self, _clock):
        config = self.write("config.json", "{}")
        projection = self.make_hub()
        before = projection.read_bytes()
        sources = Sources({"hubs": [{"name": "test", "config_file": config, "projection": projection}]}, self.root)
        client = Handler.__new__(Handler)
        client.path = "/api/state"
        client.server = Mock(sources=sources)
        client.payload = Mock()
        polls = [
            {"now": "2026-11-27T03:00:00Z", "runs": [{"id": 21, "agent": "a", "state": "claimed"}],
             "agents": [{"id": "a", "worker": "worker-test", "online": online, "seenAt": "2026-11-27T02:59:00Z"}]}
            for online in (True, False)
        ]
        polls.append({"now": "2020-01-01T00:01:00Z", "runs": [{"id": 21, "agent": "a", "state": "claimed"}],
                      "agents": [{"id": "a", "worker": "worker-test", "online": True,
                                  "seenAt": "2020-01-01T00:00:59Z"}]})
        with patch.object(sources.ruflo, "refresh", return_value=sources.ruflo.snapshot), \
                patch("sources.hub_state", side_effect=polls) as read_hub:
            for expected, run_state in (("active", "claimed"), ("unavailable", "claimed"), ("unknown", "done")):
                client.do_GET()
                status, body, media_type = client.payload.call_args.args
                self.assertEqual((status, media_type), (200, "application/json; charset=utf-8"))
                hub, = json.loads(body)["hubs"]
                self.assertEqual(hub["workers"][0]["availability"], expected)
                self.assertEqual([(run["id"], [event["id"] for event in run["events"]]) for run in hub["runs"]],
                                 [(21, [22])])
                self.assertEqual(hub["runs"][0]["state"], run_state)
        self.assertEqual(read_hub.call_count, 3)
        self.assertEqual(projection.read_bytes(), before)

    def test_source_owner_credential_requires_https_away_from_loopback(self):
        for url in ("http://192.168.5.10:3350", "http://user:password@127.0.0.1:3350", "http://127.0.0.1:3350?token=x"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                hub_state({"url": url, "owner": "fixture-owner"})


class AccessTests(unittest.TestCase):
    def test_local_and_trusted_lan_use_tls_wrapped_listeners(self):
        for address, clients in (("127.0.0.1", "127.0.0.0/8"), ("192.168.5.6", "192.168.5.0/24")):
            with self.subTest(address=address), patch("serve.ThreadingHTTPServer.__init__", autospec=True) as init:
                socket = Mock()
                init.side_effect = lambda server, *args: setattr(server, "socket", socket)
                context = Mock(spec=ssl.SSLContext)
                server = DashboardServer(8787, None, context, address=address, clients=clients)
                init.assert_called_once_with(server, (address, 8787), Handler)
                context.wrap_socket.assert_called_once_with(socket, server_side=True, do_handshake_on_connect=False)
                self.assertTrue(server.verify_request(None, (address, 5000)))

    def test_server_binds_to_loopback(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        with DashboardServer(0, None, context) as server:
            self.assertEqual(server.server_address[0], "127.0.0.1")

    def test_listener_rejects_broad_or_mismatched_networks(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        for address, clients in (("0.0.0.0", "0.0.0.0/0"), ("127.0.0.1", "192.168.5.0/24")):
            with self.subTest(address=address, clients=clients), self.assertRaises(ValueError):
                DashboardServer(0, None, context, address=address, clients=clients)

    def test_lan_listener_filters_client_subnet(self):
        class Listener:
            clients = ipaddress.IPv4Network("192.168.5.0/24")

        self.assertTrue(DashboardServer.verify_request(Listener(), None, ("192.168.5.10", 1234)))
        self.assertFalse(DashboardServer.verify_request(Listener(), None, ("192.168.6.10", 1234)))

    def test_dashboard_can_be_read_without_login(self):
        class Client:
            path = "/"

            def payload(self, status, body, media_type, **extras):
                self.response = status, body, media_type

        client = Client()
        Handler.read(client, head=False)
        status, body, media_type = client.response
        self.assertEqual(status, 200)
        self.assertIn(b'id="view"', body)
        self.assertTrue(media_type.startswith("text/html"))

    def test_untrusted_request_has_no_write_method(self):
        class Client:
            path = "/api/state"
            reject_write = Handler.reject_write

            def payload(self, status, body, **extras):
                self.status = status
        client = Client()
        for handler in (Handler.do_POST, Handler.do_PUT, Handler.do_PATCH, Handler.do_DELETE):
            handler(client)
            self.assertEqual(client.status, 405)


if __name__ == "__main__":
    unittest.main()

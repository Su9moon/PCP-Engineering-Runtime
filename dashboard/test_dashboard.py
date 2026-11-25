"""Focused V1 source mapping and read-boundary regression checks."""
import ssl
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib import error

from serve import DashboardServer, Handler
from sources import archived_hub, eo_records, es_records, hub_state, provider


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

    def test_live_worker_uses_hub_reported_assignment_and_presence(self):
        live = {"now": "2026-11-25", "runs": [{"id": 21, "agent": "codex", "state": "claimed"}],
                "agents": [{"id": "codex", "worker": "worker-test", "online": True, "use": "codex",
                            "seenAt": "2026-11-25"}]}
        config = self.write("config.json", "{}")
        with patch("sources.hub_state", return_value=live):
            hub = provider("test", config, self.make_hub())
        self.assertEqual([item["id"] for item in hub["runs"][0]["events"]], [22])
        self.assertEqual(hub["runs"][0]["worker"], "worker-test")
        self.assertEqual(hub["workers"][0]["activeRuns"], [21])
        self.assertIs(hub["workers"][0]["online"], True)

    def test_disconnected_hub_still_returns_history(self):
        config = self.write("config.json", "{}")
        with patch("sources.hub_state", side_effect=error.URLError("offline")):
            hub = provider("test", config, self.make_hub())
        self.assertEqual(hub["health"]["status"], "disconnected")
        self.assertEqual(hub["runs"][0]["mode"], "history")

    def test_source_owner_credential_requires_https_away_from_loopback(self):
        for url in ("http://192.168.5.10:3350", "http://user:password@127.0.0.1:3350", "http://127.0.0.1:3350?token=x"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                hub_state({"url": url, "owner": "fixture-owner"})


class AccessTests(unittest.TestCase):
    def test_server_binds_to_loopback(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        with DashboardServer(0, None, context) as server:
            self.assertEqual(server.server_address[0], "127.0.0.1")

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
            def payload(self, status, body, **extras):
                self.status = status
        client = Client()
        for handler in (Handler.do_POST, Handler.do_PUT, Handler.do_PATCH, Handler.do_DELETE):
            handler(client)
            self.assertEqual(client.status, 405)


if __name__ == "__main__":
    unittest.main()

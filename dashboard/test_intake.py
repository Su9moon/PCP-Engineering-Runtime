"""Focused tests for durable, authority-aware conversational intake."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engineering import Engineering
from intake import Intake, IntakeError
from intake_context import BASELINES, PCP, PLAN_WORKORDER, WORKORDER, ProjectContext
from sources import PROJECT


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                          capture_output=True).stdout.strip()


def repo(root, files):
    root.mkdir()
    git(root, "init", "-q")
    for path, content in files.items():
        file = root / path
        file.parent.mkdir(exist_ok=True, parents=True)
        file.write_text(content)
    git(root, "add", ".")
    git(root, "-c", "user.email=fixture@example.invalid", "-c", "user.name=Fixture",
        "commit", "-qm", "fixture")
    return git(root, "rev-parse", "HEAD")


class IntakeTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.runtime = self.root / "runtime"
        self.pcp = self.root / "pcp"
        self.eo = self.root / "eo"
        (self.eo / "templates").mkdir(parents=True)
        (self.eo / "templates/job.template.yaml").write_text("job_id: JOB-YYYYMMDD-NNN\nversion: 1\n")
        (self.eo / "templates/workorder.template.yaml").write_text("workorder_id: WO-YYYYMMDD-NNN\nversion: 1\n")
        self.pcp_ref = repo(self.pcp, {
            **{path: "# Baseline\nApproved guidance" for path, _ in BASELINES},
            "assets/validated/v.md": "# Validated\nquality-check",
            "assets/candidates/c.md": "# Candidate\nquality-check candidate-only",
            "assets/inbox/sources/i.md": "# Inbox\nquality-check inbox-only",
        })
        self.project_ref = repo(self.runtime, {
            "AGENTS.md": "# Rules\nRuntime work rules",
            "README.md": "# Runtime\nProject context",
            "PROJECT_STATUS.md": "# Status\nVerified project facts",
            WORKORDER: "# Workorder\nActive",
            PLAN_WORKORDER: "# Planning workorder\nActive",
        })
        self.settings = {"directory": str(self.root / "private"), "pcp_repo": str(self.pcp)}
        self.intake = self.open_store()

    def open_store(self):
        store = Intake(self.settings, self.runtime, self.eo)
        store.context = ProjectContext(self.runtime, self.pcp, pcp_commit=self.pcp_ref)
        return store

    def create(self, text="Improve draft review"):
        return self.intake.update(None, {"action": "message", "text": text})["draft"]

    def change(self, draft, action, **fields):
        return self.intake.update(draft["id"], {"version": draft["version"], "action": action, **fields})["draft"]

    def test_manual_dialogue_stores_user_turns_and_resumes(self):
        first = self.create()
        second = self.change(first, "message", text="Keep the existing runtime.")
        result = self.open_store().read(first["id"])
        self.assertEqual(result["draft"], second)
        self.assertEqual([m["role"] for m in second["messages"]], ["user", "user"])
        self.assertIsNone(second["project"])
        self.assertIn("未配置", result["capabilities"]["llmGap"])
        self.assertEqual(self.open_store().read(None)["drafts"][0]["id"], first["id"])

    def test_report_reads_eo_delivery_paths_bound_to_each_attempt(self):
        records = {"result": "results/RESULT-20261127-001/result.yaml",
                   "evidence": "evidence/EVD-20261127-001/evidence.yaml",
                   "review": "reviews/REVIEW-20261127-001/review.yaml"}
        eo = self.root / "formal-eo"
        base = repo(eo, {"README.md": "fixture"})
        for path in records.values():
            file = eo / path
            file.parent.mkdir(parents=True)
            file.write_text("fixture\n", encoding="utf-8")
        git(eo, "add", ".")
        git(eo, "-c", "user.email=fixture@example.invalid", "-c", "user.name=Fixture",
            "commit", "-qm", "Fixture delivery", "-m", "Result-Attempt: ATT-1")
        delivery = git(eo, "rev-parse", "HEAD")
        draft = self.create("交付报告")
        runs = {"t1": {"attempt": "ATT-1", "state": "DONE", "eoDelivery": delivery},
                "t2": {"attempt": "ATT-10", "state": "REVIEW_READY", "eoDelivery": delivery}}
        draft["formal"] = {"kind": "engineering", "runs": runs}
        self.intake.save(draft)
        self.intake.formal = Engineering({"eoRepo": eo, "eoBase": base, "eoRef": "refs/heads/fixture"},
                                        self.root / "unused", None, self.runtime, None)

        view = self.intake.read(draft["id"])["draft"]["formal"]["runs"]
        self.assertEqual(view["t1"]["eoRecords"], records)
        self.assertEqual(view["t2"]["eoRecords"], {})
        self.assertEqual(self.intake.load(draft["id"])["formal"]["runs"], runs)
        blob = git(eo, "hash-object", str(eo / next(iter(records.values()))))
        self.assertEqual(self.intake.formal.delivery_records(blob, "ATT-1"), {})

        (eo / next(iter(records.values()))).write_text("updated\n", encoding="utf-8")
        git(eo, "add", ".")
        git(eo, "-c", "user.email=fixture@example.invalid", "-c", "user.name=Fixture",
            "commit", "-qm", "Updated delivery", "-m", "Result-Attempt: ATT-1")
        updated = git(eo, "rev-parse", "HEAD")
        self.assertEqual(self.intake.formal.delivery_records(updated, "ATT-1"), {})

    def test_report_finds_eo_records_added_by_merge_commit(self):
        records = {"result": "results/RESULT-20261127-002/result.yaml",
                   "evidence": "evidence/EVD-20261127-002/evidence.yaml",
                   "review": "reviews/REVIEW-20261127-002/review.yaml"}
        eo = self.root / "merge-eo"
        base = repo(eo, {"README.md": "base\n"})
        git(eo, "checkout", "-qb", "left")
        (eo / "left.txt").write_text("left\n", encoding="utf-8")
        git(eo, "add", "left.txt")
        git(eo, "-c", "user.email=fixture@example.invalid", "-c", "user.name=Fixture",
            "commit", "-qm", "left")
        git(eo, "checkout", "-qb", "right", base)
        for path in records.values():
            file = eo / path
            file.parent.mkdir(parents=True)
            file.write_text("fixture\n", encoding="utf-8")
        git(eo, "add", "results", "evidence", "reviews")
        git(eo, "-c", "user.email=fixture@example.invalid", "-c", "user.name=Fixture",
            "commit", "-qm", "Create delivery records")
        git(eo, "checkout", "left")
        git(eo, "-c", "user.email=fixture@example.invalid", "-c", "user.name=Fixture",
            "merge", "--no-ff", "-m", "Merge delivery\n\nResult-Attempt: ATT-1", "right")
        delivery = git(eo, "rev-parse", "HEAD")
        self.intake.formal = Engineering({"eoRepo": eo, "eoBase": base, "eoRef": "refs/heads/fixture"},
                                         self.root / "unused", None, self.runtime, None)

        self.assertEqual(self.intake.formal.delivery_records(delivery, "ATT-1"), records)

    def test_execution_report_fields_follow_the_current_invocation(self):
        engineering = Engineering({"eoRepo": self.eo, "eoBase": "a" * 40, "eoRef": "refs/heads/fixture"},
                                  self.root / "unused", None, self.runtime, None)
        row = {"execution": "EXE-1", "invocation": "AINV-1", "provider": "done", "event": 2, "run": 3,
               "providerSession": "old-thread", "providerRule": "old-rule"}
        binding = {"authorizedAt": "fixture", "order": ["t1"], "tasks": [{"id": "t1", "depends": []}], "runs": {"t1": row}}
        execution = {"request": {"request_id": "REQ-1"}, "state": "RUNNING",
                     "attempts": [{"attempt_id": "ATT-2", "invocation_id": "AINV-2"}]}
        provider = {"event_id": 4, "run_id": 5, "state": "claimed", "session": "thread-2",
                    "rule": "fixture"}
        with patch.object(engineering, "kernel") as kernel, \
                patch.object(engineering, "provider_run", side_effect=[None, provider]) as provider_run:
            kernel.return_value.get_execution.return_value = execution
            engineering.advance(binding)
            self.assertEqual(row, {"request": "REQ-1", "execution": "EXE-1", "attempt": "ATT-2",
                                   "invocation": "AINV-2", "state": "RUNNING"})
            engineering.advance(binding)
            self.assertEqual(provider_run.call_args.args, ("AINV-2",))
            self.assertEqual([row[key] for key in ("event", "run", "provider", "providerSession", "providerRule")],
                             [4, 5, "claimed", "thread-2", "fixture"])
            kernel.return_value.authorize_attempt.assert_not_called()

    def test_only_explicit_edits_confirm_and_retain_other_fields(self):
        draft = self.create()
        draft = self.change(draft, "field", field="scope", value="Existing navigation", provenance="USER_CONFIRMED")
        draft = self.change(draft, "field", field="questions", value="MEC verification", provenance="UNRESOLVED")
        draft = self.change(draft, "field", field="scope", value="Dashboard only", provenance="USER_CONFIRMED")
        self.assertEqual(draft["dossier"]["scope"], {"value": "Dashboard only", "provenance": "USER_CONFIRMED"})
        self.assertEqual(draft["dossier"]["questions"]["value"], "MEC verification")
        self.assertEqual(draft["dossier"]["goal"]["provenance"], "UNRESOLVED")
        with self.assertRaises(IntakeError):
            self.change(draft, "field", field="goal", value="Unknown", provenance="AI_INFERRED")

    def test_retrieval_orders_and_classifies_actual_git_sources(self):
        draft = self.create()
        draft = self.change(draft, "project", project=PROJECT)
        draft = self.change(draft, "retrieve", terms="quality-check")
        materials = draft["context"]["items"]
        maturities = [item["maturity"] for item in materials]
        self.assertIn("APPROVED", maturities)
        self.assertTrue(maturities.index("VALIDATED") < maturities.index("CANDIDATE"))
        self.assertNotIn("INBOX", maturities)
        generated = self.change(draft, "generate")["packages"][0]["documents"]
        self.assertIn("assets/candidates/c.md", generated[0]["text"])
        self.assertNotIn("assets/candidates/c.md", generated[-1]["text"])
        candidate = next(item for item in materials if item["maturity"] == "CANDIDATE")
        self.assertEqual((candidate["repository"], candidate["path"], candidate["commit"], candidate["authoritative"]),
                         (PCP, "assets/candidates/c.md", self.pcp_ref, False))
        runtime = next(item for item in materials if item["path"] == "AGENTS.md")
        self.assertEqual(runtime["commit"], self.project_ref)
        with patch("intake_context.git_source", side_effect=AssertionError("cached sources were reread")):
            current = self.intake.read(draft["id"])["draft"]
            resumed = self.change(current, "retrieve", terms="quality-check")
        self.assertEqual(resumed["context"], draft["context"])

    def test_inbox_fallback_and_project_isolation(self):
        a = self.change(self.create(), "project", project=PROJECT)
        a = self.change(a, "retrieve", terms="inbox-only")
        self.assertFalse(next(item for item in a["context"]["items"] if item["maturity"] == "INBOX")["authoritative"])
        b = self.create("Totally different intake")
        self.assertIsNone(b["project"])
        self.assertEqual(b["context"]["items"], [])
        with self.assertRaises(IntakeError):
            self.change(b, "retrieve", terms="inbox-only")

    def test_missing_pcp_source_only_affects_retrieval(self):
        self.intake.context = ProjectContext(self.runtime, self.root / "missing", pcp_commit=self.pcp_ref)
        draft = self.change(self.create(), "project", project=PROJECT)
        self.assertTrue(any(PCP in gap for gap in draft["context"]["unavailable"]))
        self.assertTrue(any(item["repository"] == PROJECT for item in draft["context"]["items"]))
        self.assertEqual(len(self.change(draft, "generate")["packages"]), 1)

    def test_document_revisions_confirmation_and_no_eo_writes(self):
        before = {file.relative_to(self.eo): file.read_bytes() for file in self.eo.rglob("*.yaml")}
        draft = self.create()
        with self.assertRaises(IntakeError):
            self.change(draft, "confirm", revision=1)
        draft = self.change(draft, "generate")
        first = draft["packages"][0]
        self.assertIn("待确认", first["documents"][0]["text"])
        self.assertIn("status: DRAFT", first["documents"][2]["text"])
        draft = self.change(draft, "confirm", revision=1)
        draft = self.change(draft, "field", field="acceptance", value="Observably successful", provenance="USER_CONFIRMED")
        with self.assertRaises(IntakeError):
            self.change(draft, "confirm", revision=1)
        draft = self.change(draft, "generate")
        self.assertEqual(draft["packages"][0]["documents"], first["documents"])
        self.assertIsNotNone(draft["packages"][0]["confirmedAt"])
        self.assertEqual(draft["packages"][1]["revision"], 2)
        self.assertIn("Observably successful", draft["packages"][1]["documents"][2]["text"])
        with self.assertRaises(IntakeError):
            self.change(draft, "create_eo")
        self.assertEqual(before, {file.relative_to(self.eo): file.read_bytes() for file in self.eo.rglob("*.yaml")})
        self.assertEqual(self.open_store().read(draft["id"])["draft"], draft)

    def test_stale_writes_cannot_overwrite_saved_state(self):
        original = self.create()
        updated = self.change(original, "message", text="Another tab saves first")
        with self.assertRaises(IntakeError) as error:
            self.change(original, "message", text="Stale write")
        self.assertEqual(error.exception.status, 409)
        self.assertEqual(self.open_store().read(original["id"])["draft"], updated)

    def test_secrets_and_paths_are_rejected(self):
        with self.assertRaises(IntakeError):
            self.create("api key: should-not-persist")
        draft = self.create()
        self.assertEqual(os.stat(self.intake.path(draft["id"])).st_mode & 0o077, 0)
        with self.assertRaises(IntakeError):
            self.intake.read("../dashboard.json")
        with self.assertRaises(IntakeError):
            self.change(draft, "message", text="Bearer abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(self.intake.read(draft["id"])["draft"], draft)


if __name__ == "__main__":
    unittest.main()

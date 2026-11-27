"""Regressions for rework after a delayed or failed Worker delivery."""
from contextlib import nullcontext
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import Mock, patch

from engineering import Engineering
from engineering_worker import WorkerError, checkout, rework_context
from formal import FormalError
from test_intake import git, repo


def invocation(n):
    return f"AINV-{n:032x}"


class EngineeringRecoveryTests(unittest.TestCase):
    def test_worker_reads_last_sealed_result_across_failed_attempt_and_stale_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            base = repo(project, {"dashboard/report.js": "original\n"})
            workspaces = root / "workspaces"
            workspaces.mkdir()
            settings = {"workspaceRoot": workspaces, "projectRoot": project}
            contract = {"base_commit": base, "plan_sha256": "sealed-plan"}
            prior = checkout(settings, invocation(1), contract, None)
            (prior / "dashboard/report.js").write_text("keep this fix\n")
            git(prior, "add", ".")
            git(prior, "commit", "-qm", "Repair")
            commit = git(prior, "rev-parse", "HEAD")

            database = root / "es.sqlite"
            with sqlite3.connect(database) as db:
                db.executescript("""
                    CREATE TABLE attempts (attempt_id, execution_id, invocation_id, created_at, state, failure_json);
                    CREATE TABLE results (attempt_id, result_json);
                """)
                db.executemany("INSERT INTO attempts VALUES (?,?,?,?,?,?)", [
                    ("a1", "EXE-1", invocation(1), 1, "COMPLETED", None),
                    ("a2", "EXE-1", invocation(2), 2, "FAILED", json.dumps({"reason": "保留已有修复"})),
                    ("a3", "EXE-1", invocation(3), 3, "CLAIMED", None),
                    ("foreign", "EXE-2", invocation(4), 2, "COMPLETED", None),
                ])
                db.executemany("INSERT INTO results VALUES (?,?)", [
                    ("a1", json.dumps({"payload": {"commit": commit, "base": base}})),
                    ("foreign", json.dumps({"payload": {"commit": "0" * 40, "base": base}})),
                ])
            binding = {
                "kind": "engineering", "workorder": "WO-1", "planSha256": "sealed-plan", "authorizedAt": "confirmed",
                "runs": {"t2": {"execution": "EXE-1", "invocation": invocation(1),
                                "decisions": {"review": {"text": "继续修正报告"}}}},
            }
            (root / ("a" * 32 + ".json")).write_text(json.dumps({"formal": binding}))
            recovery = {"requestId": "REQ-1", "afterInvocation": invocation(2),
                        "priorDeliveryInvocation": invocation(1), "preserveTree": True,
                        "supervisorReceipt": "approval", "instruction": "仅复验"}
            config = {"sources": {"es": str(database)}, "intake": {"directory": str(root)},
                      "operator": {"engineering": {"approvedRecovery": recovery}}}
            request = {"request_id": "REQ-1", "constraints": contract,
                       "metadata": {"workorder_id": "WO-1", "task": {"id": "t2"}}}

            context, delivery = rework_context(config, request, "EXE-1", invocation(3))
            self.assertEqual(delivery, {"invocation": invocation(1), "commit": commit, "preserveTree": True})
            self.assertEqual(context["独立复核和 QA"], {"review": "继续修正报告"})
            self.assertEqual(context["前一次交付失败"], "保留已有修复")
            self.assertEqual(context["Supervisor 本次确认的返工范围"], "仅复验")
            candidate = checkout(settings, invocation(3), contract, delivery)
            self.assertEqual(git(candidate, "rev-parse", "HEAD"), commit)
            self.assertEqual(git(candidate, "status", "--porcelain"), "")
            self.assertEqual(checkout(settings, invocation(3), contract, delivery), candidate)
            (candidate / "dashboard/report.js").write_text("preserve unfinished edits\n")
            with self.assertRaises(WorkerError):
                checkout(settings, invocation(3), contract, delivery)

            recovery["priorDeliveryInvocation"] = invocation(2)
            with self.assertRaises(WorkerError):
                rework_context(config, request, "EXE-1", invocation(3))

    def test_review_uses_full_authorized_diff_when_prior_code_did_not_pass(self):
        settings = {"eoRepo": ".", "eoBase": "a" * 40, "eoRef": "refs/heads/fixture",
                    "workspaceRoot": ".", "budget": {"reviewChars": 1}}
        adapter = Engineering(settings, ".", None, ".", None)
        result = {"base": "a" * 40, "commit": "c" * 40}
        for passed in (False, True):
            with self.subTest(passed=passed), patch("engineering.git", return_value="different") as git_diff:
                prior = {"commit": "b" * 40, "reviewPassed": passed}
                with self.assertRaisesRegex(FormalError, "可审核"):
                    adapter.judge({}, {}, invocation(3), result, {}, prior)
                expected = prior["commit"] if passed else result["base"]
                self.assertEqual(git_diff.call_args.args[3], expected)

    def test_recovery_uses_only_explicit_attempt_budget_and_matching_override(self):
        for state in ("RECOVERABLE", "REVISION_REQUESTED"):
            for budget, matches, allowed in ((None, False, True), (3, False, False), (3, True, True)):
                with self.subTest(state=state, budget=budget, matches=matches):
                    settings = {"eoRepo": ".", "eoBase": "a" * 40, "eoRef": "refs/heads/fixture",
                                "worker": "fixture", "budget": {} if budget is None else {"attempts": budget},
                                "approvedRecovery": {"requestId": "REQ-1", "supervisorReceipt": "approval",
                                                     "afterInvocation": invocation(5 if matches else 4)}}
                    adapter = Engineering(settings, ".", None, ".", None)
                    adapter.verify_routing = Mock()
                    adapter.canonical_workorder = Mock()
                    adapter.provider_run = Mock(return_value=None)
                    adapter.emit = Mock()
                    kernel = Mock()
                    latest = {"invocation_id": invocation(6), "attempt_id": "a6", "state": "CLAIMED",
                              "authority": {"status": "CURRENT"}}
                    kernel.authorize_attempt.return_value = latest
                    kernel.get_execution.return_value = {"execution_id": "EXE-1", "attempts": [latest], "state": "QUEUED"}
                    kernel.store.transaction.return_value = nullcontext()
                    execution = {"execution_id": "EXE-1", "request_id": "REQ-1", "state": state,
                                 "attempts": [{"invocation_id": invocation(n)} for n in range(1, 6)]}
                    if allowed:
                        adapter.send(kernel, {}, execution)
                        kernel.authorize_attempt.assert_called_once_with("EXE-1", "fixture", "REQ-1-authority-6")
                        adapter.emit.assert_called_once_with(invocation(6), "EXE-1")
                    else:
                        with self.assertRaisesRegex(FormalError, "授权预算为 3 次"):
                            adapter.send(kernel, {}, execution)
                        kernel.authorize_attempt.assert_not_called()
                        adapter.emit.assert_not_called()

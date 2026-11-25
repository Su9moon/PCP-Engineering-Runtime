"""Focused V1.2 tests for plan versions and authorization separation."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from intake import Intake, IntakeError, text_input
from planning import LocalPlanner, PlanError, model_plan, normalize_plan
from sources import PROJECT


def proposal(mode="suggestion", **extra):
    return {
        "mode": mode, "objective": "Review delivery evidence",
        "tasks": [{"id": "A", "title": "Collect references"},
                  {"id": "B", "title": "Check coverage", "depends": ["A"]}],
        **extra,
    }


class ValidationTests(unittest.TestCase):
    def test_complexity_does_not_gate_configuration(self):
        c0 = normalize_plan(proposal(complexity="C0", workers=3, strategy="parallel"), text_input)
        c3 = normalize_plan(proposal(complexity="C3", workers=1, strategy="serial"), text_input)
        self.assertEqual((c0["workers"], c3["workers"]), (3, 1))
        self.assertEqual(c3["order"], ["A", "B"])

    def test_model_descriptions_keep_structure_as_text_and_clear_authorization(self):
        raw = proposal("autonomous", risk={"reversible": True}, authorization="assumed")
        raw["tasks"][0]["input"] = ["proof receipt", "commit"]
        plan = normalize_plan(model_plan(raw), text_input)
        self.assertEqual(plan["mode"], "suggestion")
        self.assertEqual(plan["authorization"], "")
        self.assertIn("reversible", plan["risk"])
        self.assertIn("proof receipt", plan["tasks"][0]["input"])

    def test_modified_runtime_contract_disables_planning(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contract = {}
            for role in ("adapter", "launcher", "tool", "core"):
                path = root / role
                path.write_text(role)
                contract[role] = {"path": str(path), "sha256": hashlib.sha256(role.encode()).hexdigest()}
            planner = LocalPlanner({"adapter": str(root / "adapter"), "cwd": directory, "contract": contract})
            with patch.dict("os.environ", {"CLAUDE_FLOW_ROUTER_FALLBACK_MAX_RETRIES": "0"}):
                self.assertTrue(planner.available())
                (root / "launcher").write_text("changed")
                self.assertFalse(planner.available())

    def test_unknown_edges_and_cycles(self):
        for tasks in (
            [{"id": "A", "title": "A", "depends": ["B"]}],
            [{"id": "A", "title": "A", "depends": ["B"]}, {"id": "B", "title": "B", "depends": ["A"]}],
            [{"id": "A", "title": "A"}, {"id": "A", "title": "Duplicate"}],
        ):
            with self.subTest(tasks=tasks), self.assertRaises(PlanError):
                normalize_plan(proposal(tasks=tasks), text_input)


class VersionTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.store = self.open()
        self.draft = self.store.update(None, {"action": "message", "text": "Improve application evidence."})["draft"]

    def open(self):
        return Intake({"directory": str(self.root / "store"), "pcp_repo": str(self.root)}, self.root, None)

    def change(self, action, **values):
        self.draft = self.store.update(self.draft["id"], {"version": self.draft["version"], "action": action, **values})["draft"]
        return self.draft

    def confirm_requirements(self):
        self.change("generate")
        self.change("confirm", revision=self.draft["packages"][-1]["revision"])

    def test_requires_current_confirmed_document_and_preserves_history(self):
        with self.assertRaises(IntakeError):
            self.change("plan_save", plan=proposal())
        self.confirm_requirements()
        orig = self.change("plan_save", plan=proposal())["plans"][0]
        self.change("plan_confirm", revision=1)
        self.change("plan_save", plan=proposal("manual", workers=2), reason="Human chooses two workers")
        plans = self.open().read(self.draft["id"])["draft"]["plans"]
        self.assertEqual(plans[0]["plan"], orig["plan"])
        self.assertIsNotNone(plans[0]["confirmedAt"])
        self.assertEqual(plans[1]["changes"]["workers"], {"before": 1, "after": 2})
        self.change("message", text="Update scope again")
        with self.assertRaises(IntakeError):
            self.change("plan_confirm", revision=2)

    def test_autonomous_confirmation_requires_explicit_proposed_scope(self):
        self.confirm_requirements()
        self.change("plan_save", plan=proposal("autonomous", authorization="Only read local fixture"))
        with self.assertRaisesRegex(IntakeError, "仓库与路径范围"):
            self.change("plan_confirm", revision=1)
        self.change("plan_save", plan=proposal("autonomous", scope="fixture"))
        with self.assertRaisesRegex(IntakeError, "拟授权操作"):
            self.change("plan_confirm", revision=2)
        self.change("plan_save", plan=proposal("autonomous", scope="fixture", authorization="Only read local fixture"))
        self.change("plan_confirm", revision=3)
        self.assertEqual(self.draft["plans"][-1]["effective"], "prospective_draft")
        with self.assertRaisesRegex(IntakeError, "此草稿操作不可用"):
            self.change("dispatch")

    def test_planner_rejects_mismatched_confirmed_snapshot_before_provider_call(self):
        self.confirm_requirements()
        package = self.draft["packages"][-1]
        self.change("message", text="Scope has changed")
        planner = LocalPlanner(None)
        with patch.object(planner, "call") as caller:
            with self.assertRaisesRegex(PlanError, "已确认文档"):
                planner.propose(self.draft, package)
            caller.assert_not_called()

    def test_ruflo_checkpoint_keeps_manual_decision(self):
        with patch.object(self.store.context, "collect", return_value=self.draft["context"]):
            self.change("project", project=PROJECT)
        self.confirm_requirements()
        evidence = {"supervisor": "fixture", "model": "fixture-model"}
        with patch.object(self.store.planner, "propose", return_value=(proposal(), evidence)) as model:
            self.change("plan_generate")
            self.assertEqual(self.draft["plans"][-1]["ruflo"], evidence)
            self.change("plan_save", plan=proposal("manual"))
            with self.assertRaises(IntakeError):
                self.change("plan_generate")
            self.assertEqual(model.call_count, 1)
        self.assertEqual(self.draft["plans"][-1]["plan"]["mode"], "manual")


if __name__ == "__main__":
    unittest.main()

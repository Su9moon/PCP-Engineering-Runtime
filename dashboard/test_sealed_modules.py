"""Exercise the installed Node loader with a replaced disk source and no network."""
import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from planning import LocalPlanner, PlanError
from sealed_modules import ModuleProofError, SealedModules

NODE = shutil.which("node")


class SealedModuleTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "@scope"
        self.root.mkdir()
        self.sources = {
            "launcher": b"import {tool} from './tool.mjs'; console.log('sealed-launcher:' + tool);\n",
            "tool": b"import {core} from './core.mjs'; export const tool = 'sealed-tool:' + core;\n",
            "core": b"export const core = 'sealed-core';\n",
        }
        self.contract = {}
        for role, content in self.sources.items():
            path = self.root / (role + ".mjs")
            path.write_bytes(content)
            self.contract[role] = {"path": str(path), "sha256": hashlib.sha256(content).hexdigest()}

    @unittest.skipUnless(NODE, "Installed Node 24 is required for the execution proof")
    def test_all_three_compiled_modules_keep_sealed_bytes_after_disk_replacement(self):
        with SealedModules(self.sources, self.contract) as modules:
            for role in self.sources:
                file = Path(self.contract[role]["path"])
                temp = file.with_suffix(".replaced")
                temp.write_text(f"throw new Error('replaced {role} was executed');\n")
                temp.replace(file)
            output = subprocess.run(
                [NODE, "--import", modules.import_url, self.contract["launcher"]["path"]],
                pass_fds=tuple(modules.fds), capture_output=True, text=True, timeout=10, check=True,
            )
            modules.check_compiled()
            self.assertEqual(output.stdout.strip(), "sealed-launcher:sealed-tool:sealed-core")
            self.assertEqual(output.stderr, "")
            with self.assertRaises(PermissionError):
                os.pwrite(modules.fds[0], b"changed", 0)

    def test_digest_and_absent_compilation_fail(self):
        with SealedModules(self.sources, self.contract) as modules:
            with self.assertRaisesRegex(ModuleProofError, "缺少实际编译"):
                modules.check_compiled()
        self.contract["core"]["sha256"] = "wrong"
        with self.assertRaisesRegex(ModuleProofError, "封印检查失败"):
            with SealedModules(self.sources, self.contract):
                self.fail("Bad digest reached launch point")

    def test_no_agent_execute_when_loaded_module_proof_fails(self):
        modules = Mock()
        modules.check_compiled.side_effect = ModuleProofError("编译证明未通过")
        runtime = Mock()
        runtime.rpc.return_value = {"tools": [{"name": "agent_execute"}]}
        adapter = SimpleNamespace(
            ReasoningGateway=lambda _: nullcontext(Mock()),
            Ruflo=lambda *_: nullcontext(runtime),
        )
        planner = LocalPlanner({"contract": self.contract, "route_port": 1, "cwd": str(self.root)})
        with patch("planning.SealedModules", return_value=nullcontext(modules)), \
                patch.object(planner, "verified_artifacts", return_value={"adapter": b""}), \
                patch.object(planner, "load_adapter", return_value=adapter), \
                patch.object(planner, "check_launcher"):
            with self.assertRaisesRegex(PlanError, "编译证明未通过"):
                planner.call("This test must not call the model")
        runtime.call.assert_not_called()


if __name__ == "__main__":
    unittest.main()

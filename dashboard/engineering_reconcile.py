"""Wake on existing Hub facts or draft changes and reconcile only authorized projects."""
from contextlib import contextmanager
from copy import deepcopy
import fcntl
import json
import os
from pathlib import Path
import sqlite3
import sys

from engineering import Engineering
from formal import FormalError
from intake import ID, Intake
from operator_grant import load_service_settings
from planning import PlanError
from sources import now


@contextmanager
def reconcile_lock(path):
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def reconcile(config_path):
    config, grant = load_service_settings(config_path)
    if not isinstance((grant or {}).get("engineering"), dict):
        return
    root = Path(__file__).resolve().parent.parent
    intake = Intake(config["intake"], root, config["sources"]["eo"], grant, config["sources"]["es"])
    if not isinstance(intake.formal, Engineering):
        return
    with reconcile_lock(intake.directory / ".engineering-reconcile"):
        for file in sorted(intake.directory.glob("*.json")):
            if not ID.fullmatch(file.stem):
                continue
            current = intake.load(file.stem)
            task = current.get("formal", {})
            if task.get("kind") != "engineering" or not task.get("authorizedAt") or task.get("held"):
                continue
            before = deepcopy(task)
            if before.get("state") == "全部已验收":
                continue
            try:
                intake.formal.advance(task, review=True)
                task.pop("obstacle", None)
            except (FormalError, PlanError, OSError, sqlite3.Error, RuntimeError, KeyError) as exc:
                task["obstacle"] = str(exc) if isinstance(exc, (FormalError, PlanError)) else f"待恢复现有执行链（{type(exc).__name__}）。"
            if task == before:
                continue
            with intake.write_lock():
                latest = intake.load(file.stem)
                binding = latest.get("formal", {})
                if binding.get("planSha256") != before.get("planSha256") or binding.get("commit") != before.get("commit"):
                    continue
                for name in ("runs", "state", "obstacle"):
                    if name in task:
                        binding[name] = task[name]
                    else:
                        binding.pop(name, None)
                latest["version"] += 1
                latest["updatedAt"] = now()
                intake.save(latest)


if __name__ == "__main__":
    try:
        reconcile(Path(sys.argv[1]))
    except BlockingIOError:
        pass

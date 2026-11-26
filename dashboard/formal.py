"""Bind a confirmed non-production draft to the existing EO, ES and Autoloop stores."""
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
from urllib.request import build_opener, ProxyHandler, Request

import yaml

from sources import now


class FormalError(ValueError):
    pass


def git(repo, *args, data=None, index=None):
    env = os.environ.copy()
    if index:
        env["GIT_INDEX_FILE"] = str(index)
    p = subprocess.run(["git", "-C", str(repo), *args], input=data, capture_output=True, env=env, check=False)
    if p.returncode:
        raise FormalError(f"EO Git 操作未完成（{args[0]}）。请核对权威引用后再试。")
    return p.stdout.decode()


def read_object(repo, commit, path):
    return yaml.safe_load(git(repo, "show", f"{commit}:{path}"))


def validate_record(record, schema):
    for key, field in schema["fields"].items():
        value = record.get(key)
        if field.get("required") and value in (None, "", []):
            raise FormalError(f"EO 的 {key} 缺少必填内容。")
        if value is None:
            continue
        kind = field["type"]
        if kind in ("list", "reference_list") and not isinstance(value, list):
            raise FormalError(f"EO 的 {key} 必须是列表。")
        if kind == "integer" and type(value) is not int:
            raise FormalError(f"EO 的 {key} 必须是整数。")
        if kind == "enum" and value not in field["values"]:
            raise FormalError(f"EO 的 {key} 不是允许的状态。")
        if kind in ("id", "internal_reference", "string", "text", "datetime") and not isinstance(value, str):
            raise FormalError(f"EO 的 {key} 必须是文本。")


class Formal:
    def __init__(self, settings, database, render):
        self.settings = settings
        self.repo = Path(settings["eoRepo"])
        self.pin = settings["eoBase"]
        self.ref = settings["eoRef"]
        if not re.fullmatch("[0-9a-f]{40}", self.pin) or not self.ref.startswith("refs/heads/"):
            raise FormalError("EO 基线须为固定提交，写入引用须为部署配置的分支。")
        self.database = Path(database)
        self.render = render

    def eo_head(self):
        return git(self.repo, "rev-parse", "--verify", self.ref).strip()

    def record(self, draft, package, plan):
        marker = f"Intake-Ref: {draft['id']}/R{package['revision']}/P{plan['revision']}"
        head = self.eo_head()
        if git(self.repo, "merge-base", head, self.pin).strip() != self.pin:
            raise FormalError("EO 权威引用与已配置 Schema/Template 基线不一致。")
        existing = git(self.repo, "log", "-1", "--format=%H", "--fixed-strings", "--grep=" + marker, head).strip()
        digest = sha256(json.dumps(plan["plan"], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if existing:
            commit_text = git(self.repo, "show", "-s", "--format=%B", existing)
            matches = re.search(r"^EO-Refs: (JOB-\d{8}-\d+) (WO-\d{8}-\d+)$", commit_text, re.M)
            if not matches or f"Plan-SHA256: {digest}" not in commit_text:
                raise FormalError("EO 既有记录与当前确认的计划不匹配。")
            return {"job": matches[1], "workorder": matches[2], "commit": existing}
        day = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d")
        records = {}
        templates = {kind: read_object(self.repo, self.pin, f"templates/{kind}.template.yaml")
                     for kind in ("job", "workorder")}
        frozen = [(d["filename"], yaml.safe_load(d["text"])) for d in self.render(draft, templates)
                  if d["filename"].endswith(".yaml")]
        paths = git(self.repo, "ls-tree", "-r", "--name-only", head).splitlines()
        if any(not draft["dossier"][field]["value"] or draft["dossier"][field]["provenance"] != "USER_CONFIRMED"
               for field in ("goal", "scope", "deliverables", "acceptance")):
            raise FormalError("正式 EO 记录需要已确认的目标、范围、交付物和验收。")
        for kind, prefix in (("job", "JOB"), ("workorder", "WO")):
            numbers = [int(m[1]) for path in paths
                       if (m := re.fullmatch(rf"{kind}s/{prefix}-{day}-(\d+)/{kind}\.yaml", path))]
            records[kind] = f"{prefix}-{day}-{max(numbers, default=0)+1:03d}"
        files = {}
        for name, value in frozen:
            kind = name.removesuffix(".yaml")
            value.update({f"{kind}_id": records[kind], "status": "READY",
                          "created_by": "human:cbnet-service-operator", "updated_at": now()})
            if kind == "job":
                value["workorder_refs"] = [records["workorder"]]
            else:
                value["job_id"] = records["job"]
                value["input_refs"] += [f"pcp-intake:{draft['id']}/R{package['revision']}/P{plan['revision']}"]
            validate_record(value, read_object(self.repo, self.pin, f"schemas/{kind}.schema.yaml"))
            files[f"{kind}s/{records[kind]}/{name}"] = yaml.safe_dump(value, allow_unicode=True, sort_keys=False).encode()
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "eo-index"
            git(self.repo, "read-tree", head, index=index)
            for path, body in files.items():
                oid = git(self.repo, "hash-object", "-w", "--stdin", data=body).strip()
                git(self.repo, "update-index", "--add", "--cacheinfo", f"100644,{oid},{path}", index=index)
            tree = git(self.repo, "write-tree", index=index).strip()
        change = (f"登记 V1.2 非生产工程工单\n\n{marker}\nPlan-SHA256: {digest}\n"
                  f"EO-Refs: {records['job']} {records['workorder']}\n")
        commit = git(self.repo, "commit-tree", tree, "-p", head, data=change.encode()).strip()
        git(self.repo, "update-ref", self.ref, commit, head)
        if any(git(self.repo, "show", f"{commit}:{path}").encode() != body for path, body in files.items()):
            raise FormalError("EO 对象的权威读回与提交内容不一致。")
        return {**records, "commit": commit}

    def kernel(self):
        source = Path(self.settings["esRepo"])
        pin = self.settings["esBase"]
        if git(source, "rev-parse", "HEAD").strip() != pin or git(source, "diff", "HEAD", "--", "src"):
            raise FormalError("ES ExecutionKernel 源码与部署记录的版本不符。")
        if not self.database.is_file():
            raise FormalError("现有 ES 权威数据库缺失。")
        sys.path.insert(0, str(source / "src"))
        try:
            from execution_server.kernel import ExecutionKernel
            return ExecutionKernel(str(self.database))
        finally:
            sys.path.pop(0)

    def request(self, binding):
        commit, wo = binding["commit"], binding["workorder"]
        if git(self.repo, "merge-base", self.eo_head(), commit).strip() != commit:
            raise FormalError("EO 权威引用已不含当前工单提交。")
        item = read_object(self.repo, commit, f"workorders/{wo}/workorder.yaml")
        if item["workorder_id"] != wo or item["status"] != "READY":
            raise FormalError("EO 工单不可用于执行。")
        req = {
            "contract_version": "pcp.execution/v0.1", "kind": "ExecutionRequest",
            "request_id": f"REQ-D01-{wo}", "source": {"type":"engineering_workorder","ref":wo,
                                                      "snapshot":{"version_ref":commit}},
            "intent": {"objective":item["objective"], "acceptance":[
                {"id": f"AC-{i}", "requirement": line} for i,line in enumerate(item["acceptance_criteria"], 1)]},
            "target": {"type":"git_repository","ref":"github://Su9moon/PCP-Engineering-Runtime"},
            "execution": {"capability":"non-production-text"},
            "constraints": {"scope":"synthetic-text-only","no_file_or_tool_use":True},
            "result_contract": {"required":["response","provider_run","codex_thread"]},
            "review":{"required":True},
        }
        return self.kernel().submit_execution(req)

    def provider_run(self, invocation):
        hub = Path(self.settings["hubDatabase"])
        if not hub.is_file():
            raise FormalError("现有 Autoloop 投影不可用。")
        with sqlite3.connect(hub.as_uri() + "?mode=ro", uri=True) as db:
            db.row_factory = sqlite3.Row
            row = db.execute(
                "SELECT events.id AS event_id, runs.id AS run_id, runs.state, runs.session, runs.summary, "
                "runs.usage, runs.claimed_at FROM events JOIN run_events ON events.id=run_events.event_id "
                "JOIN runs ON runs.id=run_events.run_id WHERE events.source=? AND events.key=? AND runs.rule=?",
                (self.settings["source"], invocation, self.settings["rule"]),
            ).fetchall()
        if len(row) > 1:
            raise FormalError("该 Invocation 出现多个 Provider Run，需人工对账。")
        return dict(row[0]) if row else None

    def dispatch(self, binding):
        es = self.kernel()
        execution = es.get_execution(binding["execution"])
        attempt = es.authorize_attempt(execution["execution_id"], self.settings["worker"],
                                       execution["request_id"] + "-authority")
        invocation = attempt["invocation_id"]
        if run := self.provider_run(invocation):
            return {"event":run["event_id"], "run":run["run_id"], "invocation":invocation}
        current = es.get_execution(execution["execution_id"])
        effective = current["attempts"][-1]
        if (current["state"] != "QUEUED" or effective["attempt_id"] != attempt["attempt_id"]
                or effective["state"] != "CLAIMED" or effective["authority"]["status"] != "CURRENT"):
            raise FormalError("ES Attempt 不可派发。")
        cfg = json.loads(Path(self.settings["hubConfig"]).read_text())
        event = {"id":invocation, "type":self.settings["eventType"], "subject":invocation,
                 "summary":execution["execution_id"]}
        if cfg["source"]["name"] != self.settings["source"] or cfg["url"] != "http://127.0.0.1:47355":
            raise FormalError("现有 Autoloop 来源或回环地址不匹配。")
        request = Request(cfg["url"] + "/v1/events", json.dumps(event).encode(),
                          headers={"Content-Type":"application/json", "Authorization":"Bearer " + cfg["source"]["key"]})
        try:
            with build_opener(ProxyHandler({})).open(request, timeout=6) as response:
                receipt = json.load(response)
        except OSError as exc:
            raise FormalError("Autoloop 回执未确认，按同一 Invocation 查询后可对账。") from exc
        if receipt.get("routed") != [self.settings["rule"]] or not (run := self.provider_run(invocation)):
            raise FormalError("Autoloop 未返回唯一、可对账的 Worker Run。")
        return {"event":run["event_id"], "run":run["run_id"], "invocation":invocation}

    def observe(self, binding):
        es = self.kernel()
        info = es.get_execution(binding["execution"])
        if not info["attempts"]:
            return {"state":info["state"]}
        attempt = info["attempts"][-1]
        inv = attempt["invocation_id"]
        run = self.provider_run(inv)
        provider = {"event":run["event_id"], "run":run["run_id"], "session":run["session"], "state":run["state"]} if run else None
        if not run or not run["session"] or not run["claimed_at"]:
            return {"state":info["state"],"provider":provider,"attempt":attempt["attempt_id"],"invocation":inv}
        if info["state"] == "QUEUED" and run["state"] in ("claimed", "done"):
            es.record_attempt_start(attempt["authority_id"], inv + "-start", f"autoloop:run:{run['run_id']}")
            info = es.get_execution(info["execution_id"])
        if info["state"] == "RUNNING" and run["state"] == "done":
            summary = (run["summary"] or "").strip()
            if summary != self.settings["expectedResult"]:
                raise FormalError("Worker 终态缺少可交付的中文回执。")
            normalized = {"outcome": {"kind":"RESULT_AVAILABLE"},
                          "payload": {"response":summary,"provider_run":run["run_id"],"codex_thread":run["session"]}}
            es.record_attempt_result(attempt["authority_id"], inv + "-result", normalized,
                                    [f"autoloop:run:{run['run_id']}",f"codex:thread:{run['session']}"])
            info = es.get_execution(info["execution_id"])
        result = info["attempts"][-1]["result"]
        return {"state":info["state"],"provider":provider,"attempt":attempt["attempt_id"],"invocation":inv,
                "result":result["value"]["payload"] if result else None}

"""Project-scoped bridge between confirmed drafts and the existing EO, ES and Autoloop stores."""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re

import yaml

from formal import Formal, FormalError, git, plan_digest, read_object, validate_record
from planning import LocalPlanner
from sources import PROJECT, now

CJK = re.compile(r"[㐀-鿿]")
SHA = re.compile(r"[a-f0-9]{40}")


def worker_path(root, invocation):
    if not re.fullmatch(r"AINV-[a-f0-9]{32}", invocation):
        raise FormalError("ES 调用标识无效。")
    return Path(root) / invocation


def json_lines(path, limit=8_000_000):
    with path.open("rb") as file:
        raw = file.read(limit + 1)
    if len(raw) > limit:
        raise FormalError("执行记录超出本机证据读取上限。")
    values = []
    for line in raw.decode().splitlines():
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if isinstance(value, dict):
            values.append(value)
    return raw, values


class Engineering(Formal):
    def __init__(self, settings, database, render, project, planner):
        super().__init__(settings, database, render)
        self.project = Path(project)
        self.planner = planner

    def validate_binding(self, package, plan):
        available = self.settings["budget"]
        proposed = plan["plan"]
        if not 1 <= len(proposed["tasks"]) <= available["tasks"]:
            raise FormalError("任务数量超出此项目的执行资源范围。")
        if not 1 <= proposed["workers"] <= available["workers"]:
            raise FormalError("计划 Worker 数超出当前登记的执行资源。")
        if not all(task.get("input") and task.get("output") and task.get("acceptance")
                   for task in proposed["tasks"]):
            raise FormalError("每个任务须有明确输入、交付物和验收条件。")
        if not all(CJK.search(task["title"]) and CJK.search(task["acceptance"]) for task in proposed["tasks"]):
            raise FormalError("任务标题与验收内容须包含完整中文。")

    def register(self, draft, package, plan):
        self.validate_binding(package, plan)
        requested = plan["plan"]
        project_head = git(self.project, "rev-parse", "HEAD").strip()
        ref = self.record(draft, package, plan)
        return {
            **ref, "kind": "engineering", "documentRevision": package["revision"],
            "planRevision": plan["revision"], "basis": package["basis"], "planSha256": plan_digest(plan),
            "sourceBase": project_head, "tasks": requested["tasks"], "order": requested["order"],
            "mode": requested["mode"], "runs": {}, "state": "待下达",
        }

    def canonical_workorder(self, binding):
        commit, workorder = binding["commit"], binding["workorder"]
        root = f"workorders/{workorder}/workorder.yaml"
        head = self.eo_head()
        if (git(self.repo, "merge-base", head, commit).strip() != commit
                or git(self.repo, "rev-parse", f"{head}:{root}") != git(self.repo, "rev-parse", f"{commit}:{root}")):
            raise FormalError("当前 EO 权威工单与冻结的执行版本不一致。")
        record = read_object(self.repo, commit, root)
        if (record["workorder_id"] != workorder or record["status"] != "READY"
                or "sha256:" + binding["planSha256"] not in record["input_refs"]):
            raise FormalError("EO 工单不在当前已确认的执行授权范围内。")
        return record

    def admit(self, kernel, binding, task, base, predecessor):
        eo = self.canonical_workorder(binding)
        workorder = binding["workorder"]
        scope = self.settings["paths"]
        request = {
            "contract_version": "pcp.execution/v0.1", "kind": "ExecutionRequest",
            "request_id": f"REQ-{workorder}-{task['id']}",
            "source": {"type": "engineering_workorder", "ref": workorder, "snapshot": {"version_ref": binding["commit"]}},
            "intent": {"objective": eo["objective"], "acceptance": [
                {"id": "AC-TASK", "requirement": task["acceptance"]},
                *({"id": f"AC-{i}", "requirement": row} for i, row in enumerate(eo["acceptance_criteria"], 1)),
            ]},
            "target": {"type": "git_repository", "ref": "github://" + PROJECT},
            "execution": {"capability": "non-production-engineering"},
            "constraints": {"paths": scope, "production": False, "base_commit": base,
                            "predecessor_invocation": predecessor, "plan_sha256": binding["planSha256"]},
            "result_contract": {"required": ["response", "commit", "tests", "codex_thread", "worker_sha256"]},
            "review": {"required": True},
            "metadata": {"workorder_id": workorder, "job_id": binding["job"],
                         "task": task, "profile": "engineering-v1.3"},
        }
        return kernel.submit_execution(request)

    def verify_routing(self):
        self.settings.setdefault("objective", self.settings["rulePrompt"])
        return super().verify_routing()

    def send(self, kernel, binding, execution):
        self.canonical_workorder(binding)
        self.verify_routing()
        prior = execution["attempts"]
        limit = self.settings["budget"]["attempts"]
        if execution["state"] in ("RECOVERABLE", "REVISION_REQUESTED") and len(prior) >= limit:
            raise FormalError("该任务已达到服务端授权的尝试预算。")
        if not prior or execution["state"] in ("RECOVERABLE", "REVISION_REQUESTED"):
            attempt = kernel.authorize_attempt(execution["execution_id"], self.settings["worker"],
                                               f"{execution['request_id']}-authority-{len(prior) + 1}")
        else:
            attempt = prior[-1]
            attempt["attempt_state"] = attempt["state"]
        invocation = attempt["invocation_id"]
        if not self.provider_run(invocation):
            with kernel.store.transaction():
                current = kernel.get_execution(execution["execution_id"])
                latest = current["attempts"][-1]
                if (latest["attempt_id"] != attempt["attempt_id"] or latest["state"] != "CLAIMED"
                        or latest["authority"]["status"] != "CURRENT" or current["state"] != "QUEUED"):
                    raise FormalError("此 ES Attempt 已失效，不能派发。")
                self.verify_routing()
                self.emit(invocation, current["execution_id"])
        return kernel.get_execution(execution["execution_id"])

    def collect(self, run, request, invocation):
        if run["state"] != "done" or not run["session"]:
            return None
        spool = Path(self.settings["workerHome"]) / "worker/runs" / f"{run['run_id']}-1"
        if (spool / "exit-1").read_text().strip() != "0":
            raise FormalError("Worker 退出码非零，交付尚不可验收。")
        raw, events = json_lines(spool / "stdout-1.log")
        sessions = {event.get("thread_id") for event in events if event.get("type") == "thread.started"}
        terminals = [event for event in events if event.get("type") == "turn.completed"]
        operations = [event["item"] for event in events if event.get("type") == "item.completed"
                      and isinstance(event.get("item"), dict)]
        outputs = [item.get("text", "") for item in operations if item.get("type") == "agent_message"]
        if sessions != {run["session"]} or len(terminals) != 1 or not outputs or not CJK.search(outputs[-1]):
            raise FormalError("Worker 缺少可核验的中文终态回执。")
        checkout = worker_path(self.settings["workspaceRoot"], invocation)
        head = git(checkout, "rev-parse", "HEAD").strip()
        base = request["constraints"]["base_commit"]
        archived = [value.get("commit") for value in events if value.get("type") == "pcp.commit.archived"]
        if (archived != [head] or not SHA.fullmatch(head) or head == base
                or git(checkout, "merge-base", head, base).strip() != base):
            raise FormalError("Worker 未留下基于授权基线的可审查 Git 提交。")
        if git(checkout, "status", "--porcelain").strip():
            raise FormalError("Worker 隔离工作区包含尚未交付的修改。")
        names = git(checkout, "diff", "--name-only", "-z", base, head).strip("\x00").split("\x00")
        allowed = request["constraints"]["paths"]
        if not all(any(name.startswith(prefix + "/") for prefix in allowed) for name in names):
            raise FormalError("提交包含授权代码目录之外的文件。")
        tests = [item["command"][:450] for item in operations if item.get("type") == "command_execution"
                 and item.get("exit_code") == 0 and re.search(r"\b(unittest|pytest|npm\s+test|node\s+--check)\b", item.get("command", ""))]
        if not tests:
            raise FormalError("Worker 没有提供真实通过的定向测试事件。")
        usage = terminals[0].get("usage")
        return {"response": outputs[-1][:3500], "commit": head, "base": base, "tests": tests[-8:], "changed": names,
                "codex_thread": run["session"], "worker_sha256": hashlib.sha256(raw).hexdigest(),
                "requested_model": self.settings["model"], "requested_effort": self.settings["effort"],
                "actual_model": "NOT_EXPOSED_BY_RUNTIME", "actual_effort": "NOT_EXPOSED_BY_RUNTIME", "usage": usage}

    def judge(self, binding, request, invocation, result):
        checkout = worker_path(self.settings["workspaceRoot"], invocation)
        diff = git(checkout, "diff", "--no-ext-diff", result["base"], result["commit"])
        if len(diff) > self.settings["budget"]["reviewChars"]:
            raise FormalError("提交差异超过当前可审核的资源范围，保留交付物待审。")
        review_data = {"task": request["metadata"]["task"], "eo": self.canonical_workorder(binding),
                       "evidence": result, "diff": diff}
        raw = json.dumps(review_data, ensure_ascii=False, separators=(",", ":"))
        decisions = {}
        for role, name in (("review", "独立代码复核"), ("qa", "独立产品验收")):
            planner = LocalPlanner({**self.planner.settings, **self.settings["roles"][role]})
            text, receipt = planner.request(
                f"你负责{name}。只看本轮原工单、变更、实际测试及交付，不替另一角色签字。"
                "以 PASS 或 REWORK 起首，再写完整中文理由；确有缺陷才退回。不要访问工具或执行任务。\n" + raw,
                f"你是 Ruflo 的{name}角色，只对本轮提交给出独立审查。",
                max_tokens=500,
            )
            item = (text or "").lstrip("* \n")
            if not item.startswith(("PASS", "REWORK")):
                raise FormalError(f"{name}未返回可核验的决定。")
            decisions[role] = {"state": "PASS" if item.startswith("PASS") else "REWORK",
                               "text": text[:2500], "receipt": receipt}
        supervisor, receipt = self.planner.request(
            "根据真实 Worker 提交及独立评审决定下一步。只接受以 CONTINUE 或 REWORK 起首的中文决定。"
            "仅两份通过才能 CONTINUE，后续依赖必须先等本项通过；不扩大范围。\n" +
            json.dumps({"task": request["metadata"]["task"], "commit": result["commit"],
                        "review": decisions}, ensure_ascii=False),
            "你是原 Ruflo Supervisor。只给出下一步，不直接调用工具。",
            max_tokens=500,
        )
        value = supervisor.lstrip("* \n")
        if not value.startswith(("CONTINUE", "REWORK")):
            raise FormalError("Supervisor 未返回可核验的继续或返工决定。")
        decisions["supervisor"] = {"state": "CONTINUE" if value.startswith("CONTINUE") else "REWORK",
                                   "text": supervisor[:2500], "receipt": receipt}
        return decisions

    def eo_delivery(self, binding, task, attempt, run, result, decisions):
        head = self.eo_head()
        marker = f"Result-Attempt: {attempt}"
        prior = git(self.repo, "log", "-1", "--format=%H", "--fixed-strings", "--grep=" + marker, head).strip()
        if prior:
            return prior
        files = {}
        folders = {"evidence": "evidence", "result": "results", "review": "reviews"}
        day = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d")
        paths = git(self.repo, "ls-tree", "-r", "--name-only", head).splitlines()
        mapping = {"result": "RESULT", "review": "REVIEW", "evidence": "EVD"}
        refs = {}
        for kind, prefix in mapping.items():
            nums = [int(m[1]) for path in paths if (m := re.fullmatch(rf"{folders[kind]}/{prefix}-{day}-(\d+)/{kind}\.yaml", path))]
            refs[kind] = f"{prefix}-{day}-{max(nums, default=0)+1:03d}"
        detail = {
            "result": {"workorder_id": binding["workorder"], "summary": result["response"], "status": "FINAL",
                       "findings": result["tests"], "conclusion": "独立代码复核、产品 QA 已通过。", "evidence_refs": [refs["evidence"]]},
            "review": {"result_id": refs["result"], "reviewer": decisions["review"]["receipt"]["supervisor"],
                       "decision": "APPROVED", "comment": decisions["review"]["text"] + "\n\n" + decisions["qa"]["text"],
                       "reviewed_at": now()},
            "evidence": {"evidence_type": "test_result", "source": f"Autoloop Event {run['event_id']} / Run {run['run_id']}",
                         "locator": {"kind": "git_commit", "value": f"git://{PROJECT}/commit/{result['commit']}",
                                     "revision": result["commit"]},
                         "description": f"任务 {task} 的代码提交、定向测试及 Worker 输出证据。",
                         "verification": f"Worker JSONL SHA-256 {result['worker_sha256']}"},
        }
        for kind, fields in detail.items():
            record = read_object(self.repo, self.pin, f"templates/{kind}.template.yaml")
            record.update({f"{kind}_id": refs[kind], "created_at": now(), "updated_at": now(),
                           "created_by": "ruflo:engineering-review", **fields})
            validate_record(record, read_object(self.repo, self.pin, f"schemas/{kind}.schema.yaml"))
            files[f"{folders[kind]}/{refs[kind]}/{kind}.yaml"] = yaml.safe_dump(record, allow_unicode=True, sort_keys=False).encode()
        return self.commit_records(head, files, f"登记工程任务验收 {task}\n\n{marker}\n")

    def advance(self, binding, *, review=False):
        if not binding.get("authorizedAt") or binding.get("held"):
            return
        kernel = self.kernel()
        tasks = {task["id"]: task for task in binding["tasks"]}
        runs = binding["runs"]
        for key in binding["order"]:
            task = tasks[key]
            if not all(runs.get(dep, {}).get("state") == "DONE" for dep in task["depends"]):
                continue
            if key not in runs:
                base = binding["sourceBase"]
                predecessor = None
                # One native Worker is currently registered. Preserve already accepted commits when
                # starting a later task, even when the two tasks did not need a dependency edge.
                accepted = [runs[x] for x in binding["order"] if runs.get(x, {}).get("state") == "DONE"]
                if accepted:
                    last = accepted[-1]
                    base, predecessor = last["result"]["commit"], last["invocation"]
                req = self.admit(kernel, binding, task, base, predecessor)
                runs[key] = {"execution": req["execution_id"], "state": req["state"]}
            row = runs[key]
            execution = kernel.get_execution(row["execution"])
            if execution["state"] == "DONE" and row.get("state") == "DONE":
                continue
            if execution["state"] in ("QUEUED", "REVISION_REQUESTED", "RECOVERABLE"):
                if execution["state"] != "QUEUED" and binding["mode"] != "autonomous":
                    row["state"] = execution["state"]
                    return
                if execution["state"] == "RECOVERABLE":
                    prior_invocation = execution["attempts"][-1]["invocation_id"]
                    if row.get("reworkFor") != prior_invocation:
                        answer, receipt = self.planner.request(
                            "请核查本次 Worker 交付失败是否适合在原授权范围内返工。"
                            "只用中文答复，以 REWORK 或 HOLD 起首。不要重派原 Invocation。\n"
                            + json.dumps({"task": task, "reason": row.get("failure"),
                                          "invocation": prior_invocation}, ensure_ascii=False),
                            "你是原 Ruflo Supervisor，负责判断是否允许新尝试。",
                            max_tokens=450,
                        )
                        decision = answer.lstrip("* \n")
                        if not decision.startswith(("REWORK", "HOLD")):
                            raise FormalError("Supervisor 的返工决定无法核验。")
                        row.update(reworkFor=prior_invocation, rework={"text": answer, "receipt": receipt,
                                                                   "approved": decision.startswith("REWORK")})
                        return
                    if not row["rework"]["approved"]:
                        return
                execution = self.send(kernel, binding, execution)
            if not execution["attempts"]:
                return
            attempt = execution["attempts"][-1]
            invocation = attempt["invocation_id"]
            run = self.provider_run(invocation)
            row.update(state=execution["state"], invocation=invocation, attempt=attempt["attempt_id"])
            if not run:
                return
            row.update(event=run["event_id"], run=run["run_id"], provider=run["state"])
            if execution["state"] == "QUEUED" and run["session"] and run["claimed_at"]:
                kernel.record_attempt_start(attempt["authority_id"], invocation + "-start", f"autoloop:run:{run['run_id']}")
                execution = kernel.get_execution(row["execution"])
                row["state"] = execution["state"]
            if execution["state"] == "RUNNING" and run["state"] == "done":
                try:
                    result = self.collect(run, execution["request"], invocation)
                except FormalError as exc:
                    kernel.record_attempt_failure(
                        attempt["authority_id"], invocation + "-delivery-failed",
                        {"kind": "delivery_contract_failed", "reason": str(exc), "providerRun": run["run_id"]},
                    )
                    row["state"] = "RECOVERABLE"
                    row["failure"] = str(exc)
                    return
                kernel.record_attempt_result(
                    attempt["authority_id"], invocation + "-result",
                    {"outcome": {"kind": "RESULT_AVAILABLE"}, "payload": result},
                    [f"autoloop:run:{run['run_id']}/stdout#sha256={result['worker_sha256']}",
                     f"git://{PROJECT}/commit/{result['commit']}"],
                )
                execution = kernel.get_execution(row["execution"])
                row["state"] = execution["state"]
            if execution["state"] not in ("REVIEW_READY", "DONE"):
                return
            result = execution["attempts"][-1]["result"]["value"]["payload"]
            row["result"] = result
            if not review:
                return
            if "decisions" not in row:
                row["decisions"] = self.judge(binding, execution["request"], invocation, result)
                return
            decisions = row["decisions"]
            if not all(decisions[name]["state"] == "PASS" for name in ("review", "qa")) or decisions["supervisor"]["state"] != "CONTINUE":
                kernel.record_review(row["execution"], row["attempt"], invocation + "-review", "REWORK",
                                     decisions["review"]["receipt"]["supervisor"])
                row["state"] = "REVISION_REQUESTED"
                row["priorDecisions"] = row.pop("decisions")
                return
            row["eoDelivery"] = self.eo_delivery(binding, key, row["attempt"], run, result, decisions)
            if execution["state"] != "DONE":
                kernel.record_review(row["execution"], row["attempt"], invocation + "-review", "APPROVED",
                                     decisions["review"]["receipt"]["supervisor"])
            row["state"] = "DONE"
            return
        binding["state"] = "全部已验收"

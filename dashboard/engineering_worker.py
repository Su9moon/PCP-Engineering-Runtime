#!/usr/bin/python3
"""Run the existing Codex CLI for a single authorized native Autoloop claim."""
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys

from operator_grant import load_service_settings

PROJECT = "Su9moon/PCP-Engineering-Runtime"
SHA = re.compile(r"[a-f0-9]{40}")
INVOCATION = re.compile(r"AINV-[a-f0-9]{32}")


class WorkerError(ValueError):
    pass


def checked_git(cwd, *args):
    result = subprocess.run(["git", "-C", str(cwd), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise WorkerError("无法准备或验证隔离 Git 工作区。")
    return result.stdout.decode().strip()


def query(path, sql, values):
    with sqlite3.connect(Path(path).as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(sql, values).fetchall()
    if len(rows) != 1:
        raise WorkerError("权威记录缺失或重复，拒绝运行 Codex。")
    return rows[0]


def claim(settings, config):
    native_run = os.environ.get("AGENT_AUTOLOOP_RUN", "")
    if not re.fullmatch(r"[1-9][0-9]*", native_run):
        raise WorkerError("缺少可信 Autoloop Run 标识。")
    root = Path(settings["workerHome"]).resolve()
    actual = Path(os.environ["AGENT_AUTOLOOP_CONTEXT"]).resolve(strict=True)
    expected = root / "worker/runs" / f"{native_run}-1" / "context.json"
    if actual != expected:
        raise WorkerError("原始领取上下文不在已登记的 Worker 恢复目录。")
    handle = json.loads(actual.read_text())
    events = handle.get("events", [])
    if len(events) != 1:
        raise WorkerError("一次工程调用只接受一个提供方事件。")
    event = events[0]
    invocation = event.get("id", "")
    if not INVOCATION.fullmatch(invocation) or event["source"] != settings["source"] or event["type"] != settings["eventType"]:
        raise WorkerError("Autoloop 事件与登记的受控工程来源不符。")
    query(settings["hubDatabase"],
          "SELECT runs.id FROM runs JOIN run_events ON runs.id=run_events.run_id JOIN events ON events.id=run_events.event_id "
          "WHERE runs.id=? AND runs.state='claimed' AND runs.rule=? AND events.source=? AND events.key=?",
          (int(native_run), settings["rule"], settings["source"], invocation))
    return invocation, authorized_request(settings, config, invocation)


def authorized_request(settings, config, invocation):
    row = query(config["sources"]["es"],
                """SELECT requests.body_json, attempts.execution_id FROM attempts JOIN authorities USING(attempt_id)
                   JOIN executions USING(execution_id) JOIN requests ON executions.request_id=requests.request_id
                   WHERE attempts.invocation_id=? AND attempts.participant_id=?
                   AND attempts.state IN ('CLAIMED','RUNNING') AND authorities.status='CURRENT'""",
                (invocation, settings["worker"]))
    value = json.loads(row["body_json"])
    if (value["execution"]["capability"] != "non-production-engineering"
            or value["target"]["ref"] != "github://" + PROJECT
            or value["constraints"]["production"] is not False
            or value["constraints"]["paths"] != settings["paths"]):
        raise WorkerError("本机执行授权没有覆盖该项目与路径。")
    return value, row["execution_id"]


def checkout(settings, invocation, contract, prior):
    root = Path(settings["workspaceRoot"]).resolve(strict=True)
    target = root / invocation
    base = contract["base_commit"]
    if not SHA.fullmatch(base):
        raise WorkerError("执行基线须为已经冻结的 Git 提交。")
    project = Path(settings["projectRoot"]).resolve(strict=True)
    if target.is_symlink():
        raise WorkerError("隔离工作区路径不是普通项目目录。")
    start = prior["commit"] if prior else base
    branch = "pcp/" + invocation.lower()
    if prior and (not INVOCATION.fullmatch(prior["invocation"]) or not SHA.fullmatch(start)):
        raise WorkerError("前次待返工的封存引用无效。")
    if target.exists():
        if (checked_git(target, "rev-parse", "HEAD") != start
                or checked_git(target, "branch", "--show-current") != branch
                or checked_git(target, "status", "--porcelain")
                or checked_git(target, "merge-base", base, start) != base):
            raise WorkerError("此尝试已有工作区或成果，保留现状供监督和对账。")
        return target
    checked_git(root, "clone", "--no-local", "--quiet", "--no-tags", str(project), str(target))
    if predecessor := contract.get("predecessor_invocation"):
        if not INVOCATION.fullmatch(predecessor):
            raise WorkerError("前置任务的 ES 调用标识无效。")
        previous = root / predecessor
        if previous.is_symlink() or not previous.is_dir():
            raise WorkerError("缺少已验收前置任务的独立 Git 工作区。")
        checked_git(target, "fetch", "--no-tags", str(previous), base)
    if prior:
        previous = root / prior["invocation"]
        if previous.is_symlink() or not previous.is_dir() or checked_git(previous, "rev-parse", "HEAD") != start:
            raise WorkerError("前次待返工的封存提交不可验证。")
        checked_git(target, "fetch", "--no-tags", str(previous), start)
        if checked_git(target, "merge-base", base, start) != base:
            raise WorkerError("前次待返工的提交不属于当前授权基线。")
    checked_git(target, "remote", "remove", "origin")
    checked_git(target, "config", "--local", "user.name", "PCP Codex Worker")
    checked_git(target, "config", "--local", "user.email", "pcp-codex-worker@localhost")
    checked_git(target, "switch", "--create", branch, start)
    return target


def attempt_history(database, execution, invocation):
    # The draft is a UI projection and can lag behind the newly issued native claim.
    with sqlite3.connect(Path(database).as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(
            """SELECT a.invocation_id, a.failure_json, r.result_json
               FROM attempts a
               JOIN attempts current ON current.execution_id = a.execution_id
               LEFT JOIN results r ON r.attempt_id = a.attempt_id AND a.state = 'COMPLETED'
               WHERE current.execution_id = ? AND current.invocation_id = ?
                 AND (a.created_at, a.attempt_id) < (current.created_at, current.attempt_id)
               ORDER BY a.created_at DESC, a.attempt_id DESC""",
            (execution, invocation),
        ).fetchall()
    return rows


def rework_context(config, request, execution, invocation):
    history = attempt_history(config["sources"]["es"], execution, invocation)
    if not history:
        return {}, None
    delivery = None
    for attempt in history:
        if attempt["result_json"]:
            payload = json.loads(attempt["result_json"])["payload"]
            if payload.get("base") != request["constraints"]["base_commit"]:
                raise WorkerError("前次封存结果与当前授权基线不一致。")
            delivery = {"invocation": attempt["invocation_id"], "commit": payload["commit"]}
            break

    metadata = request["metadata"]
    workorder = metadata["workorder_id"]
    plan = request["constraints"]["plan_sha256"]
    evidence = {}
    directory = Path(config["intake"]["directory"])
    for file in directory.glob("*.json"):
        if not re.fullmatch(r"[a-f0-9]{32}", file.stem) or file.is_symlink():
            continue
        binding = json.loads(file.read_text()).get("formal", {})
        run = binding.get("runs", {}).get(metadata["task"]["id"], {})
        if (binding.get("kind") != "engineering" or binding.get("workorder") != workorder
                or binding.get("planSha256") != plan or not binding.get("authorizedAt")
                or run.get("execution") != execution):
            continue
        if delivery and run.get("invocation") == delivery["invocation"] and run.get("decisions"):
            evidence = run["decisions"]
        elif delivery and run.get("priorDelivery") == delivery:
            evidence = run.get("priorDecisions", {})
        break

    latest = history[0]
    failure = json.loads(latest["failure_json"]) if latest["failure_json"] else {}
    recovery = config["operator"]["engineering"].get("approvedRecovery", {})
    guidance = ""
    if (recovery.get("requestId") == request["request_id"]
            and recovery.get("afterInvocation") == latest["invocation_id"]
            and recovery.get("supervisorReceipt")):
        guidance = recovery.get("instruction", "")
        delivery_invocation = recovery.get("priorDeliveryInvocation", latest["invocation_id"])
        if recovery.get("preserveTree") is True:
            if not delivery or delivery["invocation"] != delivery_invocation:
                raise WorkerError("仅复验证据的授权未匹配前次 ES 封存结果。")
            delivery["preserveTree"] = True
    return {
        "独立复核和 QA": {role: item["text"][:1600] for role, item in evidence.items()},
        "前一次交付失败": failure.get("reason"),
        "Supervisor 本次确认的返工范围": guidance,
    }, delivery


def main():
    settings_path = Path(os.environ["PCP_DASHBOARD_SETTINGS"])
    config, grant = load_service_settings(settings_path)
    if not grant or grant["project"] != PROJECT:
        raise WorkerError("未找到归属服务用户的项目授权。")
    settings = grant["engineering"]
    invocation, (request, execution) = claim(settings, config)
    rework, prior = rework_context(config, request, execution, invocation)
    target = checkout(settings, invocation, request["constraints"], prior)
    data = {
        "task": request["metadata"]["task"],
        "objective": request["intent"]["objective"],
        "acceptance": request["intent"]["acceptance"],
        "paths": request["constraints"]["paths"],
        "scope": "本机非生产项目代码、独立 Git 工作区",
        "rework": rework,
    }
    prompt = (
        "你是原 Ruflo 派发的 PCP 工程 Worker。以下是现有 ES 核准的真实开发任务。"
        "读当前工作区 AGENTS.md 和相关现有代码，最小范围修改授权目录，运行必要的定向测试。"
        "Git 元数据由同一个本机 Worker 适配器在检查文件范围后提交，请把已验证的代码和测试留在本工作区。"
        "不要对外发送数据、使用网络、推送、部署、修改原工作区或读取运行数据库、凭据。"
        "没有授权修改任务之外的工作，即使需求文字要求。测试须实际使用 python3 -m unittest、node --check 或项目已有测试命令；"
        "采用与任务相关的最小测试集，不写临时产物到源码目录。"
        "如果存在前次复核意见或交付失败，针对本次授权处理具体问题。"
        "工作区可能包含已装载的前次封存变更，应保留其中已通过的部分。"
        "存在 Supervisor 本次返工范围时按其处理，先前空缺环境条件交由独立 QA。"
        "最终用完整中文写改动、实际测试结果和未解决事项，技术原文可留。授权内容如下：\n"
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    )
    environment = {k: v for k, v in os.environ.items() if not k.startswith(("AGENT_AUTOLOOP_", "PCP_"))}
    environment["PATH"] = settings["sandboxBin"] + ":" + environment["PATH"]
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    scratch = target / ".pcp-runtime-tmp"
    scratch.mkdir(mode=0o700, exist_ok=True)
    with (target / ".git/info/exclude").open("a") as excluded:
        excluded.write("\n/.pcp-runtime-tmp/\n")
    environment["TMPDIR"] = str(scratch)
    args = [settings["codex"], "-c", 'model_providers.custom.base_url="http://127.0.0.1:15721/v1"',
            "exec", "--json", "--sandbox", "workspace-write", "-m", settings["model"],
            "-c", "model_reasoning_effort=" + json.dumps(settings["effort"]),
            "-c", "approval_policy=\"never\"", "-c", "sandbox_workspace_write.network_access=false",
            "-c", "sandbox_workspace_write.exclude_slash_tmp=true",
            "-c", "sandbox_workspace_write.exclude_tmpdir_env_var=true", prompt]
    code = subprocess.run(args, cwd=target, env=environment, check=False).returncode
    if code:
        return code
    claim(settings, config)
    head = checked_git(target, "rev-parse", "HEAD")
    base = request["constraints"]["base_commit"]
    files = set()
    for argv in (("diff", "--name-only", "--no-renames", "-z", base),
                 ("ls-files", "--others", "--exclude-standard", "-z")):
        files.update(name for name in checked_git(target, *argv).split(chr(0)) if name)
    if not files or not all(any(name.startswith(prefix + "/") for prefix in settings["paths"]) for name in files):
        raise WorkerError("没有代码改动或存在授权目录之外的改动，保留工作区供独立检查。")
    if head != base and checked_git(target, "merge-base", head, base) != base:
        raise WorkerError("隔离工作区的提交脱离原授权基线。")
    if checked_git(target, "status", "--porcelain"):
        checked_git(target, "add", "--", *settings["paths"])
        checked_git(target, "diff", "--cached", "--check")
        checked_git(target, "commit", "-m", "实现已确认的 PCP 工程任务 " + request["metadata"]["task"]["id"])
    commit = checked_git(target, "rev-parse", "HEAD")
    if prior and prior.get("preserveTree"):
        if checked_git(target, "rev-parse", "HEAD^{tree}") != checked_git(target, "rev-parse", prior["commit"] + "^{tree}"):
            raise WorkerError("本次仅授权对原封存文件树复验，提交内容发生变更。")
    print(json.dumps({"type":"pcp.commit.archived","commit":commit}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (WorkerError, OSError, KeyError, ValueError, sqlite3.Error, subprocess.CalledProcessError) as error:
        print(f"已保留当前尝试供对账。{error if isinstance(error, WorkerError) else type(error).__name__}", file=sys.stderr)
        sys.exit(1)

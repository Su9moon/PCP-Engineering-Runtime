"""Read Dashboard V1 records from their owners without changing them."""
import json
import os
import queue
import re
import signal
import sqlite3
import subprocess
import threading
import time
import tomllib
from contextlib import closing
from datetime import date, datetime, timezone
from pathlib import Path
from urllib import error, parse, request

import yaml

PROJECT = "Su9moon/PCP-Engineering-Runtime"
SHA = re.compile(r"[a-f0-9]{40}")
ACTIONS = {
    "create": "EO 提供 Git/YAML 记录。未配置授权的 Job / Workorder 写入接口。",
    "dispatch": "未配置关联此 Workorder 的 ES 授权及派发适配器。",
    "provider": "面板未绑定持有此 Run 操作权限的 Autoloop 控制接口。",
    "review": "未配置授权的 EO / ES 复核写入接口。",
    "replan": "未配置面向此 Workorder 的授权 Ruflo 重规划接口。",
}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean(value):
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        return re.sub(
            r"(?i)\b(bearer\s+|(?:token|secret|api[_-]?key|password)\s*[=:]\s*)[^\s,;]+",
            r"\1[已隐藏]", value,
        )[:1800]
    return value if isinstance(value, (int, float, bool)) else None


def fields(row, *names):
    return {name: clean(row.get(name)) for name in names}


def observed(label, status, detail, **extra):
    return {"label": label, "status": status, "detail": detail, "observedAt": now(), **extra}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=4)


def database(path):
    conn = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True, timeout=2)
    conn.row_factory = sqlite3.Row
    return conn


def rows(conn, query):
    return [dict(row) for row in conn.execute(query)]


def records(root, directory, kind):
    for file in sorted(root.glob(f"{directory}/*/{kind}.yaml")):
        if not file.is_file() or not file.resolve().is_relative_to(root) or file.stat().st_size > 1_000_000:
            continue
        row = yaml.safe_load(file.read_text(encoding="utf-8"))
        if not isinstance(row, dict) or row.get(f"{kind}_id") != file.parent.name:
            continue
        path = file.relative_to(root).as_posix()
        row["path"] = path
        row["gitClean"] = (
            git(root, "ls-files", "--error-unmatch", "--", path).returncode == 0
            and not git(root, "status", "--porcelain", "--", path).stdout
        )
        yield row


def eo_records(path, formal_ref=None):
    root = Path(path).resolve()
    revision = git(root, "rev-parse", formal_ref or "HEAD").stdout.strip()
    if not SHA.fullmatch(revision):
        raise ValueError("EO checkout unavailable")

    def current(directory, kind):
        rows = {}
        if not formal_ref:
            return records(root, directory, kind)
        tree = git(root, "ls-tree", "-r", "--name-only", revision, "--", directory)
        for path in tree.stdout.splitlines():
            parts = path.split("/")
            if len(parts) != 3 or parts[2] != f"{kind}.yaml":
                continue
            result = git(root, "show", f"{revision}:{path}")
            if result.returncode or len(result.stdout) > 1_000_000:
                continue
            row = yaml.safe_load(result.stdout)
            if isinstance(row, dict) and row.get(f"{kind}_id") == parts[1]:
                rows[parts[1]] = {**row, "path":path, "gitClean":True}
        return rows.values()

    jobs = {row["job_id"]: row for row in current("jobs", "job")}
    tasks = []
    for row in current("workorders", "workorder"):
        if not any(f"{PROJECT}:" in ref for ref in row.get("input_refs", []) if isinstance(ref, str)):
            continue
        task = fields(row, "workorder_id", "job_id", "objective", "status", "created_at", "updated_at",
                      "expected_output", "path", "gitClean")
        task.update(title=clean(jobs.get(row.get("job_id"), {}).get("title")), repository=PROJECT)
        task["acceptance"] = [clean(line) for line in row.get("acceptance_criteria", [])]
        tasks.append(task)
    task_ids = {item["workorder_id"] for item in tasks}
    evidence = {row["evidence_id"]: row for row in records(root, "evidence", "evidence")}
    reviews = list(records(root, "reviews", "review"))
    results = []
    for row in records(root, "results", "result"):
        if row.get("workorder_id") not in task_ids:
            continue
        result = fields(row, "result_id", "workorder_id", "status", "summary", "conclusion", "updated_at",
                        "path", "gitClean")
        result["findings"] = [clean(line) for line in row.get("findings", [])]
        result["reviews"] = [
            fields(review, "review_id", "decision", "reviewer", "comment", "reviewed_at", "path", "gitClean")
            for review in reviews if review.get("result_id") == row["result_id"]
        ]
        result["evidence"] = []
        for evidence_id in row.get("evidence_refs", []):
            if evidence_id not in evidence:
                continue
            entry = evidence[evidence_id]
            view = fields(entry, "evidence_id", "evidence_type", "description", "verification", "path", "gitClean")
            locator = entry.get("locator") or {}
            view["locator"] = fields(locator, "kind", "revision", "sha256")
            ref = locator.get("value", "")
            prefix = f"git://{PROJECT}/commit/"
            if isinstance(ref, str) and ref.startswith(prefix) and SHA.fullmatch(ref[len(prefix):]):
                view["commit"] = ref[len(prefix):]
            result["evidence"].append(view)
        results.append(result)
    return {
        "health": observed("EO 工程记录", "connected", "读取本机 EO Git 工作区，区分跟踪记录和工作区草稿。", revision=revision),
        "tasks": tasks, "results": results,
    }


def es_records(path):
    with closing(database(path)) as conn:
        conn.execute("BEGIN")
        executions = rows(conn, """SELECT e.execution_id,e.request_id,e.state,e.updated_at,
            json_extract(r.body_json, '$.metadata.workorder_id') AS workorder_id,
            json_extract(r.body_json, '$.metadata.job_id') AS job_id
            FROM executions e JOIN requests r USING(request_id) ORDER BY e.updated_at DESC LIMIT 100""")
        attempts = rows(conn, """SELECT execution_id,attempt_id,invocation_id,state,runtime_ref,started_at,ended_at
                                 FROM attempts ORDER BY created_at""")
        reviews = rows(conn, """SELECT execution_id,attempt_id,decision,resulting_state,created_at
                                FROM reviews ORDER BY created_at""")
    for item in executions:
        item["attempts"] = [row for row in attempts if row["execution_id"] == item["execution_id"]]
        item["reviews"] = [row for row in reviews if row["execution_id"] == item["execution_id"]]
    return {
        "health": observed("ES 执行记录", "history", "读取现有 ExecutionKernel SQLite，按请求 metadata 关联工单。"),
        "executions": executions,
    }


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def hub_state(config):
    url = parse.urlsplit(config["url"])
    if (url.username or url.password or url.query or url.fragment or not url.hostname or url.path not in ("", "/")
            or (url.scheme != "https" and not (url.scheme == "http" and url.hostname in {"127.0.0.1", "::1", "localhost"}))):
        raise ValueError("Unsupported Hub URL")
    owner = config.get("owner")
    if not owner:
        raise ValueError("Hub owner credential absent")
    req = request.Request(config["url"].rstrip("/") + "/v1/state", headers={"Authorization": f"Bearer {owner}"})
    opener = request.build_opener(request.ProxyHandler({}), NoRedirect())
    with opener.open(req, timeout=2) as response:
        raw = response.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError("Hub response too large")
    return json.loads(raw)


def receipt_artifacts(path):
    artifacts = {}
    if not path:
        return artifacts
    for row in read_json(path).values():
        item = row.get("result") or {}
        run = (item.get("hub") or {}).get("run")
        event = row.get("event")
        if type(run) is not int or type(event) is not int:
            continue
        sha = item.get("commit")
        log = item.get("worker_log")
        artifacts[(run, event)] = {
            "commit": sha if isinstance(sha, str) and SHA.fullmatch(sha) else None,
            "files": [clean(file) for file in item.get("files", []) if isinstance(file, str)][:30],
            "exitCode": clean(item.get("worker_exit")),
            "thread": clean(item.get("session")),
            "log": Path(log).name if isinstance(log, str) else None,
        }
    return artifacts


def archived_hub(path, receipts):
    with closing(database(path)) as conn:
        conn.execute("BEGIN")
        runs = rows(conn, """SELECT id,rule,agent,state,attempts,session,created_at AS createdAt,claimed_at AS claimedAt,
                             finished_at AS finishedAt,summary,error FROM runs ORDER BY id DESC LIMIT 80""")
        events = rows(conn, """SELECT re.run_id,e.id,e.type,e.source,e.subject,e.received_at AS receivedAt
                               FROM run_events re JOIN events e ON e.id=re.event_id ORDER BY e.id DESC""")
        workers = rows(conn, "SELECT name,seen_at AS seenAt FROM seen WHERE kind='worker' ORDER BY seen_at DESC")
    for run in runs:
        run["events"] = [fields(row, "id", "type", "source", "subject", "receivedAt") for row in events if row["run_id"] == run["id"]]
        artifacts = [receipts[(run["id"], e["id"])] for e in run["events"] if (run["id"], e["id"]) in receipts]
        run["delivery"] = artifacts[0] if len(artifacts) == 1 else None
        run["mode"] = "history"
    return runs, workers


def provider(name, config_file, projection=None, receipts=None):
    live = None
    try:
        live = hub_state(read_json(config_file))
        health = observed(name, "connected", "Autoloop GET /v1/state 当前响应。", sourceAt=clean(live.get("now")))
    except error.HTTPError as exc:
        health = observed(name, "blocked" if exc.code in {401, 403} else "failed", f"Autoloop GET /v1/state HTTP {exc.code}。")
    except (TimeoutError, ConnectionError, error.URLError):
        health = observed(name, "disconnected", "配置的 Autoloop Hub 当前不可达。")
    except (OSError, KeyError, ValueError, TypeError, AttributeError):
        health = observed(name, "unconfigured", "Autoloop Hub 读取配置或响应不可用。")
    runs, workers, history_error = [], [], False
    if projection:
        try:
            runs, workers = archived_hub(projection, receipt_artifacts(receipts))
        except (OSError, sqlite3.Error, ValueError, TypeError, AttributeError):
            history_error = True
    if isinstance(live, dict):
        stored = {row["id"]: row for row in runs}
        for row in live.get("runs", []):
            if type(row.get("id")) is not int:
                continue
            prior = stored.get(row["id"], {})
            events = prior.get("events") or [fields(e, "id", "source", "type", "subject") for e in row.get("events", [])]
            stored[row["id"]] = {
                **fields(row, "id", "rule", "agent", "state", "attempts", "session", "createdAt", "claimedAt",
                         "finishedAt", "error", "summary"),
                "events": events, "delivery": prior.get("delivery"), "mode": "live",
            }
        runs = sorted(stored.values(), key=lambda row: row["id"], reverse=True)
        by_worker = {item["name"]: item for item in workers}
        by_agent = {}
        for agent in live.get("agents", []):
            worker_name = clean(agent.get("worker"))
            if not isinstance(worker_name, str) or not worker_name:
                continue
            by_agent[agent.get("id")] = worker_name
            worker = by_worker.setdefault(worker_name, {"name": worker_name})
            worker.update(fields(agent, "seenAt", "online"))
            executor = clean(agent.get("use"))
            if executor:
                worker["executors"] = sorted(set([*worker.get("executors", []), executor]))
        for run in runs:
            if run["mode"] == "live" and run["agent"] in by_agent:
                run["worker"] = by_agent[run["agent"]]
                if run["state"] == "claimed":
                    by_worker[run["worker"]].setdefault("activeRuns", []).append(run["id"])
        workers = list(by_worker.values())
    for run in runs:
        run.update(pool=name, summary=clean(run.get("summary")), error=clean(run.get("error")))
    for worker in workers:
        worker["pool"] = name
    if history_error:
        health["detail"] += " 历史投影读取失败。"
    return {"health": health, "runs": runs, "workers": workers}


def mcp_snapshot(process):
    replies = queue.Queue()

    def receive():
        for line in process.stdout:
            try:
                value = json.loads(line)
            except ValueError:
                continue
            if isinstance(value, dict) and "id" in value:
                replies.put(value)
        replies.put(None)

    def rpc(method, ident=None, **params):
        message = {"jsonrpc": "2.0", "method": method}
        if ident is not None:
            message.update(id=ident, params=params)
        process.stdin.write(json.dumps(message) + "\n")
        process.stdin.flush()
        if ident is None:
            return None
        try:
            reply = replies.get(timeout=22)
        except queue.Empty as exc:
            raise TimeoutError(method) from exc
        if reply is None or reply.get("id") != ident or "error" in reply:
            raise RuntimeError(method)
        return reply["result"]

    def tool(name, ident):
        result = rpc("tools/call", ident, name=name, arguments={})
        if result.get("isError"):
            raise RuntimeError(name)
        if isinstance(result.get("structuredContent"), dict):
            return result["structuredContent"]
        for item in result.get("content", []):
            try:
                value = json.loads(item.get("text", ""))
            except ValueError:
                continue
            if isinstance(value, dict):
                return value
        raise RuntimeError(name)

    threading.Thread(target=receive, daemon=True).start()
    info = rpc("initialize", 1, protocolVersion="2024-11-05", capabilities={},
               clientInfo={"name": "pcp-control-center", "version": "1"})
    rpc("notifications/initialized")
    tool("mcp_status", 2)
    health = observed("Ruflo MCP", "connected", "本机 stdio 已响应 mcp_status。",
                      version=clean(info.get("serverInfo", {}).get("version")))
    try:
        result = tool("agent_list", 3)
    except (RuntimeError, TimeoutError):
        return {"health": health, "registration": "unavailable", "agents": []}
    agents = result.get("agents")
    available = isinstance(agents, list) and result.get("success", True)
    return {"health": health, "registration": "observed" if available else "unavailable", "agents": [
        fields(item, "id", "agentId", "name", "type", "agentType", "status", "model", "lastActiveAt", "assignment")
        for item in agents if isinstance(item, dict)
    ] if available else []}


class RufloProbe:
    def __init__(self, settings):
        self.settings = settings
        self.lock = threading.Lock()
        self.last_start = None
        self.snapshot = {"health": observed("Ruflo MCP", "unverified", "等待本机 stdio 探测。"), "agents": []}

    def refresh(self):
        with self.lock:
            if self.last_start is None or time.monotonic() - self.last_start >= 90:
                self.last_start = time.monotonic()
                threading.Thread(target=self.probe, daemon=True).start()
            return self.snapshot

    def probe(self):
        process = None
        try:
            config = tomllib.loads(Path(self.settings["config"]).read_text())["mcp_servers"]["ruflo"]
            command, args = config["command"], config["args"]
            if not config.get("enabled", True) or Path(command).name != "npx" or args[-2:] != ["mcp", "start"]:
                raise ValueError("Missing authorized Ruflo stdio entry")
            env = {**os.environ, "npm_config_offline": "true", "PATH": str(Path(command).parent) + ":" + os.environ["PATH"]}
            process = subprocess.Popen(
                [command, *args], cwd=self.settings["cwd"], env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, start_new_session=True, text=True,
            )
            self.snapshot = mcp_snapshot(process)
        except (OSError, KeyError, ValueError, RuntimeError, TimeoutError, TypeError) as exc:
            detail = "本机 stdio 未配置。" if not self.settings else f"本机 stdio 探测失败（{type(exc).__name__}）。"
            self.snapshot = {"health": observed("Ruflo MCP", "disconnected", detail), "agents": []}
        finally:
            if process is not None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                    process.wait(timeout=3)
                except ProcessLookupError:
                    pass
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()


def supervisor_record(path):
    if not path:
        return None
    row = read_json(path)
    return {
        **fields(row, "supervisor", "model", "durationMs", "messageId"),
        "observedAt": datetime.fromtimestamp(Path(path).stat().st_mtime, timezone.utc).isoformat(),
        "effort": "NOT_EXPOSED_BY_RUNTIME",
    }


def commit_details(repo, sha):
    result = git(repo, "show", "--format=%H%n%aI%n%s", "--no-ext-diff", "--name-only", sha)
    lines = result.stdout.splitlines()
    if result.returncode or len(lines) < 3 or lines[0] != sha:
        return None
    return {"commit": sha, "date": lines[1], "subject": clean(lines[2]), "files": [clean(line) for line in lines[3:] if line][:50]}


class Sources:
    def __init__(self, config, repo):
        self.config = config
        self.repo = repo
        self.ruflo = RufloProbe(config.get("ruflo"))

    def snapshot(self):
        ruflo = self.ruflo.refresh()
        try:
            eo = eo_records(self.config["eo"], self.config.get("eo_ref"))
        except (OSError, KeyError, ValueError, yaml.YAMLError, subprocess.TimeoutExpired, TypeError):
            eo = {"health": observed("EO 工程记录", "unavailable", "EO Git 工作区或 YAML 记录无法读取。"), "tasks": [], "results": []}
        try:
            es = es_records(self.config["es"])
        except (OSError, KeyError, ValueError, sqlite3.Error):
            es = {"health": observed("ES 执行记录", "unavailable", "未配置可读取的 ExecutionKernel SQLite。"), "executions": []}
        hubs = [provider(**hub) for hub in self.config.get("hubs", [])]
        try:
            supervisor = supervisor_record(self.config.get("supervisor_evidence"))
        except (OSError, ValueError, TypeError):
            supervisor = None
        shas = {item["commit"] for result in eo["results"] for item in result["evidence"] if "commit" in item}
        commits = {sha: commit_details(self.repo, sha) for sha in shas}
        return {
            "observedAt": now(), "actions": ACTIONS, "eo": eo, "es": es, "hubs": hubs, "ruflo": ruflo,
            "supervisor": supervisor, "commits": commits,
            "connections": [
                observed("Dashboard HTTPS", "connected", "本机与已配置的局域网入口均免登录。"),
                observed("GitHub", "unverified", "提供 GitHub 源码定位。当前仅核验本机 Git 对象。"),
                observed("GPT ↔ Ruflo", "deferred", "直接管理延期到下一版本。"),
            ],
        }

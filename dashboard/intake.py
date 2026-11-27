"""Project-local, resumable conversational intake drafts and EO exports."""
from contextlib import contextmanager
import fcntl
import json
import os
import re
import tempfile
import threading
import uuid
from pathlib import Path
from subprocess import TimeoutExpired

import yaml

from formal import Formal, FormalError, plan_digest
from engineering import Engineering
from intake_context import ProjectContext
from operator_grant import FORMAL_ACTIONS
from planning import LocalPlanner, PlanError, draft_basis as basis, new_revision, normalize_plan
from sources import PROJECT, now

FIELDS = {
    "goal": "目标与问题", "users": "用户与使用场景", "scope": "实施范围",
    "exclusions": "排除范围", "constraints": "约束", "dependencies": "依赖",
    "deliverables": "预期交付物", "acceptance": "验收条件", "risks": "风险与假设",
    "questions": "待确认问题", "recommendation": "执行方式建议",
}
PROVENANCE = {
    "USER_CONFIRMED": "用户确认", "AI_SUGGESTED": "AI 建议",
    "AI_INFERRED": "AI 推断", "UNRESOLVED": "未决",
}
LLM_GAP = "此 Dashboard 未配置 Intake 专用的服务端 LLM API 端点、模型和认证。当前可手动记述、编辑和生成模板文稿。"
EO_GAP = "现有 EO checkout 提供 Git/YAML 模板与记录。此 Dashboard 未配置授权的 EO Job/Workorder 写入接口，可导出草稿。"
SECRET = re.compile(
    r"(?i)(?:\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[a-z0-9]{20,})"
    r"|\bBearer\s+[a-z0-9._~+/=-]{12,}"
    r"|(?:\b(?:password|token|api[_ -]?key)|密码|令牌|密钥)\s*[:=：]\s*\S+"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)
ID = re.compile(r"[0-9a-f]{32}")


class IntakeError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def text_input(value, limit=5000):
    if not isinstance(value, str) or len(value) > limit:
        raise IntakeError(f"请填写不超过 {limit} 字的内容。")
    if SECRET.search(value):
        raise IntakeError("内容疑似包含凭据。请移除密码、密钥或令牌再保存。")
    return value.strip()


def dossier_value(draft, field):
    item = draft["dossier"][field]
    return item["value"] if item["provenance"] == "USER_CONFIRMED" else ""


def eo_templates(path):
    if not path:
        return None, "此部署未配置本机 EO checkout，无法读取 Job/Workorder 模板。"
    templates = {}
    for kind in ("job", "workorder"):
        file = Path(path) / "templates" / f"{kind}.template.yaml"
        try:
            template = yaml.safe_load(file.read_text())
        except (OSError, yaml.YAMLError):
            return None, f"EO 草稿导出缺少 templates/{kind}.template.yaml。"
        if not isinstance(template, dict) or f"{kind}_id" not in template:
            return None, f"EO 模板结构异常：templates/{kind}.template.yaml。"
        templates[kind] = template
    return templates, EO_GAP


def build_documents(draft, templates):
    title = dossier_value(draft, "goal").splitlines()[0][:100] if dossier_value(draft, "goal") else draft["title"]
    project = draft["project"] or "待确认"
    brief = [f"# 需求说明 · {title}", "", f"项目：{project}", "", "来源：本地文档模板与当前需求档案。", ""]
    for field, label in FIELDS.items():
        item = draft["dossier"][field]
        brief.extend((f"## {label} · {PROVENANCE[item['provenance']]}", "", item["value"] or "待确认。", ""))
    brief.extend(("## 项目与经验来源", ""))
    for source in draft["context"]["items"]:
        brief.append(f"- {source['repository']}@{source['commit']}:{source['path']} [{source['maturity']}] {source['reason']}")
    for gap in draft["context"]["unavailable"]:
        brief.append(f"- 来源不可用：{gap}")
    brief.extend(("", "## 对话记录", ""))
    brief.extend(
        f"- {entry['at']} {'Ruflo' if entry['role'] == 'assistant' else '用户'}：{entry['text']}"
        for entry in draft["messages"]
    )
    docs = [{"filename": "requirements.md", "title": "需求与验收说明", "text": "\n".join(brief) + "\n"}]
    if not templates:
        return docs
    def pending(field):
        return dossier_value(draft, field) or "待确认"

    def list_value(field):
        return [line.strip() for line in dossier_value(draft, field).splitlines() if line.strip()]

    job_id, workorder_id = templates["job"]["job_id"], templates["workorder"]["workorder_id"]
    job = {
        **templates["job"], "title": title, "goal": pending("goal"), "context": f"项目：{project}\n{pending('users')}",
        "scope": list_value("scope"), "acceptance_objective": pending("acceptance"),
        "workorder_refs": [workorder_id], "status": "DRAFT", "created_at": now(), "created_by": "human:dashboard",
    }
    constraints = list_value("constraints") + list_value("exclusions")
    if not constraints:
        constraints = ["待确认"]
    refs = [
        f"{source['repository']}@{source['commit']}:{source['path']}"
        for source in draft["context"]["items"] if source["authoritative"]
    ]
    workorder = {
        **templates["workorder"], "job_id": job_id, "objective": pending("goal"), "input_refs": refs,
        "constraints": constraints, "expected_output": pending("deliverables"),
        "acceptance_criteria": list_value("acceptance") or ["待确认"], "status": "DRAFT",
        "created_at": now(), "created_by": "human:dashboard",
    }
    note = "# EO 导出草稿。占位 ID 由 EO 的正式流程分配。非权威参考和未决项见 requirements.md。\n"
    docs.extend(
        {"filename": f"{kind}.yaml", "title": f"EO {label} 草稿",
         "text": note + yaml.safe_dump(content, allow_unicode=True, sort_keys=False)}
        for kind, label, content in (("job", "Job", job), ("workorder", "Workorder", workorder))
    )
    return docs


def review_state(draft):
    if not draft["packages"]:
        return "intake"
    latest = draft["packages"][-1]
    if latest["basis"] != basis(draft):
        return "changed"
    return "confirmed" if latest["confirmedAt"] else "review"


class Intake:
    def __init__(self, settings, project_repo, eo_repo, grant=None, es_database=None):
        self.directory = Path(settings["directory"])
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        if self.directory.is_symlink() or self.directory.stat().st_mode & 0o077:
            raise OSError("Intake data directory must be private and must not be a symlink")
        self.context = ProjectContext(project_repo, settings["pcp_repo"])
        self.templates, self.eo_gap = eo_templates(eo_repo)
        self.planner = LocalPlanner(settings.get("planner"))
        self.formal = None
        formal_settings = (grant or {}).get("engineering") or (grant or {}).get("formal")
        if es_database and isinstance(formal_settings, dict) and formal_settings.get("eoRepo") == eo_repo:
            try:
                self.formal = (Engineering(formal_settings, es_database, build_documents, project_repo, self.planner)
                               if grant.get("engineering") else Formal(formal_settings, es_database, build_documents))
            except (KeyError, FormalError):
                pass
        self.lock = threading.Lock()

    def config_view(self):
        return {"project": PROJECT, "fields": FIELDS, "provenance": PROVENANCE, "llmGap": LLM_GAP,
                "eoGap": self.eo_gap, "plannerAvailable": self.planner.available(),
                "executionGap": "该草稿未关联正式 EO Workorder 或有效 ES 授权。Autoloop 派发与运行控制尚未接通。"}

    @contextmanager
    def write_lock(self):
        lock_path = self.directory / ".draft-write"
        descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        with self.lock, os.fdopen(descriptor, "a+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def path(self, ident):
        if not ID.fullmatch(ident):
            raise IntakeError("草稿不存在。", 404)
        return self.directory / f"{ident}.json"

    def load(self, ident):
        try:
            fd = os.open(self.path(ident), os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(fd, encoding="utf-8") as file:
                draft = json.load(file)
        except FileNotFoundError:
            raise IntakeError("草稿不存在。", 404) from None
        if draft["id"] != ident:
            raise IntakeError("无法恢复该草稿的身份。", 409)
        return draft

    def save(self, draft):
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.directory, delete=False) as file:
            temporary = Path(file.name)
            try:
                json.dump(draft, file, ensure_ascii=False)
                file.flush()
                os.fsync(file.fileno())
                temporary.replace(self.path(draft["id"]))
            finally:
                temporary.unlink(missing_ok=True)
        fd = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def create(self, message):
        message = text_input(message)
        if not message:
            raise IntakeError("请先用一句话描述目标。")
        now_ = now()
        draft = {
            "id": uuid.uuid4().hex, "version": 1, "title": message.splitlines()[0][:90],
            "updatedAt": now_, "createdAt": now_, "project": None,
            "messages": [{"role": "user", "text": message, "at": now_}],
            "dossier": {field: {"value": "", "provenance": "UNRESOLVED"} for field in FIELDS},
            "context": {"items": [], "unavailable": [], "searched": [], "terms": []},
            "packages": [],
        }
        self.save(draft)
        return draft

    def recent(self):
        summaries = []
        paths = sorted(
            (path for path in self.directory.glob("*.json") if ID.fullmatch(path.stem) and not path.is_symlink()),
            key=lambda path: path.stat().st_mtime_ns, reverse=True,
        )
        for file in paths[:60]:
            draft = self.load(file.stem)
            summaries.append({**{key: draft[key] for key in ("id", "title", "updatedAt", "project")},
                              "status": review_state(draft)})
        return summaries

    def read(self, ident):
        with self.lock:
            if ident is None:
                return {"drafts": self.recent(), "capabilities": self.config_view()}
            draft = self.load(ident)
            return {"draft": draft, "status": review_state(draft), "capabilities": self.config_view()}

    def update(self, ident, body):
        if ident is not None and body.get("action") == "plan_generate":
            return self.generate_plan(ident, body)
        if ident is not None and body.get("action") == "ai_reply":
            return self.ai_reply(ident, body)
        with self.write_lock():
            if ident is None:
                if body.get("action") != "message":
                    raise IntakeError("请先创建对话草稿。")
                draft = self.create(body.get("text"))
            else:
                draft = self.load(ident)
                self.check_version(draft, body)
                self.apply(draft, body)
                draft["version"] += 1
                draft["updatedAt"] = now()
                self.save(draft)
            return {"draft": draft, "status": review_state(draft), "capabilities": self.config_view()}

    @staticmethod
    def check_version(draft, body):
        if type(body.get("version")) is not int or body["version"] != draft["version"]:
            raise IntakeError("草稿已有新版本，请重新打开后再提交。", 409)

    @staticmethod
    def confirmed_package(draft):
        if review_state(draft) != "confirmed":
            raise IntakeError("请先确认当前工程文档版本。", 409)
        return draft["packages"][-1]

    def generate_plan(self, ident, body):
        with self.lock:
            draft = self.load(ident)
            self.check_version(draft, body)
            package = self.confirmed_package(draft)
            if draft["project"] != PROJECT:
                raise IntakeError("请先关联当前 Runtime 项目。")
            prior = (draft.get("plans") or [None])[-1]
            if (prior and prior["documentRevision"] == package["revision"]
                    and prior["basis"] == package["basis"] and prior["plan"]["mode"] == "manual"):
                raise IntakeError("当前是人工编排。请先显式保存为建议模式，再请求 Ruflo 建议。", 409)
        try:
            raw, evidence = self.planner.propose(draft, package)
            plan = normalize_plan(raw, text_input)
        except PlanError as exc:
            raise IntakeError(str(exc), 503) from exc
        with self.write_lock():
            current = self.load(ident)
            self.check_version(current, body)
            plans = current.setdefault("plans", [])
            plans.append(new_revision(plans, package, plan, reason="基于当前确认文档生成建议", evidence=evidence))
            current["version"] += 1
            current["updatedAt"] = now()
            self.save(current)
        return {"draft": current, "status": review_state(current), "capabilities": self.config_view()}

    def ai_reply(self, ident, body):
        with self.lock:
            draft = self.load(ident)
            self.check_version(draft, body)
            if draft["project"] != PROJECT or draft["messages"][-1]["role"] != "user":
                raise IntakeError("请关联现有项目并先保存一条用户消息。", 409)
        try:
            raw, evidence = self.planner.converse(draft)
            message = text_input(raw)
            if not message:
                raise PlanError("Ruflo 没有返回可保存的对话。")
        except PlanError as exc:
            raise IntakeError(str(exc), 503) from exc
        with self.write_lock():
            current = self.load(ident)
            self.check_version(current, body)
            current["messages"].append({"role": "assistant", "text": message, "ruflo": evidence, "at": now()})
            current["version"] += 1
            current["updatedAt"] = now()
            self.save(current)
        return {"draft": current, "status": review_state(current), "capabilities": self.config_view()}

    def apply(self, draft, body):
        action = body.get("action")
        if action == "message":
            message = text_input(body.get("text"))
            if not message:
                raise IntakeError("请输入要保存的内容。")
            draft["messages"].append({"role": "user", "text": message, "at": now()})
        elif action == "project":
            if body.get("project") != PROJECT:
                raise IntakeError("请选择此部署已核验的 Runtime 仓库。其他项目可另开待识别草稿。")
            draft["project"] = PROJECT
            self.retrieve(draft, "")
        elif action == "retrieve":
            if draft["project"] != PROJECT:
                raise IntakeError("请先关联现有项目，再检索其来源。")
            self.retrieve(draft, text_input(body.get("terms"), limit=250))
        elif action == "field":
            field = body.get("field")
            provenance = body.get("provenance")
            if not isinstance(field, str) or field not in FIELDS or provenance not in ("USER_CONFIRMED", "UNRESOLVED"):
                raise IntakeError("需求字段或来源状态无效。")
            value = text_input(body.get("value"))
            draft["dossier"][field] = {"value": value, "provenance": provenance if value else "UNRESOLVED"}
            if field == "goal" and value and provenance == "USER_CONFIRMED":
                draft["title"] = value.splitlines()[0][:90]
        elif action == "generate":
            draft["packages"].append({
                "revision": len(draft["packages"]) + 1, "createdAt": now(), "confirmedAt": None,
                "basis": basis(draft), "project": draft["project"], "sources": draft["context"]["items"],
                "documents": build_documents(draft, self.templates),
            })
        elif action == "confirm":
            packages = draft["packages"]
            if (not packages or type(body.get("revision")) is not int
                    or packages[-1]["revision"] != body["revision"] or packages[-1]["basis"] != basis(draft)):
                raise IntakeError("需求或来源已发生变化。请重新生成并预览当前版本。", 409)
            if not packages[-1]["confirmedAt"]:
                packages[-1]["confirmedAt"] = now()
        elif action in FORMAL_ACTIONS:
            try:
                self.apply_formal(draft, action, body)
            except FormalError as exc:
                raise IntakeError(str(exc), 409) from exc
            except RuntimeError as exc:
                raise IntakeError("ES 拒绝该状态变更，请从权威记录对账后再继续。", 409) from exc
        elif action in ("plan_save", "plan_confirm"):
            if draft["project"] not in (None, PROJECT):
                raise IntakeError("工程计划须关联本服务配置的 Runtime 仓库。", 403)
            package = self.confirmed_package(draft)
            plans = draft.setdefault("plans", [])
            if action == "plan_save":
                try:
                    plan = normalize_plan(body.get("plan"), text_input)
                except PlanError as exc:
                    raise IntakeError(str(exc)) from exc
                plans.append(new_revision(plans, package, plan, reason=text_input(body.get("reason", ""), 500)))
            else:
                if (not plans or type(body.get("revision")) is not int
                        or plans[-1]["revision"] != body["revision"]
                        or plans[-1]["documentRevision"] != package["revision"] or plans[-1]["basis"] != package["basis"]):
                    raise IntakeError("工程计划与当前确认文档不匹配。请保存新的计划版本。", 409)
                plan = plans[-1]["plan"]
                if plan["mode"] == "autonomous":
                    if not plan["scope"]:
                        raise IntakeError("请先填写自主编排的仓库与路径范围。")
                    if not plan["authorization"]:
                        raise IntakeError("请先填写自主编排的拟授权操作。")
                plans[-1]["confirmedAt"] = plans[-1]["confirmedAt"] or now()
        else:
            raise IntakeError("此草稿操作不可用。")

    def apply_formal(self, draft, action, body):
        if isinstance(self.formal, Engineering):
            self.apply_engineering(draft, action, body)
            return
        if self.formal is None:
            raise IntakeError("当前部署未启用 EO / ES 执行连接。", 503)
        if draft["project"] != PROJECT:
            raise IntakeError("项目不在正式执行授权范围内。", 403)
        if action == "formal_observe" and (binding := draft.get("formal")):
            observation = self.formal.observe(binding)
            binding["observed"] = observation
            if provider := observation.get("provider"):
                binding["dispatch"] = {"event": provider["event"], "run": provider["run"],
                                       "invocation": observation["invocation"]}
            return
        package = self.confirmed_package(draft)
        latest = (draft.get("plans") or [None])[-1]
        if not latest or not latest["confirmedAt"] or latest["basis"] != package["basis"] or latest["documentRevision"] != package["revision"]:
            raise IntakeError("请确认当前需求文档与对应工程计划。", 409)
        if dossier_value(draft, "goal") != self.formal.settings["objective"]:
            raise IntakeError("该目标不在非生产测试任务的服务端授权范围内。", 403)
        ref = {"documentRevision": package["revision"], "planRevision": latest["revision"]}
        binding = draft.get("formal")
        if binding and any(binding.get(k) != v for k, v in ref.items()):
            raise IntakeError("已有正式工单。当前版本的修改尚未获得新的执行授权。", 409)
        if action == "formal_create" and not binding:
            eo = self.formal.record(draft, package, latest)
            admission = self.formal.request(eo)
            draft["formal"] = {**ref, **eo, "request": admission["request_id"], "execution": admission["execution_id"]}
        elif action == "formal_dispatch" and binding:
            binding["dispatch"] = self.formal.dispatch(binding)
        elif not binding:
            raise IntakeError("请先创建正式 EO 工单。", 409)

    def apply_engineering(self, draft, action, body):
        if draft["project"] != PROJECT:
            raise IntakeError("项目不在服务端登记的非生产执行范围内。", 403)
        binding = draft.get("formal")
        if binding and binding.get("kind") != "engineering":
            raise IntakeError("历史正式任务仅供查看。", 403)
        if binding and action == "formal_observe":
            return
        if binding and action == "formal_hold":
            if type(body.get("held")) is not bool:
                raise IntakeError("当前接管选项无效。")
            binding["held"] = body["held"]
            binding["manualControl"] = {"at": now(), "held": body["held"], **body["serviceAuthority"]}
            return
        package = self.confirmed_package(draft)
        latest = (draft.get("plans") or [None])[-1]
        if not latest or not latest["confirmedAt"] or latest["basis"] != package["basis"] or latest["documentRevision"] != package["revision"]:
            raise IntakeError("请先确认当前需求文档及对应工程计划。", 409)
        if action == "formal_create" and not binding:
            draft["formal"] = self.formal.register(draft, package, latest)
        elif not binding:
            raise IntakeError("请先将此确认计划登记为 EO 工单。", 409)
        elif action == "formal_dispatch":
            if latest["plan"]["mode"] == "suggestion":
                raise IntakeError("请先保存为人工或自主编排模式并确认。", 409)
            if (binding["documentRevision"] != package["revision"] or binding["planRevision"] != latest["revision"]
                    or binding["basis"] != package["basis"]
                    or binding["planSha256"] != plan_digest(latest)):
                raise IntakeError("正式工单的已确认版本已变化。请保留原记录并新建需求。", 409)
            if not binding.get("authorizedAt"):
                binding["authorizedAt"] = now()
                binding["authorizedBy"] = body["serviceAuthority"]
                binding["state"] = "已下达，等待权威运行回执"

    def retrieve(self, draft, terms):
        try:
            draft["context"] = self.context.collect(terms, draft["context"])
        except (OSError, TimeoutExpired) as exc:
            raise IntakeError("本机 Git 来源不可读取。请稍后再检索。", 503) from exc

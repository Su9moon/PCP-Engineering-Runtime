"""Project-local, resumable conversational intake drafts and EO exports."""
import hashlib
import json
import os
import re
import tempfile
import threading
import uuid
from pathlib import Path
from subprocess import TimeoutExpired

import yaml

from intake_context import ProjectContext
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


def basis(draft):
    evidence = [draft["project"], draft["messages"], draft["dossier"], draft["context"]]
    content = json.dumps(evidence, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(content.encode()).hexdigest()


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
    brief.extend(f"- {entry['at']} 用户：{entry['text']}" for entry in draft["messages"])
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
    def __init__(self, settings, project_repo, eo_repo):
        self.directory = Path(settings["directory"])
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        if self.directory.is_symlink() or self.directory.stat().st_mode & 0o077:
            raise OSError("Intake data directory must be private and must not be a symlink")
        self.context = ProjectContext(project_repo, settings["pcp_repo"])
        self.templates, self.eo_gap = eo_templates(eo_repo)
        self.lock = threading.Lock()

    def config_view(self):
        return {"project": PROJECT, "fields": FIELDS, "provenance": PROVENANCE, "llmGap": LLM_GAP, "eoGap": self.eo_gap}

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
        with self.lock:
            if ident is None:
                if body.get("action") != "message":
                    raise IntakeError("请先创建对话草稿。")
                draft = self.create(body.get("text"))
            else:
                draft = self.load(ident)
                if type(body.get("version")) is not int or body["version"] != draft["version"]:
                    raise IntakeError("草稿已有新版本，请重新打开后再提交。", 409)
                self.apply(draft, body)
                draft["version"] += 1
                draft["updatedAt"] = now()
                self.save(draft)
            return {"draft": draft, "status": review_state(draft), "capabilities": self.config_view()}

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
        else:
            raise IntakeError("此草稿操作不可用。")

    def retrieve(self, draft, terms):
        try:
            draft["context"] = self.context.collect(terms, draft["context"])
        except (OSError, TimeoutExpired) as exc:
            raise IntakeError("本机 Git 来源不可读取。请稍后再检索。", 503) from exc

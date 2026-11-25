"""Bounded retrieval from the selected Runtime worktree and pinned PCP Git sources."""
import re
import subprocess
from pathlib import Path

from sources import PROJECT, SHA, clean

PCP = "Su9moon/personal-ai-control-plane"
PCP_COMMIT = "22bae955686f03c5f440cdcd66e13a69f1289f90"
HANDOFF_COMMIT = "b05d96d2e74b90ff77844aff2b4fe157b6e1f651"
WORKORDER = "workorders/WO-20261126-001-PCP-ENGINEERING-CONTROL-CENTER-CONVERSATIONAL-INTAKE-V1.1.md"
BASELINES = (
    ("governance/adr/ADR-2026-11-22-001_pcp-engineering-runtime.md", "工程 Runtime 的集成范围与 EO/ES 职责"),
    ("processes/experience-reuse-gate.md", "经验检索顺序与证据权限"),
    ("governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md", "执行建议和实际运行证据的区分"),
)
PROJECT_FILES = (
    ("AGENTS.md", "仓库执行规则"),
    ("README.md", "项目边界与集成入口"),
    ("PROJECT_STATUS.md", "最近的已提交实现和验收状态"),
    (WORKORDER, "本次对话入口的实施和验收边界"),
)
EXPERIENCE_PATHS = (
    ("assets/validated", "VALIDATED", True),
    ("assets/candidates", "CANDIDATE", False),
    ("assets/inbox/sources", "INBOX", False),
)
TERM = re.compile(r"[\w-]{2,32}", re.UNICODE)


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=False, capture_output=True,
        timeout=4, encoding="utf-8", errors="replace",
    )


def terms_for(text):
    return list(dict.fromkeys(term.casefold() for term in TERM.findall(text) if not term.isdecimal()))[:8]


def git_source(repo, identity, revision, path, maturity, authoritative, reason, terms=()):
    ref = f"{revision}:{path}"
    result = git(repo, "show", ref)
    if result.returncode:
        return None
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    title = next((line.lstrip("# ") for line in lines if line.startswith("# ")), Path(path).stem)
    matches = [line for line in lines if any(term in line.casefold() for term in terms)]
    return {
        "repository": identity, "path": path, "commit": revision, "title": clean(title)[:200],
        "maturity": maturity, "authoritative": authoritative, "reason": reason,
        "excerpt": clean(" ".join((matches or lines[1:])[:2]))[:380],
    }


def lookup(repo, identity, revision, areas, terms, maturity, authoritative, *, limit=3):
    if not terms:
        return [], False
    args = [argument for term in terms for argument in ("-e", term)]
    result = git(repo, "grep", "-l", "-z", "-i", "-F", *args, revision, "--", *areas)
    if result.returncode not in (0, 1):
        return [], True
    prefix = f"{revision}:"
    paths = [value[len(prefix):] for value in result.stdout.split("\0") if value.startswith(prefix)]
    items = []
    for path in paths:
        if not path.endswith(".md") or path == WORKORDER:
            continue
        item = git_source(
            repo, identity, revision, path, maturity, authoritative,
            "命中本次检索词。候选和 Inbox 仅供参考。" if not authoritative else "命中本次检索词，可供当前需求参考。",
            terms,
        )
        if item:
            items.append(item)
        if len(items) == limit:
            break
    return items, False


class ProjectContext:
    def __init__(self, project_repo, pcp_repo, *, pcp_commit=PCP_COMMIT, handoff_commit=HANDOFF_COMMIT):
        self.project_repo = Path(project_repo)
        self.pcp_repo = Path(pcp_repo)
        self.pcp_commit = pcp_commit
        self.handoff_commit = handoff_commit

    def collect(self, text, cached):
        terms = terms_for(text)
        revision = git(self.project_repo, "rev-parse", "HEAD").stdout.strip()
        key = [revision, self.pcp_commit, terms]
        if cached and cached.get("key") == key and not cached.get("unavailable"):
            return cached
        items, gaps, searched = [], [], []
        if not SHA.fullmatch(revision):
            gaps.append(f"{PROJECT}: HEAD 无法读取")
        else:
            for path, reason in PROJECT_FILES:
                source = git_source(self.project_repo, PROJECT, revision, path, "PROJECT", True, reason, terms)
                if source is None and path == WORKORDER:
                    source = git_source(self.project_repo, PROJECT, self.handoff_commit, path, "PROJECT", True, reason, terms)
                if source:
                    items.append(source)
                else:
                    gaps.append(f"{PROJECT}:{path}@{revision}")
            references, failed = lookup(
                self.project_repo, PROJECT, revision, ("docs/engineering", "reports"), terms, "PROJECT", True, limit=2,
            )
            items.extend(references)
            if failed:
                gaps.append(f"{PROJECT}: docs/engineering, reports@{revision}")
        if git(self.pcp_repo, "cat-file", "-e", f"{self.pcp_commit}^{{commit}}").returncode:
            gaps.append(f"{PCP}@{self.pcp_commit}: 本机 Git 对象不可读")
        else:
            for path, reason in BASELINES:
                source = git_source(self.pcp_repo, PCP, self.pcp_commit, path, "APPROVED", True, reason, terms)
                if source:
                    items.append(source)
                else:
                    gaps.append(f"{PCP}:{path}@{self.pcp_commit}")
            found_mature = False
            for area, maturity, authoritative in EXPERIENCE_PATHS:
                if not terms or (maturity == "INBOX" and found_mature):
                    continue
                if git(self.pcp_repo, "cat-file", "-e", f"{self.pcp_commit}:{area}").returncode:
                    gaps.append(f"{PCP}:{area}@{self.pcp_commit}")
                    continue
                matches, failed = lookup(self.pcp_repo, PCP, self.pcp_commit, (area,), terms, maturity, authoritative)
                searched.append({"path": area, "matches": len(matches)})
                if failed:
                    gaps.append(f"{PCP}:{area}@{self.pcp_commit}: 检索失败")
                items.extend(matches)
                found_mature = found_mature or bool(matches)
        return {"key": key, "terms": terms, "items": items, "unavailable": gaps, "searched": searched}

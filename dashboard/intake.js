"use strict";

const intakeLabels = {intake: "整理中", review: "待确认", confirmed: "已确认", changed: "需求已修改"};
const sourceLabels = {PROJECT: "项目事实", APPROVED: "已批准基线", VALIDATED: "已验证经验", CANDIDATE: "候选证据", INBOX: "Inbox 证据"};
let intakeRender = 0;
let intakeBusy = false;

function intakeRoute() {
  return /^#intake(?:\/([a-f0-9]{32}))?$/.exec(location.hash);
}

async function intakeApi(id, changes) {
  const target = "/api/intake" + (id ? "/" + id : "");
  const response = await fetch(target, changes ? {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(changes),
  } : {cache: "no-store"});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "草稿读取失败，请重试。");
  return data;
}

function labelFor(control, name) {
  control.setAttribute("aria-label", name);
  return control;
}

function loadIntake(force = false) {
  const route = intakeRoute();
  if (!route) return;
  const container = el("view");
  if (force !== true && container.dataset.intakeRoute === route[0] && container.querySelector(".intake-workspace")) return;
  const version = ++intakeRender;
  container.replaceChildren(node("p", "note", "正在打开草稿…"));
  const tasks = [intakeApi(null), route[1] ? intakeApi(route[1]) : Promise.resolve(null)];
  Promise.all(tasks).then(([index, session]) => {
    if (version === intakeRender && intakeRoute()?.[0] === route[0]) showIntake(index, session);
  }).catch((error) => {
    if (version === intakeRender && intakeRoute()?.[0] === route[0]) {
      container.replaceChildren(header("工程需求对话", "", link("返回工程任务", "#tasks", "btn")),
        node("p", "note warn", error.message), button("重试", loadIntake));
    }
  });
}

function showIntake(index, session) {
  const container = el("view");
  const draft = session?.draft;
  const caps = session?.capabilities ?? index.capabilities;
  const notice = node("p", "sub intake-notice");
  notice.setAttribute("role", "status");
  container.dataset.intakeRoute = intakeRoute()[0];

  async function change(payload) {
    if (intakeBusy) return false;
    intakeBusy = true;
    notice.textContent = payload.action === "plan_generate" ? "正在请求本机 Ruflo Supervisor…" : "正在保存…";
    try {
      const updated = await intakeApi(draft?.id, draft ? {...payload, version: draft.version} : payload);
      if (intakeRoute()?.[1] !== draft?.id) return true;
      if (!draft) {
        location.hash = "#intake/" + updated.draft.id;
        return true;
      }
      const latest = updated.draft;
      const summary = {id: latest.id, project: latest.project, title: latest.title, updatedAt: latest.updatedAt, status: updated.status};
      index.drafts = [summary, ...index.drafts.filter((item) => item.id !== latest.id)];
      showIntake(index, updated);
      el("view").querySelector(".intake-notice").textContent = "已保存";
      return true;
    } catch (error) {
      notice.textContent = error.message;
      return false;
    } finally {
      intakeBusy = false;
    }
  }

  const history = node("details", "intake-history",
    node("summary", "", "最近草稿 (" + index.drafts.length + ")"),
    table(["草稿", "项目", "状态", "更新时间"], index.drafts.map((entry) => [
      link(entry.title, "#intake/" + entry.id, "intake-draft-link"), entry.project ?? "待识别",
      intakeLabels[entry.status], date(entry.updatedAt),
    ]), "暂无草稿。发送第一条消息后自动保存。"));
  history.open = !draft;
  const headline = header("工程需求对话", draft ? draft.title : "先用一句话描述目标、问题或想法。",
    link("新建对话", "#intake", "btn"), link("返回工程任务", "#tasks", "btn"));
  const warnings = node("div", "note intake-capability", node("p", "", caps.dialogueAvailable ? "本机授权已启用 Ruflo 需求对话。" : caps.llmGap),
    node("p", "", "草稿通过本机 Dashboard 持久保存。请勿填写密钥、令牌或密码。"));
  const transcript = draft ? draft.messages.map((entry, position) => node("article", "intake-message",
    node("div", "intake-message-meta", node("b", "", entry.role === "assistant" ? "Ruflo" : "你"), node("span", "sub", date(entry.at))),
    node("p", "", entry.text),
    entry.ruflo ? node("p", "sub mono", entry.ruflo.model + " · " + entry.ruflo.messageId) : null,
    position === 0 ? button("用作项目目标", () => change({action: "field", field: "goal", value: entry.text, provenance: "USER_CONFIRMED"}), "btn small") : null,
  )) : [];
  const input = labelFor(node("textarea", "intake-input"), "对话消息");
  input.placeholder = "描述你希望实现的结果，或补充、修正当前需求";
  input.maxLength = 5000;
  input.rows = 3;
  const form = node("form", "intake-form", input,
    node("div", "actions", ["补充范围", "补充约束", "补充验收"].map((prefix) => button(prefix, () => {
      input.setRangeText(prefix + "：", input.selectionStart, input.selectionEnd, "end");
      input.focus();
    }, "btn small")),
    node("button", "btn primary", "保存消息")));
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (input.value.trim()) await change({action: "message", text: input.value});
  });
  const conversation = panel("对话记录", draft ? "已保存的对话 · " + date(draft.updatedAt) : "自由描述，无需先填写工程表单。",
    node("div", "intake-transcript", transcript.length ? transcript : node("p", "muted", "第一条消息会建立可续接的草稿。")), form,
    caps.dialogueAvailable && draft?.project && draft.messages.at(-1)?.role === "user"
      ? button("请 Ruflo 回复", () => change({action: "ai_reply"}), "btn primary") : null);
  const workspace = node("div", "intake-workspace",
    headline, warnings, notice, history,
    node("div", "intake-grid", conversation, draft ? intakeDossier(draft, caps, change) : null),
    draft ? intakeDocuments(draft, session.status, caps, change) : null,
    draft ? intakePlanning(draft, session.status, caps, change) : null,
    draft && (draft.formal || caps.formalActions?.length) ? intakeExecution(draft, caps, change) : null);
  container.replaceChildren(workspace);
}

function intakeDossier(draft, caps, change) {
  const projectAction = draft.project
    ? node("div", "intake-project", node("b", "", "项目 · " + draft.project))
    : node("div", "intake-project", node("p", "sub", "项目尚未识别。新项目可以先保持待识别。"),
      button("关联现有工程 Runtime", () => change({action: "project", project: caps.project})));
  const rows = Object.entries(caps.fields).map(([key, label]) => {
    const item = draft.dossier[key];
    return node("div", "intake-dossier-row", node("div", "intake-dossier-top", node("b", "", label),
      node("span", "status " + (item.provenance === "USER_CONFIRMED" ? "done" : "neutral"), caps.provenance[item.provenance]),
      button("编辑" + label, () => editIntakeField(key, label, item, change), "link")),
    node("div", "intake-field-value", item.value || "待确认"));
  });
  const context = draft.context;
  const sourceList = node("div", "intake-sources", context.items.map((source) => {
    const details = node("details", "intake-source",
      node("summary", "", sourceLabels[source.maturity] + " · " + source.title),
      node("p", "mono", source.repository + "@" + source.commit + ":" + source.path),
      node("p", "", source.reason),
      node("p", "sub", source.authoritative ? "依据类型由来源标注" : "仅供参考，需人工确认"),
      source.excerpt ? node("blockquote", "", source.excerpt) : null);
    return details;
  }));
  const search = labelFor(node("input", "search"), "经验检索关键词");
  search.type = "search";
  search.maxLength = 250;
  search.value = context.terms.join(" ");
  search.placeholder = "按当前问题输入关键词";
  const searchForm = node("form", "filters intake-source-search", search, node("button", "btn", "检索项目与经验"));
  searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    change({action: "retrieve", terms: search.value});
  });
  return panel("需求档案", "",
    projectAction, node("div", "intake-dossier", rows),
    node("div", "tag-row", Object.values(caps.provenance).map((label) => node("span", "pill", label))),
    node("h3", "", "项目与经验来源"), draft.project ? searchForm : null,
    context.searched.length ? node("div", "sub", context.searched.map((check) => check.path + " · " + check.matches + " 项").join(" / ")) : null,
    context.unavailable.map((gap) => node("p", "note warn", gap)), sourceList);
}

function editIntakeField(field, title, item, change) {
  const input = labelFor(node("textarea", "intake-input"), title);
  input.value = item.value;
  input.rows = 6;
  input.maxLength = 5000;
  const message = node("p", "sub");
  message.setAttribute("role", "status");
  const save = (provenance) => async () => {
    const ok = await change({action: "field", field, value: input.value, provenance});
    if (ok) el("detail").close();
    else message.textContent = el("view").querySelector(".intake-notice")?.textContent ?? "保存失败";
  };
  popup(title, [
    input, message, node("div", "actions row-actions",
      button("保存为用户确认", save("USER_CONFIRMED"), "btn primary"),
      button("保存为未决", save("UNRESOLVED")),
      ...(item.provenance.startsWith("AI_") ? [button("拒绝此项", () => {
        input.value = "";
        return save("UNRESOLVED")();
      })] : [])),
  ]);
  input.focus();
}

function exportDocument(filename, text) {
  const url = URL.createObjectURL(new Blob([text], {type: "text/plain;charset=utf-8"}));
  const anchor = link(filename, url);
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function intakeDocuments(draft, status, caps, change) {
  const latest = draft.packages.at(-1);
  const preview = node("div", "intake-preview");
  const versions = labelFor(node("select", "filter"), "文档版本");
  draft.packages.forEach((entry) => versions.append(new Option("R" + entry.revision + " · " + date(entry.createdAt), entry.revision)));
  if (latest) versions.value = String(latest.revision);

  function showVersion() {
    const revision = draft.packages.find((entry) => String(entry.revision) === versions.value);
    if (!revision) return;
    const selector = labelFor(node("select", "filter"), "预览文档");
    revision.documents.forEach((entry, i) => selector.append(new Option(entry.title, i)));
    const text = node("pre", "intake-document-text");
    function choose() { text.textContent = revision.documents[Number(selector.value)].text; }
    selector.addEventListener("change", choose);
    choose();
    const current = revision.revision === latest.revision && status === "review";
    preview.replaceChildren(
      node("div", "filters", selector,
        button("导出当前文件", () => {
          const doc = revision.documents[Number(selector.value)];
          exportDocument("R" + revision.revision + "-" + doc.filename, doc.text);
        }),
        button("导出完整版本", () => exportDocument("intake-R" + revision.revision + ".md",
          revision.documents.map((doc) => doc.filename.endsWith(".yaml")
            ? "## " + doc.title + "\n\n" + String.fromCharCode(96).repeat(3) + "yaml\n" + doc.text + String.fromCharCode(96).repeat(3)
            : doc.text).join("\n\n"),
        ))),
      node("p", "sub", revision.confirmedAt ? "已确认 · " + date(revision.confirmedAt) : "草稿 · R" + revision.revision),
      text,
      current ? button("确认文档 R" + revision.revision, () => change({action: "confirm", revision: revision.revision}), "btn primary") : null,
    );
  }
  versions.addEventListener("change", showVersion);
  showVersion();
  return panel("工程文档与 EO 草稿", "模板生成 · " + intakeLabels[status],
    node("div", "filters", button(latest ? "生成新版本" : "生成文档草稿", () => change({action: "generate"}), "btn primary"),
      latest ? versions : null),
    status === "changed" ? node("p", "note warn", "需求或来源已更新。生成新版本后可进行下一次确认。") : null,
    node("p", "note", caps.eoGap), preview);
}

function intakeExecution(draft, caps, change) {
  const record = draft.formal;
  if (record?.kind === "engineering" || caps.formalActions?.includes("formal_create") && !record)
    return engineeringExecution(draft, caps, change);
  const last = record?.observed;
  const run = last?.provider ?? record?.dispatch;
  const actions = new Set(caps.formalActions);
  const state = last?.state ? reportedState(esReportStates, last.state)
    : run ? "已派发，等待 Worker 回执" : record ? "待授权派发" : "待登记";
  return panel("正式工单与执行", state,
    node("div", "actions",
      actions.has("formal_create") && !record
        ? button("创建 EO Job 和 Workorder", () => change({action: "formal_create"}), "btn primary") : null,
      actions.has("formal_dispatch") && record && !run
        ? button("授权并派发非生产任务", () => change({action: "formal_dispatch"}), "btn primary") : null,
      actions.has("formal_observe") && record
        ? button("读取执行结果", () => change({action: "formal_observe"})) : null),
    record ? executionReport(draft, {
      ...run, provider: last?.provider?.state, providerSession: last?.provider?.session,
      request: record.request, execution: record.execution, attempt: last?.attempt,
      invocation: last?.invocation ?? run?.invocation, state: last?.state, result: last?.result,
    }, state, true) : null);
}

const esReportStates = {
  QUEUED: "ES 已排队", RUNNING: "ES 执行中", REVIEW_READY: "ES 已收到交付，等待验收",
  RESULT_READY: "ES 已收到交付，等待验收", DONE: "ES 已记录执行完成",
  REVISION_REQUESTED: "ES 已要求返工", RECOVERABLE: "ES 等待恢复", REJECTED: "ES 已拒绝",
  NEEDS_INPUT: "ES 等待补充资料", FAILED: "ES 已记录失败", CANCELLED: "ES 已取消", BLOCKED: "ES 已阻塞",
};
const providerReportStates = {
  queued: "排队中", claimed: "已领取", running: "运行中", done: "提供方运行已结束",
  failed: "提供方运行失败", cancelled: "提供方运行已取消", unknown: "提供方运行终态未知",
};
const roleReportStates = {PASS: "通过", REWORK: "需返工", CONTINUE: "同意继续"};

function reportedState(labels, code) {
  return code ? (Object.hasOwn(labels, code) ? labels[code] : "状态未知") + "（" + code + "）" : "未记录";
}

function reportGitRef(repo, sha, path = "") {
  return /^[a-f0-9]{40}$/.test(sha ?? "") ? repo + "@" + sha + (path ? ":" + path : "") : null;
}

function executionReport(draft, run, state, expanded, task) {
  const record = draft.formal;
  const result = run.result;
  const delivery = run.eoDelivery;
  const eoRepo = gitEO.replace("https://github.com/", "");
  const projectRepo = gitProject.replace("https://github.com/", "");
  const workerEvidence = result?.worker_output_sha256
    ? {log: "stdout-1.log", proof: result.worker_output_sha256}
    : result?.worker_sha256
      ? {log: "stdout", proof: result.worker_sha256}
      : null;
  const logRef = Number.isInteger(run.run) && /^[a-f0-9]{64}$/.test(workerEvidence?.proof ?? "")
    ? "autoloop:run:" + run.run + "/" + workerEvidence.log + "#sha256=" + workerEvidence.proof : null;
  const sections = [
    ["执行说明", [["目标", draft.title], ...(task ? [["任务", task.title + "（" + task.id + "）"]] : []),
      ["当前状态", state], ["计划阻碍", record.obstacle], ["本次执行的失败原因", run.failure]]],
    ["EO 工单与正式回写", [
      ["EO Job", record.job], ["EO Workorder", record.workorder],
      ["EO 工单提交", reportGitRef(eoRepo, record.commit, record.workorder ? "workorders/" + record.workorder + "/workorder.yaml" : "")],
      ["EO 回写提交", reportGitRef(eoRepo, delivery)],
      ...[["Result", "result"], ["Evidence", "evidence"], ["Review", "review"]].map(([label, kind]) =>
        ["EO " + label, run.eoRecords?.[kind] ? reportGitRef(eoRepo, delivery, run.eoRecords[kind]) : null]),
    ]],
    ["ES 执行记录", [["ES Request", run.request], ["ES Execution", run.execution], ["ES Attempt", run.attempt],
      ["ES Invocation", run.invocation], ["ES 状态", reportedState(esReportStates, run.state)]]],
    ["Autoloop 与 Worker 回执", [
      ["Autoloop Event", run.event], ["Autoloop Run", run.run], ["Autoloop 规则", run.providerRule],
      ["Autoloop 状态", reportedState(providerReportStates, run.provider)],
      ["Codex 会话", run.providerSession ?? result?.codex_thread],
      ["Worker 日志引用", logRef], ["Worker 交付原文", result?.response],
    ]],
    ["代码与测试", [["Git 提交", reportGitRef(projectRepo, result?.commit)],
      ["通过的定向测试命令", result?.tests?.join("\n")]]],
    ["独立验收与推进决定", [
      ...[["独立代码复核", "review"], ["独立产品 QA ", "qa"], ["Supervisor ", "supervisor"]].flatMap(([label, role]) => {
        const decision = run.decisions?.[role];
        return [[label + "决定", reportedState(roleReportStates, decision?.state)], [label + "说明", decision?.text],
          [label + "回执 ID", decision?.receipt?.messageId]];
      }),
    ]],
  ].map(([heading, rows]) => [heading, rows.map(([label, value]) =>
    [label, value === null || value === undefined || value === "" ? "未记录" : String(value)])]);
  const filename = [record.workorder, task?.id, "执行报告.md"].filter(Boolean).join("-");
  const markdown = ["# 工程执行报告", ...sections.map(([heading, rows]) => [
    "## " + heading, "", ...rows.map(([label, value]) =>
      ("    " + label + " · " + value.replace(/\r\n?|\n/g, "\n    "))),
  ].join("\n"))].join("\n\n") + "\n";
  const preview = node("details", "intake-source", node("summary", "", "查看执行报告"),
    sections.map(([heading, rows]) => node("div", "detail-block", node("h3", "", heading),
      entries(rows.map(([label, value]) => [label, node("span", "intake-field-value", value)])))));
  preview.open = expanded;
  return node("div", "stack", button("导出执行报告", () => exportDocument(filename, markdown)), preview);
}

function engineeringExecution(draft, caps, change) {
  const receipt = draft.formal;
  const allowed = new Set(caps.formalActions ?? []);
  const rows = receipt ? receipt.order.map((id) => {
    const task = receipt.tasks.find((item) => item.id === id);
    const run = receipt.runs[id] ?? {};
    const state = run.state ? reportedState(esReportStates, run.state)
      : !receipt.authorizedAt ? "等待授权下达"
      : receipt.held ? "计划暂停，等待恢复"
      : task.depends.some((dep) => receipt.runs[dep]?.state !== "DONE") ? "等待前置任务验收"
      : "等待后端下达";
    const hasDelivery = ["REVIEW_READY", "DONE", "REVISION_REQUESTED"].includes(run.state);
    const report = executionReport(draft, {
      ...run, result: hasDelivery ? run.result : null, eoDelivery: hasDelivery ? run.eoDelivery : null,
      decisions: hasDelivery ? run.decisions ?? (run.state === "REVISION_REQUESTED" ? run.priorDecisions : null) : null,
      failure: run.state === "RECOVERABLE" ? run.failure : null,
    }, state, false, task);
    return [task.title, task.depends.join(", ") || "无", state, report];
  }) : [];
  return panel("正式工程下达与交付", receipt?.state ?? "确认需求和工程计划后可登记",
    receipt ? entries([["EO Job", receipt.job], ["EO Workorder", receipt.workorder], ["EO 工单提交", receipt.commit],
      ["需求版本", "R" + receipt.documentRevision], ["计划版本", "P" + receipt.planRevision],
      ["授权来源", receipt.authorizedBy ? "可信服务主体 · " + receipt.authorizedBy.peer : "待确认下达"]]) : null,
    receipt?.obstacle ? node("p", "note warn", receipt.obstacle) : null,
    node("div", "actions",
      !receipt && allowed.has("formal_create") ? button("登记正式工程工单", () => change({action:"formal_create"}), "btn primary") : null,
      receipt && !receipt.authorizedAt && allowed.has("formal_dispatch")
        ? button("授权并下达非生产工程计划", () => change({action:"formal_dispatch"}), "btn primary") : null,
      receipt?.authorizedAt && allowed.has("formal_hold")
        ? button(receipt.held ? "恢复后续任务" : "暂停后续任务", () => change({action:"formal_hold", held:!receipt.held})) : null,
      receipt ? button("读取当前执行状态", () => loadIntake(true)) : null),
    receipt ? table(["任务","依赖","状态","运行与交付证据"], rows, "等待已授权任务") : null);
}

if (intakeRoute()) loadIntake();

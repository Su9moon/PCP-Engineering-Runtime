"use strict";

const labels = {
  overview: "总览", tasks: "工程任务", runs: "运行记录", agents: "Agent 团队", intake: "工程需求对话",
  workers: "执行节点", reviews: "交付复核", integrations: "连接与配置",
};
const statusLabels = {
  connected: "已连接", disconnected: "未连接", history: "历史记录", unconfigured: "未配置",
  unverified: "未验证", unavailable: "不可用", blocked: "阻塞", failed: "失败", deferred: "已延期",
  READY: "待处理", EXECUTING: "执行中", RESULT_READY: "结果待复核", CLOSED: "已归档", RUNNING: "运行中", DONE: "已完成", FAILED: "失败",
  COMPLETED: "已完成", NEEDS_REVIEW: "待复核", BLOCKED: "阻塞", DRAFT: "草稿",
  APPROVED: "已批准", REWORK: "需返工", NEEDS_INPUT: "待补充",
  queued: "排队中", claimed: "已领取", done: "已完成", unknown: "未知",
  idle: "空闲", active: "活跃", running: "运行中", cancelled: "已取消",
};
const el = (id) => document.getElementById(id);
const gitProject = "https://github.com/Su9moon/PCP-Engineering-Runtime";
const gitEO = "https://github.com/Su9moon/pcp-engineering-operations";
const query = {task: "", taskStatus: "", run: "", pool: ""};
let state;
let stateRequest;
let failedAt;
let suspended = false;
const STATE_TIMEOUT_MS = 15000;

function node(tag, className, ...children) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  for (const child of children.flat(Infinity)) {
    if (child !== null && child !== undefined) element.append(child instanceof Node ? child : String(child));
  }
  return element;
}

function button(label, action, className = "btn") {
  const item = node("button", className, label);
  item.type = "button";
  item.addEventListener("click", action);
  return item;
}

function link(label, url, className) {
  const item = node("a", className, label);
  item.href = url;
  return item;
}

function external(label, url) {
  const item = link(label, url);
  item.target = "_blank";
  item.rel = "noopener noreferrer";
  return item;
}

function date(value) {
  if (!value) return "未记录";
  const parsed = new Date(value);
  return Number.isNaN(+parsed) ? String(value) : new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai", dateStyle: "medium", timeStyle: "medium",
  }).format(parsed);
}

function status(value) {
  const tone = ["connected", "done", "DONE", "APPROVED", "COMPLETED"].includes(value) ? "done"
    : ["claimed", "running", "active", "RUNNING"].includes(value) ? "running"
    : ["unavailable", "failed", "FAILED"].includes(value) ? "failed"
    : ["blocked", "BLOCKED", "NEEDS_REVIEW", "NEEDS_INPUT", "REWORK"].includes(value) ? "blocked" : "neutral";
  return node("span", "status " + tone, statusLabels[value] ?? value ?? "未记录");
}

function header(title, description, ...actions) {
  return node("div", "page-head", node("div", "", node("h1", "", title), node("p", "", description)),
    actions.length ? node("div", "actions", actions) : null);
}

function panel(title, description, ...items) {
  return node("section", "card", node("div", "card-head",
    node("div", "", node("h2", "", title), description ? node("p", "", description) : null)),
  node("div", "card-body", items));
}

function optionalAction(label) {
  const control = node("button", "btn", label);
  control.disabled = true;
  control.type = "button";
  return control;
}

function unavailable(reason, ...names) {
  return node("div", "note warn", node("p", "", reason), node("div", "actions", names.map(optionalAction)));
}

function table(headers, rows, empty) {
  if (!rows.length) return node("p", "note", empty);
  return node("div", "table-wrap", node("table", "",
    node("thead", "", node("tr", "", headers.map((name) => {
      const column = node("th", "", name);
      column.scope = "col";
      return column;
    }))),
    node("tbody", "", rows.map((row) => node("tr", "", row.map((value) => node("td", "", value ?? "—")))))));
}

function entries(items) {
  return node("div", "", items.map(([label, value]) => node("div", "kv",
    node("span", "", label), node("span", "", value ?? "未记录"))));
}

function list(items) {
  return items.length ? node("ul", "details-list", items.map((value) => node("li", "", value))) : null;
}

function popup(title, children) {
  el("detail-title").textContent = title;
  el("detail-content").replaceChildren(...children);
  if (!el("detail").open) el("detail").showModal();
}

function gitRecord(record) {
  if (!record.gitClean || !record.path || !state.eo.health.revision) return node("span", "sub", record.path ?? "未记录");
  const encoded = record.path.split("/").map(encodeURIComponent).join("/");
  return external(record.path, gitEO + "/blob/" + state.eo.health.revision + "/" + encoded);
}

function commitLink(sha, label) {
  if (!/^[a-f0-9]{40}$/.test(sha ?? "")) return null;
  return external(label ?? sha.slice(0, 12), gitProject + "/commit/" + sha);
}

function taskDetails(task) {
  const executions = state.es.executions.filter((item) => item.workorder_id === task.workorder_id && item.job_id === task.job_id);
  popup(task.title ?? task.workorder_id, [
    node("div", "detail-block", node("h3", "", "EO 工单"), entries([
      ["Workorder", task.workorder_id], ["Job", task.job_id], ["仓库", task.repository], ["状态", status(task.status)],
      ["来源", gitRecord(task)], ["记录时间", date(task.updated_at ?? task.created_at)],
    ]), node("p", "note", task.objective), node("h3", "", "验收条件"), list(task.acceptance)),
    node("div", "detail-block", node("h3", "", "ES 执行与尝试"),
      executions.length ? executions.map((run) => node("div", "detail-item",
        entries([["Execution", run.execution_id], ["Request", run.request_id], ["ES 状态", status(run.state)],
          ["最近记录", date(run.updated_at)]]),
        list(run.attempts.map((item) => [item.attempt_id, item.invocation_id, item.state, item.runtime_ref].filter(Boolean).join(" · "))),
        list(run.reviews.map((item) => [item.attempt_id, item.decision, date(item.created_at)].join(" · "))),
      )) : node("p", "note", "当前 ES 记录未返回同时匹配此 Job 和 Workorder 的执行。")),
    unavailable(state.actions.dispatch, "派发任务"),
    unavailable(state.actions.replan, "请求 Ruflo 重规划"),
  ]);
}

function taskAnchor(task) {
  return node("div", "", button(task.title ?? task.workorder_id, () => taskDetails(task), "link task-link"),
    node("span", "sub", task.workorder_id));
}

function allRuns() {
  return state.hubs.flatMap((hub) => hub.runs);
}

function allHealth() {
  return [state.ruflo.health, ...state.hubs.map((hub) => hub.health), state.eo.health, state.es.health, ...state.connections];
}

function awaitingState() {
  return Boolean(stateRequest || suspended);
}

function staleState() {
  return awaitingState() || Boolean(failedAt);
}

function observation(availability, observedAt) {
  return node("div", "", status(staleState() ? "unknown" : (availability ?? "unknown")),
    awaitingState() ? node("small", "sub", "正在重新观测…") : null,
    failedAt ? node("small", "sub", "本次读取失败 " + date(failedAt)) : null,
    observedAt ? node("small", "sub", (staleState() ? "上次观察 " : "观察于 ") + date(observedAt)) : null);
}

function integration(health, showAvailability = false) {
  return node("div", "integration",
    node("div", "integration-main", node("b", "", health.label),
      node("small", "", (staleState() ? "上次记录 · " : "") + health.detail)),
    node("div", "integration-side", observation(showAvailability ? health.availability : health.status, health.observedAt),
      health.sourceAt ? node("small", "sub", (staleState() ? "上次来源时间 " : "来源时间 ") + date(health.sourceAt)) : null));
}

function metric(title, value, source) {
  return node("div", "card metric", node("div", "metric-top", title),
    node("div", "metric-value", value ?? "—"), node("div", "metric-foot", source));
}

function overview() {
  const tasks = state.eo.tasks;
  const runnable = state.hubs.flatMap((hub) => hub.workers.flatMap((worker) => worker.activeRuns ?? []));
  const liveHub = !staleState() && state.hubs.some((hub) => hub.health.availability === "active");
  const recent = allRuns().filter((run) => run.finishedAt || run.claimedAt).sort((a, b) =>
    String(b.finishedAt ?? b.claimedAt).localeCompare(String(a.finishedAt ?? a.claimedAt))).slice(0, 7);
  const taskCount = (values) => state.eo.health.status === "connected" ? tasks.filter((task) => values.includes(task.status)).length : null;
  return [
    header("工程工作总览", "工程任务、执行活动与交付状态", link("查看工程任务", "#tasks", "btn primary")),
    node("div", "grid metrics", metric("EO 工单", state.eo.health.status === "connected" ? tasks.length : null, "本地 EO Git"),
      metric("EO 待处理", taskCount(["READY", "PENDING"]), "本地 EO 工单状态"),
      metric("ES 已完成", state.es.health.status === "history" ? state.es.executions.filter((item) => item.state === "DONE").length : null, "现有 ES 记录"),
      metric("活跃 Worker 的已领取 Run", liveHub ? runnable.length : null, liveHub ? "本次 Hub 响应" : "无当前 Hub 响应")),
    node("div", "grid two-col",
      panel("最近执行活动", "按 Provider 的实际记录时间排序",
        recent.length ? node("div", "activity", recent.map((run) => node("div", "activity-item",
          node("div", "timeline-dot"), node("div", "",
            button("Run " + run.id + " · " + run.rule, () => runDetails(run), "link task-link"),
            node("small", "", run.pool + " · " + runSource(run))),
          node("div", "activity-time", date(run.finishedAt ?? run.claimedAt)),
        ))) : node("p", "note", "来源暂未返回实际执行活动。")),
      panel("来源状态", "实时响应与历史记录分别标记", allHealth().map((health) => integration(health)))),
  ];
}

function inputFilter(placeholder, key, refresh) {
  const control = node("input", "search");
  control.type = "search";
  control.placeholder = placeholder;
  control.setAttribute("aria-label", placeholder);
  control.value = query[key];
  control.addEventListener("input", () => { query[key] = control.value; refresh(); });
  return control;
}

function selectFilter(label, key, options, refresh) {
  const control = node("select", "filter");
  control.setAttribute("aria-label", label);
  control.append(new Option(label, ""), ...options.map((value) => new Option(statusLabels[value] ?? value, value)));
  control.value = query[key];
  control.addEventListener("change", () => { query[key] = control.value; refresh(); });
  return control;
}

function tasksPage() {
  const container = node("div");
  const tasks = state.eo.tasks;
  function filter() {
    const needle = query.task.toLowerCase().trim();
    const filtered = tasks.filter((task) =>
      (!query.taskStatus || task.status === query.taskStatus)
      && [task.title, task.workorder_id, task.job_id, task.repository].join(" ").toLowerCase().includes(needle));
    container.replaceChildren(table(["工单", "仓库", "EO 状态", "最近记录", "Git 来源"], filtered.map((task) =>
      [taskAnchor(task), task.repository, status(task.status), date(task.updated_at ?? task.created_at), gitRecord(task)]), "没有符合条件的 EO 工单。"));
  }
  filter();
  return [
    header("工程任务", "查看 EO 工单及其可证实的 ES 执行记录", link("新建工程任务", "#intake", "btn primary")),
    panel("EO 工单", state.eo.health.detail,
      node("div", "filters", inputFilter("搜索工单、Job 或仓库", "task", filter),
        selectFilter("全部 EO 状态", "taskStatus", [...new Set(tasks.map((task) => task.status).filter(Boolean))], filter)),
      container), node("p", "note warn", state.actions.create),
  ];
}

function runSource(run) {
  if (run.mode === "snapshot") return "Hub 历史快照";
  if (run.mode !== "live") return "历史投影";
  return staleState() ? "上次 Hub 响应" : "本次 Hub 响应";
}

function runDetails(run) {
  const artifact = run.delivery;
  const health = state.hubs.find((hub) => hub.health.label === run.pool)?.health;
  popup("Run " + run.id, [
    node("div", "detail-block", node("h3", "", "Autoloop Provider"), entries([
      ["Hub", run.pool], ["来源", runSource(run)],
      ["Hub 可用性", observation(health?.availability ?? "unknown", health?.observedAt)],
      ["Run 记录状态", status(run.state)], ["记录中的 Worker", run.worker],
      ["代理 / 规则", [run.agent, run.rule].filter(Boolean).join(" / ")],
      ["创建", date(run.createdAt)], ["领取", date(run.claimedAt)], ["完成", date(run.finishedAt)],
      ["Codex Thread / Session", artifact?.thread ?? run.session], ["Worker 退出码", artifact?.exitCode],
      ["结果摘要", run.summary || null], ["失败原因", run.error || null],
    ])),
    node("div", "detail-block", node("h3", "", "事件关联"),
      table(["Event ID", "类型 / 对象", "记录时间"], run.events.map((event) =>
        [event.id, [event.type, event.subject].filter(Boolean).join(" · "), date(event.receivedAt)]), "未返回 Event 关联。")),
    node("div", "detail-block", node("h3", "", "交付回执"), artifact ? entries([
      ["提交", commitLink(artifact.commit, artifact.commit)], ["日志文件", artifact.log], ["交付文件", list(artifact.files)],
    ]) : node("p", "note", "此 Run 未匹配到保存的交付回执。")),
    unavailable(state.actions.provider, "暂停", "取消", "重试"),
  ]);
}

function runsPage() {
  const container = node("div");
  const runs = allRuns();
  function filter() {
    const needle = query.run.trim().toLowerCase();
    const filtered = runs.filter((run) => (!query.pool || run.pool === query.pool)
      && [run.id, run.rule, ...run.events.map((event) => event.id)].join(" ").toLowerCase().includes(needle));
    container.replaceChildren(table(["Run", "Event ID", "Hub / 来源", "规则", "Run 记录状态", "最后活动"], filtered.map((run) =>
      [button("Run " + run.id, () => runDetails(run), "link task-link"), run.events.map((event) => event.id).filter(Number.isInteger).join(", ") || "未暴露",
        node("div", "", run.pool, node("span", "sub", runSource(run))), run.rule,
        status(run.state), date(run.finishedAt ?? run.claimedAt ?? run.createdAt)]), "没有符合条件的 Autoloop Run。"));
  }
  filter();
  return [
    header("运行记录", "按 Hub 保留原始 Event 和 Run 标识，ES 执行及交付决策分别查看"),
    panel("Hub 可用性", "", state.hubs.map((hub) => integration(hub.health, true))),
    panel("Autoloop Run / Event", "显示来源返回的 Run 状态与记录时间。",
      node("div", "filters", inputFilter("搜索 Event、Run 或规则", "run", filter),
        selectFilter("全部 Hub", "pool", state.hubs.map((hub) => hub.health.label), filter)), container),
  ];
}

function agentsPage() {
  const agentState = state.ruflo;
  const supervisor = state.supervisor;
  const supervisorFound = supervisor && agentState.agents.find((agent) => (agent.agentId ?? agent.id) === supervisor.supervisor);
  return [
    header("Agent 团队", "分别查看本机 MCP 连通性、注册信息和已观测模型调用"),
    node("div", "grid two-col",
      panel("Ruflo Agent 注册", "", integration(agentState.health), table(["Agent / ID", "角色", "状态", "分工"],
        agentState.agents.map((agent) => [node("div", "", agent.name ?? "未命名", node("span", "sub", agent.agentId ?? agent.id)),
          agent.agentType ?? agent.type, status(agent.status), agent.assignment]),
        agentState.registration === "observed" ? "本次 Dashboard stdio 会话的 agent_list 返回零条注册记录。" : "尚未取得可用的 agent_list 结果。")),
      panel("Supervisor 调用证据", "WO-20261125-001",
        supervisor ? entries([["Supervisor ID", supervisor.supervisor], ["注册观察", supervisorFound ? "本次返回" : "本次未观察到"],
          ["响应模型", supervisor.model], ["推理档位", "运行时未暴露"], ["耗时", supervisor.durationMs ? supervisor.durationMs + " ms" : null],
          ["证据时间", date(supervisor.observedAt)]]) : node("p", "note", "暂无模型调用证据。"))),
  ];
}

function workersPage() {
  const workers = state.hubs.flatMap((hub) => hub.workers);
  return [
    header("执行节点", "查看 Autoloop Worker 的心跳记录与可用性"),
    node("div", "grid two-col",
      panel("Worker 节点", "活跃表示该次 Hub 响应确认了有效心跳。",
        table(["Worker", "Hub", "最近心跳", "可用性 / 观察时间", "已领取 Run / 执行器"], workers.map((worker) =>
          [worker.name, worker.pool, date(worker.seenAt), observation(worker.availability, worker.observedAt),
            [...(staleState() ? [] : (worker.activeRuns ?? [])).map((id) => "Run " + id), ...(worker.executors ?? [])].join(" · ") || "—"]), "来源暂未返回 Worker 记录。")),
      panel("Hub 连接", "", state.hubs.map((hub) => integration(hub.health, true)))),
    panel("各 Hub 最近执行", "历史运行按来源分组。现有投影未提供逐 Run 的可信 Worker 标识时留空。",
      table(["Run", "Hub", "Provider 代理", "状态", "最近记录"], allRuns().slice(0, 10).map((run) => [
        button("Run " + run.id, () => runDetails(run), "link task-link"), run.pool, run.agent,
        status(run.state), date(run.finishedAt ?? run.claimedAt ?? run.createdAt),
      ]), "来源暂未返回运行历史。")),
  ];
}

function reviewsPage() {
  const cards = state.eo.results.map((result) => panel(result.result_id, result.workorder_id,
    entries([["EO Result", status(result.status)], ["Git 来源", gitRecord(result)], ["更新", date(result.updated_at)]]),
    node("p", "note", result.summary),
    node("h3", "", "交付文件与测试证据"),
    result.evidence.map((entry) => {
      const commit = state.commits[entry.commit];
      return node("div", "detail-block",
        entries([["Evidence", entry.evidence_id], ["类型", entry.evidence_type], ["Git 来源", gitRecord(entry)],
          ["提交 / Diff", commitLink(entry.commit, entry.commit)], ["SHA-256", entry.locator.sha256],
          ["提交标题", commit?.subject], ["提交时间", commit ? date(commit.date) : null],
          ["测试 / 验证", entry.verification ?? entry.description],
        ]), commit ? list(commit.files) : null);
    }),
    list(result.findings),
    node("h3", "", "EO Review 记录"),
    table(["Review", "决策", "复核者", "Git 状态"], result.reviews.map((review) =>
      [node("div", "", review.review_id, node("span", "sub", gitRecord(review))), status(review.decision), review.reviewer,
        review.gitClean ? "已跟踪，工作区无改动" : "本地工作区草稿"]), "未找到此 Result 的 EO Review。"),
    result.reviews.map((review) => node("p", "note", review.comment))));
  return [
    header("交付复核", "查看交付、Git 提交、测试证据和 EO 决策"),
    unavailable(state.actions.review, "接受结果", "要求返工", "需要补充"),
    node("div", "stack", cards.length ? cards : node("p", "note", "来源暂未返回此项目的 EO Result。")),
  ];
}

function connectionsPage() {
  return [
    header("连接与配置", "各来源的可用性及最近观察时间"),
    panel("组件连接", "", allHealth().map((health) => integration(health, true))),
    panel("写入权限", "", entries([
      ["创建工单", state.actions.create], ["授权及派发", state.actions.dispatch],
      ["Autoloop 操作", state.actions.provider], ["EO / ES 复核", state.actions.review], ["Ruflo 重规划", state.actions.replan],
    ])),
  ];
}

const views = {overview, tasks: tasksPage, runs: runsPage, agents: agentsPage, workers: workersPage, reviews: reviewsPage, integrations: connectionsPage};

function page() {
  const name = location.hash.slice(1);
  if (/^intake(?:\/[a-f0-9]{32})?$/.test(name)) return "intake";
  return Object.hasOwn(views, name) ? name : "overview";
}

function render() {
  const current = page();
  el("crumb").textContent = labels[current];
  for (const item of document.querySelectorAll(".nav a")) {
    if (item.hash === "#" + current) item.setAttribute("aria-current", "page");
    else item.removeAttribute("aria-current");
  }
  if (current === "intake") {
    if (typeof loadIntake === "function") loadIntake();
    return;
  }
  if (!state) {
    el("view").replaceChildren(failedAt
      ? node("div", "note warn", observation("unknown"), node("p", "", "请点击刷新重试。"))
      : node("p", "note", "正在读取来源记录…"));
    return;
  }
  const content = views[current]();
  if (awaitingState()) content.unshift(node("p", "note", "正在重新观测，保留上次取得的记录。"));
  else if (failedAt) content.unshift(node("p", "note warn",
    "本次读取失败 " + date(failedAt) + " · 上次成功读取 " + date(state.observedAt)));
  el("view").replaceChildren(...content);
}

async function refresh() {
  if (stateRequest) return;
  const request = new AbortController();
  stateRequest = request;
  suspended = false;
  failedAt = null;
  el("freshness").textContent = "正在读取";
  el("refresh").disabled = true;
  if (el("detail").open) el("detail").close();
  if (page() !== "intake") render();
  const timeout = setTimeout(() => request.abort(), STATE_TIMEOUT_MS);
  try {
    const response = await fetch("/api/state", {cache: "no-store", signal: request.signal});
    if (!response.ok) throw new Error("Snapshot HTTP " + response.status);
    const snapshot = await response.json();
    if (stateRequest === request) {
      state = snapshot;
      el("freshness").textContent = "最近读取 " + date(state.observedAt);
    }
  } catch {
    if (stateRequest === request) {
      failedAt = new Date().toISOString();
      el("freshness").textContent = "读取失败 " + date(failedAt);
    }
  } finally {
    clearTimeout(timeout);
    if (stateRequest === request) {
      stateRequest = null;
      el("refresh").disabled = false;
      if (el("detail").open) el("detail").close();
      render();
    }
  }
}

el("refresh").addEventListener("click", refresh);
el("detail-close").addEventListener("click", () => el("detail").close());
window.addEventListener("pagehide", (event) => {
  if (!event.persisted) return;
  suspended = true;
  stateRequest?.abort();
  stateRequest = null;
  failedAt = null;
  el("freshness").textContent = "等待重新观测";
  if (el("detail").open) el("detail").close();
  if (page() !== "intake") render();
});
window.addEventListener("pageshow", (event) => {
  if (event.persisted) refresh();
});
window.addEventListener("hashchange", () => {
  if (el("detail").open) el("detail").close();
  render();
  window.scrollTo(0, 0);
});
refresh();

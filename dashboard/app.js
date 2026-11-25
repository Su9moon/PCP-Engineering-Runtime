"use strict";

const labels = {
  overview: "总览", tasks: "工程任务", runs: "运行记录", agents: "Agent 团队",
  workers: "执行节点", reviews: "交付复核", integrations: "连接与配置",
};
const statusLabels = {
  connected: "已连接", disconnected: "未连接", history: "历史记录", unconfigured: "未配置",
  unverified: "未验证", unavailable: "未暴露", blocked: "阻塞", failed: "失败", deferred: "已延期",
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
let loading = false;
let requestError = false;

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
    : ["failed", "FAILED"].includes(value) ? "failed"
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

function integration(health) {
  return node("div", "integration",
    node("div", "integration-main", node("b", "", health.label), node("small", "", health.detail)),
    node("div", "integration-side", status(health.status), node("small", "", "观测 " + date(health.observedAt)), health.sourceAt ? node("small", "", "来源时间 " + date(health.sourceAt)) : null));
}

function metric(title, value, source) {
  return node("div", "card metric", node("div", "metric-top", title),
    node("div", "metric-value", value ?? "—"), node("div", "metric-foot", source));
}

function overview() {
  const tasks = state.eo.tasks;
  const runnable = allRuns().filter((run) => run.mode === "live" && run.state === "claimed");
  const liveHub = state.hubs.some((hub) => hub.health.status === "connected");
  const recent = allRuns().filter((run) => run.finishedAt || run.claimedAt).sort((a, b) =>
    String(b.finishedAt ?? b.claimedAt).localeCompare(String(a.finishedAt ?? a.claimedAt))).slice(0, 7);
  const taskCount = (values) => state.eo.health.status === "connected" ? tasks.filter((task) => values.includes(task.status)).length : null;
  return [
    header("工程工作总览", "工程任务、执行活动与交付状态", link("查看工程任务", "#tasks", "btn primary")),
    node("div", "grid metrics", metric("EO 工单", state.eo.health.status === "connected" ? tasks.length : null, "本地 EO Git"),
      metric("EO 待处理", taskCount(["READY", "PENDING"]), "本地 EO 工单状态"),
      metric("ES 已完成", state.es.health.status === "history" ? state.es.executions.filter((item) => item.state === "DONE").length : null, "现有 ES 记录"),
      metric("当前已领取 Run", liveHub ? runnable.length : null, liveHub ? "已连接的 Hub 响应" : "无实时 Hub 数据")),
    node("div", "grid two-col",
      panel("最近执行活动", "按 Provider 的实际记录时间排序",
        recent.length ? node("div", "activity", recent.map((run) => node("div", "activity-item",
          node("div", "timeline-dot"), node("div", "",
            button("Run " + run.id + " · " + run.rule, () => runDetails(run), "link task-link"),
            node("small", "", run.pool + " · " + (run.mode === "live" ? "在线读取" : "历史记录"))),
          node("div", "activity-time", date(run.finishedAt ?? run.claimedAt)),
        ))) : node("p", "note", "来源暂未返回实际执行活动。")),
      panel("来源状态", "实时响应与历史记录分别标记", allHealth().map(integration))),
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
    header("工程任务", "查看 EO 工单及其可证实的 ES 执行记录", optionalAction("新建工程任务")),
    panel("EO 工单", state.eo.health.detail,
      node("div", "filters", inputFilter("搜索工单、Job 或仓库", "task", filter),
        selectFilter("全部 EO 状态", "taskStatus", [...new Set(tasks.map((task) => task.status).filter(Boolean))], filter)),
      container), node("p", "note warn", state.actions.create),
  ];
}

function runDetails(run) {
  const artifact = run.delivery;
  popup("Run " + run.id, [
    node("div", "detail-block", node("h3", "", "Autoloop Provider"), entries([
      ["Hub", run.pool], ["来源", run.mode === "live" ? "在线读取" : "历史记录"],
      ["状态", status(run.state)], ["Worker", run.worker], ["代理 / 规则", [run.agent, run.rule].filter(Boolean).join(" / ")],
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
    container.replaceChildren(table(["Run", "Event ID", "Hub / 来源", "规则", "Provider 状态", "最后活动"], filtered.map((run) =>
      [button("Run " + run.id, () => runDetails(run), "link task-link"), run.events.map((event) => event.id).filter(Number.isInteger).join(", ") || "未暴露",
        node("div", "", run.pool, node("span", "sub", run.mode === "live" ? "在线读取" : "历史记录")), run.rule,
        status(run.state), date(run.finishedAt ?? run.claimedAt ?? run.createdAt)]), "没有符合条件的 Autoloop Run。"));
  }
  filter();
  return [
    header("运行记录", "按 Hub 保留原始 Event 和 Run 标识，ES 执行及交付决策分别查看"),
    panel("Autoloop Run / Event", "历史状态显示来源的最后记录。领取状态需要在线证据才能确认为当前执行。",
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
    header("执行节点", "查看 Autoloop Worker 身份、最近心跳和 Hub 的观测结果"),
    node("div", "grid two-col",
      panel("Worker 节点", "同机执行历史已观测，远程 Worker 未验证。",
        table(["Worker", "Hub", "最近心跳", "状态", "活动 Run / 执行器"], workers.map((worker) =>
          [worker.name, worker.pool, date(worker.seenAt), status(worker.online === true ? "connected" : worker.online === false ? "disconnected" : "history"),
            [...(worker.activeRuns ?? []).map((id) => "Run " + id), ...(worker.executors ?? [])].join(" · ") || "未暴露"]), "来源暂未返回 Worker 记录。")),
      panel("Hub 连接", "", state.hubs.map((hub) => integration(hub.health)))),
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
    header("连接与配置", "最近观测时间与各来源的实际能力"),
    panel("组件连接", "", allHealth().map(integration)),
    panel("写入权限", "", entries([
      ["创建工单", state.actions.create], ["授权及派发", state.actions.dispatch],
      ["Autoloop 操作", state.actions.provider], ["EO / ES 复核", state.actions.review], ["Ruflo 重规划", state.actions.replan],
    ])),
  ];
}

const views = {overview, tasks: tasksPage, runs: runsPage, agents: agentsPage, workers: workersPage, reviews: reviewsPage, integrations: connectionsPage};

function page() {
  const name = location.hash.slice(1);
  return Object.hasOwn(views, name) ? name : "overview";
}

function render() {
  const current = page();
  el("crumb").textContent = labels[current];
  for (const item of document.querySelectorAll(".nav a")) {
    if (item.hash === "#" + current) item.setAttribute("aria-current", "page");
    else item.removeAttribute("aria-current");
  }
  if (!state) {
    el("view").replaceChildren(node("p", "note", requestError ? "读取失败。请点击刷新重试。" : "正在读取来源记录…"));
    return;
  }
  const content = views[current]();
  if (requestError) content.unshift(node("p", "note warn", "最新一次读取失败，当前显示上次成功取得的记录。"));
  el("view").replaceChildren(...content);
}

async function refresh() {
  if (loading) return;
  loading = true;
  el("refresh").disabled = true;
  try {
    const response = await fetch("/api/state", {cache: "no-store"});
    if (!response.ok) throw new Error("Snapshot HTTP " + response.status);
    state = await response.json();
    requestError = false;
    el("freshness").textContent = "最近读取 " + date(state.observedAt);
  } catch {
    requestError = true;
    el("freshness").textContent = "读取失败";
  } finally {
    loading = false;
    el("refresh").disabled = false;
    render();
  }
}

el("refresh").addEventListener("click", refresh);
el("detail-close").addEventListener("click", () => el("detail").close());
window.addEventListener("hashchange", () => {
  if (el("detail").open) el("detail").close();
  render();
  window.scrollTo(0, 0);
});
render();
refresh();

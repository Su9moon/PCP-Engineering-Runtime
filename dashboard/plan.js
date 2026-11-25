"use strict";

const modeNames = {suggestion: "Suggestion · 建议", manual: "Manual · 人工", autonomous: "Autonomous · 自主"};
const planFields = {
  objective: "总体目标", approach: "实施方案", risk: "风险与假设", scope: "仓库与路径范围",
  authorization: "拟授权操作", model: "模型建议", effort: "推理档位建议", agents: "Agent 角色与职责",
  worktree: "工作区隔离", test: "定向测试", review: "独立 Review", qa: "Product QA", rework: "返工条件",
};
const taskFields = {id: "编号", title: "标题", depends: "依赖编号（空格分隔）", input: "输入", output: "交付物", acceptance: "验收条件"};

function planSelect(label, options, value) {
  const select = labelFor(node("select", "filter"), label);
  for (const [key, text] of options) select.append(new Option(text, key));
  select.value = value;
  return select;
}

function planInput(name, value = "", type = "text") {
  const control = labelFor(node("input", "search orchestration-input"), name);
  control.type = type;
  control.value = value;
  return control;
}

function planEditor(original, change) {
  const plan = original ?? {mode: "suggestion", complexity: "", strategy: "serial", workers: 1, model: "gpt-6.2-sol", effort: "high", tasks: []};
  const mode = planSelect("编排模式", Object.entries(modeNames), plan.mode);
  const complexity = planSelect("复杂度建议", [["", "未评估"], ...["C0", "C1", "C2", "C3"].map((key) => [key, key])], plan.complexity);
  const strategy = planSelect("执行策略", [["serial", "串行"], ["parallel", "并行"]], plan.strategy);
  const workers = planInput("计划 Worker 数", plan.workers, "number");
  workers.min = "0";
  const fields = Object.fromEntries(Object.entries(planFields).map(([key, label]) => {
    const input = labelFor(node("textarea", "intake-input"), label);
    input.rows = ["objective", "model", "effort"].includes(key) ? 1 : 2;
    input.value = plan[key] ?? "";
    return [key, input];
  }));
  const tasks = node("div", "stack");
  let counter = 0;
  function addTask(task) {
    const id = ++counter;
    const fields = Object.entries(taskFields).map(([key, label]) => {
      const value = key === "depends" ? (task.depends ?? []).join(" ") : task[key] ?? "";
      const input = planInput(label + " " + id, value);
      input.dataset.planField = key;
      return node("label", "orchestration-field", node("span", "sub", label), input);
    });
    const card = node("div", "detail-block", fields);
    card.append(node("div", "actions",
      button("上移", () => { if (card.previousElementSibling) tasks.insertBefore(card, card.previousElementSibling); }, "btn small"),
      button("下移", () => { if (card.nextElementSibling) tasks.insertBefore(card.nextElementSibling, card); }, "btn small"),
      button("移除任务", () => card.remove(), "btn small")));
    tasks.append(card);
  }
  for (const task of plan.tasks) addTask(task);
  if (!plan.tasks.length) addTask({id: "T1"});
  const feedback = node("p", "sub");
  feedback.setAttribute("role", "status");
  const reason = planInput("变更原因");
  function value() {
    const rows = [...tasks.children].map((card) => {
      const entries = Array.from(card.querySelectorAll("[data-plan-field]")).map((input) => [input.dataset.planField, input.value]);
      const task = Object.fromEntries(entries);
      task.depends = task.depends.split(/[\s,，]+/).filter(Boolean);
      return task;
    });
    return {mode: mode.value, complexity: complexity.value, strategy: strategy.value, workers: workers.valueAsNumber,
      ...Object.fromEntries(Object.entries(fields).map(([key, input]) => [key, input.value])), tasks: rows};
  }
  popup("编辑工程计划", [
    node("p", "note", "修改保存为新版本。执行参数供审阅，正式授权和派发另行确认。"),
    node("div", "filters", mode, complexity, strategy, node("label", "", node("span", "sub", "计划 Worker 数"), workers)),
    ...Object.entries(fields).map(([key, input]) => node("label", "orchestration-field", node("span", "sub", planFields[key]), input)),
    node("h3", "", "任务与依赖"), tasks,
    button("添加任务", () => addTask({})),
    node("label", "orchestration-field", node("span", "sub", "变更原因"), reason), feedback,
    button("保存计划版本", async () => {
      if (!Number.isInteger(workers.valueAsNumber)) {
        feedback.textContent = "请填写计划 Worker 数，允许显式填写 0。";
        workers.focus();
        return;
      }
      const ok = await change({action: "plan_save", reason: reason.value, plan: value()});
      if (ok) el("detail").close();
      else feedback.textContent = el("view").querySelector(".intake-notice")?.textContent ?? "保存失败";
    }, "btn primary"),
  ]);
}

function intakePlanning(draft, status, caps, change) {
  const versions = draft.plans ?? [];
  const current = versions.at(-1);
  const package_ = draft.packages.at(-1);
  const ready = status === "confirmed";
  const selected = node("div", "stack");
  const selector = planSelect("工程计划版本", versions.map((row) =>
    [String(row.revision), "P" + row.revision + " · 文档 R" + row.documentRevision]), String(current?.revision ?? ""));
  function showPlan() {
    const version = versions.find((row) => String(row.revision) === selector.value);
    if (!version) return;
    const plan = version.plan;
    const onCurrent = version.revision === current.revision && ready && package_.revision === version.documentRevision;
    const isConfirmed = !!version.confirmedAt;
    const info = entries([
      ["模式", modeNames[plan.mode]], ["复杂度建议", plan.complexity], ["风险", plan.risk], ["仓库与范围", plan.scope],
      ["拟授权操作", plan.authorization], ["执行配置", plan.strategy + " · 计划 Worker " + plan.workers],
      ["任务依赖顺序", plan.order.join(" → ")], ["作者", version.author], ["记录时间", date(version.createdAt)],
      ["变更原因", version.reason], ["计划确认", isConfirmed ? date(version.confirmedAt) : "待确认"],
    ].map(([label, value]) => [label, value || "待明确"]));
    selected.replaceChildren(
      info,
      node("p", "note", plan.objective || "目标待补充", plan.approach ? "\n" + plan.approach : ""),
      table(["编号与任务", "依赖", "输入", "交付物", "验收"], plan.tasks.map((task) => [
        task.id + " · " + task.title, task.depends.join(", ") || "无", task.input, task.output, task.acceptance,
      ]), "暂无任务"),
      node("details", "intake-source", node("summary", "", "测试、Review 与配置"),
        entries(Object.entries(planFields).filter(([key]) =>
          !["objective", "approach", "risk", "scope", "authorization"].includes(key)).map(([key, label]) => [label, plan[key] || "待明确"]))),
      version.ruflo ? node("div", "detail-block", node("h3", "", "实际 Ruflo 规划调用"),
        entries([["Supervisor", version.ruflo.supervisor], ["模型", version.ruflo.model],
          ["消息 ID", version.ruflo.messageId], ["请求档位", version.ruflo.requestedEffort],
          ["实际档位", version.ruflo.actualEffort], ["耗时", version.ruflo.durationMs == null ? null : version.ruflo.durationMs + " ms"],
          ["观测", date(version.ruflo.observedAt)]])) : null,
      Object.keys(version.changes).length ? node("details", "intake-source",
        node("summary", "", "本次版本变化 · " + version.author),
        ...Object.entries(version.changes).map(([key, value]) => node("div", "detail-item",
          node("b", "", planFields[key] ?? key), node("pre", "intake-document-text", JSON.stringify(value, null, 2))))) : null,
      ready ? node("div", "actions",
        button("编辑为新版本", () => planEditor(plan, change)),
        onCurrent && !isConfirmed ? button("确认计划 P" + version.revision, () => change({action: "plan_confirm", revision: version.revision}), "btn primary") : null) : null,
      onCurrent ? null : node("p", "sub", "此为历史计划，当前文档或计划版本已更新。"),
    );
  }
  selector.addEventListener("change", showPlan);
  showPlan();
  const suggest = ready && caps.plannerAvailable && !(current?.plan.mode === "manual" && current.documentRevision === package_.revision);
  const controls = node("div", "filters",
    suggest ? button("生成 Ruflo 工程计划", () => change({action: "plan_generate"}), "btn primary") : optionalAction("生成 Ruflo 工程计划"),
    ready ? button("手动编排", () => planEditor(current?.plan, change)) : null,
    current ? selector : null);
  let note = "确认当前需求文档版本后可规划。";
  if (ready) note = suggest ? "Ruflo 读取当前已确认档案和来源，返回可编辑建议。" :
    (caps.plannerAvailable ? "人工计划保持有效。显式保存为建议模式后可请求新建议。" : "Ruflo 规划仅在本机地址、已配置适配器时可用。");
  return panel("工程计划与编排", note, controls, selected,
    node("p", "note warn", caps.executionGap),
    node("details", "intake-source", node("summary", "", "执行来源与交付证据"),
      node("p", "", "当前计划尚无正式任务、Run、Worker 或 Review / QA 结果关联。"),
      ...((state?.hubs ?? []).map((hub) => integration(hub.health)))),
    node("div", "actions", optionalAction("正式派发"), link("查看实际运行记录", "#runs", "btn"), link("查看交付证据", "#reviews", "btn")));
}

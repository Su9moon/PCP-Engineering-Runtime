"use strict";

const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {join} = require("node:path");
const {setImmediate} = require("node:timers/promises");
const test = require("node:test");
const {runInNewContext} = require("node:vm");

const intake = readFileSync(join(__dirname, "intake.js"), "utf8");
const eoRepo = "Su9moon/pcp-engineering-operations";
const project = "Su9moon/PCP-Engineering-Runtime";
const workorder = "WO-20261127-002";
const sourceCommit = "a".repeat(40);
const deliveryCommit = "b".repeat(40);
const codeCommit = "c".repeat(40);
const proof = "d".repeat(64);

function renderFixture() {
  const view = {dataset: {}, loaded: false, querySelector() { return this.loaded; }, replaceChildren() { this.loaded = false; }};
  const requests = [];
  const downloads = [];
  const anchor = {click() { downloads.push({name: this.download, blob: this.url}); }, remove() {}};
  const node = (tag, _style, ...children) => ({tag, children: children.flat(Infinity).filter((child) => child != null)});
  const context = {
    gitEO: "https://github.com/" + eoRepo, gitProject: "https://github.com/" + project,
    location: {hash: ""}, el: () => view, node, panel: (...items) => node("panel", "", items),
    entries: (items) => node("entries", "", items), table: (_columns, rows) => node("table", "", rows),
    button: (label, action) => ({tag: "button", label, action}),
    document: {body: {append() {}}}, link: (_name, url) => Object.assign(anchor, {url}),
    URL: {createObjectURL: (blob) => blob, revokeObjectURL() {}}, Blob, setTimeout: (action) => action(),
    fetch: async (path, options) => {
      requests.push([path, options.cache, options.method ?? "GET"]);
      return {ok: true, json: async () => ({})};
    },
  };
  runInNewContext(intake + "\nshowIntake = () => { el().loaded = true; };", context);
  return {context, view, requests, downloads};
}

function buttons(element, label) {
  if (element.tag === "button" && element.label === label) return [element];
  return (element.children ?? []).flatMap((child) => buttons(child, label));
}

function text(element) {
  return typeof element === "string" ? element : (element.children ?? []).map(text).join("\n");
}

function draft(runs) {
  const tasks = [{id: "t1", title: "服务可用性展示", depends: []},
    {id: "t2", title: "中文终态报告", depends: ["t1"]}];
  return {title: "工程验证", formal: {kind: "engineering", job: "JOB-20261127-002",
    workorder, commit: sourceCommit, order: ["t1", "t2"], tasks, runs, authorizedAt: "2026-11-27"}};
}

test("engineering report and download cite the same task and authoritative references", async () => {
  const {context, downloads} = renderFixture();
  const view = context.engineeringExecution(draft({t1: {state: "DONE", event: 47}, t2: {
    request: "REQ-2", execution: "EXE-2", attempt: "ATT-2", invocation: "AINV-2", state: "DONE",
    event: 50, run: 49, provider: "done", providerRule: "engineering",
    eoDelivery: deliveryCommit, eoRecords: {result: "results/RESULT-20261127-002/result.yaml",
      evidence: "evidence/EVD-20261127-002/evidence.yaml", review: "reviews/REVIEW-20261127-002/review.yaml"},
    result: {commit: codeCommit, worker_sha256: proof, codex_thread: "thread-2",
      response: "完成报告修改。\n保留技术原文。", tests: ["python3 -m unittest test_report", "node --check intake.js"]},
    decisions: {review: {state: "PASS", text: "代码复核通过", receipt: {messageId: "resp-review"}},
      qa: {state: "PASS", text: "产品验收通过", receipt: {messageId: "resp-qa"}},
      supervisor: {state: "CONTINUE", receipt: {messageId: "resp-supervisor"}}},
  }}), {}, () => {});

  buttons(view, "导出执行报告")[1].action();
  const [{name, blob}] = downloads;
  assert.equal(name, workorder + "-t2-执行报告.md");
  const exported = await blob.text();
  const displayed = text(view);
  for (const value of [
    "中文终态报告（t2）", "ES 已记录执行完成（DONE）", "提供方运行已结束（done）", "JOB-20261127-002",
    eoRepo + "@" + sourceCommit + ":workorders/" + workorder + "/workorder.yaml",
    eoRepo + "@" + deliveryCommit + ":results/RESULT-20261127-002/result.yaml",
    eoRepo + "@" + deliveryCommit + ":evidence/EVD-20261127-002/evidence.yaml",
    eoRepo + "@" + deliveryCommit + ":reviews/REVIEW-20261127-002/review.yaml",
    "REQ-2", "EXE-2", "ATT-2", "AINV-2", "thread-2", "autoloop:run:49/stdout#sha256=" + proof,
    project + "@" + codeCommit, "python3 -m unittest test_report", "node --check intake.js",
    "resp-review", "resp-qa", "resp-supervisor", "通过（PASS）", "同意继续（CONTINUE）",
  ]) {
    assert.ok(displayed.includes(value), value);
    assert.ok(exported.includes(value), value);
  }
  assert.match(exported, /Autoloop Event · 50\n +Autoloop Run · 49/);
  assert.doesNotMatch(exported, /Autoloop Event · 47/);
});

test("partial and pending tasks show separate gaps even if the provider reports done", async () => {
  const {context, downloads} = renderFixture();
  const view = context.engineeringExecution(draft({t1: {
    state: "REVIEW_READY", provider: "done", event: 50, run: 49, exitCode: 0, result: {response: "已交付复核"},
  }}), {}, () => {});
  const actions = buttons(view, "导出执行报告");
  actions.forEach((button) => button.action());
  const [partial, pending] = await Promise.all(downloads.map(({blob}) => blob.text()));
  assert.match(partial, /ES 已收到交付，等待验收（REVIEW_READY）/);
  assert.match(partial, /提供方运行已结束（done）/);
  for (const label of ["EO 回写提交", "EO Result", "EO Evidence", "EO Review", "ES Request",
    "Git 提交", "通过的定向测试命令", "独立代码复核决定", "独立产品 QA 决定"]) {
    assert.ok(partial.includes(label + " · 未记录"), label);
  }
  assert.doesNotMatch(partial, /已记录执行完成|通过（PASS）|undefined/);
  assert.match(pending, /等待前置任务验收/);
  assert.match(pending, /Autoloop Run · 未记录/);
});

test("a running retry excludes prior delivery, and the historical export tolerates missing provider observation", async () => {
  const {context, downloads} = renderFixture();
  const engineering = context.engineeringExecution(draft({t1: {
    state: "RUNNING", result: {commit: codeCommit, response: "前次交付"},
    priorDecisions: {review: {state: "REWORK", text: "前次复核"}},
  }}), {}, () => {});
  buttons(engineering, "导出执行报告")[0].action();
  const legacy = context.intakeExecution({title: "D01", formal: {workorder, commit: sourceCommit,
    dispatch: {event: 30, run: 29, invocation: "AINV-D01"},
    observed: {state: "DONE", result: {response: "D01 合成验证通过。", worker_output_sha256: proof}},
  }}, {}, () => {});
  buttons(legacy, "导出执行报告")[0].action();
  const [retry, historical] = await Promise.all(downloads.map(({blob}) => blob.text()));
  assert.doesNotMatch(retry, /前次交付|前次复核/);
  assert.match(retry, /Git 提交 · 未记录/);
  assert.equal(downloads[1].name, workorder + "-执行报告.md");
  assert.match(historical, /D01 合成验证通过。/);
  assert.match(historical, /ES 已记录执行完成（DONE）/);
  assert.match(historical, /Autoloop Event · 30\n +Autoloop Run · 29/);
  assert.match(historical, /autoloop:run:29\/stdout-1\.log#sha256=/);
  assert.match(historical, /EO 回写提交 · 未记录/);
});

test("worker log references keep the selected path paired with its digest", async () => {
  const {context, downloads} = renderFixture();
  const view = context.engineeringExecution(draft({t1: {
    state: "DONE", event: 50, run: 49, provider: "done",
    result: {worker_sha256: "a".repeat(64), worker_output_sha256: "b".repeat(64)},
  }}), {}, () => {});
  buttons(view, "导出执行报告")[0].action();
  const exported = await downloads[0].blob.text();
  assert.ok(exported.includes("autoloop:run:49/stdout-1.log#sha256=" + "b".repeat(64)));
  assert.ok(!exported.includes("stdout-1.log#sha256=" + "a".repeat(64)));
});

test("reading current report bypasses the already-rendered intake guard via GET only", async () => {
  const {context, view, requests} = renderFixture();
  const id = "a".repeat(32);
  context.location.hash = "#intake/" + id;
  view.dataset.intakeRoute = context.location.hash;
  view.loaded = true;
  const panel = context.engineeringExecution(draft({}), {}, () => assert.fail("unexpected update"));
  buttons(panel, "读取当前执行状态")[0].action();
  await setImmediate();
  assert.deepEqual(requests, [["/api/intake", "no-store", "GET"], ["/api/intake/" + id, "no-store", "GET"]]);
  assert.equal(view.loaded, true);
});

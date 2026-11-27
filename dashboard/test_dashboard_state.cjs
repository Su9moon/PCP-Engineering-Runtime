"use strict";

const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { join } = require("node:path");
const { setImmediate } = require("node:timers/promises");
const test = require("node:test");
const { runInNewContext } = require("node:vm");

const app = readFileSync(join(__dirname, "app.js"), "utf8");
const observedAt = "2026-11-27T03:00:00Z";
const failedAt = "2026-11-27T03:05:00Z";

class Element {
  children = [];
  listeners = {};
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  get textContent() { return this.children.map((child) => child instanceof Element ? child.textContent : child).join(""); }
  set textContent(value) { this.replaceChildren(value); }
  setAttribute() {}
  addEventListener(name, listener) { this.listeners[name] = listener; }
  close() { this.open = false; }
}

function snapshot(workerAvailability, hubAvailability = "active", time = observedAt) {
  const health = {label: "Fixture Hub", availability: hubAvailability, observedAt: time, detail: "Hub 观察"};
  return {
    observedAt: time, actions: {}, connections: [], ruflo: {health}, eo: {health}, es: {health},
    hubs: [{health, workers: [{
      name: "fixture-worker", pool: health.label, availability: workerAvailability, observedAt: time, seenAt: observedAt,
      activeRuns: workerAvailability === "active" ? [21] : [],
    }], runs: [{id: 21, pool: health.label, mode: hubAvailability === "active" ? "live" : "history",
      state: "claimed", events: [{id: 22}]}]}],
  };
}

function response(data) {
  return {ok: true, json: async () => data};
}

function openPage(hash, fetch, globals = {}) {
  const elements = Object.fromEntries(["view", "crumb", "refresh", "detail", "detail-close", "freshness"]
    .map((id) => [id, new Element()]));
  const window = new Element();
  window.scrollTo = () => {};
  const location = {hash};
  runInNewContext(app, {
    AbortController, AbortSignal, setTimeout, clearTimeout, fetch, location, window, Node: Element, Option: Element,
    Date: class extends Date {
      constructor(...args) { super(...(args.length ? args : [failedAt])); }
    },
    document: {getElementById: (id) => elements[id], createElement: () => new Element(), querySelectorAll: () => []},
    ...globals,
  });
  return {elements, window, location, text: () => elements.view.textContent};
}

function assertOnlyStateGets(requests, count) {
  assert.deepEqual(requests.map(([path, options]) => [path, options.method ?? "GET", options.cache]),
    Array.from({length: count}, () => ["/api/state", "GET", "no-store"]));
}

test("refresh and cache restore immediately withdraw old active states", async () => {
  const refresh = Promise.withResolvers();
  const restore = Promise.withResolvers();
  const replies = [response(snapshot("active")), refresh.promise, restore.promise,
    response(snapshot("unavailable", "active", "2026-11-27T03:06:00Z"))];
  const requests = [];
  const page = openPage("#workers", (...args) => {
    requests.push(args);
    return replies.shift();
  });
  await setImmediate();
  assert.match(page.text(), /fixture-workerFixture Hub.*活跃观察于.*Run 21/);

  page.elements.refresh.listeners.click();
  assert.match(page.text(), /fixture-workerFixture Hub.*未知正在重新观测…上次观察/);
  assert.doesNotMatch(page.text(), /活跃观察于/);

  page.window.listeners.pagehide({persisted: true});
  assert.equal(requests[1][1].signal.aborted, true);
  page.window.listeners.pageshow({persisted: true});
  assert.match(page.text(), /fixture-workerFixture Hub.*未知正在重新观测…上次观察/);
  refresh.resolve(response(snapshot("active")));
  await setImmediate();
  assert.doesNotMatch(page.text(), /活跃观察于/);

  restore.reject(new Error("fixture disconnected"));
  await setImmediate();
  assert.match(page.text(), /fixture-workerFixture Hub.*未知本次读取失败.*11:05:00上次观察.*11:00:00/);
  assert.doesNotMatch(page.text(), /活跃观察于/);
  page.location.hash = "#runs";
  page.window.listeners.hashchange();
  assert.match(page.text(), /Run 2122Fixture Hub上次 Hub 响应/);
  page.window.listeners.pagehide({persisted: true});
  page.window.listeners.pageshow({persisted: true});
  await setImmediate();
  assert.match(page.text(), /活跃观察于.*11:06:00.*Run 2122Fixture Hub本次 Hub 响应/);
  page.location.hash = "#workers";
  page.window.listeners.hashchange();
  assert.match(page.text(), /fixture-workerFixture Hub.*不可用观察于.*11:06:00/);
  assert.doesNotMatch(page.text(), /上次观察|本次读取失败/);
  assertOnlyStateGets(requests, 4);
});

test("opening a new page reads changed Hub availability and keeps Run and Event IDs", async () => {
  const requests = [];
  let latest = snapshot("active");
  const fetch = (...args) => {
    requests.push(args);
    return response(latest);
  };
  const before = openPage("#runs", fetch);
  await setImmediate();
  assert.match(before.text(), /活跃观察于.*Run 2122Fixture Hub本次 Hub 响应/);
  latest = snapshot("unknown", "unavailable", failedAt);
  const after = openPage("#runs", fetch);
  await setImmediate();
  assert.match(after.text(), /不可用观察于.*11:05:00.*Run 2122Fixture Hub历史投影/);
  after.location.hash = "#integrations";
  after.window.listeners.hashchange();
  assert.match(after.text(), /Fixture HubHub 观察不可用观察于.*11:05:00/);
  after.location.hash = "#workers";
  after.window.listeners.hashchange();
  assert.match(after.text(), /fixture-workerFixture Hub.*未知观察于.*11:05:00/);
  assertOnlyStateGets(requests, 2);
});

test("initial read and manual refresh work without AbortSignal.any", async () => {
  const requests = [];
  const replies = [response(snapshot("active")), response(snapshot("unavailable", "active", failedAt))];
  const page = openPage("#workers", (...args) => {
    requests.push(args);
    return replies.shift();
  }, {AbortSignal: {timeout: AbortSignal.timeout}});
  await setImmediate();
  assert.match(page.text(), /fixture-workerFixture Hub.*活跃观察于.*11:00:00/);
  page.elements.refresh.listeners.click();
  await setImmediate();
  assert.match(page.text(), /fixture-workerFixture Hub.*不可用观察于.*11:05:00/);
  assertOnlyStateGets(requests, 2);
});

test("a historical Hub response preserves the Run without presenting it as current", async () => {
  const data = snapshot("unknown", "unknown");
  data.hubs[0].health.sourceAt = "2020-01-01T00:01:00Z";
  data.hubs[0].runs[0].mode = "snapshot";
  const page = openPage("#runs", () => response(data));
  await setImmediate();
  assert.match(page.text(), /未知观察于.*11:00:00来源时间.*2020.*Run 2122Fixture HubHub 历史快照/);
  assert.doesNotMatch(page.text(), /活跃观察于|本次 Hub 响应/);
});

test("a timed-out first read shows the failure time and allows retry", async () => {
  let expire;
  const cleared = [];
  const requests = [];
  const page = openPage("#workers", (...args) => {
    requests.push(args);
    if (requests.length === 2) return response(snapshot("active"));
    const {signal} = args[1];
    return new Promise((resolve, reject) => {
      signal.addEventListener("abort", () => reject(signal.reason), {once: true});
    });
  }, {
    setTimeout: (callback, delay) => {
      assert.equal(delay, 15000);
      expire = callback;
      return requests.length + 1;
    },
    clearTimeout: (timer) => cleared.push(timer),
  });
  assert.equal(page.elements.refresh.disabled, true);
  expire();
  await setImmediate();
  assert.match(page.text(), /未知本次读取失败.*11:05:00/);
  assert.doesNotMatch(page.text(), /上次观察/);
  assert.equal(page.elements.refresh.disabled, false);
  page.elements.refresh.listeners.click();
  await setImmediate();
  assert.match(page.text(), /活跃观察于/);
  assert.deepEqual(cleared, [1, 2]);
  assertOnlyStateGets(requests, 2);
});

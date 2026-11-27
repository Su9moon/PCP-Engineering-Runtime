import { readFileSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const [role, provider, configPath, revision] = process.argv.slice(2);
const config = JSON.parse(readFileSync(configPath, "utf8"));
const providerModule = file => import(pathToFileURL(join(provider, file)).href);
if (config.url !== "http://127.0.0.1:47355" || config.hub?.listen !== "127.0.0.1:47355") {
  throw new Error("现有 Autoloop 配置与本机端口不一致。");
}
if (role === "hub") {
  const { serve } = await providerModule("host/http.ts");
  const server = serve(47355, "127.0.0.1", { commit: revision });
  process.on("SIGTERM", () => { server.close(); server.closeAllConnections(); });
} else if (role === "worker") {
  const { hubClient } = await providerModule("protocol/client.ts");
  const { createWorker } = await providerModule("worker/worker.ts");
  const signal = new AbortController();
  process.on("SIGTERM", () => signal.abort());
  const { name, key, capacity } = config.worker;
  console.log("已启动现有 Worker", name);
  await createWorker({ hub: hubClient(config.url, key), name, capacity, wait: 8, log: console.log }).run(signal.signal);
} else {
  throw new Error("未知的 Autoloop 服务角色。");
}

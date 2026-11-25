# PCP Engineering Control Center V1.2 — WO-20261126-002

## 发布前实际基线

- 部署工作区 /home/cbnet/.local/state/pcp-control-center/WO-20261125-001/worktree，分支 dashboard/wo-20261125-001，从 f854fc325cebfa41a6b2fd50c5f496d59d0bb121 继续。主工作区的既有分支、提交和未提交内容保全。
- 工单从远端提交 d7f1ce5f78e70b22aecc6aafc9739e37caa76851 按原字节提取，SHA-256 5d04821a6b71a54906e2762d359e4454607bd92503e5600727944bfd9f3aec22。PCP 权威文件全部取自 22bae955686f03c5f440cdcd66e13a69f1289f90，包括角色组织 V0.2。
- cbnet 实际环境为 Windows / WSL2 Ubuntu 24.04，运行原 pcp-dashboard-v1.service，继续使用现有 Python stdlib、TLS、七页视图与原子 JSON 需求草稿。以同一服务在 127.0.0.1:8787 与 192.168.5.4:8787 提供 HTTPS。

## 实施和可观测结果

- Ruflo 3.80.0 的 mcp_status 和 agent_list 已调用。原 Supervisor agent-1795518410276-gkzvoy 收到完整工单的三个原文段，并生成 P0–P3 工程计划。正式计划消息 resp_08c22c8d4764ec6f016b07699f78d087d08a619c0bb0e9678f，gpt-6.2-sol，2610 token，23126 ms，路由 HTTP 200。请求 effort high，实际 effort NOT_EXPOSED_BY_RUNTIME。
- Supervisor 明确将未接通的真实派发单独阻断，决定由本机 Codex 在既有隔离部署工作区完成 P1/P2 的规划、编排草稿、只读证据、文档和定向测试。没有据此取得 EO/ES 或 Worker 权限。
- Dashboard 从已确认 V1.1 档案向可核验的本机原 Supervisor 请求规划。发布后以本机 Edge 请求已确认的 R1 需求。第 7 版的回执为 resp_0e723ef45085db6f016b077245bb5487d0a3dd342e6321c222，实际 gpt-6.2-sol，19657 ms，路由 HTTP 200，前 6 版逐项比对一致。请求使用 high，实际档位未由运行时公开。输入绑定到同一份已确认快照，结果仅保存校验通过的结构化计划。
- 草稿 3a7203c08bce43b9b59e2b79a5f81d86 保存建议、人工和自主拟议模式。浏览器实测 C0 可人工设为并行三 Worker，C3 可保存成串行单 Worker 的拟议配置，模式和复杂度与实际授权分开。模型未覆盖当前 Manual 版本。用户编辑、任务依赖、确认和前后值均随新版本保存。服务重启和新浏览器实际恢复原计划；V1.1 原草稿和文档仍可读。
- 实测本机及 LAN 的 Intake HTTPS 返回 200。LAN 的 plan_generate 在调用模型前返回 403；可继续查看和编辑草稿。现有匿名个人工作台未新增身份系统，本机边界不代表已验证操作者身份或正式授权。独立 MEC 设备未直接实测。
- 复用首轮首个规划与 19 份决策、20 个 Run 回执及三个验收提交。T1 f44294f2a7df54e0983d272be76c64b3e7e219ff，T2 db65a7e3830c5e9016a4da21908d65dd74104493，T3 febad72a35130e7e4940524140f035c54a4c897e。复用 V1.1 的 19 项 Python 与 18 项浏览器历史证据，未重跑 POC。
- 原 Ruflo Hub 127.0.0.1:47355 离线，持久投影有 29 Event、28 Run，WO-003 Run 28 仍是 claimed。旧纵向 POC 的 3350 Hub 仅有旧 fixture 规则，5 条历史 Run 已结束。无 V1.2 新 Event、Run、Worker、正式 EO Job 或 ES Attempt，本次计划和历史运行在界面按来源分开。

## 测试和交付

- 代码提交 203641ab113489c896fd82697cf2c75aefb4dd67、28103d9df5d4aa2016f9ea2ed5014f0fde7d3b8f。最终封存代码 647a8bc6cb74339943cd74f95f73ad25a750c506。Dashboard 完整 Diff SHA-256 a511d60bc4c2a509187fef97d489c904e7783bc2aecac9c54a8341006bba85b8。
- 在干净的封存 checkout 执行 25 项 Python 定向测试，全部通过。覆盖档案、DAG、版本确认、风险与授权、同调用模型回执和监听边界。无网络夹具在核验后替换三个原模块文件，实际 Node 仍执行封印的三份原字节。摘要、封印或加载证明失败按测试条件拒绝模型请求。22 项浏览器断言通过，另检查了 JS 语法。
- 变更集中在 dashboard/planning.py、sealed_modules.py、plan.js、serve.py、intake.py、intake_context.py、intake.js、index.html、intake.css、定向测试、现有 runbook 和项目状态。工单为原始传输文件。未提交传输分支的旧基线。
- JSON 和封存核验保存在 /home/cbnet/.local/state/pcp-control-center/WO-20261126-002。浏览器截图和 JSON 保存在 D:/0 codex/runtime/2026-11-26/pcp-dashboard-v1.2。
- 启动、停止和证书说明见 [Dashboard runbook](../dashboard/README.md)。

## 独立 Review、返工和 Product QA

- 独立 Reviewer agent-1795648619885-l8pj66 要求补齐纯规划入口、已确认快照绑定、Worker 空值与 0、耗时显示、授权与 scope 的独立门禁。补项复核还要求实际 Node 加载绑定已核验字节。同一 Node 进程完成原 MCP 的 tools/list 后，调用方在 agent_execute 前检查 launcher、tool、core 的 Inspector 编译回执与封存摘要，避免校验与加载使用不同文件版本。
- Reviewer 对最终补项签 PASS（resp_02e1f81b18f358ae016b07715c4f2087d0bd7e6c34423a6468）。独立 Product QA agent-1795649951500-ph98xw 对本机 P1/P2 证据签 PASS（resp_088d609f3bdee143016b077199bf9c87d0aede7fa57452a881），要求恢复入口后单次浏览器复测。两人审阅了提交的证据。本机工具执行定向测试和浏览器检查。
- 原 Supervisor 对 P2 签 PASS、对 P3 签 BLOCKED（resp_09d8b8cd07064603016b0772726a3087d0ba3cc238a24f3a77）。补交原审批文本和新定向测试结果后，P1 仍为 REWORK（resp_04edb1f365f3c380016b0772c9bd1c87d0957e9e079cf95d3e）。Reviewer 审阅了补项 B 的实现和测试证据，尚未独立复算最终 Diff 和重跑定向测试。回环监听、Host/Origin 与版本检查未提供操作者身份和正式仓库权限。

## 交付时服务状态

- pcp-dashboard-v1.service 保持 active。为保留 Supervisor 终验结论，已从该服务的私有设置移除本次规划开关。带当前草稿版本的本机模型 POST 返回 503，LAN 同类请求返回 403。两端读取均为 200，均保留七个版本。两端可免登录使用既有工作台和草稿编辑，正式派发保持禁用。
- 真实规划截图 `04-reviewed-ruflo-plan.png` 记录的是暂停前的实际回执。暂停后的状态保存在 `final-delivery-service-state.json`。

## 未解除条件

- P1 解除条件包括独立 Reviewer 对封存 Diff 复算摘要和复跑定向测试，以及在保持免登录工作台的前提下为模型调用提供已授权的操作者识别。正式确认须按服务端当前档案和仓库权限验证。现有确认仍为本地草稿决定。

- P3 需要实际授权的 EO Job / Workorder 写入，及匹配该任务的 ES Attempt / Invocation 授权。当前只有 EO Git/YAML 草稿与历史 ES 读取。
- 安全恢复原 Hub 和 Worker 前需查清并隔离旧 Run 28 的残留状态，保证不会恢复旧任务。首轮旧连接器只允许 probe/t1-t3 与保留 fixture 路径，不能把这些受限槽位冒用于本工单。具备已授权且受支持的现有路径后，由 Ruflo 发起一项新非生产任务。
- 当前回执可证明真实规划、人工编辑、计划恢复和本机 QA。运行中自动重排、暂停、恢复、接管、Worker 返工和交付回链均需真实新 Run 后再次验收。

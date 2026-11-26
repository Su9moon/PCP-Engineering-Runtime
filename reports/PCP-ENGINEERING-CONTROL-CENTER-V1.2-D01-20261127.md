# WO-20261126-002 D01 真实编排续作

## 部署与范围

- 在 V1.2 `aa10e159383cd2f5a9fbdb82e5a0ac25d0ca2105` 上续作。正式执行代码由 Reviewer 和 QA 验收，部署代码 `c51a98de770114d6f8db8eecb803736a9a24e2c5`。完整差异 SHA-256 为 `1f76bbcf8660ec2d711e252e4b9f3c266fe8fb3972fc4b4930075a65982949de`。
- 现有 `pcp-dashboard-v1.service` 服务继续提供 [本机访问](https://127.0.0.1:8787/#intake) 和 [私有局域网地址](https://192.168.5.6:8787/#intake)。实际 WLAN 地址从 192.168.5.4 变为 192.168.5.6。监听地址、TLS IP SAN 和两条既有 Hyper-V 8787 规则随地址更新，来源仍为 192.168.5.0/24，TLS 私钥保留。
- 免登录查看和普通草稿编辑沿用原产品。本机模型动作依赖服务账号私有 0600 配置、实际回环连接和精确 HTTPS 同源。授权属于服务及明确范围，不识别个体操作者。非生产正式动作只对已授权的单个草稿开放。LAN 不能触发模型、正式动作或修改该正式草稿。
- 复用原 EO Git 对象仓库和模板、ES ExecutionKernel 与既有 SQLite、Autoloop Hub 47355 和 `ruflo-local`。恢复前做一致性备份，保留 Run 28 原 Worker 文件及摘要。原 Hub 按租约把 Run 28 标为 `unknown`，重试计数 0。Worker 采用独立恢复目录，没有加载旧续接记录。未重派历史任务。

## 一次真实链路

| 环节 | 实际证据 |
|---|---|
| 中文需求对话 | Ruflo `gpt-6.2-sol`，HTTP 200，6319 ms，`resp_059c927ef62ad8cd016b089afe16bc87d0a0441876c7931433` |
| 中文工程计划 | 原 Supervisor `gpt-6.2-sol`，HTTP 200，25485 ms，`resp_0545f4de7cb9ca57016b089b04404887d093707ee184fa3ffd` |
| 人工编排 | 草稿 `29c0e94e849e44498173b9d427992aed`，需求 R1，Manual P2，1 个只读 Worker 串行。C0–C3 仍是建议。 |
| EO 权威读回 | `JOB-20261127-001`、`WO-20261127-001`，本机 EO ref `runtime/wo-20261126-002-d01`，提交 `6785b6d08d1a0a0a05fb11291158e0a90f59e4d0` |
| ES 真实授权 | `REQ-D01-WO-20261127-001`，`EXE-0feda448f1f24a76ad36a16840797041`，`ATT-fd2bc68acae84dafaafac069156bc70b`，`AINV-24f4121befed455c8c62771219f7bedc` |
| 真正派发 | Supervisor 放行 `resp_07cb54635f4a934a016b089ca4f6a087d0ac481233d7d8c809`，Dashboard 单次点击，Event 30／Run 29，状态 `done`，0 次重试 |
| Codex Worker | `ruflo-local`，线程 `01a219a5-5dfc-7a52-ac5b-c302121af7bd`，实际会话模型 `gpt-6.2-sol`，会话档位 `high`。认领至完成 14.322 秒，退出码 0，输入 15989 token（缓存 12672），输出 11 token。|
| 中文交付 | “D01 合成验证通过。”。Worker JSONL 中无工具事件，合成目录保持空，stdout SHA-256 `e8ddf658df8e18db9ee1d5972491fd1d294ad2d1e85cba6ddde575fe819c6edb`。Dashboard 已显示并导出执行报告。 |
| 独立 Reviewer / QA | 独立 Reviewer PASS，`resp_0e5c77a6ce189f6e016b089e02532087d084f4f9016723c2ea`。独立 Product QA PASS，`resp_08d305c36c67891d016b089e888b8c87d081bfa2949fa790a1`。两人分别复核同一原始运行证据包。 |
| ES 最终状态 | 原 Supervisor `ACCEPT_D01`，`resp_0e5392c3041dd4fe016b089e9fa9b087d0979374a86ede4ac9`。原 ExecutionKernel 持久化 `APPROVED`，实际回读 `DONE`。 |

## 定向验证

- 独立 Reviewer 从干净 checkout 生成完整 Diff，检查后续返工差异并复核最终变更。QA 使用独立 checkout 和隔离温测。两轮返工修复了正式草稿跨监听器保护、现行 EO blob 与冻结文件比对、Autoloop 规则唯一性及回执恢复、Worker 工具事件拒绝。
- P1 的定向 Python 5/5 通过，两个 Node 脚本的语法检查通过。独立 QA 的 64 个内存请求通过真实 Handler 路径，覆盖本机同源授权、LAN 拒绝和正式入口关闭。
- P3 的授权测试 3/3、EO/ES 隔离夹具五项通过。该夹具使用现有 EO Schema/Template 和真实 ExecutionKernel，Autoloop 投影为合成数据。真实运行证据另列。历史 25 项 Python／22 项浏览器断言沿用。
- 实测本机及 WSL 的 192.168.5.6 HTTPS 200。LAN 对模型请求和正式草稿修改回 403。独立 MEC 设备未实际访问。Windows 在同一主机上访问 LAN IP 超时，WSL mirrored 配置未显式设置同主机地址回环，原因尚未独立验证。
- 运行证据位于 `/home/cbnet/.local/state/pcp-control-center/WO-20261126-002/`。浏览器截图与中文执行报告位于 `D:/0 codex/runtime/2026-11-27/pcp-dashboard-v1.2-d01/`。不在仓库中提交凭据、私有部署配置或模型日志。

## 交付后的运行状态

- 最终浏览器读回和导出均为 `DONE`。关闭这一次验证的建单和派发权限，保留结果读取与本机模型入口。现有 Dashboard、Hub 和 Worker 均为 active。
- 本次的 Hub 和 Worker 采用本机用户的临时 systemd 单元。宿主机重启后需按已验收的启动边界恢复二者。

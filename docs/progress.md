# 35 天进度

起始日：2026-09-21 ｜ 每天 3 小时 ｜ 完成就打勾（`[x]` 完成 ／ `[–]` 已学过、跳过实操）

> **进度说明（09-21 更新）**：D2 / D3 的内容此前已自学过（旧教程工程里有对应练习），跳过实操直接进 D4。
> **进度说明（09-22 更新）**：D5 拆成两次执行 —— 09-22 看完视频，09-23 写代码并做验证（`docs/daily/D05-2-LCEL实操与验证.html`）。
> 表格「日期」列是**原始排期**；D4 起实际执行提前 3 天（D4 实际 09-21、D5 实际 09-22 起）。W1 结束时再决定要不要把日期列改成实际日期。

| 天 | 日期 | 阶段 | 主题 | 目录 | 状态 |
|---|---|---|---|---|---|
| D1 | 09-21 | W1 | 环境搭建 + LangChain 全景 | `week1-basics/day01-setup` | [x] 09-21 完成 |
| D2 | 09-22 | W1 | 模型的创建与调用 | `week1-basics/day02-switch-model` | [–] 内容已学过 |
| D3 | 09-23 | W1 | 调用方式与流式输出 | `week1-basics/day03-stream` | [–] 内容已学过 |
| D4 | 09-24 | W1 | Message 与提示词模板 | `week1-basics/day04-messages` | [x] 09-21 完成 |
| D5 | 09-25 | W1 | LCEL 管道 | `week1-basics/day05-lcel` | [ ] 09-22 视频完，实操延至 09-23 |
| D6 | 09-26 | W1 | 结构化输出 | `week1-basics/day06-structured` | [ ] |
| D7 | 09-27 | W1 | 周末产出：流式对话 CLI 工具 | `week1-basics/day07-cli` | [ ] |
| D8 | 09-28 | W2 | 工具（Tools）基础 | `week2-tools-agent/day08-tools` | [ ] |
| D9 ★ | 09-29 | W2 | 手写 Agent 循环（脱离框架） | `week2-tools-agent/day09-handwritten-agent` | [ ] |
| D10 | 09-30 | W2 | 用 create_agent 重建 | `week2-tools-agent/day10-create-agent` | [ ] |
| D11 | 10-01 | W2 | Agent 进阶用法 | `week2-tools-agent/day11-agent-advanced` | [ ] |
| D12 | 10-02 | W2 | 上下文与记忆 | `week2-tools-agent/day12-memory` | [ ] |
| D13 | 10-03 | W2 | 记忆持久化 | `week2-tools-agent/day13-persist` | [ ] |
| D14 | 10-04 | W2 | 周末产出：多功能智能助手 | `week2-tools-agent/day14-assistant` | [ ] |
| D15 | 10-05 | W3 | RAG 原理与三种架构 | `week3-rag/day15-corpus` | [ ] |
| D16 | 10-06 | W3 | 文档加载 | `week3-rag/day16-loaders` | [ ] |
| D17 ★ | 10-07 | W3 | 文本切分（关键实验） | `experiments/chunking` | [ ] |
| D18 | 10-08 | W3 | 向量与 Embedding | `experiments/embedding` | [ ] |
| D19 | 10-09 | W3 | 向量库 + 最小可用 RAG | `week3-rag/day19-mvp` | [ ] |
| D20 | 10-10 | W3 | 检索优化 | `week3-rag/day20-retrieval` | [ ] |
| D21 | 10-11 | W3 | Rerank 与混合检索 | `experiments/retrieval` | [ ] |
| D22 | 10-12 | W4 | 表格处理与长文摘要 | `week4-adv/day22-table-summary` | [ ] |
| D23 ★ | 10-13 | W4 | RAG 评估（数据意识） | `experiments/rag-eval` | [ ] |
| D24 | 10-14 | W4 | 包成能给别人用的产品 | `week4-adv/day24-webapp` | [ ] |
| D25 | 10-15 | W4 | LangGraph 入门：状态图 | `week4-adv/day25-langgraph` | [ ] |
| D26 | 10-16 | W4 | 状态、记忆与图化改造 | `week4-adv/day26-graph-rag` | [ ] |
| D27 | 10-17 | W4 | 人工介入（Human-in-the-Loop） | `week4-adv/day27-hitl` | [ ] |
| D28 | 10-18 | W4 | 可观测：trace 与成本 | `week4-adv/day28-observability` | [ ] |
| D29 | 10-19 | W5 | 选题与数据准备 | `project` | [ ] |
| D30 | 10-20 | W5 | 数据管线 | `project/data_pipeline` | [ ] |
| D31 | 10-21 | W5 | Agent 主链路 | `project/src` | [ ] |
| D32 | 10-22 | W5 | 界面与可用性 | `project/src` | [ ] |
| D33 | 10-23 | W5 | 健壮性补齐 | `project/src` | [ ] |
| D34 ★ | 10-24 | W5 | 提效度量（最关键的一天） | `project/benchmarks` | [ ] |
| D35 | 10-25 | W5 | 演示、文档与包装 | `project` | [ ] |

★ = 重点日，不要跳过

## 里程碑 tag

| 天 | tag | 含义 |
|---|---|---|
| D7 | `w1-cli-v0.1` | 流式对话 CLI |
| D14 | `w2-assistant-v0.2` | 带工具和记忆的助手 |
| D19 | `w3-rag-baseline` | RAG 基线，后面都对着它比 |
| D21 | `w3-rag-v0.4` | 加完过滤 / MMR / 混合检索 |
| D24 | `w4-web-v0.5` | 能给别人用的网页版 |
| D28 | `w4-obs-v0.6` | 接上可观测，有 trace |
| D32 | `w5-project-alpha` | 项目界面完成 |
| D35 | `v1.0-demo` | 最终作品，面试演示用这个 |

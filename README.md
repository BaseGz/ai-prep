# 影石实习准备 · 35 天 AI 应用开发

> A 35-day sprint building a demonstrable LLM application — RAG + Agent + MCP, in Python.

一个逐日推进的 AI 应用开发仓库：**2026-09-21 → 2026-10-25，每天 3 小时，35 天做出一个能演示、有提效数据的完整作品。**

目标岗位要求「能独立完成小型全栈原型 + 有自己动手做过的 AI 小项目 + 有数据意识」，所以——**这个仓库不是学习笔记，是证据。**

---

## 30 秒看懂（建议按这个顺序看）

| 看什么 | 在哪 | 说明 |
|---|---|---|
| 📊 **效果数据** | [`project/benchmarks/`](project/benchmarks/) | 工具 vs 人工的用时/准确率对照（D34 产出） |
| 🕳️ **我踩过的坑** | [`errors/index.md`](errors/index.md) | 按「现象 / 我以为 / 实际 / 怎么定位」四段记 |
| 🧪 **四组对比实验** | [`experiments/`](experiments/) | 切分粒度 / Embedding 选型 / 检索方案 / RAG 评估 |
| 🎬 **演示视频** | 待 D35 补链接 | 3 分钟走完主流程 |

> `git log --grep="exp"` 可以看到全部带数据的对比实验提交 —— 动手调过的痕迹都在里面。

## 效果数据

同一批任务，人工做一遍、工具做一遍，记录用时与准确率。**没有这张表，前面所有优化都只是「感觉还行」。**

| 任务 | 人工 | 工具 | 提效 |
|---|---|---|---|
| （D34 填真实数据，例：100 条素材打标 + 生成文案） | — 分钟 | — 分钟 | — × |

## 技术栈

| 层 | 选型 | 版本 |
|---|---|---|
| 语言 / 环境 | Python + 项目内 `.venv` | 3.12 |
| 框架 | `langchain` | 1.4.2 |
| 模型接入（OpenAI 兼容协议） | `langchain-openai` | 1.6.2 |
| 模型接入（官方集成） | `langchain-deepseek` | 1.1.0 |
| 编排（D25 起） | `langgraph` | — |
| 向量库（D18 起） | `chromadb` | — |

选型理由（改一次就换供应商、轮子最全）写在 [`docs/decisions.md`](docs/decisions.md)。

## 快速开始

```bash
git clone <this-repo>
python -m venv .venv && .venv/Scripts/activate     # Windows
pip install -r requirements.txt
cp .env.example .env                                # 填入自己的模型 API key
python week1-basics/day01-setup/env_check.py        # 自检：版本 / 依赖 / key / .gitignore
python week1-basics/day01-setup/hello_model.py      # 首次调用，会打印 token 用量
```

> 仓库内**不含任何 API key**：`.env` 已在 `.gitignore` 中，只提交 `.env.example`。

## 仓库导览

| 目录 | 是什么 |
|---|---|
| [`docs/plan/`](docs/plan/) | 35 天计划表、资源导航、面试手册、Git 规范（4 个 HTML） |
| [`docs/daily/`](docs/daily/) | 每日执行单，一天一份，双击就能看当天全部任务 |
| [`docs/journal/`](docs/journal/) | 每日日志：一句话结论 + 当天踩的坑 |
| [`docs/decisions.md`](docs/decisions.md) | 技术选型记录：选了什么、**舍弃了什么**、什么条件下换 |
| [`docs/progress.md`](docs/progress.md) | 35 天进度表 |
| [`errors/index.md`](errors/index.md) | 报错档案 —— 面试讲「踩过什么坑」的素材来源 |
| [`experiments/`](experiments/) | 四组对比实验，面试主打 |
| [`week1-basics/`](week1-basics/) … [`week4-adv/`](week4-adv/) | 每天一个练习目录，README 写明当天学什么、提交什么 |
| [`project/`](project/) | 第 5 周的完整作品，面试 80% 时间花在这里 |
| [`datasets/`](datasets/) | 语料（原始大文件不入库，只提交清单与来源） |

## 我是怎么用 AI 编程工具提效的

（D35 补齐，三条，每条一个具体例子）

1. **写之前**：让 AI 先给出 2–3 种实现方案和各自代价，我选一个 —— 例如「手写 Agent 循环 vs 直接用 `create_agent`」。
2. **写之中**：只让它写我已经想清楚的部分，边界条件自己补。
3. **写之后**：让它当 reviewer 找我的逻辑漏洞，而不是让它直接改。

## 进度与里程碑

当前进度：**D1 / 35** ｜ 最近更新：2026-09-21

| 里程碑 | tag | 含义 |
|---|---|---|
| D7 | `w1-cli-v0.1` | 流式对话 CLI |
| D14 | `w2-assistant-v0.2` | 带工具和记忆的助手 |
| D19 | `w3-rag-baseline` | RAG 基线（后面所有优化都对着它比） |
| D21 | `w3-rag-v0.4` | 加完过滤 / MMR / 混合检索 |
| D24 | `w4-web-v0.5` | 能给别人用的网页版 |
| D28 | `w4-obs-v0.6` | 接上可观测，有 trace |
| D32 | `w5-project-alpha` | 项目界面完成 |
| D35 | `v1.0-demo` | 最终作品 |

## 三条方针

1. 当天代码当天跑通、当天提交
2. 每 7 天不上新课，只做产出和复盘
3. 从 D15 起，所有练习一律用自己的语料 —— 面试时它就是项目本身

---

### 维护备忘（本机）

- 本地路径：`D:\AI_learning_project\03-Internship preparation\`（独立 Git 仓库）
- 上下文交接：[`docs/context.md`](docs/context.md) ｜ 新会话开场词：[`docs/新会话提示词.md`](docs/新会话提示词.md)
- 提交规范：[`docs/plan/影石实习-Git记录规范与每日Commit安排.html`](docs/plan/)（4 份规划 HTML 都在 `docs/plan/`）
- 提交模板已配置：`git config --local commit.template .gitmessage`
- commit 类型只用 7 种：`feat` / `exp` / `fix` / `refactor` / `docs` / `chore` / `test`（`exp` 专给带数据的对比实验）

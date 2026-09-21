# 项目上下文交接 · 影石（Insta360）AI 应用开发实习准备

> **这个文件是给「新会话」读的。** 换了聊天窗口、换了工作区，只要把这份文件带上，就能无缝接着做，不需要重新解释一遍前因后果。
>
> 最后更新：2026-09-21 ｜ 状态：**技术栈已定为 Python 轨（3.12.8 + 项目内 venv）**，D1 进行中（代码已写，尚未提交）

---

## 0. 一句话

用户是大三学生，目标拿到**影石（Insta360）AI 应用开发实习**。本项目的唯一使命：把他从「已学完 RAG/LangChain 之前的全部基础」带到「有一个能演示、有提效数据的完整 AI 项目」。

**当前进度：35 天路线已定、4 份规划文档已出、仓库已建好，D1（环境搭建 + 首次模型调用）已动手，代码在工作区待提交。**

---

## 1. 目标岗位的硬条件（决定一切取舍的源头）

JD 里的硬要求：

- 熟悉 JavaScript/TypeScript 或 Python 至少一门；理解 HTTP / API / JSON 等基础概念
- **不只会写页面**：写过接口、脚本或简单后端服务（Node.js / Python 均可），能独立完成小型全栈原型
- **调用过大模型 API**，或用过 Coze / Dify，有自己动手做过的 AI 小项目或 Demo（面试要准备演示）
- 熟悉 Cursor / Claude Code / Copilot 等 AI 编程工具，**能说清自己如何用 AI 提升开发效率**
- **每周实习 5 天，连续 6 个月及以上**（硬性，不可谈）

加分项（三选一即可满足「了解 RAG / Agent 框架（LangChain 等）/ MCP」这一条）：

- 对接过开放平台 API（飞书 / 微信 / Notion 等），或做过爬虫、自动化脚本、批量数据处理
- 了解 RAG、Agent 框架（LangChain 等）、MCP 中任意一项
- 能看懂 Figma 设计稿与组件体系，或做过 Figma 插件、浏览器插件、Illustrator/PS 脚本
- 做过数据看板、工具类页面，**有把工具交付给别人真正用起来的经验**
- 对 AI 提效、内部工具、**设计工程（Design Engineering）** 方向感兴趣
- **有数据意识：做工具时会想「怎么证明它省了多少时间」**

用户现状：RAG、LangChain、MCP 三项**都还没学**；它们之前的内容（JS/TS 或 Python、HTTP/API/JSON、后端接口、大模型 API、Coze/Dify、AI 编程工具）**已学完**。

---

## 2. 已确立的核心判断（新会话请直接沿用，不要重新推导）

### 2.1 LangChain 学到什么程度

**结论：学到「能独立交付一个可演示的 AI 项目」就够，不要往源码层钻。**
理由：LangChain 在 JD 里是加分项中的三选一，真正决定过不过的是「能独立完成小型全栈原型 + 有自己动手做过的 AI 项目 + 面试能演示」。

**必须掌握的 6 块**（要练到不查文档能写）：

1. **统一模型接入** —— `init_chat_model` / `ChatOpenAI(base_url=...)`，接国内模型（DeepSeek / 通义 / 智谱走 OpenAI 兼容协议）；**必须会传图**（影石做相机，多模态是天然加分位）
2. **消息体系与结构化输出** —— System/Human/AI Message、`ChatPromptTemplate`、few-shot；重点是 `with_structured_output()` + Pydantic（这是「玩具」和「工程」的分水岭）
3. **LCEL 管道** —— `prompt | model | parser`，`invoke / stream / batch / ainvoke`，能解释 `stream` 为什么能做出打字机效果
4. **Tool Calling（最关键）** —— `@tool`、`bind_tools()`、ToolMessage 回传、多轮循环。核心认知：**模型不执行任何东西，它只输出「想调哪个函数、参数是什么」，执行和结果回填是你的代码干的**
5. **Agent 与 LangGraph** —— 用 `create_agent` / LangGraph，**不要用 `AgentExecutor`**；会 StateGraph 的 state / node / 条件边 / checkpointer / `interrupt`
6. **RAG 组装 + 可观测** —— Loader、`RecursiveCharacterTextSplitter`、Embedding、Chroma/FAISS、Retriever、MMR、metadata 过滤、Rerank、引用溯源；再用 LangSmith 或 LangFuse 看 trace

**明确不要碰**（做了纯亏）：

- 旧版 API：`LLMChain`、`initialize_agent`、`AgentExecutor`、`ConversationBufferMemory`。**中文教程里约 80% 还是这套写法，跟错教程会让用户写出一堆过时代码，面试很减分。** 这是筛选教程的第一原则。
- 读 LangChain 源码 / 自造 Runnable 子类 / 提 PR
- 背 Chain 类型名（SequentialChain、RouterChain 那一堆）
- 几百个第三方集成的 loader（用到再查）

**5 条自测线**（达到即到位）：① 空白项目 30 分钟写出带工具调用的 Agent 并逐行解释；② 换模型改动不超过 5 行；③ 能回答「为什么这么切分 / 检索不到怎么排查 / 怎么证明比塞进上下文更好」；④ 有 trace 截图，说得出每步耗时和 token；⑤ 有一个**别人真在用**的东西 + 用前用后的时间对比。

### 2.2 学习顺序取舍

**RAG 和 MCP 不必都学。** 时间分配：**LangChain（Agent + Tool）> RAG > MCP**。
MCP 只需知道它是什么、能说出它和「自己写 `@tool` 函数」的区别即可；真要加分，花很低成本做个 Demo（自己写个 MCP server 让 Claude Code 连上）。

### 2.3 面试讲项目的固定结构

**问题是什么 → 我为什么这么选（舍弃了什么）→ 结果数据 → 踩过的坑。**
「舍弃了什么」和「踩过的坑」这两段是面试官判断有没有真做过的最快方式。

---

## 3. 路线：35 天 × 每天 3 小时

起始日 **2026-09-21（周一）**，结束 **2026-10-25**。每天设计 3 小时（2 小时版砍文档，4 小时版加笔记和推代码）。

| 阶段 | 天 | 主题 | 目标 |
|---|---|---|---|
| W1 | D1–7 | 打通链路 | 模型、消息、管道、结构化输出摸熟，产出一个能跑的 CLI 工具 |
| W2 | D8–14 | 工具与 Agent | 从「会调 API」跨到「会做 Agent」，**D9 是整份计划最高价值节点** |
| W3 | D15–21 | RAG 核心链路 | 从零搭出真正可用的文档问答系统 |
| W4 | D22–28 | RAG 进阶 + LangGraph + 可观测 | 变成能给别人用的产品，加流程控制与人工确认 |
| W5 | D29–35 | 项目冲刺 | 把碎片变成能演示、有数据、能写进简历的完整作品 |

### 四个重点日（不可跳）

| 天 | 内容 | 为什么关键 |
|---|---|---|
| **D9** | 不用任何框架，用 while 循环手写 Agent | 这 30 行比看 10 小时教程有用，做完才知道框架替你做了什么 |
| **D17** | 文档切分对比实验（500 / 1000 / 2000） | 面试必问「你怎么切的、为什么」，这天的结论就是答案 |
| **D23** | RAG 评估表（20 个测试问题 + 四项指标） | 直接对应 JD 的「数据意识」，没有它前面全是「感觉还行」 |
| **D34** | 真实数据测提效（人工 100 条 vs 工具 100 条） | 整个计划里最对应 JD 的一天 |

### 8 个里程碑 tag

`w1-cli-v0.1`(D7) → `w2-assistant-v0.2`(D14) → `w3-rag-baseline`(D19) → `w3-rag-v0.4`(D21) → `w4-web-v0.5`(D24) → `w4-obs-v0.6`(D28) → `w5-project-alpha`(D32) → `v1.0-demo`(D35)

**D19 的基线 tag 尤其别省**——没有基线，后面「优化了」就无法证明。

### 三条铁律

1. 当天代码当天跑通
2. 每个第 7 天（D7 / D14 / D21 / D28 / D35 这类产出日）不上新课，只做产出
3. **从 D15 起所有练习都用用户自己的语料**——面试时它就是项目

---

## 4. 已交付的 4 份规划文档

**唯一位置**：`D:\AI_learning_project\03-Internship preparation\docs\plan\`（在仓库内，随代码一起版本管理）

| 文件 | 内容 |
|---|---|
| `影石实习-35天学习计划表.html` | 35 天逐日任务，精确到视频第几讲几时几分、文档哪个页面；勾选进度存在本地浏览器 |
| `影石实习-AI学习资源导航.html` | 10 个学习模块的视频与文档直链、四周节奏、双轨（Python / JS-TS）技术栈对照、避坑清单 |
| `影石实习-学习留存与面试准备手册.html` | 留存清单（每日 10 分钟）+ 25 道面试题（6 组，含回答要点） |
| `影石实习-Git记录规范与每日Commit安排.html` | 仓库三分法、commit 模板、**35 天 × 59 条 commit 可直接复制**、8 个 tag、禁入清单 |

另有 `gitmessage-template.txt`（复制到仓库根目录改名 `.gitmessage` 用，**用户仓库里已配好**）。

### 关键资源速查

- 主力教程：尚硅谷《LangChain 从入门到实战 2026 版》 https://www.bilibili.com/video/BV1rv7A6oEeP/
- LangGraph 专攻：黑马《2026 最新版 LangChain + LangGraph 开发实战》 https://www.bilibili.com/video/BV178w1z7EHQ/
- RAG 最全：B 站《大模型 RAG 入门到精通实战》（54 讲，36–39 讲是切分精华） https://www.bilibili.com/video/BV1hccSeJEUD/
- 官方免费英文课（**只挑一门英文课就挑这个**）：LangChain Academy《Introduction to LangGraph》 https://academy.langchain.com/courses/intro-to-langgraph
- 开源系列：南哥 AGI 研习社 https://space.bilibili.com/509246474
- 官方文档（注意地址已从 `python.langchain.com` 迁到此处，站内可切 Python / JavaScript）：
  - LangChain https://docs.langchain.com/
  - LangGraph 示例库 https://github.com/langchain-ai/langgraph/tree/main/examples
  - Chroma https://docs.trychroma.com/
  - MCP https://modelcontextprotocol.io/ ｜ server 仓库 https://github.com/modelcontextprotocol/servers
- 文档路径规律（已验证）：官方文档页面为 `docs.langchain.com/oss/python/langchain/<页面>`，如 `/models`、`/tools`、`/retrieval`

---

## 5. 用户侧项目仓库（每天真正用的东西）

**路径：`D:\AI_learning_project\03-Internship preparation`**（上级 `D:\AI_learning_project` 是长期学习项目根，总控交接见其 `00-交接总览\交接文档-长期学习项目.md`）—— 已 `git init`，分支 `main`，3 次提交（`d8235f3` → `ecb167f`），已配 `git config --local commit.template .gitmessage`。

### 设计原则：仓库不是复习资料，是给面试官看的

按「面试官能不能直接看懂」分成 **学 / 证 / 用** 三块：

```
D:\AI_learning_project\03-Internship preparation\
├── README.md                    总入口，顶部三行链接（效果数据 / 踩的坑 / 演示视频）
├── .gitignore                   已写好；原则：向量库和原始数据不入库，生成它们的脚本必须入库
├── .gitmessage                  四段式提交模板（已 local 配置）
├── docs/
│   ├── context.md               ★ 本文件：上下文交接
│   ├── plan/                    4 份 HTML 交付物 + 说明
│   ├── daily/                   ★ 每日执行单（D01 起，一天一份 HTML，双击就能看）
│   ├── journal/                 每日日志（模板已给，已有 D0 立项 2026-09-20.md / D1 2026-09-21.md）
│   ├── progress.md              35 天进度表（含日期与打勾位）
│   ├── decisions.md             技术选型记录，已填一条（选 DeepSeek 的理由/代价/何时换）
│   ├── interview.md             25 题自答区，A1/B1/C1/D1/E1/F1 已给答案骨架
│   ├── stack.md                 ★ 待拍板：Python 还是 JS/TS
│   └── feedback.md              别人试用的记录表（JD 明确要这条）
├── errors/index.md              报错档案（四段式模板）—— 这个文件最值钱
├── experiments/                 ★ 「证」的核心，集中放，面试前 5 分钟能打开
│   ├── chunking/                D17 切分对比
│   ├── embedding/               D18 向量选型
│   ├── retrieval/               D21 检索方案（含 tag w3-rag-v0.4）
│   └── rag-eval/                D23 评估表
├── week1-basics/                D1–D7，每天一个 dayNN-主题/ 目录，内含 README
├── week2-tools-agent/           D8–D14
├── week3-rag/                   D15、D16、D19、D20（D17/18/21 落在 experiments/）
├── week4-adv/                   D22、D24–D28（D23 落在 experiments/）
├── project/                     D29–D35 的产物：src / data_pipeline / benchmarks
└── datasets/                    语料（raw/ 里的原始数据不入库）
```

**重要结构决策：把对比实验从每日目录里拎出来，集中放 `experiments/`。** 散着放，面试时要翻 35 个文件夹等于没有；集中放，面试前能一次打开四份牌——切分对比、检索方案对比、RAG 评估表、提效度量表。

**每个每日 README 里写了什么**（新会话若需生成更多，照此格式）：标题（D几 · 主题）→ 目录/预计时长/对应日期/阶段 → 一、今天学什么（视频章节含时长 + 官方文档页面）→ 二、今天动手做什么（带勾选框）→ 三、今天提交什么（**可直接复制进 PyCharm 的消息全文**）→ 四、今天必须留下的。

---

## 6. 硬约定（必须遵守）

### commit 类型（只用这 7 种）

`feat` / **`exp`（自定义，专给对比实验）** / `fix` / `refactor` / `docs` / `chore` / `test`

`exp` 是专门为「跑了一组对比实验、有数据」设计的（D17 切分、D18 选型、D21 检索、D23 评估、D34 提效）。面试官一条 `git log --grep="exp"` 就能看到所有动手调过的痕迹，**比任何自述都硬，绝对不要混进 `feat`**。

### commit 正文（四段式）

**现象 / 我以为（原因）/ 做法 / 结论** —— 其中「我以为」那一段最值钱，面试官能从中看出是不是真想过。

示例（D9）：

```
feat(day09): 手写 while 循环 Agent，脱离框架

现象：模型返回的 tool_calls 结构看不懂，第一次直接把它塞回 messages 报错
原因：tool_calls 是意图不是消息，必须先执行工具，再把结果包成 ToolMessage 回传
做法：循环 调模型 → 有 tool_calls 就执行 → 追加 ToolMessage → 直到没有
结论：框架替我做的就是循环控制 + 消息组装 + 异常兜底；模型本身没有执行权限
```

### 每天 2–6 条 commit，一个 commit 只做一件事

「加了工具」和「修了工具的 bug」必须拆开提交。

### 分支极简

日常就在 `main` 一条线。只在第 5 周做项目、或 D26 做图结构破坏性改造时才开分支，目的是保住能跑的旧版本（D26 建议开 `experiment/` 分支，保住 `w3-rag-v0.4`）。

### 一条要转达用户的洞察

**`git log` 的日期分布本身就是「我连续学了 35 天」的证据**，比一个塞满代码但只提交过 3 次的仓库可信得多。所以千万不要最后一天批量补——这反而会暴露。

---

## 7. 用户偏好（务必遵守）

1. **用 PyCharm 做 git 提交，不要给命令行指令**——命令行只作备选。所有提交说明按 GUI 写：Ctrl+K 提交流程、Alt+9 的 Git 工具窗打 tag。
2. 要求 **「精确到章节」** 的粒度：视频具体到第几讲几时几分、文档具体到哪个页面。
3. 交付物要**中文、可直接打开**（HTML / Markdown），结论先行、少铺垫。
4. 项目放在 **D 盘**（明确要求过）。
5. 用户会**持续进行**这个项目，希望内容可以跨会话延续。

### PyCharm 相关要点（已写进交付物）

- **Ctrl + K 默认勾选整个 changelist（当天所有改动）** —— 最大的坑，必须手动取消勾选不属于这条 commit 的文件。
- PyCharm 提交框是**一个大文本框，没有分开的标题和正文字段**。Git 按「第一行 + 一个空行」切分，**那个空行必须留**，否则整段消息会变成一条超长标题，`git log --oneline` 糊成一团。
- 必须改的设置（`Settings | Version Control | Commit`）：`Clear initial commit message` 勾上；`Force non-empty commit comments` 勾上；`Reformat code` / `Rearrange code` / `Optimize imports` **全关**（它们会在提交前自动改代码，污染 diff）。
- `Commit message inspections` 里「限制主题行宽度」和「限制正文行宽度」都勾上、都设 **72**。
- 打 tag：Alt+9 → Log → 右键那条 commit → New Tag。只在 8 个里程碑日做。
- 首次提交时 PyCharm 会问 `.idea/` 要不要纳入版本控制，个人仓库选忽略。

---

## 8. 未决 / 待办

| 事项 | 说明 | 状态 |
|---|---|---|
| ~~技术栈 Python 还是 JS/TS~~ | **已定：Python 轨**。理由/代价/何时换见 `docs/stack.md`；包清单已写进该文件，后续每日任务按 Python 细化 | ✅ 已决（2026-09-20） |
| 每日提醒自动化 | 用户说过「持续进行」，已问过是否要建每天固定时间的提醒（到点提醒今天是 D几、该看什么、该提交什么），**用户尚未答复** | 待确认 |
| 用户是否已开始 D1 | D1 材料（执行单 `week1-basics/day01-setup/README.md` + `env_check.py` + `hello_model.py` + `docs/daily/D01` HTML）已全部就绪 | 材料就绪，待用户执行 |
| **文档过时修正** | 计划表 D1 写的「看懂 Overview 页 *Agent development lifecycle* 图」**已失效**：新版官方文档改版，该图不存在，页面核心改为 `Agent = Model + Harness` + LangChain/LangGraph/Deep Agents 三方取舍。**后续凡引用「某张图」的旧笔记都要先验证** | 已在 D1 执行单修正，待回写进计划表 HTML |
| 第 5 周项目选题 | D29 才定。推荐二选一：**多模态素材整理 Agent**（拖一批照片/视频进去 → 视觉模型打标签 + 生成文案 + 语义检索，踩中多模态 + 设计工程）或 **内部知识库 Agent**（说明书/FAQ/客服工单 RAG + 工具调用 + `interrupt` 人工确认）。**无论选哪个都要带提效度量**（如 100 张图人工 40 分钟 → 工具 2 分钟，做成表格 + 截图） | 未定 |

---

## 9. 新会话开场提示词（可直接复制）

**完整版**（粘进新建的项目聊天，第一次发言用）：

```text
我在准备影石（Insta360）AI 应用开发实习，这件事不是从零开始：完整的项目上下文我已经整理在
D:\AI_learning_project\03-Internship preparation\docs\context.md，请先完整读它，再读同目录下的 progress.md 和 journal/ 里最新
的那篇日志，然后严格按里面的约定往下推。

背景一句话：我是大三学生，RAG / LangChain / MCP 之前的基础（编程语言、HTTP/API/JSON、后端接口、
大模型 API、Coze/Dify、Cursor 等 AI 编程工具）都已经学完；目标岗位的硬条件是「每周实习 5 天、连续
6 个月以上，能独立完成小型全栈原型，有能演示的 AI 小项目」，加分项里要求了解 RAG / LangChain /
MCP 任意一项。目前已经定好 35 天路线（2026-09-21 起，每天 3 小时，四个重点日 D9 手写 Agent 循环 /
D17 切分粒度实验 / D23 RAG 评估 / D34 提效度量），四份交付物放在 D:\AI_learning_project\03-Internship preparation\docs\plan\，
仓库骨架也已建好在 D:\AI_learning_project\03-Internship preparation，接下来就是逐天执行。

有三条我的习惯必须遵守：一是我用 PyCharm 做 git 提交，不要给我命令行指令，按 GUI 描述操作（提交是
Ctrl+K，打 tag 在 Alt+9 的 Git 工具窗里右键 New Tag）；二是内容要精确到章节，视频具体到第几讲几时
几分、文档具体到哪个页面；三是中文交付、结论先行、能给可直接打开的文件（HTML 或 Markdown）。

还有一个待办：docs\stack.md 里的技术栈（Python 还是 JS/TS）我还没拍板，你可以先问我，定了之后再把
后面的任务细化到具体包和写法。

我今天要做 D__（日期 ____），请开始。
```

**精简版**（只想快速接上时用）：

```text
继续我的影石实习准备项目：先读 D:\AI_learning_project\03-Internship preparation\docs\context.md，再读 docs\progress.md 和
journal/ 里最新的日志。我用 PyCharm 提交、要精确到章节、中文交付结论先行。今天做 D__。
```

---

## 10. 相关文件索引

| 用途 | 路径 |
|---|---|
| 上下文交接（本文件） | `D:\AI_learning_project\03-Internship preparation\docs\context.md` |
| 新会话开场提示词（可复制） | `D:\AI_learning_project\03-Internship preparation\docs\新会话提示词.md` |
| 长期学习项目根（上级） | `D:\AI_learning_project\`（目录总览见其 `README.md`，总控交接见 `00-交接总览\交接文档-长期学习项目.md`） |
| 本项目仓库根 | `D:\AI_learning_project\03-Internship preparation\` |
| 4 份 HTML 规划文档 | `D:\AI_learning_project\03-Internship preparation\docs\plan\` |
| 日常执行入口 | `D:\AI_learning_project\03-Internship preparation\docs\progress.md` |
| 每日执行单（D01 起） | `D:\AI_learning_project\03-Internship preparation\docs\daily\D01-环境搭建与LangChain全景.html` |
| 技术选型待办 | `D:\AI_learning_project\03-Internship preparation\docs\stack.md` |
| 报错档案（最值钱） | `D:\AI_learning_project\03-Internship preparation\errors\index.md` |

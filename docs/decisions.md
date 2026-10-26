# 技术选型决策记录

> 规则：每做一个技术选择，就写一条。三段 —— **选了 A 不选 B 的理由 / 代价是什么 / 什么条件下会换掉它**。
> 面试官判断你有没有真做过，很大程度看这一页。

---

## D1 · 用 DeepSeek 作为默认模型

**理由**：OpenAI 兼容协议，国内可直连，便宜，`base_url` 一改就能用。
**代价**：不是最强的模型，复杂推理会差一些；但学习阶段够用。
**什么时候换**：需要多模态输入（影石场景）时，换成支持传图的模型。

---

## D1 · 技术栈选 Python，不选 JS/TS

**理由**：JD 写的是「Python 或 JS/TS 至少一门」，两者等价；但中文教程和官方文档都是 Python 优先，
35 天 × 3 小时里「照着视频能跑通」比「语言更贴岗位」更值钱。四个重点日（D9/D17/D23/D34）全是数据与
实验，Python 侧的 chromadb / pandas 更顺手。JS/TS 的岗位优势（插件、Design Engineering）是加分项不是硬条件。
**代价**：少一个直接对上「设计工程」的语言证据；以后真要写 Figma / 浏览器插件还得补 TS。
**什么时候换**：第 5 周选题若偏插件形态，界面层改用 TS + HTTP 接口对接 Agent，主链路仍是 Python；整体不换栈。

---

## D1 · 环境用项目内 venv + Python 3.12，不用 conda、不用 3.13

**理由**：PyCharm 项目内 venv 跟着项目走，换电脑/重装只认 `.venv`，不会污染全局；Python 3.12 的
第三方轮子（Chroma / pypdf / 各类 loader）最全。LangChain 1.x 要求 `3.10 <= Python < 4.0`，3.12 稳在区间中段。
**代价**：venv 不跨项目复用，每个项目都得重装一次（本项目只此一份，可接受）。
**什么时候换**：需要同一环境里管多版本 CUDA / 多套 Python 并存时，才换 conda。

---

## D1 · 一个 git 仓库 = 一个独立 PyCharm 工程，不复用旧教程工程

**理由**：PyCharm 的提交窗口只认「当前工程根所在的仓库」。工程根 = 仓库根时，`Ctrl+K` 的列表里只有这个仓库的改动，不会误提交。
另外旧教程工程 `D:\python_langchain\langchain1.2_tutorial` 的解释器是 conda base（miniconda 3.14.7），
其 `requirements.txt` pin 在 `langchain==1.2.12`（实测 conda base 里实际装的是 1.3.16），与本项目要的 `1.4.2` 不一致；
而且那个文件夹不是 git 仓库，在里面写的代码进不了版本库。
**代价**：环境要重建一次（约 5 分钟）；旧教程里的 notebook 不能直接复用，得改写成 `.py` 并升到 1.4.2 的写法。
**什么时候换**：只有当多个仓库确实共享同一套严格相同的依赖时，才考虑把 venv 放到仓库外统一管理；本项目不适用。

---

## D1 · 新旧两个 LangChain 环境物理隔离：不合并、不互装、不互相 pip install

**理由**：实测本机安装情况（2026-09-21 核对 `.dist-info` 目录）：

| 环境 | 路径 | 实测装到的 langchain |
|---|---|---|
| 旧教程工程用的 conda base | `D:\minianaconda` | langchain 1.3.16 ／ langchain-core 1.6.1 ／ langgraph 1.2.11 ／ pydantic 2.13.4 |
| **本项目 venv** | `03-Internship preparation\.venv` | langchain 1.4.2 ／ langchain-core 1.6.3 ／ langchain-openai 1.6.2 ／ langchain-deepseek 1.1.0 ／ langgraph 1.2.11 ／ openai 3.16.2 ／ pydantic 2.13.5 |
| 系统 Python 3.12 | `C:\...\Programs\Python\Python312` | 只有 openai 2.24.0，无 langchain |

两个环境的包各自装在自己的 `site-packages` 里，**同名包版本不同也不会冲突** —— pip 只认「当前激活的是哪个解释器」。
旧工程目录下没有 `.venv`，它一直直接用 conda base，所以那边不需要、也不应该为本项目改动。

**代价**：磁盘上多一份约 300MB 依赖；同一行 `import langchain` 在两个工程里行为可能不同（旧 1.3.16 / 新 1.4.2），
跨工程复制代码不能假设 API 一致。

**三条纪律**（违反任何一条才会真出问题）：
1. 不在本项目 PyCharm 工程里把解释器切成 `D:\minianaconda`；
2. 不在未激活 `.venv` 的终端里裸敲 `pip install`（那会装进全局环境）；
3. 旧工程继续用 conda base 没关系，但**不要**在那边执行本项目的 `requirements.txt`。

**什么时候换**：不换。只有明确要复跑旧教程代码时才切回 conda base，且切回去只读不装。

---

## D10 · 用 `create_agent`，不手写循环（D9 的手写版留作对照）

**理由**：

同一道两单题，手写 30 行循环产出 **8 条消息**，`create_agent` 产出 **7 条**，类型序列完全一致 ——
少的唯一一条是 `SystemMessage`，它变成了 `create_agent` 的参数，不再进 `messages`。
这说明「模型想调什么 → 工具返回什么 → 再问一轮」这条链路，两边是同一条，不存在框架独有的魔法。

框架替掉的是五件事：工具执行、`ToolMessage` 回填（含 `tool_call_id` 配对）、
「没有 `tool_calls` 就停」的判断、多个 `tool_calls` 的遍历、轮数上限。
`stream(stream_mode="updates")` 还把这两步暴露成 `[model]` / `[tools]` 事件 —— 手写版要自己插打印才看得见。

**代价**：

1. **循环里插不进手。** 想按轮数换 prompt、改写工具返回值、失败重试，只能写 middleware，
   不能像手写版那样直接改 `messages` 再进下一轮。
2. **默认上限 9999 轮，且超限抛异常。** 手写版 `MAX_ROUNDS = 8` 是软着陆（返回一句话），
   框架版直接 `GraphRecursionError`，调用方必须 `try/except` 兜住。生产环境里这是要显式处理的一条。
3. **事件粒度不是「一条消息一次」。** 两个并行 `tool_call` 被拆成两个 `[tools]` 事件
   （实测两单题：**6 个事件对应 7 条消息**），拿事件数推算轮数会算错。

**什么时候换**：

只做标准 tool-calling → 一律 `create_agent`；需要改循环内部行为（逐步提示、结果改写、按轮数换模型）
→ 写 middleware，或退回 D9 那种手写循环。

---

## 模板（复制这一段用）

## D__ · （决定了什么）

**理由**：
**代价**：
**什么时候换**：

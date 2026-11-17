# D13 · 记忆持久化

> 目录 `week2-tools-agent/day13-persist/` ｜ 预计 3h ｜ 对应 2026-10-03（周六） ｜ 阶段：第 2 周 工具与 Agent

## 一、今天学什么

| 类型 | 内容 | 时长 |
|---|---|---|
| 视频 | 南哥 AGI 研习社 **EP04**「短期记忆持久化与记忆管理策略」（[BV1i1kNBLEY3](https://www.bilibili.com/video/BV1i1kNBLEY3)，24:15）。**EP03「Agent 3 种调用方式」跳过** —— `invoke` / `stream` / `batch` 在 D5（`chain.batch`）、D8（三种调用方式表）、D10（实验 3 的 `stream`）已练过 | 24 分钟 |
| 文档 | LangGraph [persistence 总览](https://docs.langchain.com/oss/python/langgraph/persistence)（只看 Checkpointer vs. store 对比表 + Quickstart）+ [checkpointers 页](https://docs.langchain.com/oss/python/langgraph/checkpointers)（Core concepts / Get and update state / Checkpointer libraries） | 20 分钟 |

> 核实记录（11-10）：计划表原来只给了 UP 主空间链接（`space.bilibili.com/509246474`），没有具体视频坐标，
> 已按合集补上 BV 号；「约 50 分钟」实测 **46:56**，准确。
> 另外 EP05「长期记忆持久化」（[BV1DsrUBREsL](https://www.bilibili.com/video/BV1DsrUBREsL)，14:01）是 D12 里
> 说「后面补」的 Store，列为**选做**。
>
> 依赖：`pip install langgraph-checkpoint-sqlite`（venv 里原本没有，11-10 已装）。

## 二、今天动手做什么

- [x] 把对话历史存到 SQLite，**关掉进程重新启动**后还能接着聊（90 分钟）
- [x] 三个实验：换 `thread_id` / 打印 checkpoint 明细 / 换回 `InMemorySaver` 对照

## 三、今天提交什么

在 PyCharm 里分 **2 次** 提交（代码 / 文档）。Ctrl + K 打开提交窗口后，**记得取消勾选不属于本次提交的文件**。

### 第 1 条：代码

```text
feat(day13): 对话历史落 SQLite，换掉 InMemorySaver 后重启仍能续聊

现象：
同一份脚本，第一次运行库里 0 条、答完写入 2 条、文件 4096 字节；
关掉进程重新启动，启动日志显示「已有 2 条消息、3 个 checkpoint」，
直接问「我叫什么」答出「你叫 Base，你在准备 AI 实习」。

我以为：
把对话存成文本追加到文件里就够了，读回来拼进 messages 即可；
持久化就是把 messages 序列化。

做法：
sqlite3.connect(DB, check_same_thread=False) + SqliteSaver(conn) 一个构造参数换掉 InMemorySaver；
用 get_state / get_state_history 读回来，用 sqlite_master 直接查表看结构；
三个实验：换 thread_id、打印 checkpoint 明细、换回 InMemorySaver 对照。

结论：
持久化存的不是对话文本，是图的每一个 super-step —— 一轮对话 3 个 checkpoint，
表里是 checkpoints + writes 两张，按 thread_id 索引。
「记住」在工程上等于：一张表 + 一个 id + 一个连接；
而连接必须跨线程，因为执行节点的不止一个线程。
```

### 第 2 条：文档

```text
docs(day13): 持久化不是存对话，是存每一个 super-step

现象：
第一轮对话 2 条消息，库里却是 3 个 checkpoint、3 行 writes；
删掉 check_same_thread=False 直接报 ProgrammingError，两个线程 id 对不上。

我以为：
checkpoint 数应该等于轮数；SQLite 是单文件、单进程，加线程参数是多余的小心。

做法：
把 get_state_history 的 step / source / next / 消息数逐条打出来，
确认 step=-1 是输入、step=0 之后是节点执行；
再删掉 check_same_thread=False 复现报错，抄下两个线程 id。

结论：
super-step 才是持久化的最小单位，一轮对话是多个 super-step 拼出来的。
文档没写 check_same_thread，因为那是 sqlite3 的常识、不是 LangGraph 的 API ——
这类「文档缺口」只能靠跑出来补。
```

## 四、今天必须留下的

- [ ] 代码当天跑通
- [ ] 日志 → `docs/journal/2026-10-03.md`
- [ ] 一句话结论：________________________________

---

> 「重启不丢上下文」是内部工具的基本要求，不是加分项。

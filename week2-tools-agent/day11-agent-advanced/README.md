# D11 · Agent 进阶用法

> 目录 `week2-tools-agent/day11-agent-advanced/` ｜ 预计 3h ｜ 对应 2026-10-01（周四） ｜ 阶段：第 2 周 工具与 Agent

## 一、今天学什么

| 类型 | 内容 | 时长 |
|---|---|---|
| 视频 | 尚硅谷 **P57–P62**（结构化输出 4 种策略 / 错误处理 / 流式输出） | 实测 **83:20** |
| 文档 | Agents 页：`Structured output` / `## Streaming` / `Fault tolerance` | 20 分钟 |

> **坐标核实（2026-10-27）**：计划写的「第 07 章后半 约 50 分钟」偏短 —— `BV1rv7A6oEeP` 的
> P57–P62 实测 **83:20**；**P63「实战：多功能智能助手」16:55 留给 D14**（周末产出的题目就是它）。
> 另：Agents 页**没有**「多工具」「错误处理」这两个小节，真实位置是
> `Core components > Structured output`、独立小节 `## Streaming`、`Configure the harness > Fault tolerance`。

## 二、今天动手做什么

- [ ] 工具加到 4 个；接上 `response_format`，看结构化结果落在哪里（30 分钟）
- [ ] 故意让一个工具抛异常，对比三种结果：裸 `raise` / 工具内 `try` / `ToolRetryMiddleware`（40 分钟）
  - 实测基线：裸 `raise` → 异常冒顶、整轮消息全丢；加 `ToolRetryMiddleware(max_retries=1)` → 不中断，
    错误以 `Tool 'query_refund' failed after 2 attempts ... Please try again.` 回填，模型自己转去查物流

## 三、今天提交什么

在 PyCharm 里分 **2 次** 提交。Ctrl + K 打开提交窗口后，**记得取消勾选不属于本次提交的文件**。

### 第 1 条（结构化输出）

```text
feat(day11): Agent 接入结构化输出，结果落在 structured_response

现象：
加了 response_format 之后，messages 最后一条不再是 AIMessage，
而是一条内容为 "Returning structured response: ..." 的 ToolMessage。

我以为：
结构化输出是让模型直接吐一段 JSON 字符串，我从 content 里 json.loads 解析。

实际：
框架把它做成了一次「假工具调用」—— 最后那条 AIMessage 的 tool_calls 里，
工具名就叫 OrderAnswer（我的 Pydantic 类名）。schema 就是这个工具的参数表。

做法：
response_format=OrderAnswer（Pydantic）；先试过 ProviderStrategy，
DeepSeek 直接 400 This response_format type is unavailable now，只能走 ToolStrategy。

结论：
结构化输出 = 给模型一个只有 schema、没有实现的工具，逼它按这个形状填参数；
结果在 result["structured_response"]，不在 messages 里。
```

### 第 2 条（错误处理）

```text
fix(day11): 工具抛异常会中断整轮，改用 ToolRetryMiddleware 兜住

现象：
裸 @tool raise RuntimeError 之后，agent.invoke 直接把异常抛到顶层，
前面已经跑过的几轮消息一条都拿不到，structured_response 也没有。

我以为：
框架会像 D9 我手写的那样，把工具异常包成 ToolMessage 回传，循环继续。
README 里也写着「执行工具那一步没有 try/except」—— 我原以为补上就行。

实际：
create_agent 默认不兜工具异常；兜底是 ToolRetryMiddleware，
它默认 on_failure='continue'，重试完把错误包成一条 ToolMessage 交给模型。

做法：
middleware=[ToolRetryMiddleware(max_retries=1)]；max_retries=1 的文案是
failed after 2 attempts（1 次原始 + 1 次重试）。

结论：
工具失败不是异常，是一条「坏消息」—— 把错误当结果回传，模型自己会找替代路径
（实测它失败后转去查了物流，最后在 status 里写「退款查询失败」）。
```

## 四、今天必须留下的

- [ ] 代码当天跑通
- [ ] 日志 → `docs/journal/2026-10-01.md`
- [ ] 一句话结论：________________________________

---

> 「工具失败时不要中断整个循环，把错误当结果回传给模型」——这个设计点面试很爱问。

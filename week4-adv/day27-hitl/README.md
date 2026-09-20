# D27 · 人工介入（Human-in-the-Loop）

> 目录 `week4-adv/day27-hitl/` ｜ 预计 3h ｜ 对应 2026-10-17（周六） ｜ 阶段：第 4 周 RAG 进阶 + LangGraph + 可观测

## 一、今天学什么

| 类型 | 内容 | 时长 |
|---|---|---|
| 视频 | Academy Module 3 Lesson 1–5（Streaming / Breakpoints / Editing State / Human Feedback / Dynamic Breakpoints / Time Travel） | 约 60 分钟 |
| 文档 | 官方 human-in-the-loop / interrupt 相关页面 | 20 分钟 |

## 二、今天动手做什么

- [ ] 加 interrupt——敏感操作执行前先弹确认，用户同意才继续（70 分钟）

## 三、今天提交什么

在 PyCharm 里分 **1 次** 提交。Ctrl + K 打开提交窗口后，**记得取消勾选不属于本次提交的文件**。

### 第 1 条

```text
feat(langgraph): 加 interrupt，敏感操作前人工确认

涉及写操作时暂停，用户确认后才继续
拒绝时的回退路径也要写清楚
```

## 四、今天必须留下的

- [ ] 代码当天跑通
- [ ] 日志 → `docs/journal/2026-10-17.md`
- [ ] 一句话结论：________________________________

---

> 内部工具几乎都需要这一步。面试讲这个很加分，它体现你有工程风险意识。

# D28 · 可观测：trace 与成本

> 目录 `week4-adv/day28-observability/` ｜ 预计 3h ｜ 对应 2026-10-18（周日） ｜ 阶段：第 4 周 RAG 进阶 + LangGraph + 可观测

## 一、今天学什么

| 类型 | 内容 | 时长 |
|---|---|---|
| 视频 | 尚硅谷 第 08 章 中间件 + 第 03 章 LangSmith 的使用 | 约 60 分钟 |
| 视频 | LangSmith 可观测文档 + trace 快速开始 | 25 分钟 |

## 二、今天动手做什么

- [ ] 接上 LangSmith（国内网络不便时用自建 LangFuse），跑一遍项目，在 trace 里截图每一步的耗时和 token（65 分钟）

## 三、今天提交什么

在 PyCharm 里分 **2 次** 提交。Ctrl + K 打开提交窗口后，**记得取消勾选不属于本次提交的文件**。

### 第 1 条

```text
feat(day28): 接入 LangSmith（或自建 LangFuse）可观测

跑一遍 D24 的网页版，导出完整 trace
```

### 第 2 条

```text
docs(traces): trace 截图与耗时分析

每一步耗时与 token 消耗
定位最慢的一步，写清原因
```

提交完成后打 tag：Git 工具窗（Alt + 9）→ Log → 右键那条 commit → New Tag → `w4-obs-v0.6`

## 四、今天必须留下的

- [ ] 代码当天跑通
- [ ] 日志 → `docs/journal/2026-10-18.md`
- [ ] 一句话结论：________________________________

---

> 「我通过 trace 定位到检索为空导致回答跑偏」——这句话比任何理论都有说服力。

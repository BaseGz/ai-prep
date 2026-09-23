# D5 · LCEL 管道

> 目录 `week1-basics/day05-lcel/` ｜ 预计 3h ｜ 计划日 2026-09-25（周五） ｜ 阶段：第 1 周 打通链路
> **实际执行：视频 09-22 看完，实操与验证 09-23 进行**（比计划日提前 3 天）

## 一、今天学什么

| 类型 | 内容 | 时长 |
|---|---|---|
| 视频 | 全模块拆解 第 5 讲 链结构 25:00（**已看完；未讲管道符语义**） | 25 分钟 |
| 视频 | 尚硅谷 P19 测试 invoke 传递三种不同的参数类型 22:08 | 22 分钟 |
| 视频 | 尚硅谷 P20 invoke 的返回值的详细说明 8:42 | 9 分钟 |
| 视频 | 尚硅谷 P21 流式调用、批量调用与异步调用 18:41 | 19 分钟 |
| 文档 | 官方 Models 页 **`Invocation`** 大节 → Invoke / Stream / Batch | 20 分钟 |
| 补课 | `learn_runnable.py` → `probe_types.py`（本地脚本，**零 token**） | 15 分钟 |

> ⚠️ **两处旧引用已核实失效**（2026-09-23 实测，原写法已替换）：
> ① 「尚硅谷中 LCEL 相关小节」—— 该课 `BV1rv7A6oEeP` 全 **120 P 中没有任何一讲**叫 LCEL / 管道 / Runnable，
> 已换成对症的 **P19 / P20 / P21**；
> ② 「官方 Models 页面中 LCEL / Runnable 部分」—— 该页**没有** Runnable 或管道符说明，
> 改为 `Invocation` 大节下的 Invoke / Stream / Batch。

## 二、今天动手做什么

- [x] 补地基：跑通 `learn_runnable.py`（普通函数 → 运算符重载 → 自己写 `__or__` → Runnable）
- [x] 看证据：跑通 `probe_types.py`（今天 10 个疑问的可执行答案，零 token）
- [ ] 把第 4 天的对话改写成 prompt | model | parser，四种调用各写一遍（invoke / stream / batch / ainvoke）（60 分钟）

## 三、今天提交什么

在 PyCharm 里分 **3 次** 提交。Ctrl + K 打开提交窗口后，**记得取消勾选不属于本次提交的文件**。

| 条 | 标题 | 勾选这些文件 |
|---|---|---|
| 1 | `feat(day05): LCEL 管道跑通，四种调用各验证一遍` | `lcel_demo.py`、`pipe_proof.py`、`learn_runnable.py`、`probe_types.py` |
| 2 | `exp(day05): batch 与 for + invoke 的耗时对比` | 写耗时对比的那个脚本（`lcel_demo.py` 或单独建） |
| 3 | `docs: 补 D4/D5 日志结论，同步进度与文档过时清单` | `NOTES-管道符与类型链.md`、本文件、`docs/journal/2026-09-24.md`、`docs/journal/2026-09-25.md`、`docs/progress.md`、`docs/context.md` |

> **三条的消息全文见 `docs/daily/D05-2-LCEL实操与验证.html` 第 6 节**（可直接复制）。
> 这里只留勾选清单 —— 消息只在执行单里维护一份，避免两处不一致。

## 四、今天必须留下的

- [ ] 代码当天跑通
- [x] 日志 → `docs/journal/2026-09-25.md`（**已起草**；建议用自己的话改一遍，面试要讲的是你自己的版本）
- [ ] 一句话结论：________________________________

---

> 要能一句话说清「管道符到底做了什么」——说不出就是没懂。

---

## 附：本目录文件清单

| 文件 | 是什么 | 什么时候用 |
|---|---|---|
| `README.md` | 本文件 —— 当日总览与提交清单 | 每天开工先看 |
| `learn_runnable.py` | **补地基**：普通函数 → 运算符重载 → 自己写 `__or__` → Runnable | 看不懂 `Runnable` / 重载时先跑它 |
| `pipe_proof.py` | **验收**：用代码证明管道符语义（6 步，零 token） | 补完地基后再跑 |
| `probe_types.py` | **答案合集**：D5 全部疑问的可执行版（10 段，零 token） | 复习时跑一遍 |
| `NOTES-管道符与类型链.md` | 上面那些结论的书面版（含速查表与面试素材） | 面试前翻 |
| `NOTES-路由与多链.md` | 路由 / 多链 / 「谁来做选择」（D5 延伸） | 同上 |
| `lcel_demo.py` | **今天的正题**（待写） | 改写 D4 对话 + 四种调用各跑一遍 |

> 全部脚本**零 token**：`learn_runnable.py` / `pipe_proof.py` / `probe_types.py` 均不调用真模型。
> `probe_types.py` 第 7~9 段会构造一个 `ChatDeepSeek` 对象，但用的是假 key 且只做本地类型校验 —— **不发任何网络请求**。

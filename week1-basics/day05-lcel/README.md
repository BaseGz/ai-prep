# D5 · LCEL 管道

> 目录 `week1-basics/day05-lcel/` ｜ 预计 3h ｜ 对应 2026-09-25（周五） ｜ 阶段：第 1 周 打通链路

## 一、今天学什么

| 类型 | 内容 | 时长 |
|---|---|---|
| 视频 | 全模块拆解 第 5 讲 链结构 25:00 | 25 分钟 |
| 视频 | 尚硅谷中 LCEL 相关小节（管道与 Runnable 接口） | 约 35 分钟 |
| 文档 | 官方 Models 页面中 LCEL / Runnable 部分 | 20 分钟 |

## 二、今天动手做什么

- [ ] 把第 4 天的对话改写成 prompt | model | parser，四种调用各写一遍（invoke / stream / batch / ainvoke）（60 分钟）

## 三、今天提交什么

在 PyCharm 里分 **1 次** 提交。Ctrl + K 打开提交窗口后，**记得取消勾选不属于本次提交的文件**。

### 第 1 条

```text
refactor(day05): 第 4 天对话改写为 LCEL 管道

prompt | model | parser，invoke / stream / batch / ainvoke 四种各写一遍
一句话总结管道符：把上一个 Runnable 的输出接给下一个的输入
```

## 四、今天必须留下的

- [ ] 代码当天跑通
- [ ] 日志 → `docs/journal/2026-09-25.md`
- [ ] 一句话结论：________________________________

---

> 要能一句话说清「管道符到底做了什么」——说不出就是没懂。

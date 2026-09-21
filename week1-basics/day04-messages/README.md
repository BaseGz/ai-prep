# D4 · Message 与提示词模板

> 目录 `week1-basics/day04-messages/` ｜ 预计 3h ｜ **计划日 2026-09-24**（前三天内容已学过，本轮提前到 09-21 开始） ｜ 阶段：第 1 周 打通链路

## 一、今天学什么

### 视频 · 尚硅谷《2026 版 LangChain 教程》

链接：<https://www.bilibili.com/video/BV1rv7A6oEeP/> —— 在播放页右侧「选集」里点对应集数。

**必看 5 讲，合计 67 分 35 秒：**

| 分 P | 标题 | 时长 | 看完要带走的一句话 |
|---|---|---|---|
| **P25** | 认识消息与消息的两种格式 | 11:28 | 模型要的是**消息列表**，不是字符串；消息有两种写法（消息对象 / 元组） |
| **P26** | 4 种消息对象中字段的说明 | 13:29 | System / Human / AI / Tool 四种消息各自装什么 |
| **P27** | 对话历史的管理和优化 | 11:36 | 所谓「记忆」，就是有人替你维护了一个列表 |
| **P28** | 案例：多轮对话聊天机器人 | 11:46 | 把历史 append 回去，模型才「记得」 |
| **P30** | ChatPromptTemplate 的两种实例化方式和三种调用方式 | 19:16 | 模板 = 带变量的消息列表，仅此而已 |

**加看（时间够再看，合计 44 分 28 秒）：** P29 content 和 content_blocks 的使用 13:47 ｜ P31 ChatPromptTemplate 初始化的 6 种参数类型 14:20 ｜ P32 部分变量预填充 / 消息占位符 16:21

> 今天不看的：P23 / P24（LangSmith 介绍，留给 D28）、P33 之后的工具与 Agent（W2 的内容）。

### 文档 · 官方 Messages 页面（精确到小节）

<https://docs.langchain.com/oss/python/langchain/messages>

| 小节 | 读什么 |
|---|---|
| **Basic usage** → Text prompts ／ **Message prompts** ／ Dictionary format | 同一个 prompt 的三种写法；**`Message prompts` 就是「提示词模板」** |
| **Message types** → System ／ Human ／ AI ／ Tool message | 四种消息。AI message 下的 **Token usage** 小节细看 —— D28 算成本靠的就是 `usage_metadata` |
| **Message content** → Standard content blocks（选看） | `content_blocks` 是什么，为什么 P29 专门讲一节 |

⚠️ **一处修正**：官方文档**已经没有独立的「Prompt templates」页面**了（1.x 改版后并入 Messages 页的 Message prompts 小节）。计划表里那条已同步改掉 —— 以后站内搜 `Prompt templates` 会搜不到，别以为是自己找错了。

## 二、今天动手做什么

- [ ] 写 `messages_demo.py`：手动拼 messages 数组做 3 轮对话（60 分钟）
  - **骨架已经放好了**，文件里三处 `TODO` 由你自己填
  - **硬性约束：全程不许用任何记忆类**（不用 `InMemorySaver`、不用 `RunnableWithMessageHistory`、不用 `create_agent`）——今天的全部意义就是体会「上下文是我自己 append 出来的」
  - 导包：光标停在报红的类名上按 **`Alt`+`Enter`** → 选「导入此名称」（Windows 默认按键映射下的「显示上下文操作」）。整理 import 用 **`Ctrl`+`Alt`+`O`**（优化导入）。**别切按键映射方案**，切了 `Ctrl`+`K` 提交就废了
- [ ] 记下每一轮的 token 数，看它怎么随轮数涨（10 分钟）

## 三、验收标准（做不到就是没懂）

- [ ] 第 1 轮告诉模型一个信息（比如你的名字），**第 2 轮它能答出来**
- [ ] 把历史列表清空再问同一个问题，**它答不出来了** —— 这条是关键，证明上下文确实来自那个数组
- [ ] token 数逐轮递增

## 四、今天提交什么

在 PyCharm 里分 **1 次** 提交。Ctrl + K 打开提交窗口后，**记得取消勾选不属于本次提交的文件**（比如 `docs/journal/` 之外的改动）。

```text
feat(day04): 手动维护 messages 数组实现 3 轮对话

自己 append HumanMessage / AIMessage，全程不用任何记忆类
结论：所谓上下文，就是你自己维护的一个数组
```

## 五、今天必须留下的

- [ ] 代码当天跑通
- [ ] 日志 → `docs/journal/2026-09-24.md`
- [ ] 一句话结论：________________________________

---

> 这一步想明白，后面理解 Agent 记忆和上下文裁剪会轻松很多。
> 面试可复用的一句话：**「上下文不是模型的能力，是调用方每次都把历史重新发一遍。」**

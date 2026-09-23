# NOTES · 多链、路由与「谁来做选择」

> D5（LCEL 管道）延伸笔记 ｜ 2026-09-22 ｜ 环境实测：langchain 1.4.2 / langchain_core 1.6.3
>
> **一句话结论：LangChain 从来不会「自动」选链。选哪条链永远是你自己写的一步代码，你写了哪种，就决定了要不要调模型。**

---

## 1. 先破一个常见误解

很多教程给人一种印象：把 N 条链注册进去，框架就会自己看用户问题、挑最合适的那条。

**没有这回事。** 框架不知道你有几条链、每条是干什么的。「选哪条链」这行代码必须你自己写。

同理，**「根据提示词去找场景相近的提示词模板」这个机制在框架里不存在**。
`prompt_template` 是给模型看的**指令**（"你是一名 Python 工程师…"），里面全是角色设定和输出格式，
拿它去跟用户问句算任何形式的「相近度」都没有意义。

---

## 2. 四种路由方式（关键差别只有一个：谁来判断）

| 方式 | 判据是什么 | 要调模型吗 | 实现原语 |
|---|---|---|---|
| **代码路由** | 你手写的条件（关键词 / 长度 / 身份 / 菜单项） | **不调** | `RunnableBranch`、`if/else` |
| **语义路由** | 向量距离：用户问句 vs 每条链的**典型示例句** | 只调 **embedding** 接口，不调对话模型 | embedding + 余弦相似度 |
| **大模型路由** | 大模型读懂语义后的判断 | **调 1 次**对话模型 | `with_structured_output` + 枚举 |
| **Agent 自选** | 大模型在循环里每轮自己决定 | **调 N 次** | `@tool` + `create_agent` |

> 注意第 2 行：语义路由比的是**你准备的示例句**，不是提示词模板本身。
> 顺带一个事实：DeepSeek 只提供对话接口、**没有 embedding 接口**，走这条路要用通义（DashScope）。

---

## 3. 版本事实（本机实测，务必记住）

**教程里那套路由链在你这个环境里已经跑不起来了。**

| 实测项 | 结果 |
|---|---|
| `langchain.chains` 模块 | **不存在** → `ModuleNotFoundError: No module named 'langchain.chains'` |
| `RouterChain` / `MultiPromptChain` / `LLMRouterChain` / `RouterOutputParser` | **全部移除** |
| `langchain_community` | 未安装（社区版 `SemanticRouter` 那类工具不在本项目依赖里） |
| `RunnableBranch` | ✅ 在 `langchain_core.runnables` |
| `ChatDeepSeek.with_structured_output` | ✅ 可用（默认 `method='function_calling'`） |
| `langchain` 1.x 顶层导出 | 空列表（已退化为纯 meta 包） |

**凡是写 `from langchain.chains.router import MultiPromptChain` 的文章，都是 0.x 时代的，直接跳过。**

这与本项目此前两次「教程已失效」同类：
- D1：官方 Overview 页的 *Agent development lifecycle* 图已随改版下线（核心改为 `Agent = Model + Harness`）
- D4：官方 *Prompt templates* 独立页已下线（并入 Messages 页的 `Message prompts` 小节）

→ 本仓库第 3 条同类记录。**凡引用旧教程代码/旧文档页面，先在本机验证再写进代码。**

### 旧版是怎么做的（了解即可，不要照抄）

`prompt_infos` 每条是 `{name, description, prompt_template}`。框架内部把
`name + description` 拼成列表填进 `MULTI_PROMPT_ROUTER_TEMPLATE`，连同用户输入发给模型，
要它返回 JSON `{"destination": "python"}`；解析后再用选中的 `prompt_template` **发起第 2 次调用**生成答案。

所以：**是模型读你手写的 `description` 做出判断** —— 既不是字符串匹配，也不是向量检索。
代价是贵一倍、慢一倍、且不确定（靠 `RouterOutputParser` 解析纯文本 JSON，模型稍不听话就崩）。

---

## 4. 现代做法：`with_structured_output` + 枚举

### 4.1 关键变化

| | 旧版（0.x） | 现代（1.x） |
|---|---|---|
| 路由输出 | 让模型写一段 JSON 文本 | 用 schema 强约束，直接返回对象 |
| 解析 | `RouterOutputParser` 解析文本，会失败 | 框架/SDK 保证结构合法 |
| 越界选项 | 模型可能编出一个不存在的链名 | **枚举外的值根本无法通过校验** |
| 写法 | 专用链类 | 一条普通 LCEL 链 + 一个 `if` / `RunnableBranch` |

### 4.2 完整代码（本项目栈，已验证 API 签名）

```python
from enum import Enum
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = init_chat_model("deepseek:deepseek-chat", temperature=0)


class RouteEnum(str, Enum):
    python = "python"
    golang = "golang"
    other = "other"


class Route(BaseModel):
    destination: RouteEnum = Field(description="这句话最适合由哪位专家来回答")


ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "你是分诊台。读用户的话，判断该交给哪位专家。\n"
     "- python：Python 语法、库、报错\n"
     "- golang：Go 语法、并发、工具链\n"
     "- other：不属于以上任何一类"),
    ("human", "{input}"),
])

# ★ 全部的关键就在这一行：schema 是枚举，模型无法返回不存在的选项
route_chain = ROUTER_PROMPT | llm.with_structured_output(Route)


def make_expert(sys_prompt: str):
    return (
        ChatPromptTemplate.from_messages([("system", sys_prompt), ("human", "{input}")])
        | llm
        | StrOutputParser()
    )


EXPERTS = {
    "python": make_expert("你是 Python 工程师，只回答 Python 相关问题。"),
    "golang": make_expert("你是 Go 工程师，只回答 Go 相关问题。"),
    "other":  make_expert("你是通用助手。"),
}


def ask(text: str) -> str:
    """先路由（第 1 次调用），再执行（第 2 次调用）"""
    decision = route_chain.invoke({"input": text})      # -> Route 对象，不是字符串
    expert = EXPERTS[decision.destination.value]        # 查表，不是 if/elif 一长串
    return expert.invoke({"input": text})


if __name__ == "__main__":
    print(ask("asyncio.gather 里一个任务抛异常，其他任务会怎样？"))
    print(ask("Go 里 select 和 switch 有什么区别？"))
```

### 4.3 三个要点

1. **路由那一次调用要用 `temperature=0`**（或换一个更便宜的小模型）—— 分类任务不需要创造性。
2. **`with_structured_output` 默认 `method='function_calling'`**（实测签名确认）。DeepSeek 支持 function calling，所以默认就能用；
   不要随手改成 `json_schema`，那需要服务端支持。
3. **仍然要兜底**：枚举里有 `other` 只解决了「选项越界」，不解决「模型选错」。生产代码要能记录路由命中分布，
   才能知道分类准不准。

---

## 5. 代码路由：判断标准与分类举例

### 5.1 判断标准只有一条

> **你能写出一个「不用模型就能算出来的布尔表达式」吗？能 → 就用代码路由。**

这是最省（零 token）、最快（零延迟）、最稳（同样输入永远同样结果）的一种，**能用就用**。

### 5.2 常见的分类维度（都是真实场景）

| 维度 | 判据示例 | 路由到 |
|---|---|---|
| **关键词** | 输入里有 `Traceback` / `报错` | 调试专家链 |
| **输入长度** | `len(text) > 2000` | 先摘要链，再问答链 |
| **是否含代码** | 输入里有 ` ``` ` | 代码审查链 |
| **用户身份 / 套餐** | `user.plan == "vip"` | 强模型链；免费用户走便宜模型链 |
| **显式菜单** | 用户点了「翻译 / 总结 / 润色」 | 对应的那条链（**最可靠，因为用户自己说了**） |
| **附件类型** | 有图片 | 视觉模型链（影石这种多模态场景常用） |
| **语言** | 含中文字符比例 > 0.3 | 中文链 / 英文链 |
| **时间段** | 不在工作时间 | 转人工话术链 |

### 5.3 代码例子

```python
from langchain_core.runnables import RunnableBranch

def has_code(x: dict) -> bool:
    return "```" in x["input"]

def is_long(x: dict) -> bool:
    return len(x["input"]) > 2000

def is_vip(x: dict) -> bool:
    return x.get("role") == "vip"

router = RunnableBranch(
    (has_code, code_review_chain),        # 含代码块      → 代码审查
    (is_long,  summarize_then_answer),    # 超长           → 先摘要
    (is_vip,   strong_model_chain),       # 会员           → 强模型
    default_chain,                        # 兜底：最后一个位置参数，不是元组
)
```

**要点**

- 条件函数只读输入的**某个属性**，完全不「理解」语义 —— 这正是它的优点：可测、可 log、可解释。
- `RunnableBranch` 的最后一个参数是**兜底链**（不是 `(条件, 链)` 元组），它本身就是一个 Runnable。
- 每个分支都是 Runnable，所以可以和 LCEL 任意拼接：`prompt | router | parser` 也成立。

---

## 6. 链 vs Agent 选工具：本质是同一件事

**是的，完全同一套机制。** 区别只有两个：**循环** 和 **谁决定停止**。

| | 静态路由（多链） | Agent 选工具 |
|---|---|---|
| 决定的时机 | 一次性、前置 | 每轮都决定 |
| 决定次数 | **1 次** | **N 次**，直到模型不再要工具 |
| 是否依赖上一步结果 | 否 | **是 ← 这是最关键的差别** |
| 模型输出的形式 | `{"destination": "python"}` | `tool_calls: [{name, args}]` |
| 选项的描述写在哪 | `description` 字段 | **`@tool` 的 docstring** |
| 谁执行 | 你的代码查表 | 你的代码查注册表 |
| 停止条件 | 执行完就结束 | 模型不再返回 `tool_calls` |

### 一句话记住

> **tool 就是「带执行体的链」，而 `@tool` 的 docstring 就是路由用的 `description`。**

模型在两种场景下做的事完全一样：**读一堆「选项 + 各自描述」，输出一个选择**。
它从来不执行任何东西 —— 执行、回填、循环控制全是你的代码干的。

### 关于 Codex / Claude Code

**是的，就是同一个机制。** 它的系统提示里有一张工具清单（读文件 / 写文件 / 执行命令 / 搜索），
每轮由模型自己决定：调哪个、调几个（可以并行）、什么时候停。所谓 subagent、skills 也是这层思路的展开。

**你 D9 要手写的那个 `while` 循环，就是它的最小实现。**

### 面试可讲的一句话

> 路由用「一次额外调用」换确定性；Agent 用「多次调用」换灵活性和多步能力。
> 两者底层是同一个机制 —— **模型输出意图，代码负责执行**。区别只在循环。

---

## 7. 那还有必要学「链」吗？

**要，但学的对象变了。**

| 要学 | 不要学 |
|---|---|
| 组合思维：数据怎么在节点间流动 | `RouterChain` / `MultiPromptChain` / `SequentialChain` 那堆**具体链类名** |
| Runnable 统一接口：`invoke / stream / batch / ainvoke` | `LLMChain` / `AgentExecutor` / `ConversationBufferMemory` |
| 条件 / 并行 / 回退：`RunnableBranch`、`RunnableParallel`、`with_fallbacks` | 读源码、自造 Runnable 子类 |
| **因为 Agent 内部就是一条链，RAG 管线也是链** | 背链类型清单（`docs/context.md §2.1` 已列为「明确不要碰」） |

> **学「链」这个抽象和它的原语，不学「链」的类名清单。**
>
> 你今天学的 LCEL（`prompt | model | parser`）就是这一切的地基 —— 上面所有路由、
> 所有 Agent、所有 RAG 管线，拆开看都是一串 Runnable 拼起来的。

---

## 8. 怎么选：决策清单

1. **能写成规则吗？** → 能就用**代码路由**（最省最稳，零 token）
2. **不能，但有典型问句样本** → **语义路由**（只调 embedding，比调模型快一个量级）
3. **不能，且类别只有几句话能描述** → **大模型路由**（`with_structured_output` + 枚举）
4. **用户会问什么完全不可预期、而且要来回多轮** → **别路由**，交给 Agent 自己选

第 4 条是官方现在的主推方向：**把「路由」从「框架功能」变成「模型能力」** ——
不再需要 `RouterChain` 这类专用组件，`create_agent` + 一组 tools 就够了。

---

## 9. 官方文档位置（1.x 已把路由挪出 chains 目录）

| 内容 | 地址 |
|---|---|
| Router（本笔记主对应页） | `docs.langchain.com/oss/python/langchain/multi-agent/router` |
| 多智能体总览 | `docs.langchain.com/oss/python/langchain/multi-agent/` |
| handoffs / subagents / skills | 同目录下三页 |
| 结构化输出 | `docs.langchain.com/oss/python/langchain/structured-output` |

官方原话（值得背）：

- 路由这一步「often a single LLM call **or rule-based logic**」→ **官方明确说了可以是规则，不一定要模型**
- 「Use a router when you have clear input categories and want **deterministic or lightweight** classification」

实现上用 LangGraph 的 `Command`（走单条）或 `Send`（并行扇出多条），不再有专门的链类。

---

## 10. 四个常见误解（自测题库）

### 10.1 路由选错 ≠ 幻觉（两个阶段、两种错）

**路由是分类任务，生成才是创造任务 —— 幻觉只可能发生在第二个阶段。**

| 阶段 | 任务性质 | 出错的表现 | 四种方式的错分别是什么性质 |
|---|---|---|---|
| ① 选链 | **分类** | 答非所问、用错专家 | 代码路由：你的 `if` 写错了（**确定、可复现、可测**，不是模型的锅）<br>语义路由：向量太近 / 阈值不当（召回问题）<br>大模型路由：模型判断失误（**在有效选项里选错**，仍不是幻觉）<br>Agent：某轮选错工具，下一轮还能自己纠正 |
| ② 执行链 | **生成** | **幻觉** —— 编造不存在的事实 | 与路由方式无关，取决于链内 prompt、模型、上下文是否给足 |

> 唯一带点「幻觉味」的路由事故：旧版让模型**用纯文本写 JSON**，它可能编出一个**根本不存在的链名**。
> 枚举 schema 治的就是这个 —— 越界选项过不了校验。
>
> 另有一条间接链路：路由错了 → 送进的链**缺该有的上下文** → 它为了回答而硬编 → 这才是幻觉。
> 所以幻觉的根因是「上下文不足」，不是「路由错了」本身。

### 10.2 「拿链的描述算相似度取最高」—— 把两种机制粘在一起了

| 路由方式 | 有「描述」这一说吗 | 到底拿什么比 |
|---|---|---|
| 代码路由 | **没有** | 不比。走 `RunnableBranch` 里的布尔表达式 |
| 语义路由 | 有，但准备的是**每条链的典型示例问句**（3–5 句） | **向量比**：用户问句 vs 示例句 |
| 大模型路由 | 有 `description` 字段 | 模型**读懂**它做判断（不是算相似度） |
| Agent | 有 `@tool` 的 docstring | 同上，且每轮重算 |

> 要点：**`description` 字段是给「模型读」的（大模型路由）；向量比的是你自己写的「示例问句」（语义路由）。**
> 不存在「拿链的描述算余弦相似度」这种机制。

### 10.3 「用户描述越精准 → 链越准 → 答案越准」—— 因果链断两次

**第一处断点：决定路由精度的是「你路由边界的区分度」，不是用户的描述质量。**

- 用户控制不了你的 `description` / 示例句。两条链边界模糊（如「写作」和「润色」各写三句含糊的话），
  用户说得再精准也会被分错。
- 代码路由**根本不看描述**，只看布尔式 —— 用户描述再精准也影响不了它。
- 反直觉：**用户描述「最精准」的形态，恰恰是不需要路由的** —— 他直接点了菜单「翻译」。
  越精准 ≈ 越接近显式菜单 → 走的是代码路由（零成本那一种）。

**第二处断点：路由对 ≠ 答案对。**

> 路由只负责「把问题送进对的门」。门后面的 prompt 质量、模型能力、上下文够不够，才决定答案质量。
> **路由正确是必要条件，不是充分条件。**

### 10.4 「选链不花 token」—— 必须把「选链」和「执行链」分开算

| 阶段 | 代码路由 | 语义路由 | 大模型路由 | Agent |
|---|---|---|---|---|
| **① 选链** | **0** | 调 **embedding** 接口（便宜，**但不是零**；只是不调对话模型） | **1 次**对话调用 | **N 次** |
| **② 执行链（生成答案）** | **1 次** | **1 次** | **1 次** | **1 次** |

> **执行链必然花 token** —— 链要产出答案，末尾一定要调模型，这一步谁跑都省不掉。
> 路由能省下的**只是「选择」那一部分成本**。
> 代码路由之所以被推荐，就是因为它把「选择」压到了 0：**零 token、零延迟、结果永远一致**。

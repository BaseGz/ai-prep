# 报错档案

> **这是整个仓库最值钱的文件。** 面试问「踩过什么坑」，你不会记得三个月前的细节，但这个文件记得。
> 按「现象 / 我以为 / 实际 / 怎么定位到的」记，四段缺一不可 —— 缺了「我以为」，就只是照着报错改代码，没什么可讲的。

## 模板

```markdown
## D__ · 一句话描述问题

**现象**：
（原始报错信息，别概括，原样贴）

**我以为**：
（你当时的错误判断 —— 这段最能体现你是想过的）

**实际**：
（真实原因）

**怎么定位到的**：
（打印了什么、查了什么文档、二分了什么）

**结论**：
（一句可复用的经验，面试时直接念这句）
```

---

## D1 · LANGSMITH_TRACING=true 但 API key 为空，控制台被 401 刷屏

**现象**：

```
LangSmithMissingAPIKeyWarning: API key must be provided when using hosted LangSmith API
Failed to multipart ingest runs: langsmith.utils.LangSmithAuthError: Authentication failed for
https://api.smith.langchain.com/runs/multipart. HTTPError('401 Client Error: Unauthorized for url:
https://api.smith.langchain.com/runs/multipart', '{"error":"Unauthorized"}\n')
```

出现位置：`hello_model.py` 输出的开头与结尾各一次。**模型回复本身是成功的。**

**我以为**：

401 通常是 key 的问题 —— 第一反应是 DeepSeek 的 key 失效、或者 base_url 配错。
但同一个程序里回复已经正常拿到了，模型那一侧显然是通的，这个判断不成立。

**实际**：

两套凭据、两个服务，毫不相干：

- `api.deepseek.com` —— 模型调用，成功；
- `api.smith.langchain.com` —— **LangSmith 追踪服务**（LangChain 官方可观测平台，另一家公司）。

根因在 `.env`：`LANGSMITH_TRACING=true` 打开了追踪开关，但 `LANGSMITH_API_KEY` 是空的 ——
开关开着却没有钥匙，langsmith 客户端就不断尝试上传 trace 并被服务端拒绝。
`.env.example` 模板里默认写的是 `true`，这个坑是模板本身带来的。

**怎么定位到的**：

读报错里的**域名** —— 不是 `deepseek`，而是 `smith.langchain.com`，说明是另一个服务在报错，与模型无关。
再回 `.env` 比对两个 `LANGSMITH_` 开头的键，发现一个 `true`、一个是空的。

**结论**：

**看到 401 先看域名属于谁。** 追踪服务的凭据和模型供应商的凭据是两套，互不相关；
不用的功能要显式关掉（`LANGSMITH_TRACING=false`），别留个空 key 让它自己在后台报错。

---

## D4 · 手工构造 tool_calls 消息 + deepseek-flash → 400 `reasoning_content` must be passed back

**现象**：

```
OpenAIInvalidRequestError: Error code: 400 - {'error': {'message':
 'The `reasoning_content` in the thinking mode must be passed back to the API.',
 'type': 'invalid_request_error', ...}}
```

抛出位置：`langchain_deepseek/chat_models.py:396 (ChatDeepSeek._generate)`，
经 `langchain_openai/chat_models/base.py:1907`。触发场景是在 notebook 里**手工拼一条带 `tool_calls`
的 assistant 消息**（`get_weather` 例子），再连同 `tool` 消息一起发出去。

**我以为**：

这是 `langchain-deepseek` 的序列化缺陷 —— 它虽然能接收并存储 `reasoning_content`，
但构造下一个请求时把它丢了，导致 400；社区 issue 已多次提交，**升级库就能修好**。

**实际**：

不是库的 bug，是**模型选择**的问题。对照实验（同一份消息，只改模型名）：

| 写法 | 模型 | 结果 |
|---|---|---|
| 字典 `{"role":"assistant","tool_calls":[...]}` | `deepseek-flash` | ❌ 400 |
| 消息对象 `AIMessage(tool_calls=[...])` | `deepseek-flash` | ❌ 400（**和字典格式一样失败**） |
| 字典格式 | `deepseek-chat` | ✅ 正常返回 |

`deepseek-flash` 在服务端跑的是**思考模式**，这类模型要求把上一轮的 `reasoning_content`
原样回传才能继续；而我们**自己伪造**的那条 assistant 消息里根本没有这个字段 ——
服务端无从校验，只能拒绝。这与格式无关（两种写法都挂），也与库版本无关
（用的就是当时最新的 `langchain-deepseek 1.1.0`，所以「升级库」修不了）。

**怎么定位到的**：

把变量控制到只剩一个：同一份消息、同一份 `.env`、同一个库，**只换模型名**跑三次对照，
一次就看出「换模型就好了」→ 排除了「我的代码 / 库有问题」这两个方向。

**结论**：

**报错里写着 `thinking mode`，就先别怀疑库 —— 先看这次请求用的是哪个模型。**
手工伪造历史消息时，模型能力越强、要求的字段越多（思考模型要 `reasoning_content`，
普通模型不要）。排查任何「同样的代码换个模型就报错」的问题，第一步永远是：
**把模型名换成对照组再跑一遍。**

> 未验证的延伸：真实的工具调用流程（模型自己产生 `tool_calls`，而不是我手写）是否会撞同一个坑，
> 到 D8 / D9 用 `bind_tools` 实际跑一次再补记。若同样 400，主力模型固定用 `deepseek-chat`。

---

## D4 · 多轮对话「记住了我的名字」—— 模型没有记忆，是每轮把历史重发了一遍

> 这类坑没有报错信息，现象是「输出太正常了」。照样按四段式记，「我以为」那段才是值钱的地方。

**现象**：

（不是报错，是一条看起来「不太对劲」的正常输出）

第 2 轮我只问「我叫什么」，它准确答出「你叫 Base」。
整个脚本里我没写任何记忆类组件，也没手动把第 1 轮的问答拼进去 —— 看起来像模型自己记住了。

**我以为**：

我以为大模型会把历史对话存进内存（或某个文件）里，所以第二次调用时它依然明白我上一轮说过什么。
换句话说，我以为「记忆」是模型自带的固有能力。

**实际**：

**模型是无状态的 —— 它自己什么都不记。**

所谓「记住了」，是我的代码把整份历史（system + 前面每一轮）重新拼成一个 `messages` 数组，
每轮请求都完整重发一遍；模型每次都只是「第一次读到」这段对话而已。
不是它记得，是我每次都重新告诉它。

**怎么定位到的**：

开一个只带 system、不带任何历史的空 `messages`，把同一个问题（「我叫什么」）再问一遍 ——

> 它答「我不知道你的名字。」

一句话就证完了：模型从来没记得过，起作用的是历史消息的搬运。

**结论**：

**「记忆」不是模型的能力，是我自己维护的一个数组。**
每轮都要把历史完整重发，token 随对话轮数增长 —— 这正是 P27「对话历史的管理和优化」要解决的问题。

---

## D5 · 链顺序写反不报错，却静默产出一坨垃圾

**现象**：

`parser | model | prompt`（顺序写反），喂一个字符串进去，**不报错**：

```
steps = ['StrOutputParser', 'RunnableLambda', 'ChatPromptTemplate']
跑通了！返回 ChatPromptValue（没抛异常）
{q} 里被塞进去的 = "content='假回复' additional_kwargs={} response_metadata={}
                    tool_calls=[] invalid_tool_calls=[]"
```

对比：同一个问题换成 `model | prompt | parser`、同样喂 `dict`，**立刻报错**：

```
ValueError: Invalid input type <class 'dict'>.
            Must be a PromptValue, str, or list of BaseMessages.
```

**我以为**：

顺序写反就一定会报错 —— 于是把「**不报错**」当成了「**写对了**」的同义词，
看到跑通就以为没问题。

**实际**：

**报不报错和「顺序对不对」无关，只和「那一棒挑不挑食」有关。** 三个组件的入口宽容度完全不同：

| 组件 | 脾气 | 收到吃不下的东西时 |
|---|---|---|
| `model` | **严格** | 当场 `ValueError`（只认 3 种输入） |
| `prompt` | **仅单变量时不挑食** | 1 个变量：塞进去、不报错；≥2 个变量：`TypeError` |
| `parser` | 半严格 | 认 `str` 和有 `content` 的对象，其余报错 |

`parser | model | prompt` 恰好三棒都不拦：`parser` 收 str 原样返回 → `model` 收 str
（在它清单里，正常返回）→ `prompt` 收到一个 **`AIMessage` 对象**，不拒绝，
直接 `str()` 化塞进 `{q}` —— 三步全跑完，结果是垃圾。

> 「`prompt` 不挑食」这句**当天就被修正过**：前提是模板只有 1 个变量（当时用的正是单变量模板）。
> 完整边界见本文件下一条 `D5 · 「传裸字符串必报错」`。

**「跑通了」和「跑对了」是两件事。**

**怎么定位到的**：

顺着「谁站在第一棒」往下追问，然后用**假模型 + 真模型的本地入口校验函数**
（`ChatDeepSeek._convert_input()` —— 纯本地类型检查，不发网络请求、零成本）
把两个方向各跑一遍对照：

- `model | prompt | parser` → 报 `ValueError`（model 站第一棒，它严格）
- `parser | model | prompt` → 静默通过（prompt 站最后一棒，它不挑食）

**两个方向结果不同** → 变量不是「顺序」本身，而是「那一棒的宽容度」。

**结论**：

**「不报错」不等于「对」。** 排查链式调用的怪结果，第一件事不是看输出，是看结构：

```python
print([s.__class__.__name__ for s in chain.steps])
```

然后对一遍类型链：`dict → prompt → PromptValue → model → AIMessage → parser → str` ——
**每一节的输出必须是下一节能吃的输入**，顺序只是这条链的结果。

---

## D5 · 「prompt 链传裸字符串必报错」—— 我自己的断言被实验推翻

> 这条的价值不在结论，在**过程**：一条被写进执行单「坑预警」的断言，
> 最后被一行**库源码**推翻。面试讲「怎么校准认知」，讲这个。

**现象**：

做执行单安排的实验 `chain.invoke("你好")`（字符串，不是字典）——
链头是含 `{question}` 的 `ChatPromptTemplate`，**预期它会报错**。

结果：

```
chain.invoke("你好")   →   没报错，正常运行，输出正常回答
```

**我以为**：

「链头是 `ChatPromptTemplate` 就必须传变量字典」—— 多篇博客都这么说，
我自己也这么推理过，并把它**写进了执行单的「坑预警」**：

> `chain.invoke("你好")` 报错 → 链的第一个环节是 prompt，它要变量字典。

**实际**：

这条规则**不完整**。翻 `.venv` 源码，`langchain_core/prompts/base.py` 第 161-195 行
的 `_validate_input()` 里写着「单变量模板特例」：

```python
if not isinstance(inner_input, dict):
    if len(self.input_variables) == 1:        # ← 只有 1 个变量才宽容
        var_name = self.input_variables[0]
        inner_input_ = {var_name: inner_input}
    else:
        raise TypeError(...)                  # ← ≥2 个变量直接拒
```

官方注释也承认这件事 —— `langchain_core/prompts/chat.py` 第 871 行，
标题就是 `!!! note "Single-variable template"`。

四种输入实测：

| 模板 | 传入 | 结果 |
|---|---|---|
| `{question}`（1 变量） | `"你好"` | ✅ 不报错，与 `{"question": "你好"}` 产出**逐字相同** |
| `{question}`（1 变量） | `12345` | ✅ 照样塞进去（不限 `str`） |
| `{question}{style}`（2 变量） | `"你好"` | ❌ `TypeError` |
| 任何模板 | `{"wrong": "..."}` | ❌ `KeyError`（**另一种错**，别混） |

**⚠️ 别把这条和 `model.invoke("你好")` 混为一谈** —— 那个也是合法的，但走的是**另一条完全独立的机制**：

| 链头 | 机制 | 代码位置 | 性质 |
|---|---|---|---|
| `ChatPromptTemplate` | `_validate_input()` 的单变量特例 | `prompts/base.py:163` | **特例**：变量数一变就报错 |
| `ChatModel` | `_convert_input()` 类型归一化 | `chat_models/base.py` | **契约**：`str` / 消息列表 / `PromptValue` 是定义内的合法输入，与变量数无关，永远成立 |

→ 一句话：**`model` 收 str 是「说明书里写着就收」，`prompt` 收 str 是「本来不该收、单变量时网开一面」。**
遇到「这个写法到底合不合法」，先问一句：**我是在跟契约打交道，还是在跟宽容打交道？**

**怎么定位到的**：

**不信博客、不信自己的推理 → 直读库源码 + 跑最小实验。** 三步：

1. 先承认「实验结果和预期矛盾」，不找借口；
2. `grep` 整个 `langchain_core/prompts/` 目录搜 `input_variables` 相关判断 → 命中 `base.py:163`；
3. 设计四组对照（单变量 str / 单变量数字 / 双变量 str / 缺变量 dict），零 token 本地跑完。

**结论**：

**「必须传 dict」是简化说法；真实规则是「模板只有一个变量时，非 dict 会被自动塞进那个变量」。**

工程上两条：

1. **永远显式传 dict** —— 便利就是陷阱：今天少写一层 dict 很爽，明天模板加第二个变量，
   老代码突然炸，而且报错处看不出跟「加了个变量」有关系。
2. **网上的「标准答案」可能只是「常见情形」** —— 这次靠源码推翻，下次可能得靠实验。

---

## D6 · `pip install basemodel` —— 装的是同名但毫不相干的野包

**现象**：

想用 `pydantic.BaseModel`，结果去装了 `basemodel`。7 个候选版本**全部被丢弃**：

```
Discarding .../BaseModel-20190604.1625.tar.gz: Requested basemodel from ... has
inconsistent version: expected '20190604.1625', but metadata has '20260924.1504'
...（另外 6 个版本同样 discard）
ERROR: Could not find a version that satisfies the requirement basemodel
       (from versions: 20190515.1326, ..., 20190604.1625)
ERROR: No matching distribution found for basemodel
```

**我以为**：

把这个报错当成「环境/网络问题」—— 以为换个源、或者升级 pip 就能装上。

**实际**：

两件事，一件比一件值得记。

**一、装错包了。** PyPI 上确实有个包叫 `basemodel`（全小写），但它是别人 2019 年发的废弃包：
作者 `billsteve`，摘要原文 `"SqlAlchemy's spuer class"`（「super」还拼错了），
最后一次发版 **2019-06-04**，7 年没动，总共 7 个版本、零依赖。
它跟 pydantic 的 `BaseModel` **毫无关系**。
而 `from pydantic import BaseModel` 在 venv 里本来就正常（pydantic 2.13.5 已装）——
**什么都不用装。**

**二、它为什么装不上。** 这个包的版本号是**构建时按当前时间现场生成**的：

```
expected '20190604.1625'      ← 文件名 / URL 上写的版本（2019）
metadata has '20260924.1504'  ← 解包后真实读出来的 = 2026-09-24 15:04
                                 ↑ 就是我敲这条命令的那一分钟
```

文件名和元数据**永远对不上** → pip 判定这个包是坏的 → 7 个候选全部 discard
→ 最后那句 `No matching distribution found`。

**怎么定位到的**：

1. 先确认自己没受影响：`from pydantic import BaseModel` → 正常，
   **说明这个报错跟我的代码无关**；
2. 确认没留垃圾：`import basemodel` → `ModuleNotFoundError`（失败是干净的，不用清理）；
3. 拉 PyPI 真实档案（`https://pypi.org/pypi/basemodel/json`）→ 看到 2019 年的作者、摘要和 7 个版本；
4. 回头盯住报错里那两串时间戳 —— `20260924.1504` 正好是**当下**，
   才想通「它按构建时间生成版本号，所以永远和文件名对不上」。

**结论**：

**「安装包 X」这类提示，是按你写错的符号名去 PyPI 找包的 —— 找到的同名包可能跟你要的库毫无关系。**
看到它先问一句：**我要的东西，真是这个包名吗？** 我要的是 `pydantic` 里的一个类，不是叫 `basemodel` 的包。

这是 IDE 第二次骗我：D5 是它自动塞 `from email import parser`，
这次是（PyCharm 弹的快速修复 / 自己手敲）让我装野包。
**补全和快速修复都要过一遍自己的脑子。**

---

## D6 · 用 `deepseek-flash` 做结构化输出 → 400 `Thinking mode does not support this tool_choice`

**现象**：

```python
model = init_chat_model("deepseek:deepseek-flash", ...)
structured = model.with_structured_output(Person)
structured.invoke("张三是一名30岁的软件工程师")
```

```
✗ OpenAIInvalidRequestError
  400 - {'error': {'message': 'Thinking mode does not support this tool_choice', ...}}
```

**我以为**：

`with_structured_output` 是个「解析输出」的功能，跟模型选哪个没关系。

**实际**：

**结构化输出底层就是「工具调用」** —— LangChain 把 `Person` 的 JSON Schema 塞进请求的
`tools` 字段（并指定 `tool_choice` 强制模型用它），模型照表填。
而 `deepseek-flash` 是 **thinking 模式**，**不支持 `tool_choice`**，所以直接 400。

换成 `deepseek-chat` 就好了。

**怎么定位到的**：

1. 报错里明写 `Thinking mode` → 先怀疑模型而不是库（**这条规矩 D4 就立过**）；
2. 同一份类、同一个 `.env`，只换模型名跑对照 → `deepseek-chat` 成功。

**结论**：

~~**`deepseek-flash` 不能用于任何依赖工具调用的功能**~~ —— 结构化输出、`bind_tools`、
Agent 全都撞同一面墙。做这些事一律用 `deepseek-chat`。

> ⚠️ **这条结论在 D8 被收窄了，见下方「D8 · 「flash 不能用于工具调用」—— 我自己的断言被实验推翻」。**
> flash 跑 `tool_choice` 的 `none` / `auto` / `required` 都正常；真正卡住的应该是
> **「指定具体函数名」** 那一种，而 `with_structured_output` 恰好用的就是那一种。
> 保守做法（此处仍用 `deepseek-chat`）不变，但原因要写准。

它和 D4 那条 `reasoning_content must be passed back` **同源**：
都是「flash 是 thinking 模型」这一个事实的不同侧面。
→ **报错里出现 `thinking mode`，第一反应是「我用的哪个模型」，不是「库是不是有 bug」。**

---

## D6 · `result.name` 不报错，返回 `None` —— 属性名撞车

**现象**：

```python
result = model.invoke("张三是一名30岁的软件工程师")

print(result)          # AIMessage：一整段文字
print(result.name)     # None        ← 不报错！
print(result.age)      # AttributeError
```

**我以为**：

`model.invoke()` 会按 `Person` 的结构返回一个 `Person` 对象，`result.name` 就该是「张三」。

**实际**：

`model.invoke()` 收到字符串，就当成**一句普通提问**，返回一整段 `AIMessage`
（模型用自己的话复述一遍：「好的，这是一个很常见的人物设定。请问你希望我围绕张三做些什么呢？」）。

要模型**吐出符合 `Person` 模板的数据**，得先套一层：

```python
structured = model.with_structured_output(Person)
result = structured.invoke("张三是一名30岁的软件工程师")

print(result)        # name='张三' age=30 occupation='软件工程师'
print(result.name)   # 张三
```

**最阴的一处**：`result.name` **不报错，返回 `None`** ——
因为 `AIMessage` 恰好**也有一个叫 `name` 的字段**（本意是「消息发送者」，默认 `None`）。
于是先安静地给你一个 `None`，要到 `result.age` 才炸。
**先给一个假答案，再给一句真报错。**

**怎么定位到的**：

写最小脚本逐项打印：`type(result)` → `AIMessage`（不是 `Person`）；
`hasattr(result, 'name')` → `True` —— 才明白不是「取不到」，是**取到了另一个东西的同名字段**。

**结论**：

**`model.invoke()` 是「问问题」，`with_structured_output(Person)` 才是「要数据」。**
两者返回类型完全不同：前者 `AIMessage`，后者你自己定义的 pydantic 类。

两条规矩：
1. 判断「拿到的是不是我要的类型」别靠 `print` 看着像，靠 **`type()`**；
2. **两个不同的类有同名字段时，取错不会报错，只会给你一个 `None`**
   —— 又一次静默失败，和 D5 那两条同一个家族。

---

## D6 · 不继承 `BaseModel` 不报错 —— 静默给你一份空 Schema

**现象**：

写一个**什么都不继承**的普通类交给 `with_structured_output()`：

```python
class NotPydantic:          # 没有继承任何东西
    name: str
    age: int

bad = model.with_structured_output(NotPydantic)
print(bad.invoke("张三是一名30岁的软件工程师"))   # {}
```

**全程不报错**：建链成功、`invoke()` 成功、返回**空字典 `{}`**。
它生成的 Schema 是个**空壳**：

```json
"parameters": {"properties": {}, "type": "object"}
```

**我以为**：

「必须继承 `BaseModel`，不然 LangChain 会拒绝（报错）」——
所以**只要不报错，就说明类写得没问题**。

**实际**：

**LangChain 根本没检查你继没继承 `BaseModel`。** 它只做一件事：
去你那个类上找 `model_json_schema()`。找到就用，找不到就给一份空表 ——
模型照着空表填，于是填出个 `{}` 回来。

继承的真实作用**不是「通过审查」，是「获得造表的工具」**：

```
class Person(BaseModel)  →  白得 model_json_schema()  →  产出 JSON Schema
                                                            ↑
                                          LangChain 真正要的东西就是这个
```

完整因果是 **继承（手段）→ `model_json_schema()`（能力）→ Schema（目的）**。
说「`Person` 是 pydantic 类，因为它继承了 `BaseModel`」在**定义**上是对的
（Python 里「pydantic 类」和「继承 `BaseModel` 的类」基本是同义），
但漏了中间那一环 —— **而漏掉的那一环，正好就是「不继承会怎样」的答案**。

**怎么定位到的**：

原本想验证「不继承应该报错」，结果实验当场推翻预期（`invoke()` 正常返回 `{}`）。
按 D5 立的规矩**不找借口、直查**：

1. 打印建链结果 → `RunnableSequence`（建链这一步确实**不校验**）；
2. 打印它生成的 Schema → `{"properties": {}, "type": "object"}` —— **字段全没了**；
3. 对比 `Person`：`isinstance(result, Person)` → `False`，`model_fields` 空；
4. 想通：LangChain 只从普通类里读到了 `__doc__`（当 description），**字段信息全部丢失**。

**结论**：

**`BaseModel` 在这里的身份是「合同的打印机」** —— 合同是 Schema，
`BaseModel` 是能打出合同的机器。**LangChain 要的是合同，不是机器。**

工程上两条：

1. **结构化输出抽出 `{}` 或字段全空时，第一件事不是看模型，是打印 Schema**：
   ```python
   print(Person.model_json_schema())
   ```
   Schema 是空的 → 你的类没被识别，**跟模型无关**，别去调 prompt。
2. **继承不生效的唯一信号就是「空 Schema」** —— 它不会红着脸拒绝你，
   只会安静地给你一个 `{}`。又一次静默失败。

---

> **D6 一天之内撞到 2 次静默失败**（`result.name` → `None`、空 Schema → `{}`），
> 另有 2 次是响亮的报错（装错包 / flash 400）。
> 把 D5 那句话扩一句：**「跑通了」≠「跑对了」，「没报错」更不等于「对」。**

---

## D6 · 字段缺失不报错 —— 模型会「编造一个像真的值」，比填 0 危险得多

**现象**：

```python
class Person(BaseModel):
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")

s = model.with_structured_output(Person)
print(s.invoke("张三是一名软件工程师"))     # 输入句里根本没提年龄
```

```
→ name='张三' age=30 occupation='软件工程师'
```

`age=30` —— **输入里从来没有「30」这个信息**。不报错。

第二条更狠：

| 输入 | 抽出结果 |
|---|---|
| `"张三是一名软件工程师"` | `name='张三' age=30 occupation='软件工程师'` |
| `"请介绍一下这家公司"`（**连人都没有**） | `name='张三' age=30 occupation='工程师'` |

第二行输入里没有姓名、没有年龄、没有职业，它**照样交回一个填满的 `Person`**。

**我以为**：

缺失的字段要么留空、要么给个默认值（`0` / `None`），要么 pydantic 报「缺字段」。

**实际**：

**模型会把缺失的槽位「补全」成一个看起来合理的值。** 不是 `0`，是 `30` ——
一个**随手编的、但完全合法的整数**。

**这不是 pydantic 的锅，是模型的默认行为。** pydantic 只在「值**不合法**」时抛错，
而 `30` 是个合法整数，所以校验一路绿灯。

两个对照把边界划清了（都实测过）：

| 情形 | 结果 |
|---|---|
| **值不合法**（绕过模型，手工喂 `age="三十岁"`） | ✅ `ValidationError: Input should be a valid integer, unable to parse string as an integer` —— **校验还在** |
| **值合法但是编的**（输入没提年龄，模型给 `30`） | ❌ 谁都拦不住 —— **校验没有机会触发** |
| 显式约束 `Field(ge=1, le=120)`，输入故意说「999 岁」 | 模型主动贴合成 `age=120` —— **它在生成时就被 Schema 约束住了** |

**怎么定位到的**：

1. 先怀疑「模型填了 0」，换两条不同输入对答案 → 拿到的是 `30`，不是 `0`，**且两次都编**
2. 想让 pydantic 报错 → 报不出来，因为 `30` 合法
3. 换思路：**绕过模型**，手工构造一个 `age="三十岁"` 的 `tool_call`，
   直接喂给链路最后一步（`chain.steps[-1]` = `PydanticToolsParser`）→ `ValidationError` 立刻抛出来
4. 结论：**校验在，模型也在「合规地编」**

**结论**：

**结构化输出不会告诉你「这个值是不是编的」。Schema 只保证【形状】，不保证【真实性】。**

工程上两条：

1. **必填字段要在 prompt 里明确「没有就说不知道 / 留空」** ——
   否则你拿到的是一个看起来很正常的假数据。**`0` 一眼可疑，`30` 不像** ——
   这正是它比「填 0」更危险的地方。
2. 排查「校验为什么没拦住」时，先分清是哪种：
   - **值不合法** → pydantic 会抛（校验完好，去查 schema 定义）
   - **值合法但内容是编的** → 谁都拦不住，**这是提示词的活，不是 pydantic 的活**

---

## D7 · `/extract` 输入为空 → 模型编出一个根本不存在的人

**现象**：

先跟 CLI 聊「我是一名20岁男学生龚政」，再敲**光秃秃的** `/extract`，返回：

```
name='张伟' age=28 gender='男' identity=<Identity_type.white_collar: '白领'>
```

**「张伟」这个人从头到尾没出现过，而且不报错。**
而 `/extract 我是一名20岁男学生龚政` 这种带内容的写法又是对的 ——
所以一开始以为是"偶尔失灵"。

**我以为**：

`/extract` 分支里写了 `messages.append(...)`，等于把信息存进记忆了，
抽取器下一轮自然读得到。抽不到，大概是模型或库的问题。

**实际**：

两处同时断：

1. 抽取器调用时递的是 `removeprefix("/extract").strip()` —— **只递当前这一行**，
   不是整份对话记录；
2. 而我敲的是光秃秃的 `/extract`，去掉前缀后是**空字符串** —— 等于递了一张**白纸**。
   可 `Person` 四个字段全是必填，模型只能**编一个**交差。

之前跟内容时能抽对，**不是因为"记住了"，是因为我当面又说了一遍**。

**怎么定位到的**：

写了个**纯本地、不调模型、零费用**的脚本，把「存进记事本的是什么」和
「递给抽取器的是什么」分别用 `repr()` 打出来 —— 一眼看到 `''`。
再做对照实验：把整份 `messages` 喂给抽取器，立刻抽对了（`龚政 / 20 / 男 / 学生`）。

**结论**：

**必填 Schema + 空输入 = 高质量编造。** 和 D6 那条「字段缺失 → 编造」同族，
但触发条件更极端：那次是少一个字段，这次是**一个字的输入都没有**。

→ **调用抽取器之前，先确认递进去的东西不是空的**；没内容就给它一句提示，
别让它对着空气填表。

---

## D7 · 「存进 `messages`」不等于「被读到」—— 记忆是「存 + 递」的合体

**现象**：

（不是报错，是「明明存了却查不到」）

在 `/extract` 分支里写了 `messages.append({...})`，注释还写着「把抽取结果加入记忆」，
可抽取器就是读不到之前聊过的内容。

**我以为**：

`messages.append()` 就是在"记住"，存进去了自然读得到。

**实际**：

`messages` 只是本地的一本**记事本**。**「存进去」和「被读到」是两件独立的事** ——
记事本会不会被读，取决于**调用时递了什么**：

| 分支 | 调用时递的 | 记事本被读了吗 |
|---|---|---|
| 普通聊天 | `model.invoke(messages)` ← **整本记事本** | ✅ 读了 |
| `/extract` | `structured.invoke(去掉前缀的那一行)` ← **一张纸条** | ❌ 完全没读 |

而且那行 append 本身也是错的：对光秃秃的 `/extract`，
`removeprefix(...).strip()` 是空字符串 —— **存进去的是一片空白**，连"存"都没存对。

**怎么定位到的**：

把所有 `append` 和所有 `invoke` 的参数都打成 `repr()` 对照着看 ——
两条通道的差异一眼就出来了。

**结论**：

**「记忆 = 存 + 递」，缺一个都等于没有。**

模型和抽取器都是**无状态**的（这正是 D4 那条），所谓记忆全靠每次调用时
**把上下文重新递过去**。

→ 排查「它怎么不记得了」，先问两句：**存了吗？递了吗？** —— 多数时候是后者。

---

## D8 · 重开 notebook 只跑 Cell 3 → `NameError: name 'get_weather' is not defined`

**现象**：

```
NameError: name 'get_weather' is not defined
```

报错发生在 `In[2]`，而定义 `get_weather` 的 Cell 2 屏幕上明明白白躺着一条
`In[4]` 的旧输出。

**我以为**：

Cell 2 跑过、输出还在屏幕上，定义自然还在 kernel 里 —— 直接跑 Cell 3 就行。

**实际**：

**notebook 里存的输出是历史记录**（跟着 `.ipynb` 文件走的），不代表当前 kernel 里
还有这个变量。重开 notebook 拿到的是一个**全新的空 kernel**，屏幕上那些 `In[4]`
只是上次的存档。

同一族的第二个表现（差点漏掉）：`tool_choice的使用.ipynb` 的 Cell 1 源码已经改成
`model="deepseek:deepseek-chat"`，但输出里 `model_name` 仍是 **`deepseek-flash`** ——
**改了源码没重跑，代码和输出是两套状态**。这种不一致不会报错，只会让后面所有结论
都建立在假的模型上。

**怎么定位到的**：

对比每个 cell 的 `execution_count`：定义 cell 是 `In[4]`，报错却在 `In[2]` ——
**编号倒退**，说明那个定义 cell 在当前 kernel 里从没执行过。再看执行时间戳，
输出是前一天的。

**结论**：

**报错先问一句：定义它的 cell，在当前这个 kernel 里跑过吗？**

kernel 重启后一律 **Restart & Run All**；单独跑 cell 省下的那点时间，
迟早用调试还回去。

→ 顺带一条：**屏幕上的输出不是证据，`execution_count` 才是。**

---

## D8 · `parse_docstring=True` 写进函数签名 → Schema 里多出一个假参数

**现象**：

```python
def get_weather(city, if_forecast, parse_docstring=True):
```

能跑，不报错，工具也照常被调用 —— 所以很久都没发现。

**我以为**：

`parse_docstring` 是「要不要解析 docstring」的开关，放哪都行，写进函数括号里
只是顺手。

**实际**：

**两个括号管两拨人**：

| 位置 | 给谁看 |
|---|---|
| `@tool(...)` 的括号 | **框架**的配置 |
| 函数的括号 | **模型**看的参数表 —— 每个参数都会变成 Schema 的一个字段 |

同一段 docstring，只改这一处，实测两次 `convert_to_openai_tool()`：

正确 `@tool(parse_docstring=True)`：

```json
{"properties": {"city": {"description": "城市名称", "type": "string"}},
 "required": ["city"]}
```
`description = '查询天气'`

错误（写进签名）：

```json
{"properties": {"city": {"type": "string"},
                "parse_docstring": {"default": true, "type": "boolean"}},
 "required": ["city"]}
```
`description = '查询天气\n\n    Args:\n        city: 城市名称'`

**三重伤害**：

1. 多一个假参数 `parse_docstring`，模型得凭空给它编个值；
2. **`city` 的 `description` 丢了** —— 没开解析，docstring 里的「城市名称」根本没进 Schema，
   模型不知道该填什么；
3. 工具的 `description` 变成整段 docstring 原文，`Args:` 这种格式垃圾一起塞进去了。

**怎么定位到的**：

写了两个只差这一处的工具，用 `convert_to_openai_tool()` 把两边的 JSON 打出来对比 ——
一眼看到 `parse_docstring` 变成了一个 `boolean` 参数，而 `city` 的 `description` 消失了。

**结论**：

**装饰器配置给框架看，函数签名给模型看，两者不能串。**

判断标准只有一句：**这个参数模型需要填吗？** 不需要，就不该出现在签名里。

→ 任何时候怀疑「模型怎么填得这么离谱」，先 `convert_to_openai_tool()` 看一眼
**它到底看见了什么** —— 你写的不等于它读的。

---

## D8 · 「flash 不能用于工具调用」—— 我自己的断言被实验推翻

**现象**：

D6 那条我写下的结论是：

> **`deepseek-flash` 不能用于任何依赖工具调用的功能** —— 结构化输出、`bind_tools`、
> Agent 全都撞同一面墙。

可 D8 跟着 P33–P39 用 `deepseek-flash` 跑 `bind_tools`，**正常返回 `tool_calls`，
一次 400 都没出现**。

**我以为**：

要么 D6 那条记错了，要么 DeepSeek 已经把 flash 修好了。

**实际**：

把 `tool_choice` 的四种取值逐个跑一遍，flash 的表现是：

| `tool_choice` | 结果 | 证据 |
|---|---|---|
| `"none"` | ✅ 不调工具，正常回答 | `content` 有正文 |
| `"auto"` | ✅ 返回 `tool_calls` | 带 `reasoning_content`，确认是 thinking 模式 |
| `"required"` | ✅ 返回 `tool_calls` | `model_name: 'deepseek-flash'`、`finish_reason: 'tool_calls'` |
| 指定具体函数名 | ✅ 返回 `tool_calls` | 调用了 `get_weather2`，`args: {city: 杭州}`；但**这次跑的是哪个模型无法确认**（见下） |

**四种取值全部通过** —— 我原来的推断（「卡在指定具体函数名」）**也不成立**。

⚠️ 而且这次实验本身有个致命瑕疵：`tool_choice的使用.ipynb` 的 Cell 1 源码写的是
`deepseek-chat`，可 Cell 6 的输出里 `model_name` 明明是 `deepseek-flash` ——
**源码和 kernel 里的实际对象是两套状态**。所以除了 Cell 6 那条能凭 `model_name` 确认，
其余几格到底跑的是 chat 还是 flash，**都不可靠**。

换句话说：这个对照实验**废了一半** —— 不是结论错了，是**实验条件没控住**。

**怎么定位到的**：

不是设计好的实验，是跟着 P39 抄代码时撞出来的 —— 教程里用 `tool_choice="required"`，
我用的是 flash，本以为必炸，结果没炸。于是回头把四种取值排成表逐个对照。

**结论**：

**断言写得太绝对，迟早被自己打脸 —— 而且这次连新推断也一起被打脸。**

「flash 不能用于工具调用」→「可能只卡指定具体函数名」→ **四种全过，推断也推翻**。
两次都下早了。

真正该记的不是「flash 到底行不行」，是这句：

> **做对照实验前，先确认你对照的是不是一个东西。**
> 模型名没打出来、kernel 里跑的还是旧对象 —— 这种实验做十次也证明不了任何事。

→ 这也是坑 1（屏幕输出 ≠ kernel 状态）的活例子：**连我自己设计的实验，
都被同一个问题废掉了一半。**

→ 要重做的话：Restart & Run All → 只钉一个模型 → 每一格都把
`response.response_metadata['model_name']` 打出来 → 再填这张表。

---

## D9 · `run(question)` 收了参数却没用 —— 换题测试时才发现「换题没反应」

**现象**：

`agent_loop.py` 的第 7 题（尾号 8899 名下两单物流都查）跑通了，输出完全正确。
但把 `if __name__ == "__main__":` 里那句 `print(run("..."))` 换成别的问句，
**输出一个字都不变**，永远在答同一题。

```python
def run(question: str) -> str:
    messages = [
        SystemMessage("你是一个物流智能查询助手"),
        HumanMessage("尾号 8899 名下两单的物流都查一下"),   # ← 写死
    ]
...
print(run("我尾号 8899 那个耳机到哪了？"))                # ← 这个实参被吞了
```

**我以为**：

参数传进去了，函数就会按参数问。前面几道题的测试是「通过」的，所以以为循环写得没问题。

**实际**：

`messages` 里放的是**字符串字面量**，`question` 这个形参从头到尾没有任何地方读它。
那几道题的「通过」不是 `run()` 通过了，是**我手改第 108 行换来的**——
`run(question)` 只是接了个参数，没有被使用。

**怎么定位到的**：

想换题测试才发现的：改第 144 行，输出不变；回去读函数体，才看见 `HumanMessage(question)` 里
写的是带引号的字符串。用 `print(question)` 在函数开头打一次，确认参数是到了的——**到了，但没被用**。

**结论**：

> **收了不用，比不收更危险。**
> 不收参数会立刻 `NameError`；收了不用是**静默失效**，测试照样能过，过的还是别的东西。

和 D7 的「存了没递」（`append` 了历史却不传给模型）是同一个病：
**每多一层参数 / 每多一个中间变量，就多一个「以为它生效了」的错觉。**
判据很简单：**这个参数，函数体里到底有没有被读一次？**

---

## D9 · 一次返回两个 `tool_calls`，只执行了一个（缩进少一层）

**现象**：

单工具题目全部正常，「尾号 8899 那个耳机到哪了」两轮拿到终答。
但换成「尾号 8899 名下两单的物流都查一下」——模型第 2 轮同时要调
`track_package(ORD-...-001)` 和 `track_package(ORD-...-002)`，
**只打印了一条** `[第 2 轮] track_package(...)`，另一单的物流始终没出现。

**我以为**：

`for tool_call in response.tool_calls:` 下面写的东西自然都在循环里。
而且前面几道题跑得好好的，循环应该是没问题的。

**实际**：

`if t is None:` 和 `result = t.invoke(tool_call)` 的缩进只对齐了 `for`，
**少一层，落在了循环外面**——每轮只处理最后一个调用，前面几个既不执行、
也不回填 `ToolMessage`。

```python
for tool_call in response.tool_calls:      # 8 空格
    name = tool_call["name"]               # 12 空格 ✓
    t = TOOL_MAP.get(name)                 # 12 空格 ✓
if t is None:                              # 8 空格  ✗ 跑到循环外了
...
result = t.invoke(tool_call)               # 8 空格  ✗ 只执行最后一个
```

**怎么定位到的**：

用输出里的 `[第 N 轮]` 计数对账：模型说调了两个工具，日志只有一条——
**数量对不上就是分发层的事**，不是模型的事。再看缩进，一眼就看出来了。

**结论**：

> **单工具测不出多调用的 bug。**
> 服务端一次可以给多个 `tool_calls`（并行意图），只要测试里没有「一次必须调两个工具」的题，
> 这个 bug 会一直藏着，直到 D8 那种双调用场景在真实使用中炸开。

顺带记住：查这类问题**先数数**（模型要几个 vs 我执行了几个），
比从头读代码快得多。

---

## D9 · 工具说得含糊，模型就用常识替你补

**现象**：

「尾号 1024 的订单发货了吗？」——`find_order` 明确说状态是「待发货」，
模型却还是调了 `track_package`；而 `track_package` 当时的兜底文案是
`未找到该订单的物流信息`（**同一句话同时表示「查无此单」和「有单未发货」**）。
模型最终答：「还没揽收入库，还没发货。」——**答对了。**

但同一句话，换成假订单号 `ORD-99999999-999` 来问，模型改口成：
「未找到该订单，**可能**是订单号有误，**也可能**是尚未发货」——列了两种可能。

**我以为**：

只要工具返回了文字，模型就会照实转述，不会自己加解释。
第一次预测「模型看到待发货就不会再调 `track_package`」，**实测它调了**。

**实际**：

两件事：

1. **模型会拿别的工具的结果做交叉验证**，比我的预测谨慎——所以「订单状态」和
   「物流记录」这两个信息源它会都看。
2. 更关键：**工具的话有歧义时，模型不会停下来问，它会用常识补齐。**
   1024 那题之所以「答对」，是因为上一轮 `find_order` 给了「这单存在且待发货」的上下文，
   模型据此把「未找到物流信息」解释成「还没发货」。
   假订单号那题没有这个上下文，它就只能列两种可能——**这不是周到，是它真的不知道。**

**怎么定位到的**：

同一句兜底文案跑两道题：一道有 `find_order` 兜底、一道没有。
答案口径不一致（一道给结论、一道列可能），才意识到问题不在文案，在**数据**——
`track_package` 手里只有物流表，**没有订单表**，它物理上无法区分这两种情况。

修法是「让 `track_package` 能看到订单表」（两张表提到模块级共享）+ 三级判断
（订单不存在 / 存在但无轨迹 / 正常轨迹），**不是改那句提示语**。
改完再跑同样的两题：都给出了明确结论。

**结论**：

> **工具说得含糊，模型就替你补 —— 补对是运气，补错是事故。**

推论三条：

1. **歧义要在工具里消灭，不能指望模型问。** 模型的默认行为是「往下编」，不是「回头确认」。
2. **「列几种可能」是危险信号**，不是严谨信号 —— 多数时候意味着它拿到的信息不足以下结论。
3. **兜底文案不能说人话，要说结构化的话**：`订单不存在` / `订单存在但尚未发货` 是两句不同的事实，
   不能合成一句「未找到物流信息」。

## D10 · 拿掉一个工具，模型不沉默 —— 它把「订单状态」改名叫「物流情况」

**现象**：

只给 `find_order`（删掉 `track_package`），问「尾号 8899 名下两单的物流都查一下」。消息 **4 条**，
第 4 条没有任何 `tool_calls`，直接给表：

```
| 订单号 | 产品 | 下单日期 | 物流状态 |
| ORD-20261015-001 | 无线蓝牙耳机 Pro | 2026-10-15 | ✅ 已签收 |
| ORD-20261018-002 | 65W 充电底座      | 2026-10-18 | 🚚 运输中 |
```

结尾：「如需查询具体物流轨迹（如快递公司、运单号、到达节点），可以告诉我订单号或产品名称，**我再帮您进一步核实**。」

**我以为**：

工具不够时它会说「我没有查物流的工具」—— 老实退让。

**实际**：

它用 `find_order` 的 `status` 字段顶了「物流状态」这一列，标题写成「物流情况如下」。
两个值都能在 `find_order` 返回里逐字找到，**所以不是幻觉，是概念偷换** —— 数据真、信息假。
更麻烦的是最后那句「我再帮您进一步核实」：`track_package` 已经不在工具列表里，
它对自己能力的描述是错的 —— **这种错误比编数据更难发现，因为数据层面无懈可击。**

**怎么定位到的**：

1. 比对 `MOCK_TRACKS` 的节点数（0415 是 4 条、1018 是 2 条），回答里一个轨迹节点都没有；
2. 看消息条数是 **4**（基线 7），第 4 条 `tool_calls` 为空 —— 全程只调了一次工具。

**结论**：

> **工具不够时，模型的默认反应不是拒绝，是换个名字接着答。**

判断有没有越界，**看它调了几次工具，不要看它答得像不像**。
另一条危险信号：模型主动承诺「我再帮您核实」时，先确认它手里真的还有那个工具。

## D10 · 以为 `create_agent` 会优雅停下 —— 它默认 9999 轮、超限直接抛异常

**现象**：

`agent.invoke(..., config={"recursion_limit": 3})` 跑两单题，程序崩：

```
langgraph.errors.GraphRecursionError: Recursion limit of 3 reached without hitting a stop condition.
```

**我以为**：

框架会像 D9 的 `MAX_ROUNDS = 8` 那样，返回一句「超过最大轮数，已强制停止」。

**实际**：

默认 `recursion_limit` 是 **9999**，超限**抛异常**，不返回任何内容 —— 不 `try/except` 整个程序就崩。
手写版是软着陆，框架版是硬失败。这不是风格差异，是**谁来承担失败**的差异。

**怎么定位到的**：

`inspect.signature(agent.invoke)` 看到第 2 个参数是 `config`；
打印 `agent.config` 看到默认 `recursion_limit: 9999`；把值改成 3 跑一次，拿到报错原文。

**结论**：

> **框架给的默认值，是它替你做的决定。** 9999 轮比手写 8 轮危险得多 —— 失控时烧的是真金白银。

另：`recursion_limit` 放在 config **第一层**，不是 `configurable` 下面；也不能塞进 input 字典。



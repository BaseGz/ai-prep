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


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


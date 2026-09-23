# NOTES · 管道符、执行顺序与类型链

> D5（LCEL 管道）补课笔记 ｜ 2026-09-23 ｜ 本机实测环境：langchain 1.4.2 / langchain_core 1.6.3
>
> **配套可执行版：`probe_types.py`** —— 本文每一条结论都能在那里跑出来，**零 token**（不调真模型、不花钱）。
> **前置材料：`learn_runnable.py`** —— 从普通函数讲到 Runnable；看不懂本文就先跑它。
>
> **一句话结论：`|` 不认角色、只认顺序；能不能接下去，看「上一棒吐出的类型」在不在「下一棒的能吃清单」里。**

---

## 0. 为什么会有这份笔记

今天卡住的不是「怎么用」，而是三个**没人教的前提**：

| 我想知道的 | 有现成资料吗 |
|---|---|
| `Runnable` 是什么 | **没有**。官方 Models 页只讲 `invoke / stream / batch`，**一个 Runnable 字都没解释** |
| 「重载」是什么 | **没有**。这是 Python 语言特性，所有 LangChain 教程都默认你会 |
| 管道符为什么能这么写 | **没有**。原写的官方 LCEL 页已 **404** |

两个配套事实（本机/线上均已核实）：

- 尚硅谷 `BV1rv7A6oEeP` 全 **120 P 中没有任何一讲**叫 LCEL / 管道 / Runnable；
- 看的那一讲《链结构》**没有讲**「前者输出接后者输入」这个语义。

→ 所以这份笔记**不引用任何教程**，全部结论来自本机代码实测。

---

## 1. `|` 是谁定义的？

**结论：`|` 不是语法糖，是 `Runnable` 上重载的 `__or__` 方法。**

证据：

- `Runnable.__or__` 真实存在（是一个方法对象）；
- 反证：一个没定义 `__or__` 的普通类，用 `|` 直接报
  `TypeError: unsupported operand type(s) for |: 'NoOr' and 'NoOr'`。

**顺带把「重载」补上**：重载 = 给一个运算符定义新行为。**你早就在用** ——
`3 + 5` 和 `"a" + "b"` 走的是各自类型上的 `__add__`；LangChain 只是给 `|` 定义了一份新行为。

> 常见错误说法：「`|` 是 Python 3.10 引入的语法糖」。**不对** ——
> `__or__` 运算符重载从 Python 2 就有（`int | int` 位或、`set | set` 并集）；
> Python 3.10 新增的是**类型标注**里的 `X | Y`（如 `str | None`），与运算符重载是两件事。

---

## 2. 执行顺序是「默认的」还是「我写的」？

**结论：没有默认顺序。`|` 不认角色，只认你写的先后 —— 从左到右。**

同一批零件，两种写法两个结果：

| 写法 | 逐棒执行 | 结果 |
|---|---|---|
| `(A \| B).invoke(1)` | A 收到 1 → 吐出 2；B 收到 2 → 吐出 20 | **20** |
| `(B \| A).invoke(1)` | B 收到 1 → 吐出 10；A 收到 10 → 吐出 11 | **11** |

> 所以「写成 `parser | model | prompt` 会不会先跑 prompt」—— **不会**。
> 执行顺序就是 `parser → model → prompt`。**既没有默认顺序，也没有自动重排或纠正。**

---

## 3. 「谁站在第一棒」是什么意思？

**结论：第一棒收到的是你 `invoke()` 传进去的原物；之后每一棒收到的，都是上一棒吐出来的东西。**

实测（三棒探针，每棒往字符串尾部追加自己的名字）：

```
chain.invoke("原料")
   一棒  收到 '原料'                  ← 你传的原文
   一棒  吐出 '原料 +一棒'
   二棒  收到 '原料 +一棒'            ← 一棒的吐出物
   二棒  吐出 '原料 +一棒 +二棒'
   三棒  收到 '原料 +一棒 +二棒'      ← 二棒的吐出物
```

**每一棒的「收到」都等于上一棒的「吐出」**，只有第一棒收到的是「原料」本身。
这就是「谁站在第一棒」的全部含义 —— 它决定「你该往 `invoke()` 里塞什么」。

---

## 4. 「前者输出成为后者输入」有直接证据吗？

**有，而且是逐字成立的：下游收到的，就是上游吐出的那个对象本身。**

实测：

```
prompt.invoke({'q': '你好'})  返回类型 = ChatPromptValue
（链里）下游收到的类型                 = ChatPromptValue   ← 同一个类
```

没有任何转换、猜测或重新构造 —— **形状对得上，管道才通**。

---

## 5. 为什么 `invoke` 有时传字符串、有时传字典？

**结论：传什么由「第一棒想吃什么」决定，没有统一答案。**

实测：`chain = prompt | model | parser` 的 `chain.first` 是 `ChatPromptTemplate`，
而它要的是变量字典 → 所以必须 `invoke({"q": "..."})`。

| 链的第一棒 | invoke 要传 |
|---|---|
| `ChatPromptTemplate` | `dict`（变量字典） |
| 聊天模型 | `str` / 消息列表 / PromptValue |
| `StrOutputParser` | 字符串或消息对象 |

---

## 6. 左边放一个字典，也能接管道？

**能 —— 因为 `Runnable` 除了 `__or__` 还实现了反向的 `__ror__`。**

实测：

```
type(dict | Runnable)        = RunnableSequence
(dict | Runnable).invoke(1)  = {'a': 2, 'b': 1}
(dict | prompt).invoke(1)    = 2 / 1
```

**为什么重要**：RAG 的标准写法

```python
{"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | model | parser
```

第一段「字典 | prompt」就是靠 `__ror__` 成立的。**D15 会亲手写这一行。**

---

## 7. `model` 只能吃 `ChatPromptValue` 吗？

**不是。能吃 3 种：`str` / 消息列表 / `PromptValue`。只有 `dict` 被拒绝。**

实测（借用真模型的入口校验函数，纯本地、不发请求）：

| 喂进去 | 结果 |
|---|---|
| `"你好"` | 接受，统一转成 `StringPromptValue` |
| `[HumanMessage(...)]` | 接受，统一转成 `ChatPromptValue` |
| `[Human, AI 两条]` | 接受，统一转成 `ChatPromptValue` |
| `ChatPromptValue` | 接受（原样送进去） |
| `{"q": "你好"}` | **拒绝** `ValueError` |

报错原文自己交代了清单：

```
Invalid input type <class 'dict'>. Must be a PromptValue, str, or list of BaseMessages.
                                     ↑ 就这三种
```

**顺带一个设计洞察**：三种输入进去之前会被**统一归一化成 `PromptValue`**（字符串走 `StringPromptValue`，消息列表走 `ChatPromptValue`）。模型内部只处理一种东西，对外却愿意收三种 —— 这也是 `hello_model.py` 里直接 `llm.invoke("你好")` 能跑通的原因（被自动包成了一条 HumanMessage）。

---

## 8. 写反成 `parser | model | prompt`，会报错吗？

**★ 不会报错 —— 它跑通，然后吐出一坨垃圾。这是今天最反直觉的一条。**

实测（喂一个字符串 `"你好"`）：

```
steps = ['StrOutputParser', 'RunnableLambda', 'ChatPromptTemplate']
跑通了！返回 ChatPromptValue（没抛异常）
{q} 里被塞进去的 = "content='假回复' additional_kwargs={} response_metadata={}
                    tool_calls=[] invalid_tool_calls=[]"
```

三步全都执行完了。但 `{q}` 里被塞进去的是**一整个 `AIMessage` 对象被 `str()` 化之后的那坨东西**。

原因：**`prompt` 在「模板恰好只有 1 个变量」时不挑食** —— 它收到非字典输入不会拒绝，而是把那个东西塞进唯一的变量位。

> ⚠️ **这一句在 09-23 被实验修正过**：前提是「变量恰好 1 个」。变量 ≥2 个时，同样的写法直接 `TypeError`。
> 完整边界见 **§15** —— 这是 D5 最值钱的一条发现。

---

## 9. 那写反成 `model | prompt | parser` 呢？

**这个会报错。**

```
steps = ['RunnableLambda', 'ChatPromptTemplate', 'StrOutputParser']
ValueError: Invalid input type <class 'dict'>.
            Must be a PromptValue, str, or list of BaseMessages.
```

因为 `model` 站在第一棒，而它**入口严格**，不认 `dict`。

> **两个方向结果不同 → 结论：报不报错不看顺序，看「那一棒挑不挑食」。** 见下方 §11。

---

## 10. `Runnable` 到底是什么？函数？用法？

**都不是。它是一个抽象基类 —— 准确说，一份「身份」或「契约」。**

实测：

```
inspect.isclass(Runnable)       = True
必须你自己实现的方法            = ['invoke']          ← 只要一个
基类白送的方法                  = ['invoke', 'stream', 'batch', 'ainvoke', 'abatch', 'astream']
prompt / model / parser 都是？  = True True True
```

**定义只有一句：只要你会 `invoke`，你就是 Runnable。**

你只须实现 `invoke`，`batch / stream / ainvoke` 全部由基类拿 `invoke` 给你拼出来。

| 猜测 | 判定 |
|---|---|
| 它是一个**函数**？ | ❌ 你没法写 `Runnable(...)` 造一个出来 |
| 它是一种**用法**？ | ❌ 用法指动作（`invoke()`、`\|`）；Runnable 是「能做这些动作的东西的统称」 |
| 它是一个**类 / 协议**？ | ✅ |

### 一个你应该很熟的类比

Python 的 `Iterable`：只要类实现了 `__iter__`，`for` 就能遍历它。
没人会问「`Iterable` 是函数还是用法」—— **它是一个协议**。

`Runnable` 之于 `invoke`，就是 `Iterable` 之于 `__iter__`。

---

## 11. 速查表：三个组件的脾气完全不同

| 组件 | 脾气 | 收到吃不下的东西时 | 后果 |
|---|---|---|---|
| **`model`** | **严格** | 当场 `ValueError` | 好事 —— 立刻暴露 |
| **`prompt`** | **单变量时才不挑食** | 1 个变量：塞进变量位、不报错；**≥2 个变量：`TypeError`** | 单变量时**静默出垃圾**，最危险 |
| **`parser`** | 半严格 | 认 `str` 与有 `content` 的对象，其余报错 | 视输入而定 |

**这张表比任何「正确顺序」都重要** —— 它解释了为什么同样的错误，有时报错、有时悄悄出错。
（`prompt` 那一行是 09-23 修正后的版本，原写作「不挑食」—— 少了「单变量」这个前提。）

---

## 12. 要背的是类型链，不是顺序

```
dict  →  prompt  →  PromptValue  →  model  →  AIMessage  →  parser  →  str
```

**每一节的输出，必须正好是下一节能吃的输入。** 「正确顺序」只是这条链的结果，不是原因。

跑完觉得结果怪，第一件事永远是：

```python
print([s.__class__.__name__ for s in chain.steps])   # 先确认顺序对不对
```

---

## 13. 今天两次「静默失败」（比报错危险得多）

| 现场 | 写法 | 表现 |
|---|---|---|
| ① | `parser \| prompt`（`invoke("我是字符串")`） | 不报错，字符串被当成 `{q}` 的值 → 「用户问：我是字符串」 |
| ② | `parser \| model \| prompt` | 不报错，整个 AIMessage 被 `str()` 化塞进 `{q}` → 一坨乱码 |

**共同根因：`prompt` 遇到非字典输入时不拒绝，而是默默塞进变量位**（前提：模板只有 1 个变量，见 §15）。
**报错是好事，静默失败才要命** —— 这就是这条经验的价值。

---

## 14. 面试可讲的三句话

1. **`|` 不是语法糖，是 `Runnable.__or__` 运算符重载**；拼出来的是 `RunnableSequence`，
   语义是「上一个的输出成为下一个的输入」，且**只组装不执行**（要 `.invoke()` 才跑）。
2. **链的正确性由「类型链」保证，不由顺序约定保证** ——
   `dict → prompt → PromptValue → model → AIMessage → parser → str`，每节的输出必须是下一节能吃的输入。
3. **框架组件的入口宽容度不一样**：`model` 严格（报错）、`prompt` 单变量时宽容（静默出错）、
   `parser` 半严格。**生产代码里「不报错」往往比「报错」更值得警惕。**

---

## 15. ★ 单变量特例：`prompt` 的「宽容」是有前提的

**结论：模板恰好只有 1 个输入变量时，非 dict 输入会被自动塞进那个变量；≥2 个变量时直接 `TypeError`。**

这不是推理出来的，**源码里写着**。`langchain_core/prompts/base.py` 第 161-195 行，`_validate_input()`：

```python
def _validate_input(self, inner_input):
    if not isinstance(inner_input, dict):
        if len(self.input_variables) == 1:          # ← 单变量特例
            var_name = self.input_variables[0]
            inner_input_ = {var_name: inner_input}
        else:
            raise TypeError(                        # ← 多变量挡在这里
                "Expected mapping type as input to ChatPromptTemplate. Received ..."
            )
    else:
        inner_input_ = inner_input
    missing = set(self.input_variables).difference(inner_input_)
    if missing:
        raise KeyError(...)                         # ← 另一种错：dict 但缺变量
    return inner_input_
```

官方注释也承认这件事 —— `langchain_core/prompts/chat.py` 第 871 行，标题就是
`!!! note "Single-variable template"`：只有单个输入变量时，用非 dict 调用会把参数注入那个变量位置。

### 四种输入，四条不同结局（本机实测）

| 模板 | 你传的 | 结果 |
|---|---|---|
| `{question}`（1 个变量） | `"你好"` | ✅ 不报错，等价于 `{"question": "你好"}` —— 产出的 PromptValue **逐字相同** |
| `{question}`（1 个变量） | `12345` | ✅ 照样塞进去（**不限 str**，任何非 dict 都吃） |
| `{question}{style}`（2 个变量） | `"你好"` | ❌ **`TypeError`**：Expected mapping type as input to ChatPromptTemplate. Received `<class 'str'>` |
| 任何模板 | `{"wrong": "..."}` | ❌ **`KeyError`**：missing variables `{'question'}` |

**最后两行是两种不同的错**：一条是「类型不对」，一条是「变量名不对」—— 看报错就能分清。
`chain.invoke("你好")` 同样不报错（链头是 prompt，走同一条校验路径）。

### ⚠️ 关键区分：特例 ≠ 定义内的合法输入

**`model.invoke("你好")` 也能跑，但和这件事毫无关系。** 两条独立机制、两个代码位置：

| 链头 | `invoke("你好")` | 机制 | 代码位置 | 性质 |
|---|---|---|---|---|
| `ChatPromptTemplate` | 接受 —— **仅当恰好 1 个变量** | `_validate_input()` 的单变量特例 | `prompts/base.py:163` | **特例**：变量数一变就报错 |
| `ChatModel`（如 ChatDeepSeek） | 接受 —— **永远** | `_convert_input()` 类型归一化 | `chat_models/base.py` | **定义内的合法输入**：str / 消息列表 / PromptValue 三选一 |
| `StrOutputParser` | 接受 | 原样返回 | — | — |

**区别就一句话**：

- `prompt` 收到 str，是「**本来不该收，单变量时网开一面**」→ 是**宽容**，随时可能消失；
- `model` 收到 str，是「**说明书里写着就收**」→ 是**契约**，写死的行为（见 §7 的能吃清单）。

**所以 D4 notebook 里一直写的 `model.invoke("...")` 完全没问题** —— 那是合法用法，不是踩了特例。
**要警惕的只有 `prompt` 那一条**：别依赖它的宽容。

### 工程启示（这才是重点）

**① 便利就是陷阱。** 今天少写一层 `dict` 很爽；明天给模板加第二个变量，老代码**突然炸**，
而且报错处看不出跟「我加了个变量」有任何关系。

**② 永远显式传 dict。** `invoke({"question": "你好"})` 在任何变量数下都正确，没有例外。

**③ 网上资料普遍讲错。** 「必须传 dict」在博客里是标准答案，但它**不完整** ——
这是「用源码校准认知」的活案例，也是面试可讲的排障故事。

---

## 16. 附：D5 其余问答速查

| # | 问题 | 结论 |
|---|---|---|
| 1 | `Plain() + Plain()` 为什么报错 | 运算符能否生效，取决于对象写没写对应方法（`__add__` / `__or__`）。反证法 |
| 2 | `\|` 是谁定义的 | 「`a \| b` → 调 `a.__or__(b)`」是 **Python 内置规则**；`\|` 之后干什么由 `__or__` 自己写 |
| 3 | `lambda x: ...` 是自定义语法吗 | 不是，lambda 是 Python 内置语法。**关键在传函数本身而非执行结果**，把计算推迟到 `invoke` —— 「只组装不执行」的实现基础 |
| 4 | `(a\|b).invoke(1)` 的 20 从哪来 | `Step` 是空壳，×2 藏在构造时传入的 `double` 里 —— **行为取决于装进什么函数** |
| 5 | `(a\|b).invoke(1)` 怎么读 | 顺着数据流：`1 → step_a(×2) → 2 → step_b(×10) → 20`。左边离输入近先执行 |
| 6 | 「实例」什么意思 | 类 = 图纸，实例 = 实物。`StrOutputParser()` 那个括号就是「图纸 → 实物」的动作 |
| 7 | 接口不一样能接吗 | 玩具版运行时 `AttributeError`；LangChain 有 **coerce 转接头**（普通函数自动包成 `RunnableLambda`），转不了的**组装时**就 `TypeError` |
| 8 | `RunnableLambda` 定义在哪 | 不在项目里，从 `.venv/Lib/site-packages/langchain_core/runnables/` import。`Ctrl+点击`可跳源码 |
| 9 | 解析器是什么 | 链尾环节，把 `AIMessage` 抠成干净的 `str`/`dict` —— 「起了正式名字的函数」，无魔法 |
| 10 | `asyncio.run` 为什么要包 | `await` 只能写在 `async def` 里；它是**同步 ↔ 异步的转接头** |
| 11 | IDE 为什么不报红 | Python 是动态类型，**输入形状是运行时的事**，静态检查看不见 —— 所以今天这些坑 IDE 帮不上忙 |

---

## 17. stream「看起来不流式」怎么排查（09-23 已定案）

**结论：不是 bug，是错觉 —— 上游真流式，只是太快了。**

排查方法：给每个 chunk 打时间戳 + 数块数。

```python
t0 = time.perf_counter()
stamps = []
for chunk in chain.stream({"question": "..."}):
    stamps.append(time.perf_counter() - t0)
print(f"块数={len(stamps)} 首块={stamps[0]:.2f}s 末块={stamps[-1]:.2f}s")
```

实测（`deepseek-flash`，问「讲一下现在深圳发展的怎么样了」）：

| 指标 | 数值 |
|---|---|
| 字数 / 块数 | 259 字 / **1067 块** |
| 总耗时 | 6.12s（首块延迟 0.24s） |
| **文字速度** | **44 字/秒**（块间隔平均 5.5ms） |

→ **上游是真流式**（块一批批到达、有时间间隔）。
但人眼要看出「打字机效果」需 ≲20 字/秒，**44 字/秒 视觉上就是逐行刷屏** —— 所以感觉「不流式」。

**排除项**：代码没写错（`end=""` + `flush=True` 都对）；网关也正常透传 SSE
（原怀疑 `DEEPSEEK_BASE_URL` 没透传，实测否定了）；system 要求回答简短也压缩了时长。

**想真看到逐字效果**：让它输出长一点（500 字以上），把 6 秒拉成十几秒。

> 若仍怀疑是 PyCharm Run 窗口的显示缓冲，用 3 行无模型代码即可判定：
> ```python
> for i in range(10):
>     print(i, end=" ", flush=True)
>     time.sleep(0.5)
> ```
> 数字逐个跳出 = 控制台无缓冲；卡 5 秒后一起出 = 需勾「模拟终端中的输出」。

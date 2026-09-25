# D6 结构化输出 · 笔记（Schema 才是主角）

> 本文件里的每条结论都**在本机 venv 里实跑过**（`deepseek-chat`，temperature=0）。
> 凡是我没实测的，会明确标「未验证」。踩坑的完整五段式在 `errors/index.md` 的 **D6** 四条里。

## 0. 一句话

**结构化输出 = 把「你的类」翻译成 JSON Schema，塞进请求的 `tools` 字段当合同，
模型照合同填表，最后 pydantic 把填好的表收回成对象。**
主角是 **Schema**，`Person` 只是「能造出 Schema 的容器」。

## 1. 链路长什么样（实测）

```python
s = model.with_structured_output(Person)
print([type(x).__name__ for x in s.steps])
# ['_ChatModelBinding', 'PydanticToolsParser']
```

- `with_structured_output(Person)` 返回的是 **`RunnableSequence`** —— 和 D5 的
  `prompt | model | parser` 是**同一个类**。所以它一样有 `.invoke / .stream / .batch`，
  也能直接接在 `prompt |` 后面。
- **可简写为**：`with_structured_output(Person) = model.bind_tools([Person]) | PydanticToolsParser(tools=[Person])`

完整类型链：

```
你的类 → JSON Schema → 塞进请求 tools → 模型输出 tool_calls(JSON 文本) → PydanticToolsParser → Person 实例
```

## 2. 四个概念，各归各位

| 概念 | 是什么 | 关键点 |
|---|---|---|
| **`BaseModel`** | pydantic 的基类 | 继承它 = 白得 `model_json_schema()`。**LangChain 不检查你继没继承**，它只要 Schema |
| **`JSON Schema`** | 一个普通 `dict` | 跨语言标准（json-schema.org），不是 pydantic / LangChain 发明的 |
| **`RunnableSequence`** | 链本身 | D5 那个类的复用，不是新概念 |
| **模型的角色** | 表格填写员 | 它读到的**是一段文本**（JSON），不是你的 Python 代码 |

**`BaseModel` 的完整因果**：继承（**手段**）→ `model_json_schema()`（**能力**）→ Schema（**目的**）。
「`Person` 是 pydantic 类因为它继承了 `BaseModel`」在**定义**上对，但漏了中间那环 ——
而漏掉的那环正好是「不继承会怎样」的答案（→ 空 Schema + 静默 `{}`）。

**模型为什么能填表**：训练时见过海量「tools 定义 + 用户一句话 → function-call JSON」的样本，
学到的是「照着给的 Schema 填表」，**不是理解你的 Python 代码**。
它输出的也只是**文本**，把它变成对象的是 `PydanticToolsParser`（就是 D5 学过的 parser）。

## 3. 字段三要素：谁给谁看

| 要素 | 写给谁 | 作用 |
|---|---|---|
| **字段名** | 模型 **+** 代码 | 代码靠它取值（`result.name`）；模型靠它猜语义 |
| **类型注解** | pydantic + 模型 | 决定 Schema 里的 `type`，也决定回收时的**校验/转换**（`"30"` → `30` ✅；`"三十岁"` → `ValidationError`） |
| **`Field(description=...)`** | **只给模型** | 写进 JSON Schema 的 `description`，模型靠它区分语义相近的字段 |

三样**一起**变成 JSON Schema 里的 `properties` 发给模型。抓到的请求体（原文）：

```json
"tools": [{"type": "function", "function": {
    "name": "Person", "description": "人物的信息",
    "parameters": {
      "properties": {
        "name":       {"description": "姓名", "type": "string"},
        "age":        {"description": "年龄", "type": "integer"},
        "occupation": {"description": "职业", "type": "string"}},
      "required": ["name", "age", "occupation"],
      "type": "object"}}}]
```

`Field(description="姓名")` 原封不动出现在 `tools[0].function.parameters` 里。

## 4. 多字段自动识别：四组实验（实测，`deepseek-chat`）

输入统一用 `"远景科技成立于2021年，主要做智能客服方案。"`

| # | 字段名 | 类型注解 | description | 结果 |
|---|---|---|---|---|
| ① | `name/age/occupation` | 正常 | **故意写歪**（公司名称…） | ✅ **照抽对** —— 字段名够强，描述没起作用 |
| ② | `a/b/c` | `str/int/str` | 无 | ✅ **仍抽对** —— 类型 + 输入语义给了线索 |
| ③ | `a/b` | 都是 `str` | `a=公司名称 b=主营业务` | ✅ 正确 |
| ③' | `a/b` | 都是 `str` | **互换描述** | ✅ **结果跟着翻转** —— 描述决定一切 |
| ③'' | `a/b` | 都是 `str` | 无 | ❌ b 拿到 `'2021年成立 智能客服方案'`（**垃圾**） |

**字段顺序 vs 字段名**（补充实测）：

| 做法 | 结果 |
|---|---|
| 字段名有意义（`company/business`），**声明顺序倒过来** | ✅ 两次**完全一样** —— 模型**按名字/描述对应，不按位置** |
| 字段名无意义（`x/y`），无 description，**声明顺序倒过来** | ❌ **结果跟着变**，`y` 拿到 `'2021'`（垃圾）—— 没名字时才**按位置瞎抓** |

→ **线索优先级：字段名 / 类型（最强）→ `description`（名字没用时接管）→ 位置（最后兜底，出垃圾）。**

**一句话规矩**：字段名写清楚 + **`description` 一定要写**。
不是因为它每次都用得上，而是**你没法预知哪天输入会变歧义** —— 那天它从「可有可无」变成「唯一线索」。

## 5. 校验的边界：什么拦得住、什么拦不住

**这套链路里，`ValidationError` 很少出现 —— 不是因为校验被削弱了，是因为「没机会触发」。**

| 情形 | 结果 |
|---|---|
| **值不合法**（绕过模型，手工喂 `age="三十岁"` 给 `PydanticToolsParser`） | ✅ `ValidationError: Input should be a valid integer, unable to parse string as an integer` —— **校验完好** |
| **值合法但是编的**（输入没提年龄，模型给 `30`） | ❌ 拦不住 —— **校验没有机会触发** |
| 显式约束 `Field(ge=1, le=120)`，输入说「张三今年 999 岁」 | 模型主动贴合成 `age=120` —— **它在生成时就被 Schema 约束住了** |

两条可复用结论：

1. **pydantic 的校验没有被削弱。** 模型在生成时就被 Schema 约束着，所以送过来的值本来大多合规。
   「校验比想象弱」是个**错觉** —— 真相是**它和模型是双保险**：模型先自己守规矩，pydantic 再兜一层。
2. **Schema 只保证【形状】，不保证【真实性】。** 输入里没有的信息，模型会**编一个像真的** ——
   `age=30` 而不是 `0`。想防这个得在 **prompt** 里写「没有就说不知道」，不是改 Schema。

## 6. 今天踩的坑（完整版见 `errors/index.md`）

| 坑 | 一句话 |
|---|---|
| `pip install basemodel` | 装的是 2019 年的野包；它的版本号按构建时间生成，永远和文件名对不上 |
| `deepseek-flash` + 结构化输出 | 400 `Thinking mode does not support this tool_choice` —— flash 是 thinking 模型，**不能用于任何工具调用场景**（D8/D9 的 `bind_tools` 同样） |
| `result.name` → `None` | `AIMessage` 恰好也有个 `name` 字段（消息发送者），**取错不报错，给假答案在前** |
| 不继承 `BaseModel` | **不报错**，只生成空 Schema → 静默返回 `{}` |
| 字段缺失 | 模型**编造**一个像真的值，不报错 —— 比填 `0` 更危险 |

> **D6 的贯穿主题**：这一天撞到的，几乎全是「**不报错但不对**」。
> D5 那句「跑通了 ≠ 跑对了」在 D6 要再扩一句：**「没报错」更不等于「对」。**

## 7. 面试可以直接念的三句

1. **「我用 `with_structured_output` 做过结构化抽取。它的本质是把 Pydantic 模型转成 JSON Schema
   塞进 `tools`，靠工具调用让模型照合同填表，再用 `PydanticToolsParser` 把结果收成对象。」**
2. **「它返回的是 `RunnableSequence`，和 LCEL 的 `prompt | model | parser` 是同一个类，
   所以能直接接在链上，也能 `batch`。」**
3. **「我踩过一个静默坑：输入里没提的字段，模型会编一个像真的值 —— Schema 只保证形状不保证真实性，
   所以校验通不代表数据对。」**

## 8. 还没做 / 待验证

- 本文件所有结论都来自**同一天的实测**，没有查官方文档逐条对照
- `include_raw=True` 看 `raw / parsed / parsing_error` 三个出口 —— **未验证**
- `method="json_mode"` / `method="json_schema"` 的差异 —— **未验证**（已知 `json_mode` 要求提示词含「json」）
- 真实工具调用（`bind_tools` + 模型自己产生 `tool_calls`）会不会撞 D4 那个 `reasoning_content` 400 —— **留给 D8/D9**

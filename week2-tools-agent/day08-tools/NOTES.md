# D8 笔记 · 工具（Tools）基础

> 对应 `week2-tools-agent/day08-tools/` 三个 notebook（P33–P35）

## 1. 工具是什么

工具 = **普通 Python 函数 + 一份「模型能读懂的描述」**。
函数负责真正执行，描述（docstring / `args_schema`）负责告诉模型「什么时候该调它、要什么参数」。

## 2. 三种调用方式

| 方式 | 代码 | 谁执行 |
|---|---|---|
| 直接调用 | `get_weather.invoke({"city": "珠海"})` | 我自己 |
| 模型决定调不调 | `model.bind_tools([get_weather]).invoke(...)` → 返回 `tool_calls` | 模型只「说」，不执行 |
| 完整流转 | 拿到 tool_calls → 执行 → `ToolMessage` 回传 → 再 invoke | 我写循环 |

## 3. 定义工具的两条路

- **不用 @tool**：普通函数 + `convert_to_openai_tool(fn)` 查看解析结果；描述靠 docstring。
- **用 @tool**：`@tool` 装饰器，可传 `description` / `name_or_callable` / `args_schema`。

## 4. 关键细节（都在 notebook 里实测过）

- docstring 声明了参数描述、但函数签名没写类型 → 报错。
- 参数有默认值 → 不再出现在 schema 的 `required` 里。
- `description` 参数优先级高于 docstring。
- `args_schema` 两种写法：Pydantic 模型 / 原始 Json schema。

## 5. 一句话记住

**模型只输出「调哪个函数、参数是什么」的意图（`tool_calls`），执行、回传、循环全得自己写。**
这是 D9 手写 Agent 循环的地基。

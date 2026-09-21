# 主技术栈：**Python**

> 拍板时间：2026-09-20 ｜ 决定人：我 ｜ 影响范围：D2 起全部任务细化到具体包与写法

## 结论

**选 Python，不选 JS/TS。**

## 理由

1. **教程与文档的密度差一个量级。** B 站中文 LangChain / LangGraph 教程 95% 是 Python；
   官方文档 `docs.langchain.com/oss/python/...` 也是 Python 优先，同一页面的 JS 版本更新滞后。
   35 天 × 3 小时的预算里，**「照着视频能跑通」比「用更贴岗位的语言」更值钱。**
2. **JD 是「Python 或 JS/TS 至少一门」，两者等价。** 硬条件里没有偏向，选哪门都不扣分；
   扣分的是「两门都半桶水」。
3. **D9 / D17 / D23 / D34 四个重点日全是数据与实验。** Python 侧的 `chromadb`、`pandas`、
   `pypdf`、评估表格工具链更顺手，实验结论更容易出图出表 —— 这四个日子直接对应 JD 的加分项。
4. **JS/TS 的岗位优势在这一轮用不上。** 「浏览器插件 / Figma 插件 / Design Engineering」是加分项，
   不是硬条件；等第 5 周真要做前端界面时，用 Streamlit 或 FastAPI + 静态页兜住即可，
   **不需要为了界面把整个学习主线换成 JS/TS。**

## 代价（不选 JS/TS 失去什么）

- **少一个和「设计工程」直接对话的语言证据。** 面试如果聊到前端/插件方向，我只能用 Python 侧的
  证据兜（比如「界面我用 Streamlit/FastAPI 出的，前端能力我有独立项目」）。
- **以后真要写 Figma 插件 / 浏览器插件，还得补 TS。** 但那是入职后的事，不是拿到 offer 的前提。
- LangChain.js 生态的第三方集成数量比 Python 少，不过本轮用不到那些集成。

## 什么条件下会换掉它

- 第 5 周（D29 起）如果最终选题偏向**浏览器插件 / Figma 插件**形态，界面层改用 TS，
  但**主链路（Agent + RAG）保持 Python**，用 HTTP 接口对接 —— 不整体换栈。
- 出现只有 JS 才有的关键依赖（目前没看到）。
- 面试反馈明确说「我们这条线只写 TS」（拿到反馈再算）。

## 本轮的包清单（Python 轨）

| 用途 | 包 | 什么时候用 |
|---|---|---|
| 主框架（create_agent / init_chat_model / LCEL） | `langchain==1.4.2` | D1 起 |
| OpenAI 兼容协议接入（DeepSeek / 通义 / 智谱） | `langchain-openai==1.6.2` | D1 起 |
| DeepSeek 官方集成（等价写法，用来对比） | `langchain-deepseek==1.1.0` | D1 起 |
| 环境变量 | `python-dotenv` | D1 起 |
| 结构化输出 | `pydantic`（随 langchain 装） | D6 起 |
| 状态图 / 流程控制 | `langgraph` | D25 起 |
| 向量库 | `chromadb` | D19 起 |
| 文档加载 | `pypdf` / `unstructured`（用到再装） | D16 起 |
| 服务端界面 | `streamlit` 或 `fastapi + uvicorn` | D24 起 |
| 可观测 | `langsmith` | D28 起 |

**环境约定：Python 3.12.8 + PyCharm 项目内 venv（`D:\AI_learning_project\03-Internship preparation\.venv`）。**
理由见 `docs/decisions.md`。

## 环境记录（D1 实测）

- 解释器：`C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\python.exe` → `Python 3.12.8`
- 依赖安装：`pip install -r week1-basics/day01-setup/requirements.txt`
- 自检脚本：`week1-basics/day01-setup/env_check.py`（版本 / 依赖 / key / gitignore 四项）
- 首次调用：`week1-basics/day01-setup/hello_model.py`

## 已作废的备选（留档，别再翻出来重提）

- ~~JS/TS 轨：`@langchain/core` / `@langchain/openai` / `@langchain/langgraph` + Zod~~
  —— 作废原因见上面「理由」第 1、4 条。

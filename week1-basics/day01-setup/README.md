# D1 · 环境搭建 + LangChain 全景

> 目录 `week1-basics/day01-setup/` ｜ 预计 2.5–3h ｜ 对应 2026-09-21（周一） ｜ 阶段：第 1 周 打通链路
> 技术栈：**Python 轨**（已定，见 `docs/stack.md`）

## 结论先行

今天的产出不是「学会 LangChain」，而是**把环境一次配死**：Python 3.12 + PyCharm venv +
`langchain 1.4.2 / langchain-openai 1.6.2 / langchain-deepseek 1.1.0` + `.env` 里的 DeepSeek key，
跑出一个能打印 token 数的模型调用。后面 34 天不再碰配置。

一句话记住：**LangChain = Model + Harness**（模型 + 环绕模型的脚手架）。这是官方新版 Overview 的原话，面试可以直接用。

---

## 一、今天学什么

### 1. 视频：尚硅谷《LangChain 从入门到实战 2026 版》第 01 章（挑讲，约 39 分 35 秒）

BV 号 `BV1rv7A6oEeP` ｜ https://www.bilibili.com/video/BV1rv7A6oEeP/
这一章共 10P，**只挑下面 7P**，P07 / P08 / P09 跳过（理由写在表后）。

| 分 P | 标题 | 时长 |
|---|---|---|
| P01 | 01-课程介绍 | 04:09 |
| P02 | 02-为什么需要 LangChain | 10:50 |
| P03 | 03-大模型相关岗位介绍 | 04:17 |
| P04 | 04-LangChain 是什么 | 07:15 |
| P05 | 05-LangChain 的主要模块和 API 文档 | 04:17 |
| P06 | 06-LangChain 家族四大支柱 | 04:43 |
| P10 | 10-大模型开发的 4 个递进场景 | 04:04 |

**跳过的三讲和理由：**

- **P07 conda 的安装及虚拟环境的配置（16:51）** —— 你用 PyCharm 自带 venv，不走 conda。真要看，只看前 5 分钟听它讲「为什么要隔离环境」。
- **P08 / P09 大模型应用场景 Agent 开发（09:48 + 05:55）** —— 这两讲是 Agent 的引子，**留到 D8 当天的课前热身**，今天看了也用不上。

看的时候只记两件事：**四支柱分别叫什么**、**4 个递进场景的顺序**。别记 API。

### 2. 视频：B 站《LangChain 从基础到实战全模块拆解》第 1 讲（29:51）

BV 号 `BV1WgcZzRE9E` ｜ 第 1 讲「课程简介」｜ 29 分 51 秒
这是**全局地图**，告诉你后面 35 天走过的每一块在整体里是什么位置。当纪录片看，不用记。

> **选看（不占今天预算）：第 2 讲「langchain 基础——安装与 hello world」47 分 19 秒。**
> 装包或 venv 卡住时直接跳这一讲看，别自己硬扛。

### 3. 文档：两页，共约 20 分钟

| 页面 | 时长 | 看什么 |
|---|---|---|
| [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview) | 15 分钟 | ① 开头那句 **"Agent = Model + Harness"**；② **LangChain vs LangGraph vs Deep Agents** 那段取舍（面试高频）；③ 下面的 `create_agent` 代码块，今晚只要看懂形状 |
| [Install LangChain](https://docs.langchain.com/oss/python/langchain/install) | 5 分钟 | **Python 3.10+** 这条硬门槛；`pip install -U langchain`、`pip install -U langchain-openai` 的官方写法 |

> ⚠️ **计划表里那处已经过时，这里修正：** 原计划写「看懂 Overview 页的 *Agent development lifecycle* 图」——
> 新版文档已经改版，**这张图没有了**。现在这一页的核心是 `Agent = Model + Harness` + 三方框架取舍。
> 以后凡是遇到「图上讲了什么」的笔记，先确认图还在不在。

---

## 二、今天动手做什么（约 60–70 分钟）

全程 **PyCharm GUI**，不用命令行（终端只用于 `pip install`）。

- [ ] **① 配解释器**：PyCharm 打开 `D:\AI_learning_project\03-Internship preparation`
      → 菜单 **文件 → 设置**（英文版是 `File` → `Settings`；**快捷键 `Ctrl+Alt+S` 被输入法 / 截图 / 网盘类软件抢走是常事，
      按了没反应就用菜单，别在这卡住**；更快：点窗口右下角状态栏的解释器名 → **添加新解释器**；
      万能兜底：`Ctrl+Shift+A`（查找操作）→ 输 `解释器`）
      → 左栏 **项目: 03-Internship preparation** → **Python 解释器**
      → **添加解释器** → **添加本地解释器…**
      → 左栏选 **Virtualenv 环境** → 上方选 **新的**
      → **位置**：`D:\AI_learning_project\03-Internship preparation\.venv`
      → **基础解释器**：`C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\python.exe`（3.12.8）
      → **继承全局 site-packages** 不勾、**对所有项目可用** 不勾 → 确定
      （完整中英对照表见 `docs/daily/D00-PyCharm工程搭建与D1-D3补齐.html`）
      **⚠️ 不要复用旧教程工程 `D:\python_langchain\langchain1.2_tutorial` 的解释器**（那是 conda base + langchain 1.2.12，
      混用会互相覆盖版本）。理由见 `docs/decisions.md` 的「一个 git 仓库 = 一个独立 PyCharm 工程」。
- [ ] **② 为什么选 3.12 不选 3.13**：LangChain 要求 `3.10 <= Python < 4.0`，3.13 也能跑；
      但 D15 之后要装 Chroma / pypdf / 各类 loader，3.12 的轮子最全，能少踩一半坑。**这条写进 decisions.md 了。**
      （你机器上还有 miniconda 的 3.14.7 —— 那个更别用。）
- [ ] **③ 装包**：PyCharm 底部 `Terminal` →
      `pip install -r week1-basics/day01-setup/requirements.txt`
      （装完在底部 `Python Packages` 面板里能看到 langchain 1.4.2）
- [ ] **④ 配 key**：仓库根目录把 `.env.example` 复制一份改名 `.env`（PyCharm 里选中文件 `Ctrl+C` → `Ctrl+V` → 改名），
      填 `DEEPSEEK_API_KEY=sk-...`。**`.env` 已在 .gitignore 里，永远不进库。**
- [ ] **⑤ 自检**：右键 `env_check.py` → Run。四项全 OK 才算过。
- [ ] **⑥ 首次调用**：右键 `hello_model.py` → Run。看到回复 + token 数就成了。
- [ ] **⑦（顺手 5 分钟）** 把 `hello_model.py` 里的 `MODEL` / `BASE_URL` 临时换成通义那一行，再跑一次，
      亲眼确认「换供应商只改两行」。然后改回来。

---

## 三、今天提交什么

PyCharm `Ctrl + K`。**每次提交前手动取消勾选不属于本条的文件**（默认会勾上当天所有改动）。
注意：`.venv/` 和 `.env` 不应该出现在任何一次的文件列表里 —— **出现了就是 .gitignore 没生效，先停下来修**。

### 第 1 条

```text
chore(day01): 初始化 Python 虚拟环境与依赖

Python 3.12.8 + PyCharm venv(.venv)，装 langchain 1.4.2 /
langchain-openai 1.6.2 / langchain-deepseek 1.1.0
DEEPSEEK_API_KEY 走 .env，已确认被 .gitignore 忽略
```

文件：`requirements.txt`、`.env.example`

### 第 2 条

```text
feat(day01): 跑通首次模型调用与环境自检

hello_model.py 走 OpenAI 兼容协议接入 DeepSeek，一行 init_chat_model
即可返回结果；env_check.py 检查版本/依赖/key/gitignore 四项
```

文件：`hello_model.py`、`env_check.py`

### 第 3 条

```text
docs(journal): D1 日志

结论：环境一次配好，后面 34 天不再折腾配置
```

文件：`docs/journal/2026-09-21.md`、`docs/stack.md`、`docs/decisions.md`

> **打 tag 放在 D7**（`w1-cli-v0.1`），今天不用。

---

## 四、今天必须留下的

- [ ] 代码当天跑通（`env_check.py` 四项全 OK + `hello_model.py` 打印出回复）
- [ ] 日志 → `docs/journal/2026-09-21.md`
- [ ] **一句话结论**：________________________________
      （要求：写「环境一次配死，后面 34 天不再碰配置」，或你自己更准的一句）
- [ ] 如果今天踩了坑，往 `errors/index.md` 抄一份（第一个坑大概率是 API key / base_url 配错）

---

## 五、今天最可能踩的两个坑（提前给答案）

| 现象 | 真实原因 | 怎么修 |
|---|---|---|
| `AuthenticationError: ... 401` | key 填错 / 前后带空格 / `.env` 里引号被当成值的一部分 | `.env` 里**不加引号**，`DEEPSEEK_API_KEY=sk-xxx` 顶格写 |
| `APIConnectionError` / `NotFoundError 404` | `base_url` 少了 `/v1`，或写成了 `https://api.deepseek.com/v1/chat/completions` | 只写到 `/v1` 为止，后面的路径框架自己拼 |

遇到了别急着改 —— **先把原始报错贴进 `errors/index.md`**，再动手。那个文件是面试最值钱的素材。

---

> 今天不求快。目标是环境一次配好，后面 34 天不用再折腾配置。

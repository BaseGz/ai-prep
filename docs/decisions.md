# 技术选型决策记录

> 规则：每做一个技术选择，就写一条。三段 —— **选了 A 不选 B 的理由 / 代价是什么 / 什么条件下会换掉它**。
> 面试官判断你有没有真做过，很大程度看这一页。

---

## D1 · 用 DeepSeek 作为默认模型

**理由**：OpenAI 兼容协议，国内可直连，便宜，`base_url` 一改就能用。
**代价**：不是最强的模型，复杂推理会差一些；但学习阶段够用。
**什么时候换**：需要多模态输入（影石场景）时，换成支持传图的模型。

---

## D1 · 技术栈选 Python，不选 JS/TS

**理由**：JD 写的是「Python 或 JS/TS 至少一门」，两者等价；但中文教程和官方文档都是 Python 优先，
35 天 × 3 小时里「照着视频能跑通」比「语言更贴岗位」更值钱。四个重点日（D9/D17/D23/D34）全是数据与
实验，Python 侧的 chromadb / pandas 更顺手。JS/TS 的岗位优势（插件、Design Engineering）是加分项不是硬条件。
**代价**：少一个直接对上「设计工程」的语言证据；以后真要写 Figma / 浏览器插件还得补 TS。
**什么时候换**：第 5 周选题若偏插件形态，界面层改用 TS + HTTP 接口对接 Agent，主链路仍是 Python；整体不换栈。

---

## D1 · 环境用项目内 venv + Python 3.12，不用 conda、不用 3.13

**理由**：PyCharm 项目内 venv 跟着项目走，换电脑/重装只认 `.venv`，不会污染全局；Python 3.12 的
第三方轮子（Chroma / pypdf / 各类 loader）最全。LangChain 1.x 要求 `3.10 <= Python < 4.0`，3.12 稳在区间中段。
**代价**：venv 不跨项目复用，每个项目都得重装一次（本项目只此一份，可接受）。
**什么时候换**：需要同一环境里管多版本 CUDA / 多套 Python 并存时，才换 conda。

---

## D1 · 一个 git 仓库 = 一个独立 PyCharm 工程，不复用旧教程工程

**理由**：PyCharm 的提交窗口只认「当前工程根所在的仓库」。工程根 = 仓库根时，`Ctrl+K` 的列表里只有这个仓库的改动，不会误提交。
另外旧教程工程 `D:\python_langchain\langchain1.2_tutorial` 的解释器是 conda base（miniconda 3.14.7），
其 `requirements.txt` pin 在 `langchain==1.2.12`（实测 conda base 里实际装的是 1.3.16），与本项目要的 `1.4.2` 不一致；
而且那个文件夹不是 git 仓库，在里面写的代码进不了版本库。
**代价**：环境要重建一次（约 5 分钟）；旧教程里的 notebook 不能直接复用，得改写成 `.py` 并升到 1.4.2 的写法。
**什么时候换**：只有当多个仓库确实共享同一套严格相同的依赖时，才考虑把 venv 放到仓库外统一管理；本项目不适用。

---

## D1 · 新旧两个 LangChain 环境物理隔离：不合并、不互装、不互相 pip install

**理由**：实测本机安装情况（2026-09-21 核对 `.dist-info` 目录）：

| 环境 | 路径 | 实测装到的 langchain |
|---|---|---|
| 旧教程工程用的 conda base | `D:\minianaconda` | langchain 1.3.16 ／ langchain-core 1.6.1 ／ langgraph 1.2.11 ／ pydantic 2.13.4 |
| **本项目 venv** | `03-Internship preparation\.venv` | langchain 1.4.2 ／ langchain-core 1.6.3 ／ langchain-openai 1.6.2 ／ langchain-deepseek 1.1.0 ／ langgraph 1.2.11 ／ openai 3.16.2 ／ pydantic 2.13.5 |
| 系统 Python 3.12 | `C:\...\Programs\Python\Python312` | 只有 openai 2.24.0，无 langchain |

两个环境的包各自装在自己的 `site-packages` 里，**同名包版本不同也不会冲突** —— pip 只认「当前激活的是哪个解释器」。
旧工程目录下没有 `.venv`，它一直直接用 conda base，所以那边不需要、也不应该为本项目改动。

**代价**：磁盘上多一份约 300MB 依赖；同一行 `import langchain` 在两个工程里行为可能不同（旧 1.3.16 / 新 1.4.2），
跨工程复制代码不能假设 API 一致。

**三条纪律**（违反任何一条才会真出问题）：
1. 不在本项目 PyCharm 工程里把解释器切成 `D:\minianaconda`；
2. 不在未激活 `.venv` 的终端里裸敲 `pip install`（那会装进全局环境）；
3. 旧工程继续用 conda base 没关系，但**不要**在那边执行本项目的 `requirements.txt`。

**什么时候换**：不换。只有明确要复跑旧教程代码时才切回 conda base，且切回去只读不装。

---

## D10 · 用 `create_agent`，不手写循环（D9 的手写版留作对照）

**理由**：

同一道两单题，手写 30 行循环产出 **8 条消息**，`create_agent` 产出 **7 条**，类型序列完全一致 ——
少的唯一一条是 `SystemMessage`，它变成了 `create_agent` 的参数，不再进 `messages`。
这说明「模型想调什么 → 工具返回什么 → 再问一轮」这条链路，两边是同一条，不存在框架独有的魔法。

框架替掉的是五件事：工具执行、`ToolMessage` 回填（含 `tool_call_id` 配对）、
「没有 `tool_calls` 就停」的判断、多个 `tool_calls` 的遍历、轮数上限。
`stream(stream_mode="updates")` 还把这两步暴露成 `[model]` / `[tools]` 事件 —— 手写版要自己插打印才看得见。

**代价**：

1. **循环里插不进手。** 想按轮数换 prompt、改写工具返回值、失败重试，只能写 middleware，
   不能像手写版那样直接改 `messages` 再进下一轮。
2. **默认上限 9999 轮，且超限抛异常。** 手写版 `MAX_ROUNDS = 8` 是软着陆（返回一句话），
   框架版直接 `GraphRecursionError`，调用方必须 `try/except` 兜住。生产环境里这是要显式处理的一条。
3. **事件粒度不是「一条消息一次」。** 两个并行 `tool_call` 被拆成两个 `[tools]` 事件
   （实测两单题：**6 个事件对应 7 条消息**），拿事件数推算轮数会算错。

**什么时候换**：

只做标准 tool-calling → 一律 `create_agent`；需要改循环内部行为（逐步提示、结果改写、按轮数换模型）
→ 写 middleware，或退回 D9 那种手写循环。

---

## D11 · 结构化输出走 `ToolStrategy`，工具异常交给 `ToolRetryMiddleware`

**理由**：

**结构化输出是一次「假工具调用」。** 加了 `response_format=OrderAnswer` 之后，messages 尾部变成
`AIMessage(tool_calls=['OrderAnswer'])` + `ToolMessage("Returning structured response: ...")`。
`OrderAnswer` 不是普通工具名，是我的 Pydantic 类名 —— **框架把我的 schema 注册成了一个只有参数表、
没有实现的工具**，逼模型按这个形状填参数。结果落在 `result["structured_response"]`，**不在 messages 里**。

DeepSeek 上只能走这条路：`ProviderStrategy` 直接 400 `This response_format type is unavailable now`，
`response_format=OrderAnswer`（裸 Pydantic 类）会落到 `AutoStrategy`，实测同样走 ToolStrategy。

**工具异常不会自己消失。** 裸 `@tool` 里 `raise` 之后，`agent.invoke` 把 `RuntimeError` 抛到顶层，
**一条消息都拿不到，`structured_response` 也没有**。框架默认不做 D9 那种「包成 ToolMessage 继续跑」。
兜底是 `ToolRetryMiddleware`，它默认 `on_failure='continue'`：重试完把错误包成一条 `ToolMessage`
交给模型，循环继续。实测模型会自己换路径 —— 转去调 `track_package`，最后在 `status` 里写
「退款进度查询失败」。

**代价 / 坑**：

1. **`max_retries` 只管得住一半的重试。** 实测 `max_retries=0` 时文案是 `after 1 attempt`，
   但模型读到结尾那句 `Please try again.` **自己又调了一次** `query_refund`，一共调了两次。
   `max_retries=1` / `=3` 反而都直接转去查物流、只调一次。**「重试」有两个来源：
   中间件的自动重试（可控）+ 模型看到错误提示后的自主重试（不可控）。**
2. **`structured_response` 在 messages 之外。** 打印 `messages[-1]` 只能看到
   `Returning structured response: ...` 那行字，真正的对象要单独取；将来做持久化、序列化时
   这一层要额外处理。
3. **prompt 决定「失败后怎么补」，而且会把字段语义带歪。** 在 `system_prompt` 里加一句
   「某个工具失败就先尝试用其它工具回答，最后说明哪部分没查到」之后，`status` 从
   `退款进度查询失败` 变成 `退款进度未知（物流已签收）` —— 模型确实照做了，但把一个物流事实
   塞进了退款字段。**引导 prompt 能提高完整度，也会污染字段语义，schema 越严格越要先想清这个副作用。**

**什么时候换**：

默认 `response_format=<Pydantic 类>`；模型填的格式不合规、需要它重来 → `ToolStrategy(handle_errors=...)`
（注意它处理的是 **schema 校验失败**，不是工具抛异常）；工具本身会挂 → `ToolRetryMiddleware`。
两者不是一件事：前者在 `response_format` 里，后者在 `middleware=` 里。

---

## D12 · 短期记忆靠 `checkpointer` + `thread_id`，裁剪自己写中间件

**理由**：

**`create_agent` 默认无状态。** 不传 `checkpointer` 时，两次 `invoke` 各是独立的 2 条消息，
第二次问「我叫什么」答「之前的对话中没有提到过」—— 这跟 D9 手写版一样，`messages` 是要自己递进去的。

**记忆不是模型的属性，是图的状态。** 加 `checkpointer=InMemorySaver()` 并在 `invoke` 里传
`config={"configurable": {"thread_id": "u1"}}` 之后，同一个 thread 的条数是 2 → 4 → 6 → 8，
第 4 轮能答出名字；换一个 `thread_id` 立刻回到 2 条。「记住谁」由 `thread_id` 决定，不由模型决定。

**框架不会替你省 token。** 默认全量塞进上下文，对话越长越贵越慢，裁剪必须自己写中间件。
实测的写法只有一种能真正减消息：`RemoveMessage(id=REMOVE_ALL_MESSAGES)` 先清空、再塞回去 ——
`messages` 是 append-only 的，直接 append 减不了任何东西。

**代价 / 坑**：

1. **裁剪窗口里装的是「历史 + 本轮问题」，不是「几轮对话」。** 第 4 轮进 `before_model` 时是
   **7 条**（u1, a1, u2, a2, u3, a3, u4），`msgs[-6:]` 从索引 1 开始 —— 丢的是 `u1`「我叫 Base」，
   保住的却是 `a1`「你好，Base！」。所以 `keep_last_n(6)` 能答出名字，**靠的是模型自己的回声，
   不是用户的原始陈述**。同配置我连跑四次，三次答「你叫 Base」、一次答「你没有告诉我」——
   这种记忆不稳定。
2. **`keep_last_n(5)` 就崩塌。** 窗口从索引 2 开始，连 `a1` 一起丢，模型答「我不知道你的名字，
   因为你还没有告诉我」—— 这句话在它的窗口里是**真的**，它没撒谎，只是看不见。
3. **「永远保留第一条 + 最近 n 条」是定点豁免，不是策略。** 它只钉住第 1 轮；关键信息出现在
   第 2 轮、第 3 轮照样丢。它好用的前提是「重要的事正好在开头」，而这个前提通常不成立。
4. **`n` 取大了会重复。** `msgs[0]` 已经在 `msgs[-n:]` 里时，拼起来是两条一样的消息。
   边界判断写 `len(msgs) <= n + 1` 就返回 `None`，把这种情况挡在外面。
5. **`InMemorySaver` 是进程内的。** 进程一退，上下文全没 —— 这是 D13 要解决的问题。

**什么时候换**：

跨进程 / 重启续聊 → 换成 SQLite 或 Postgres 的 checkpointer（D13）；
信息本身重要（用户身份、偏好、承诺过的事）→ 抽成结构化事实存进长期记忆，**别指望窗口**；
对话长、预算紧、又不能丢语义 → `SummarizationMiddleware`（一次 LLM 调用换一段压缩记忆，
代价是摘要会失真，且摘要本身要花钱）。

---

## D13 · 持久化落 SQLite checkpointer，不上 Postgres / Redis

**理由**：

**换一个构造参数就能验证核心命题。** `checkpointer=SqliteSaver(conn)` 顶替 `InMemorySaver()`，
其余代码一行不动，就能证明「关掉进程还记不记得」。Postgres / Redis 是同一个概念的不同后端，
多出来的是部署成本，不是理解成本。

**课程里 Docker + Postgres + DBeaver 那一段跳过。** 三个具体理由：Docker Desktop 在这台机器上
要开 WSL2/Hyper-V、装完要重启、占几个 G，为了一段可选演示吃掉 3 小时里的一大块；
DBeaver 只是「表里有什么」的可视化查看器，一条 `select count(*) from checkpoints` 就够；
而今天的验收标准本来就是「重启不丢上下文」，换个后端证明的是同一件事，成本高好几倍。

**代价**：

1. **单文件、单机、单用户、低并发。** 多个进程同时写同一个 `memory.db` 会锁表，
   所以只能本地开发 / 单实例演示。
2. **连接必须跨线程用。** `check_same_thread=False` 是硬性要求（LangGraph 把 `put` 丢到线程池），
   关掉之后并发控制就完全交给 SQLite 自己的锁 —— 出问题只会在运行期炸，编译期看不出来。
3. **没有可视化客户端。** 想看表结构、查某条 thread 的历史，得自己写 SQL。

**什么时候换**：

部署成多人用的服务、或要跨机器共享会话 → `PostgresSaver`（多一步 `.setup()` 建表）；
需要 TTL / 高频读写 → `RedisSaver`；
只是本地跑、验证概念 → SQLite 够用，别提前上重装备。

---

## D14 · `calc` 用 AST 白名单递归求值，不用 `eval`

**理由**：

**`eval` 执行的是代码，不是算式。** 调用链是「用户说话 → 模型生成工具参数 → 参数进入 `eval`」，
中间没有任何环节能保证参数只含数字和运算符。而这个进程里有 `.env`，
一句「帮我算 `__import__('os').environ`」就足够把 API key 打成回答。

**白名单比黑名单可靠。** `ast.parse` 不会拒绝任何语法合法的表达式，
所以判定的方式不是「识别坏东西」（永远列不全），而是**只承认三种节点**
——`Constant` / `BinOp` / `UnaryOp`，加 `+ - * /` 四个运算符，其余一律拒绝。
和 D14 `save_note` 里「先算落点再判边界」是同一个思路。

**失败要翻译成人话。** 工具返回「算不了：不支持的运算符：Pow」，模型能换写法或如实告知；
直接 `raise` 则会撞上 D11 的 `ToolRetryMiddleware`，白跑一次还污染上下文。

**代价**：

1. **表达能力受限。** `2**10`、`%`、`//` 全部被拒，要支持就得显式加 `ast.Pow` 等节点。
2. **要多写十几行。** 递归求值 + 运算符查表，比一行 `eval` 长得多，
   而且每加一种运算都要同时改「白名单」和「查表」两处。
3. **仍挡不住失控的计算量。** 白名单能挡代码执行，但 `9999999*9999999*...` 这类合法算式
   照样能吃掉 CPU/内存；真要做限流得另加长度或深度上限。

**什么时候换**：

永远不换回 `eval`。需要更强能力时（科学计算、单位换算），换成一个**专用库**
（如 `pint`、`sympy` 的受限求值接口），而不是放宽自己的白名单。

---

## D15 · 语料用影石 X4 官方在线手册（114 页中文 HTML），不用官网产品页

**理由**：

**业务相关性。** 这套语料的用途是练 RAG，但它的最终归宿是 D29 之后的项目、以及面试时能讲清楚的业务背景。
X4 是影石的主力全景机型，型号参数、存储兼容、防水维护这些问题，客服每天都在回。

**官网产品页抓不了，在线手册站能抓 —— 这是实测的，不是猜的。**
`insta360.com/cn/support/product-support?name=x6` 返回 200、104 KB，**可见文字 0 字**，
是前端动态渲染；`onlinemanual.insta360.com/x4/zh-cn/...` 是服务端渲染，单页正文 687–7454 字，
另有 `sitemap.xml` 列出 12,860 条 URL，可以按产品 + 语言精确取子集。
如果用产品页，D16 写加载器时才发现全是空壳，等于白白重来一次。

**规模刚好落在能测出召回率的区间。** 114 页：少于 20 页检索永远全命中、测不出召回；
多于 500 页 D19 建索引要等太久。单语言取子集也避免了「同内容中英双语」把页数灌水一倍。

**代价**：

1. **主题单一。** 114 页全是同一个产品的操作说明，测不出「多来源互相冲突」这类问题
   （比如两个文档对同一参数给出不同值）—— 那恰恰是真实企业知识库最常见的形态。
2. **页面偏短。** 正文中位数 1171 字，D17 的切分实验对比空间有限（大页面只有 7000 多字的那几页）。
3. **内容会漂移。** 手册随固件和产品迭代更新，`raw/` 又不入库，换台机器要重新抓一遍；
   引用具体参数时得注明抓取日期。
4. **只有中文。** 多语言检索、跨语言对齐这块完全测不到。

**什么时候换 / 补**：

D29 项目需要「多源冲突」或更长的时间跨度时，加第二套语料（官方 PDF 手册 + 帮助中心 FAQ，
同一参数在 PDF 与网页之间对比）；要做多语言检索时再拉 `en-us` 子集，但那时要按语言分开建索引，
不能混在一个库里。

---

## D16 · 明知官方写「should no longer be used」，今天还是用 `langchain-community`

**背景**：官方文档对这批加载器的原话是 ——

> `PyPDFLoader`, `PyMuPDFLoader`, `PDFMinerLoader`, and `PDFPlumberLoader` live in the unmaintained
> `langchain-community` package but **should no longer be used**. Prefer one of the partner packages above.

而今天的 `loaders.py`，`PyPDFLoader` 和 `BSHTMLLoader` 都从 `langchain_community.document_loaders` 导入。

**理由**：

**1. 先对齐课程，再谈迁移。**
P34 / P35 的代码就是 `langchain_community.document_loaders`。今天同时在学「加载器是什么」和「换一套包」，
两件事会互相遮住 —— 分不清是概念没懂还是 API 用错了。

**2. 替代品的成本不在这 3 小时里。**
Docling 要下版面分析模型；Unstructured 在 Windows 上要 poppler / libreoffice / tesseract，
`pip install "unstructured[md]"` 会拖进 45 个包（整个 spaCy 生态 + numba + llvmlite），150–250 MB，
还会顺手升级 `setuptools` / `certifi` —— 这台机器挂着 MITM 代理，底层包能不动就不动。
今天装完，「加载器概念」大概率一个字都没学到。

**3. 接口是 `BaseLoader` 定的，换包只改 import 一行。**
`load()` / `lazy_load()` / `Document(page_content, metadata)` 这套接口不随包变。
所以现在写的代码不是废的 —— 迁移时改的是名字，不是结构。

**代价**：

1. **每次运行顶部一条 `DeprecationWarning`**，`loaders.py` 第一行就是它。它不是报错，程序照跑。
2. **包不再修 bug。** 今天 `PyPDFLoader(..., extract_images=True)` 报 `No module named 'PIL'` ——
   可选依赖缺失这个问题，社区版不会有人改好。
3. **API 不统一。** `TextLoader` 叫 `encoding`，`BSHTMLLoader` 叫 `open_encoding`。
   这类历史遗留只会在迁移时被统一，现在只能一个个试。

**判断标准不是「官方说了什么」，是「迁移成本 vs 今天的学习目标」。**
官方那句是面向新项目的长期建议，不是今天的禁令。

**什么时候换**：

- 要处理**扫描版 PDF**（需要 OCR）时 → Docling
- 表格、多栏排版**还原不准**，影响检索质量时 → Docling / Unstructured
- 需要**按文档结构切分**（标题层级直接进 metadata）时 → 那时的问题已经转到切分器上了

---

## 模板（复制这一段用）

## D__ · （决定了什么）

**理由**：
**代价**：
**什么时候换**：

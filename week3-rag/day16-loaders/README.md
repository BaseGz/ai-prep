# D16 · 文档加载

> 目录 `week3-rag/day16-loaders/` ｜ 预计 3h ｜ 对应 2026-10-06（周二） ｜ 阶段：第 3 周 RAG 核心链路

## 一、今天学什么

| 类型 | 内容 | 时长 |
|---|---|---|
| 视频 | 《RAG 向量数据库全套》**P34 文件加载器（一）17:48** + **P35（二）25:05**（[BV1TKe3zmEQT](https://www.bilibili.com/video/BV1TKe3zmEQT)） | 43 分钟 |
| 文档 | 官方 [Document loader integrations](https://docs.langchain.com/oss/python/integrations/document_loaders)：`Interface` 小节 + Webpages/PDFs 两张表 + sunset 说明 | 20 分钟 |

> **计划表原写的「第 4 讲 文档的加载与切割 07:10」已作废**：它属于《大模型 RAG 入门到精通》`BV1hccSeJEUD`，
> 该 BV 号自 D15 起接口返回 `-404`（2026-11-21 复核仍为 404）；且同合集第 4 讲实际是「大模型微调流程 06:30」，与加载无关。
> 加载内容由 P34/P35 覆盖，共 42:53，比原计划省 7 分钟。P36「文本拆分器」是 D17 的内容，今天不看。

## 二、今天动手做什么

- [ ] 加载 3 种格式（PDF / HTML / Markdown），打印 Document 的正文和 metadata，看清元数据里有什么可用信息（70 分钟）
- [ ] 三处「你的活」：统计 PDF 空页 / 给每条补 `section` 字段 / 把 `load()` 换成 `lazy_load()`

依赖（已装好，换机器时用）：

```bash
.venv/Scripts/python.exe -m pip install langchain-community pypdf beautifulsoup4 lxml
```

> `langchain-community` 官方已标注 sunset、建议换 Docling / Unstructured。今天仍用它：
> 课程 API 就是它、替代品在 Windows 上要额外的系统依赖、而 `load()/lazy_load()` 接口换包不改。
> 代价：每次运行会打 `DeprecationWarning`，且不再修 bug。详细取舍见 `docs/decisions.md` 的 D16 一条。

## 三、今天提交什么

在 PyCharm 里分 **2 次** 提交（代码 / 文档）。Ctrl + K 打开提交窗口后，**记得取消勾选不属于本次提交的文件**：
`.env`、`.venv/`、`.idea/`、`__pycache__/`、`datasets/raw/` 下的原始文件。

### 第 1 条：代码

```text
feat(day16): 三种格式统一成 Document，先看清 metadata 再谈切分

现象：
114 页 HTML 加载成 114 个 Document、0.42 秒；PDF 42 页变成 42 条，首页只有 24 字；
HTML 每页开头约 100 字是「搜索您的问题 简体中文 English 日本語」这类导航，不是正文。

我以为：
加载器的作用是「把正文抽出来」，metadata 只是附带信息。

做法：
分别用 PyPDFLoader / BSHTMLLoader / TextLoader 加载三类文件，逐条打印 page_content 长度与 metadata；
统计 PDF 里正文少于 100 字的页；给每个 Document 补 section 字段（源路径第一段），再按栏目计数。

结论：
加载器不判断正文，它只做两件事 —— 决定切分单位（PDF 按页、HTML/MD 按文件）+ 把文件信息抄进 metadata；
三种格式的 metadata 字段数是 16 / 2 / 1，这个差别直接决定了后面能不能做过滤。
噪声和空页不会自动消失，得自己处理。
```

勾选：`week3-rag/day16-loaders/loaders.py`、`week3-rag/day16-loaders/README.md`

### 第 2 条：文档

```text
docs(day16): 记下「官方让你别用 community，我今天还是用了」这个取舍

现象：
官方文档明写 PyPDFLoader 等已随 langchain-community sunset、should no longer be used，
建议换 Docling / Unstructured 这类合作方包。

我以为：
文档说不要用，就应该找替代品。

做法：
先对齐课程 API（P34/P35 讲的就是 community），只装 pypdf / bs4 / lxml 四个轻依赖；
把迁移代价记进 decisions：load() / lazy_load() 接口由 BaseLoader 定义，换包只改 import 一行。

结论：
文档的「不要用」是面向新项目的长期建议，不是今天的禁令；
判断标准是「迁移成本 vs 今天的学习目标」，而不是「官方说了什么」。
代价也记清楚：每次运行都打 DeprecationWarning，而且这个包不再修 bug。
```

勾选：`docs/journal/2026-10-06.md`、`docs/decisions.md`、`docs/progress.md`、`docs/daily/D16-文档加载.html`

## 四、今天必须留下的

- [ ] 代码当天跑通
- [ ] 日志 → `docs/journal/2026-10-06.md`
- [ ] 一句话结论：________________________________

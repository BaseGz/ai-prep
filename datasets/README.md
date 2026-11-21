# 语料

## 这是什么

RAG 练习用的真实语料。**从 D15 起所有练习都用它**，D29 之后它直接变成项目的数据集。
面试时这套语料就是我的项目背景。

## 规则

1. 原始大文件放 `datasets/raw/`，已 gitignore，**不入库**
2. 清洗后的数据（小体积）可以入库
3. 每个数据集在这里写清：来源 / 规模 / 怎么拿到 / 字段含义

## 数据集清单

| 名称 | 来源 | 规模 | 字段 | 加入日期 |
|---|---|---|---|---|
| `x4-manual`（影石 X4 官方在线手册，中文） | `onlinemanual.insta360.com/x4/zh-cn/`（公开，服务端渲染，URL 取自官方 `sitemap.xml`） | **114 个 HTML 页面 / 3.4 MB**；正文中位数 1171 字，最长 7454 字 | 页面路径 / 标题 / 正文文本（原始 HTML 保留 `<script>`、导航等噪声，留给 D16 的加载器处理） | 2026-11-19 |
| `x4-manual-pdf`（同款官方用户手册 PDF） | `res.insta360.com/static/.../X4_UserManual_CN.pdf`（公开） | **1 个 PDF / 3.2 MB / 42 页**；每页正文中位 237 字 | 逐页文本 + PDF 内嵌元数据（作者、创建时间、总页数）；与 HTML 版同一份内容，用于对照两种加载器的粒度差异 | 2026-11-21 |

目录分布：`operating_tutorials` 47 / `troubleshooting` 32 / `camera` 25 / `specs` 7 / `accessories-kit` 3。

> 同一份手册同时留 HTML 与 PDF：HTML 一页一个 Document（114 条），PDF 一页一个 Document（42 条）——
> 同样的内容，加载器不同，切分粒度和 metadata 完全不同。这个对照是 D16 的核心观察。

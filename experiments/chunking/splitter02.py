from langchain_text_splitters import RecursiveCharacterTextSplitter, HTMLHeaderTextSplitter

with open("x4-faq.html", encoding = "utf-8") as f:
    text_data = f.read()


# 定一个章节的标签
label_split = [ # 定义章节的结构
    # (标签, 章节名称)
    ('h1', '一级标题'),
    ('h2', '二级标题'),
    ('h3', '三级标题'),
]
# 创建切割器 (HTML)
html_splitter = HTMLHeaderTextSplitter(label_split)
# 切割文本 (HTML) -> list
docs_list = html_splitter.split_text(text_data)

print('切割之后的结果:-------------------------------------------------')
print(docs_list)

# html_splitter = HTMLHeaderTextSplitter(label_split)
# docs_list_2 = html_splitter.split_text_from_url('https://plato.stanford.edu/entries/goedel/')
#
# print('切割之后的结果:-------------------------------------------------')
# print(docs_list_2[0])
# print("=" * 10)
# print(f"总共有多少个章节:{len(docs_list_2)}")

# 由于章节内容太多，可以切两次

# 递归切割器
# 默认分隔符： ["\n\n", "\n", " ", ""]
text_splitter = RecursiveCharacterTextSplitter(
    # 每一块最大的大小，其中大小由length_function决定
    chunk_size=100,
    # 递归的重叠数量
    chunk_overlap=20,
    # 确定块大小的函数
    length_function=len,
    # 是否支持正则表达式
    is_separator_regex=False,
    # 分隔符
    separators=["\n\n", "\n", "。","?","!", "，"," "]
)

docs2_list = text_splitter.split_documents(docs_list)
print('切割之后的结果:-------------------------------------------------')
print(docs2_list)


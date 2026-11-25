from langchain_text_splitters import MarkdownHeaderTextSplitter

with open('x4-shooting.md', encoding= 'utf-8') as f:
    text_data = f.read()

label_split =[
    ('#','一级标题'),
    ('##','二级标题'),
    ('###','三级标题')
]

markdown_splitter = MarkdownHeaderTextSplitter(label_split, strip_headers=True) # 是否在内容中删除章节标题

docs = markdown_splitter.split_text(text_data)

print(docs)

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


with open('git-guide.txt', encoding='utf-8') as f:
    git_data = f.read()
docs = [Document(page_content=git_data, metadata={"source": "git-guide.txt"})]

SEP = ["\n\n", "\n", "。", "，", " "]
for size in (200, 300):
    text_splitter_1 = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=0,
    )
    text_splitter_2 = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=0,
        separators=SEP
    )
    for label, sp in (("默认", text_splitter_1), ("加句号", text_splitter_2)):
        chunks_list = sp.split_documents(docs)
        print(f"size:{size}, 标签:{label}, 块数：{len(chunks_list)}, 各块长度列表:{[len(c.page_content) for c in chunks_list]}")


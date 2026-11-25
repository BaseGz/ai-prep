from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


with open('git-guide.txt', encoding='utf-8') as f:
    git_data = f.read()
docs = Document(page_content=git_data, metadata={"source": "git-guide.txt"})

SEP = ["\n\n", "\n", "。", "，", " "]
sp = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=0,
    separators=SEP
)
sp3 = RecursiveCharacterTextSplitter(chunk_size=300,
                                     chunk_overlap=0,
                                     separators=SEP,
                                     add_start_index=True
                                     )


a = sp.split_text(git_data)        # 入口一：喂字符串
b = sp.split_documents([docs])      # 入口二：喂 Document 列表
c3 = sp3.split_documents([docs])
print([c.metadata["start_index"] for c in c3[:5]])
print(len(a), type(a[0]))
print(len(b), type(b[0]), b[0].metadata)

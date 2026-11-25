import tiktoken
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

enc = tiktoken.get_encoding("cl100k_base")
with open('git-guide.txt', encoding='utf-8') as f:
    git_data = f.read()
docs = Document(page_content=git_data, metadata={"source": "git-guide.txt"}) # str

sp = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base", chunk_size=256, chunk_overlap=32)
chunks = sp.split_documents([docs])   # 注意形状
print(len(git_data), len(enc.encode(git_data)))

print([len(enc.encode(c.page_content)) for c in chunks])

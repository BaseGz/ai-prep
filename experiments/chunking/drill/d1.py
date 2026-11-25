from langchain_text_splitters import RecursiveCharacterTextSplitter


with open('git-guide.txt', encoding='utf-8') as f:
    git_data = f.read()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=0
)
chunks_list = text_splitter.create_documents([git_data])

print(f"全文多少字:{len(git_data)}")
print(f"切出了几块：{len(chunks_list)}")

one_list = [len(c.page_content) for c in chunks_list]
print(f"每块多少个字：{one_list}")






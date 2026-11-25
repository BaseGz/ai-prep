from langchain_text_splitters import RecursiveCharacterTextSplitter


with open('git-guide.txt', encoding='utf-8') as f:
    git_data = f.read()

print(f"全文多少字:{len(git_data)}\n")

for size in (100, 200, 500, 1000):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=0
    )
    chunks_list = text_splitter.create_documents([git_data])
    one_list = [len(c.page_content) for c in chunks_list]
    print(f"size={size:<5} -> {len(chunks_list):>2} 块 | 最短 {min(one_list):>3} | 最长 {max(one_list):>3}")
    print(f"           每块字数：{one_list}\n")

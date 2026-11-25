from langchain_text_splitters import RecursiveCharacterTextSplitter


with open('git-guide.txt', encoding='utf-8') as f:
    git_data = f.read()

ENDS = ("。", "！", "？", "；", "\n", "”", "」")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=0,

)
chunks_list = text_splitter.create_documents([git_data])

print(f"全文多少字:{len(git_data)}")
print(f"切出了几块：{len(chunks_list)}")

one_list = [len(c.page_content) for c in chunks_list]
print(f"每块多少个字：{one_list}")

# enumerate接住两个值（ 序号 ， 元素 ）
for i, c in enumerate(chunks_list):
    text = c.page_content
    print(f"#{i} 长{len(text)} 尾 {text[-20:]!r}")         # 7 块都打
    if i < len(chunks_list) - 1:
        print(f"          下头 {chunks_list[i + 1].page_content[:20]!r}")   # 只有前 6 块
cut = [c for c in chunks_list[:-1] if not c.page_content.rstrip().endswith(ENDS)]
print(f"\n被切断 {len(cut)} / {len(chunks_list) - 1}")



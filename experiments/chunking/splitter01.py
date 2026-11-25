# 读取文件
from langchain_classic import text_splitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

with open('x4-guide.txt' , encoding = 'utf-8') as f:
    # 读出文件内容
    text_data = f.read()


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
# 切割文本 ( 只能接 document ) -> 返回的是列表
# chunks_list = text_splitter.split_documents([text_data])
# 切割文本 ( 接一个字符串 ) -> 返回的是列表
chunks_list = text_splitter.create_documents([text_data])

print(len(chunks_list))

print(chunks_list[0])
print("==================================================")
print(chunks_list[1])
print(chunks_list[2])
# UnstructuredMarkdownLoader 需要 unstructured 包（45 个依赖），今天不安装。
# 想让标题进 metadata 改用 D17 的 MarkdownHeaderTextSplitter。
from langchain_community.document_loaders import UnstructuredMarkdownLoader

# 整个md文件是一个document
# loader = UnstructuredMarkdownLoader(file_path='../x4-quickstart.md')
# 分给多个document
loader = UnstructuredMarkdownLoader(file_path='../x4-quickstart.md', mode = 'elements')

data = loader.load()
# data = loader.load_and_split()
print(data)


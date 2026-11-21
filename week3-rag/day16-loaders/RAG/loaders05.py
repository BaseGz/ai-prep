from langchain_community.document_loaders import PyPDFLoader

# loader = PyPDFLoader(file_path='../X4_UserManual_CN.pdf')
loader = PyPDFLoader(file_path='../X4_UserManual_CN.pdf') # extract_images=True

# 每一页对应一个document
data = loader.load()
print(data)

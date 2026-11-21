from langchain_community.document_loaders import CSVLoader

loader = CSVLoader(file_path='../x4-specs.csv', encoding='utf-8')

data = loader.load()

for record in data[:2]:
    print(record)
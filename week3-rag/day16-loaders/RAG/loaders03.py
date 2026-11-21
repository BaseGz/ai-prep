from langchain_community.document_loaders import JSONLoader

# loader = JSONLoader(
#     file_path = '../x4-specs.json',
#     jq_schema = '.specs[].name',
#     text_content=False
# )

# loader = JSONLoader(
#     file_path = '../x4-specs.json',
#     jq_schema = '.specs[] | {id, name}',
#     content_key='name',
#     text_content=False
# )

def create_metadata(record: dict, metadata: dict) -> dict:
    metadata['id'] = record.get('id')
    metadata['name'] = record.get('name')
    metadata['value'] = record.get('value')
    return metadata

loader = JSONLoader(
    file_path = '../x4-specs.json',
    jq_schema = '.specs[]',
    metadata_func=create_metadata,
    content_key='name',
    text_content=False
)

data = loader.load()
print(data)


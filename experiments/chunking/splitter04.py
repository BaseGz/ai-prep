import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
""""
百分位数：侧重数据的相对位置，适合根据数据分布的整体情况来决定分割点的场景
text_splitter = SemanticChunker(OpenAIEmbeddings(), breakpoint_threshold_type="percentile")

标准差：侧重数据的离散程度，适合波动性较大的数据分析
text_splitter = SemanticChunker(OpenAIEmbeddings(), breakpoint_threshold_type=""standard_deviation")

四分位距：通过识别数据的中心趋势和离散范围来确定异常值或分割点，适用于需要去除极端值或识别主体数据集的场合
text_splitter = SemanticChunker(OpenAIEmbeddings(), breakpoint_threshold_type="interquartile")
"""
with open('semantic-mix.txt', encoding='utf-8') as f:
    text_data = f.read()

load_dotenv(override=True)
embeddings = OpenAIEmbeddings(
    model="embedding-3",
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4",
    check_embedding_ctx_length=False,
)

# 创建分割对象（百分位数）
text_splitter = SemanticChunker(
    embeddings,
    breakpoint_threshold_type='percentile',
    breakpoint_threshold_amount=80,                                  # ③ 新增
    sentence_split_regex=r"(?<=[。！？!?])\s*(?=\S)",                # ④ 新增
)
docs_list = text_splitter.create_documents([text_data])
print(docs_list[0])      # ⑤ 换掉原来的 print

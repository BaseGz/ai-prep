"""D6 · 结构化输出：从一句话里抽出结构化线索

要验证三件事：
① Pydantic schema 怎么定义（字段名 + description 就是给模型的说明书）
② with_structured_output() 返回什么、拿到的东西怎么用
③ 抽出来的结果怎么直接驱动代码分支 —— 不再靠字符串匹配
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
API_KEY = os.getenv("DEEPSEEK_API_KEY")


class Lead(BaseModel):
    """从一句话里抽取出的客户线索。"""

    name: str = Field(description="客户姓名")
    company: str = Field(description="公司名称；原文没提到就填「未知」")
    need: str = Field(description="客户需求，用不超过 10 个字概括")
    urgency: Literal["高", "中", "低"] = Field(description="紧急程度")


def build_extractor():
    """建模型 → 把 schema 挂上去 → 返回一个能 invoke 的对象。"""
    model = init_chat_model(
        MODEL,
        model_provider="deepseek",
        base_url=BASE_URL,
        api_key=API_KEY,
        temperature=0,
    )
    return model.with_structured_output(Lead)


def route(lead: Lead) -> str:
    """拿到结构化结果之后，代码直接分支 —— 这就是今天要带走的东西。"""
    if lead.urgency == "高":
        return f"【立即跟进】{lead.name}（{lead.company}）→ 转销售主管"
    if lead.urgency == "低":
        return f"【进池子】{lead.name}（{lead.company}）→ 排进周报"
    return f"【今日回复】{lead.name}（{lead.company}）"


def main() -> None:
    extractor = build_extractor()
    print("① 返回对象类型：", type(extractor).__name__)

    text = "你好，我是远景科技的王磊，我们下个月要上线智能客服，想聊聊你们的方案，越快越好。"
    lead = extractor.invoke(text)

    print("② 抽取结果：", lead)
    print("   类型：", type(lead).__name__)
    print("③ 逐个字段点出来：")
    for k, v in lead.model_dump().items():
        print(f"   {k:<10} = {v}")
    print("④ 代码直接分支（没有一句字符串匹配）：", route(lead))


if __name__ == "__main__":
    main()

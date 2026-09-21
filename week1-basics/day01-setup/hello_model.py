"""D1 · 第一次模型调用（最小可运行）

D1 要亲手验证的就一件事：**一行初始化模型，就能拿到回复。**

默认走 OpenAI 兼容协议（langchain-openai）。这个选择的直接好处是：
同一份代码，只改 base_url + 模型名，就能切到通义 / 智谱 / OpenRouter。

运行前确认仓库根目录 .env 里 DEEPSEEK_API_KEY 有值；先跑 env_check.py 更省事。
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
API_KEY = os.getenv("DEEPSEEK_API_KEY")


def build_model():
    """初始化模型。D2 会拿这一段去换 3 家供应商，改的只有两行。"""
    if not API_KEY:
        raise SystemExit(
            "没读到 DEEPSEEK_API_KEY。检查仓库根目录有没有 .env，以及里面有没有填值。"
        )
    return init_chat_model(
        MODEL,
        model_provider="openai",  # 走 OpenAI 兼容协议
        base_url=BASE_URL,
        api_key=API_KEY,
        temperature=0,
    )


def to_text(message) -> str:
    """LangChain 1.x 的 content 可能是 str，也可能是「内容块」列表，两种都接住。"""
    content = message.content
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, dict):
            parts.append(block.get("text", ""))
        else:
            parts.append(str(block))
    return "".join(parts)


def main() -> None:
    llm = build_model()

    print("=" * 60)
    print(f"模型    ：{MODEL}")
    print(f"base_url：{BASE_URL}")
    print("=" * 60)

    # 三种消息角色：system 定规矩，human 是提问。D4 会正式讲消息体系
    messages = [
        ("system", "你是一个说话极简的助手，每次回答不超过 20 个字。"),
        ("human", "用一句话确认：链路已经通了。"),
    ]

    reply = llm.invoke(messages)

    print("回复：", to_text(reply))
    print("token：", reply.usage_metadata)  # 输入/输出/总 token，D28 算成本要用
    print("模型名（服务端返回）：", reply.response_metadata.get("model_name"))

    print("-" * 60)
    print("换供应商只改 2 行（MODEL + BASE_URL），别的代码一个字不动。")
    print("通义  ：qwen-plus      https://dashscope.aliyuncs.com/compatible-mode/v1")
    print("智谱  ：glm-4-flash    https://open.bigmodel.cn/api/paas/v4")
    print("-" * 60)


# ——— 等价写法（D2 会让用户自己对比，这里先留个参照）———
# 官方包接入 DeepSeek 是另一个包、另一个类，效果一样：
#
#   from langchain_deepseek import ChatDeepSeek
#   llm = ChatDeepSeek(model="deepseek-chat", temperature=0)
#
# 差别只在：官方包帮你把 base_url 写好了，兼容协议这条路则要自己填。
# 记这一句就够：base_url 一改就能换供应商，是框架给的第一个真实价值。


if __name__ == "__main__":
    main()

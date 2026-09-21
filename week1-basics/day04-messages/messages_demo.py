"""D4 · 手动维护 messages 数组，做 3 轮对话

今天只有一个目标：**亲手验证「上下文」到底是什么。**

硬性约束：全程不许用任何记忆类 —— 不用 InMemorySaver、不用
RunnableWithMessageHistory、不用 create_agent。消息历史就是一个普通的
Python list，你自己 append，每轮把整份发出去。

填完三处 TODO 后跑，观察三件事：
  1. 第 2 轮起，模型还记不记得第 1 轮告诉它的信息？
  2. 把历史清空再问同一个问题，它还答得出来吗？（这条最关键）
  3. token 数是不是逐轮递增？

对应视频：尚硅谷 P25 / P26 / P27 / P28
（P30 讲的 ChatPromptTemplate 是同一件事的另一种写法，明天 D5 会用到）
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
API_KEY = os.getenv("DEEPSEEK_API_KEY")

SYSTEM_PROMPT = "你是一个说话极简的助手，每次回答不超过 30 个字。"


def build_model():
    if not API_KEY:
        raise SystemExit("没读到 DEEPSEEK_API_KEY，先确认仓库根目录 .env 有值。")
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
    return "".join(
        block.get("text", "") if isinstance(block, dict) else str(block)
        for block in (content or [])
    )


def ask(llm, history: list, question: str):
    """★ 今天的内容全在这三行里。

    append 进去 → 整份发出去 → 把回复也 append 回来。
    没有任何魔法：「记忆」不是模型的能力，是调用方每次都把历史重新发一遍。
    """
    history.append(HumanMessage(question))      # ① 用户这句话进历史
    reply = llm.invoke(history)                 # ② 把「到目前为止的全部历史」发出去
    history.append(AIMessage(to_text(reply)))   # ③ 模型的回答也进历史，下一轮才「记得」
    return reply


def main() -> None:
    llm = build_model()

    # 这就是全部的「上下文」：一个普通的 list，第一项是 system
    history: list = [SystemMessage(SYSTEM_PROMPT)]

    # TODO ① 设计 3 个有依赖关系的问题，填进下面这个列表
    #   要求：第 1 轮给模型一个信息，第 2 轮问它记不记得，第 3 轮基于前两轮追问。
    #   例：1) 我叫 Base，今年大三  2) 我叫什么？  3) 那我该找什么阶段的实习？
    questions: list[str] = [
        "我叫 Base，今年大三",
        "我叫什么？",
        "那我该找什么阶段的实习？",
    ]

    total_tokens = 0  # 累计 token：用来看「历史越长，每轮越贵」

    for i, q in enumerate(questions, 1):
        print(f"\n{'=' * 55}\n第 {i} 轮")
        print(f"我  ：{q}")
        reply = ask(llm, history, q)
        print(f"AI  ：{to_text(reply)}")
        print(f"本轮 token：{reply.usage_metadata}")
        # TODO ② 打印当前 history 的条数和累计 token，观察它怎么随轮数涨
        #   注意：ask() 已经把本轮的「我」和「AI」都追加进 history 了，
        #        所以第 1 轮跑完就是 3 条（system + human + ai）
        total_tokens += (reply.usage_metadata or {}).get("total_tokens", 0)
        print("history 里现在是：" + " → ".join(type(m).__name__ for m in history))
        print(f"history 长度：{len(history)} 条    累计 token：{total_tokens}")

    # TODO ③ 还原本：新开一个只留 system 的空历史，把同一个问题再问一遍
    #   想验证什么：模型自己并不记得任何东西 —— 拿掉 history，它就失忆
    #   提示：history_fresh = [SystemMessage(SYSTEM_PROMPT)]
    #        再 ask(llm, history_fresh, "我叫什么？")，和第 2 轮的回答对比
    print(f"\n{'=' * 55}\n【对照组】新开一个只有 system 的空历史\n")

    history_fresh: list = [SystemMessage(SYSTEM_PROMPT)]
    reply_fresh = ask(llm, history_fresh, "我叫什么？")

    print(f"AI（无历史）：{to_text(reply_fresh)}")
    print(f"本轮 token：{reply_fresh.usage_metadata}")
    print("\n" + "=" * 55)
    print("对照完这两次回答，你就知道「上下文」到底存在哪里了。")


if __name__ == "__main__":
    main()

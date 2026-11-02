"""D12 · 上下文与记忆：短期记忆 + 裁剪策略"""
import sys
from pathlib import Path

DAY09 = Path(__file__).resolve().parents[1] / "day09-handwritten-agent"
sys.path.insert(0, str(DAY09))

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import before_model
from langchain_core.messages import RemoveMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import REMOVE_ALL_MESSAGES

from agent_loop import model

QUESTIONS = ["我叫 Base", "我在学 LangChain", "我在准备实习", "我叫什么？"]
SYSTEM = "你是一个简洁的助手，回答不超过两句话。"


def chat(agent, thread_id, questions):
    """在同一个 thread 里连问几句，打印每句的答复和累积的消息条数"""
    cfg = {"configurable": {"thread_id": thread_id}}
    for q in questions:
        r = agent.invoke({"messages": [{"role": "user", "content": q}]}, cfg)
        print(f"  问「{q}」")
        print(f"  答：{r['messages'][-1].content[:60]}")
        print(f"  messages 条数 = {len(r['messages'])}")
    print()


def keep_last_n(n):
    """只保留最近 n 条消息的中间件"""

    @before_model
    def trim(state: AgentState, runtime) -> dict | None:
        msgs = state["messages"]
        if len(msgs) <= n:
            return None
        return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *msgs[-n:]]}

    return trim


def keep_first_and_last_n(n):
    """永远保留第一条 + 最近 n 条（官方 trim 例子的写法）"""

    @before_model
    def trim(state: AgentState, runtime) -> dict | None:
        msgs = state["messages"]
        if len(msgs) <= n + 1:          # 再裁也不会变少，直接跳过
            return None
        return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), msgs[0], *msgs[-n:]]}

    return trim


if __name__ == "__main__":
    print("=== 实验 1：没有 checkpointer ===")
    a1 = create_agent(model, [], system_prompt=SYSTEM)
    for q in ["我叫 Base", "我叫什么？"]:
        r = a1.invoke({"messages": [{"role": "user", "content": q}]})
        print(f"  问「{q}」-> {r['messages'][-1].content[:50]} | messages={len(r['messages'])}")

    print()
    print("=== 实验 2：checkpointer + 同一个 thread_id ===")
    a2 = create_agent(model, [], system_prompt=SYSTEM, checkpointer=InMemorySaver())
    chat(a2, "u1", QUESTIONS)

    print("=== 实验 3：换一个 thread_id 问同样的话 ===")
    chat(a2, "u2", ["我叫什么？"])

    print("=== 实验 4：裁剪到最近 5 条 ===")
    a3 = create_agent(
        model, [], system_prompt=SYSTEM,
        middleware=[keep_last_n(5)], checkpointer=InMemorySaver(),
    )
    chat(a3, "t1", QUESTIONS)

    print("=== 实验 5：裁剪到最近 6 条 ===")
    a4 = create_agent(
        model, [], system_prompt=SYSTEM,
        middleware=[keep_last_n(6)], checkpointer=InMemorySaver(),
    )
    chat(a4, "t2", QUESTIONS)

    print("=== 实验 6（你的活 ②）：保留第一条 + 最近 4 条 ===")
    a5 = create_agent(
        model, [], system_prompt=SYSTEM,
        middleware=[keep_first_and_last_n(4)], checkpointer=InMemorySaver(),
    )
    chat(a5, "t3", QUESTIONS)

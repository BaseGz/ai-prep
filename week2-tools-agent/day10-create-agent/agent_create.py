"""D10 · 用 create_agent 重建 D9 的 Agent"""
import inspect
import sys
from pathlib import Path

DAY09 = Path(__file__).resolve().parents[1] / "day09-handwritten-agent"
sys.path.insert(0, str(DAY09))

from langchain.agents import create_agent
from agent_loop import find_order, track_package, model

QUESTION = "尾号 8899 名下两单的物流都查一下"


def show(result):
    msgs = result["messages"]
    print("返回的键：", list(result.keys()))
    print("消息条数：", len(msgs))
    for i, m in enumerate(msgs, 1):
        calls = [c["name"] for c in getattr(m, "tool_calls", []) or []]
        head = str(m.content).replace("\n", " ")[:36]
        print(f"{i}. {type(m).__name__} | 调用 {calls or '-'} | {head}")


def main():
    print(inspect.signature(create_agent))
    agent = create_agent(
        model,
        [find_order, track_package],
        system_prompt="你是一个物流智能查询助手",
        name="logistics_assistant",
    )
    print("返回的对象类型：", type(agent).__name__)
    result = agent.invoke({"messages": [{"role": "user", "content": QUESTION}]})
    show(result)
    print(result["messages"][-1].content)



if __name__ == "__main__":
    main()

"""D14 · 多功能智能助手 v0.2：工具 + 记忆 + 流式

这份是骨架：外壳（CLI / 流式 / SQLite 记忆 / 工具注册）已经写好，
"""
import sqlite3
import sys
from pathlib import Path

DAY09 = Path(__file__).resolve().parents[1] / "day09-handwritten-agent"
sys.path.insert(0, str(DAY09))

from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk
from langchain_core.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver

from agent_loop import find_order, model, track_package

DB = Path(__file__).with_name("assistant.db")
THREAD = "cli"

SYSTEM = """你是影石的内部助手，能查订单、查物流、算数、记笔记。
回答简洁；需要数据时必须调工具，不要凭记忆编造。"""


@tool(parse_docstring=True)
def calc(expression: str) -> str:
    """
    计算一个四则运算表达式

    Args:
        expression: 只含数字和 + - * / ( ) 的表达式，例如 (12+8)*3
    """
    # TODO 1（你）: 先写 return str(eval(expression)) 跑通，
    #               再换成 ast 白名单（那时自己加 import ast / operator）
    raise NotImplementedError("calc 还没写")


@tool(parse_docstring=True)
def save_note(title: str, content: str) -> str:
    """把一段内容记成笔记文件

    Args:
        title: 笔记标题，会用作文件名
        content: 笔记正文
    """
    # 1. 锚点
    NOTES_DIR = Path(__file__).with_name("notes")

    # 2. 清洗：非法字符换成 _
    result = ""
    for ch in title:
        if ch.isalnum() or ch in ["-", "_", " "]:
            result += ch
        else:
            result += "_"
    name = result

    # 3. 收尾：去掉尾部的空格和句点
    name = name.strip("_ .")      # 一个字符串，里面装三个字符
    # 4. 兜底：没有实际内容 → 默认名
    #    判据不是 not name，是「去掉 _ 和空格后还剩不剩」
    #    保留设备名也在这里一并处理
    if not name:
        name = "未命名-笔记"
    RESERVED = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}
    if Path(name).stem.upper() in RESERVED:
        name = f"note-{name}"

    # 5. 限长：截到 80
    name = name[:80]
    # 6. 拼 + 解析（要加 .md 就在这一步加，三处保持一致）
    p = (NOTES_DIR / f"{name}.md").resolve()

    # 7. 断言
    assert p.parent == NOTES_DIR.resolve(), f"越界了: {p}"

    # 8. 落盘 + 回执
    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    p.write_text(content, encoding="utf-8")

    return f"已写入 {p.name}（{len(content)} 字）"


TOOLS = [find_order, track_package, calc, save_note]


def build():
    conn = sqlite3.connect(DB, check_same_thread=False)
    agent = create_agent(
        model, TOOLS, system_prompt=SYSTEM, checkpointer=SqliteSaver(conn)
    )
    return agent, conn


def main():
    agent, conn = build()
    cfg = {"configurable":
               {"thread_id": THREAD}}
    print("助手已启动（/exit 退出）")
    while True:
        q = input("\n你> ").strip()
        if q in {"/exit", "/quit"}:
            break
        if not q:
            continue
        print("助手> ", end="", flush=True)
        for chunk, _meta in agent.stream(
            {"messages": [{"role": "user", "content": q}]},
            cfg,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                print(chunk.content, end="", flush=True)
        print()
    conn.close()


if __name__ == "__main__":
    main()

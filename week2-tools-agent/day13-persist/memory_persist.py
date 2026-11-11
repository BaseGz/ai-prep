"""D13 · 记忆持久化：SQLite checkpointer，重启不丢上下文"""
import sqlite3
import sys
from pathlib import Path

DAY09 = Path(__file__).resolve().parents[1] / "day09-handwritten-agent"
sys.path.insert(0, str(DAY09))

from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from agent_loop import model

DB = Path(__file__).with_name("memory.db")
THREAD = "u1"
SYSTEM = "你是一个简洁的助手，回答不超过两句话。"


def build():
    """实验：工具列表里塞一个 find_order，看 super-step 怎么变多"""
    conn = sqlite3.connect(DB, check_same_thread=False)
    agent = create_agent(model, [], system_prompt=SYSTEM, checkpointer=SqliteSaver(conn))
    return agent, conn


def show_tables(conn):
    """直接查库，眼见为实"""
    names = [r[0] for r in conn.execute(
        "select name from sqlite_master where type='table' order by name")]
    print("  库里的表：", names)
    for t in names:
        n = conn.execute(f"select count(*) from {t}").fetchone()[0]
        print(f"    {t}: {n} 行")


def main():
    size_before = DB.stat().st_size if DB.exists() else 0
    agent, conn = build()
    cfg = {"configurable": {"thread_id": THREAD}}

    snap = agent.get_state(cfg)
    history = list(agent.get_state_history(cfg))
    msgs = snap.values.get("messages", []) or []
    print(f"[启动] 数据库 {DB.name} 大小 {size_before} 字节")
    print(f"[启动] thread={THREAD} 已有 {len(msgs)} 条消息，历史 checkpoint {len(history)} 个")

    if not msgs:
        print("[第一次运行] 库里是空的 —— 先建立记忆")
        r = agent.invoke({"messages": [{"role": "user", "content": "我叫 Base，我在准备 AI 实习"}]}, cfg)
    else:
        print("[第二次运行] 新进程，库里已有记录 —— 直接验证它记不记得")
        r = agent.invoke({"messages": [{"role": "user", "content": "我叫什么？我在准备什么？"}]}, cfg)

    print("  答：", str(r["messages"][-1].content)[:80])
    print(f"  本轮结束后 {len(r['messages'])} 条")

    snap2 = agent.get_state(cfg)
    print(f"[结束] 库里 {len(snap2.values['messages'])} 条消息，"
          f"checkpoint {len(list(agent.get_state_history(cfg)))} 个，"
          f"文件 {DB.stat().st_size} 字节")
    show_tables(conn)
    conn.close()


if __name__ == "__main__":
    main()

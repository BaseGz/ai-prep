"""D11 · Agent 进阶用法：4 个工具 + 结构化输出 + 错误处理"""
import sys
from pathlib import Path

DAY09 = Path(__file__).resolve().parents[1] / "day09-handwritten-agent"
sys.path.insert(0, str(DAY09))

from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from agent_loop import find_order, track_package, model

MOCK_COUPONS = {
    "8899": ["满 100 减 15（有效至 2026-11-30）", "免运费券 ×1"],
    "6666": [],
}


@tool
def query_coupon(phone_tail: str) -> str:
    """查询某个手机号尾号名下可用的优惠券。

    Args:
        phone_tail: 手机号后四位，例如 8899
    """
    coupons = MOCK_COUPONS.get(phone_tail)
    if coupons is None:
        return f"没有找到尾号 {phone_tail} 的账户"
    if not coupons:
        return f"尾号 {phone_tail} 名下暂无可用优惠券"
    return "；".join(coupons)


@tool
def query_refund(order_id: str) -> str:
    """查询某个订单的退款进度（本工具故意抛异常，用来演示错误处理）。

    Args:
        order_id: 订单号，例如 ORD-20261015-001
    """
    raise RuntimeError("退款服务暂时不可用（下游 503）")


class OrderAnswer(BaseModel):
    """订单状态的结构化结果"""

    order_id: str = Field(description="订单号")
    status: str = Field(description="当前状态")
    summary: str = Field(description="一句话总结，不超过 30 字")


def build_agent(with_retry: bool = False):
    middleware = [ToolRetryMiddleware(max_retries=1, initial_delay=0.1)] if with_retry else []
    return create_agent(
        model,
        [find_order, track_package, query_coupon, query_refund],
        system_prompt="你是一个物流智能查询助手，如果某个工具失败，先尝试用其它工具回答，最后说明哪部分没查到。",
        response_format=OrderAnswer,
        middleware=middleware,
    )


def ask(agent, question):
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    print("消息条数：", len(result["messages"]))
    for i, m in enumerate(result["messages"], 1):
        calls = [c["name"] for c in getattr(m, "tool_calls", []) or []]
        print(f"{i}. {type(m).__name__} 调用={calls or '-'} | {str(m.content)[:58]}")
    print("结构化结果：", result.get("structured_response"))
    return result


if __name__ == "__main__":
    print("=== 实验 1：4 个工具 + 结构化输出 ===")
    ask(build_agent(), "尾号 8899 的订单现在什么状态？挑最新那单说")
    print()
    print("=== 实验 2：问到会抛异常的工具（没有 middleware）===")
    try:
        ask(build_agent(), "订单 ORD-20261015-001 的退款进度怎么样了？")
    except Exception as e:
        print(">>> 中断：", type(e).__name__, "|", str(e)[:120])
    print()
    print("=== 实验 3：加上 ToolRetryMiddleware 再问一次 ===")
    ask(build_agent(with_retry=True), "订单 ORD-20261015-001 的退款进度怎么样了？")

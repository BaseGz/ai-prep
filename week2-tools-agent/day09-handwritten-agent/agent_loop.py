# 1. 导入依赖、加载环境变量
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool

# 从.env文件中加载环境变量
load_dotenv(override=True)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")

# 2.模型的初始化
model = init_chat_model(
    model="deepseek:deepseek-chat",
    api_key=DEEPSEEK_API_KEY,
    api_base=DEEPSEEK_BASE_URL,

)
# 模拟数据提到模块顶部 MOCK_ORDERS / MOCK_TRACKS
MOCK_ORDERS = {
    "8899": [
        {"order_id": "ORD-20261015-001", "product": "无线蓝牙耳机 Pro",
         "created_at": "2026-10-15", "status": "已签收"},
        {"order_id": "ORD-20261018-002", "product": "65W 充电底座",
         "created_at": "2026-10-18", "status": "运输中"},
    ],
    "1024": [
        {"order_id": "ORD-20261020-003", "product": "磨砂手机壳",
         "created_at": "2026-10-20", "status": "待发货"},
    ],
}

MOCK_TRACKS = {
    "ORD-20261015-001": ["已揽收", "运输中", "派送中", "已签收"],
    "ORD-20261018-002": ["已揽收", "运输中"],
    "ORD-20261020-003": [],
}

# 3. 定义两个工具
    # 3.1 find_order
    # 返回：这个号名下的订单多行文本，每行一单（订单号order_id、商品product、下单时间created_at、状态status）
@tool(parse_docstring=True)
def find_order(phone_tail : str) -> str:
    """
    根据手机号后四位查找订单

    Args:
        phone_tail : 手机号后四位
    """
    orders = MOCK_ORDERS.get(phone_tail)
    if not orders:
        return f"未查询到尾号 {phone_tail} 名下的订单"

    lines = [f"共查到 {len(orders)} 条订单："]
    for o in orders:
        lines.append(f"- 订单号 {o['order_id']}｜产品 {o['product']}｜下单 {o['created_at']}｜状态 {o['status']}")
    return "\n".join(lines)
    # 3.2 track_package
    # 返回：物流节点轨迹文本 + 当前状态（已揽收 / 运输中 / 派送中 / 已签收）

@tool(parse_docstring=True)
def track_package(order_id : str) -> str:
    """
    根据订单信息查询物流信息

    Args:
        order_id : 订单号
    """
    exists = any(
        o["order_id"] == order_id
        for orders in MOCK_ORDERS.values()
        for o in orders
    )
    # 订单是否存在
    if not exists:
        return f"系统中不存在订单 {order_id}，请核对订单号是否正确。"
    # 存在，但是有物流信息吗
    track = MOCK_TRACKS.get(order_id)
    if not track:
        return f"订单 {order_id} 尚未发货，暂无物流信息。"
    # 正常轨迹
    steps = "\n".join(f"{i}. {node}" for i, node in enumerate(track, 1))
    return (
        f"订单 {order_id} 的物流轨迹（共 {len(track)} 条）：\n"
        f"{steps}\n当前状态：{track[-1]}"
    )


    # 4. 绑定工具
    # 工具注册表（代替绑定工具，多一个工具需要改动的地方小）
TOOL_MAP = {"find_order": find_order, "track_package": track_package}
model_with_tools = model.bind_tools(list(TOOL_MAP.values()))

MAX_ROUNDS = 8


# 5. 给模型添加一个记忆区，每次调用新开一个 messages
def run(question : str ) -> str:
    messages = [
        SystemMessage("你是一个物流智能查询助手"),
        # HumanMessage("我尾号 8899 那个耳机到哪了？")
        # HumanMessage("尾号 8899 的充电底座发货了吗？")
        # HumanMessage("尾号 6666 的订单到哪了？")
        # HumanMessage("你们支持退货吗？")
        HumanMessage(question)
    ]
# 6. for 循环：
    for round_no in range(1, MAX_ROUNDS + 1):
    #      - 调模型
    #      - 追加 response
        response = model_with_tools.invoke(messages)
#      - 将模型回答添加到记忆当中
        messages.append(response)
#      - 没有 tool_calls → return
        if not response.tool_calls:
            # 7. 打印最终答案
            return response.content
#      - 有 → 遍历执行 → 追加 ToolMessage
        for tool_call in response.tool_calls:
            name = tool_call["name"]
            t = TOOL_MAP.get(name)
        # 未知工具：必须造一条 ToolMessage 回填，否则模型看不到任何结果，
        # 下一轮很可能重复调用 → 死循环
            if t is None:
                messages.append(
                    ToolMessage(
                        content=f"不存在名为 {name} 的工具，可用工具只有："
                                f"{'、'.join(TOOL_MAP)}",
                        tool_call_id=tool_call["id"],
                    )
                )
                continue

            result = t.invoke(tool_call)
            print(f"  [第 {round_no} 轮] {name}({tool_call['args']})")
            print(f"  → {result.content}")
            messages.append(result)

    return f"超过最大轮数 {MAX_ROUNDS}，已强制停止。"

if __name__ == "__main__":
    print(run("我尾号 8899 那个耳机到哪了？"))
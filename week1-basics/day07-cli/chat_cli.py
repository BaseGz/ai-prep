# 1. 加载 env，建 model
from enum import Enum
from typing import Literal

from langchain.chat_models import init_chat_model
import os

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

# 读取.env配置文件中的信息，相关的环境变量以.env文件中的优先
load_dotenv(override=True)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")

# 2.模型的初始化
model = init_chat_model(
    model="deepseek:deepseek-chat",
    api_key=DEEPSEEK_API_KEY,
    api_base=DEEPSEEK_BASE_URL,

)

# print(model.invoke("你是谁，一句话说完"))  测试

# 2. 建 extractor（结构化抽取器）
class Identity_type(str, Enum):
    student = "学生"
    teacher = "老师"
    doctor = "医生"
    worker = "工人"
    white_collar = "白领"
    other = "其他"

class Person(BaseModel):
    name: str = Field(description="人的名字")
    age: int = Field(description="人的年龄")
    gender: Literal["男", "女"] = Field(description="人的性别")
    identity: Identity_type = Field(description="人的身份")

# 3. 开对话记录 —— 一个空列表，第一条先塞系统提示词（定人设/回答长度）
messages = [
    {
        "role": "system",
        "content":"你是一个友好的AI助手，负责帮他解决他生活或者工作上的问题"
    }
]

print(f"请输入具体问题，当输入/EXIT的时候，结束对话")

i = 1
while True:
    # 判断用户是提问还是命令
    print("\n", "=" * 10, f"第{i}轮对话开始", "=" * 10, "\n")

    user_input = input("请输入：")

    # /EXIT  唯一能跳出循环的路
    if user_input == "/EXIT":
        print("会话已结束，欢迎下次再来")
        break

    # /extract  后面跟的内容 → 交给抽取器（不是模型）→ 拿到对象 → 按对象里的字段打印不同的话
    if user_input.startswith("/extract"):
        structured_model = model.with_structured_output(Person)
        result = structured_model.invoke(user_input.removeprefix("/extract").strip())
        print(result)
        # 把抽取结果加入记忆
        messages.append({
            "role": "user",
            "content": user_input.removeprefix("/extract").strip()
        })
        continue

    # 将用户信息添加到消息列表中
    messages.append({
            "role": "user",
            "content": user_input
    })

    # 提交记忆给模型得到回答
    ai_msg = model.invoke(messages)
    print(ai_msg.content)

    # 把模型的回答也加入记忆，下一轮才“记得”之前的对话
    messages.append({
        "role": "assistant",
        "content": ai_msg.content
    })

    i += 1


    # /history → 只是数一下记录里有几条



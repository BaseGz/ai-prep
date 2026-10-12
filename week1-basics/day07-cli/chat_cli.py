# 1. 加载 env，建 model
from enum import Enum
from typing import Literal

from langchain.chat_models import init_chat_model
import os

from dotenv import load_dotenv
from openai import APIError
from pydantic import BaseModel, Field

# 1.读取.env配置文件中的信息，相关的环境变量以.env文件中的优先
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

# 3. 建 extractor（结构化抽取器）
class IdentityType(str, Enum):
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
    identity: IdentityType = Field(description="人的身份")

# extractor 只建一次，循环里复用
extractor = model.with_structured_output(Person)

# 4. 开对话记录 —— 一个空列表，第一条先塞系统提示词（定人设/回答长度）
SYSTEM_PROMPT = (
    "你是小 Prep，一个友好的 AI 助手，负责帮用户解决生活或工作上的问题。"
    "回答要求：\n"
    "1. 用简体中文，语气自然、直接，不说废话。\n"
    "2. 控制长度：一般问题 150 字以内；需要分步或对比时用要点列表，总共不超过 300 字。\n"
    "3. 如果收到形如 Person(name=..., age=..., gender=..., identity=...) 的消息，"
    "那是用户的背景资料而非提问，请确认已记住，并在后续回答中自然地利用这些信息。"
)
messages = [
    {
        "role": "system",
        "content":SYSTEM_PROMPT
    }
]

print("请输入具体问题，当输入/EXIT的时候，结束对话")

i = 1
try:
    while True:
        # 判断用户是提问还是命令
        print("\n", "=" * 10, f"第{i}轮对话开始", "=" * 10, "\n")
        i += 1

        try:
            user_input = input("请输入：")
        except EOFError:
            print("\n输入流已结束，会话退出")
            break


        # /EXIT  唯一能跳出循环的路
        if user_input.upper() == "/EXIT" :
            print("会话已结束，欢迎下次再来")
            break

        # /extract  后面跟的内容 → 交给抽取器（不是模型）→ 拿到对象 → 按对象里的字段打印不同的话
        if user_input.startswith("/extract"):
            try:
                result = extractor.invoke(user_input.removeprefix("/extract").strip())
            except APIError as e:
                print(f"\n[抽取失败] 模型服务异常：{e}，请重试")
                continue

            print(result)

            # 把抽取结果加入记忆（结构化对象转字符串，作为 user 消息
            messages.append({
                    "role": "user",
                    "content": str(result)
                 })

            # 若 /extract 后面有原始文本，也补一条进记忆，保留用户的说法
            if user_input.removeprefix("/extract").strip() != "":
                messages.append({
                    "role": "user",
                    "content": user_input.removeprefix("/extract").strip()
                })
                continue

        # /history → 只是数一下记录里有几条(用户和AI总记录)
        if user_input == "/history":
            print(f"记录里一共有 {len(messages)} 条消息")
            continue

        # 将用户信息添加到消息列表中
        messages.append({
                "role": "user",
                "content": user_input
        })

        # 提交记忆给模型得到回答
        reply_content = ""
        try:
            for chunk in model.stream(messages):
                if chunk.content:
                    print(chunk.content, end="", flush=True)
                    reply_content = reply_content + chunk.content
        except APIError as e:
            print(f"\n[回答失败] 模型服务异常：{e}，请重试")
            messages.pop()
            continue

        print()

        # 把模型的回答也加入记忆，下一轮才“记得”之前的对话
        messages.append({
            "role": "assistant",
            "content": reply_content
        })

except KeyboardInterrupt:
    print("\n收到中断信号，会话已结束")
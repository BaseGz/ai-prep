"""D5 · LCEL 管道（自己写版）

要验证三件事：
① 管道符 | 到底做了什么
② 同一条链能不能四种调用：invoke / stream / batch / ainvoke
③ 输入形状对不上时怎么排查
"""
from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
API_KEY = os.getenv("DEEPSEEK_API_KEY")


def build_chain():
    """把三个 Runnable 串成一条链。今天要理解的就是 return 那一行。"""

    # TODO 1 · 建提示词模板
    #   用 ChatPromptTemplate.from_messages([...])
    #   里面放两条：("system", 要求它说话极简)、("user", "{question}")
    #   注意那个 {question} 花括号 —— 它决定了 invoke 要传进去什么形状
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个说话极其简单的助手"),
        ("user", "{question}")
    ])

    # TODO 2 · 建模型
    #   用 init_chat_model(MODEL, model_provider=..., base_url=..., api_key=..., temperature=0)
    #   这段和 D1 的 hello_model.py 一模一样，可以直接照搬

    model = init_chat_model(
        model="deepseek:deepseek-flash",
        api_key=API_KEY,
        base_url=BASE_URL,

)

    # TODO 3 · 串成链（关键行）
    #   三段接起来交给 return。想想中间要不要加解析器，不加会怎样
    return prompt | model | StrOutputParser()


def main() -> None:
    chain = build_chain()

    # ★★★ 临时实验 ★★★
    # try:
    #     chain.invoke("你好")
    #     print("没报错?!链居然接受了裸字符串")
    # except TypeError as e:
    #     print("果然抛了 TypeError →", e)
    # return
    # ★★★ 临时实验结束 ★★★

    # ① invoke —— 同步，一次一个问题
    # TODO 4 · 注意第一个环节要什么类型的输入
    print("① invoke：", chain.invoke({"question": "你好"}))

    # ② stream —— 逐块拿，打字机效果的来源
    # TODO 5 · 用 for 循环逐块打印；end="" 和 flush=True 都不能少
    print("② stream：", end="", flush=True)
    for chunk in chain.stream({"question": "讲一下现在深圳发展的怎么样了"}):
        print(chunk, end="", flush=True)
    print()

    # ③ batch —— 一次给多个输入，内部并发
    # TODO 6 · 传一个「字典组成的列表」
    answers = chain.batch([
        {"question": "你叫什么名字"},
        {"question": "你叫用的什么模型"},
        {"question": "你的模型多久更新一次"},
    ])
    print("③ batch：", answers)

    # ④ ainvoke —— 异步版本，顶层不能 await，要包一层
    # TODO 7 · 用 asyncio.run(...) 包住
    print("④ ainvoke：", asyncio.run(chain.ainvoke({"question": "你好"})))


def check_console_buffer() -> None:
    """控制台缓冲自测（D5 实验痕迹，默认不调用）。

    数字一个接一个跳出来 → 控制台没有缓冲；
    卡 5 秒后 10 个数字一起出现 → PyCharm 有缓冲
    （去「设置 → 构建、执行、部署 → 控制台」勾上「模拟终端中的输出」）。

    要测时手动跑一次 check_console_buffer() 即可。
    """
    for i in range(10):
        print(i, end=" ", flush=True)
        time.sleep(0.5)


if __name__ == "__main__":
    main()

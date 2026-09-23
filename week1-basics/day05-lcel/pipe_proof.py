"""D5 补课 · 管道符到底做了什么（零 token，一个模型都不调）

★ 看不懂 Runnable、也不知道什么叫「重载」？先跑同目录的 learn_runnable.py。
  那个脚本从「普通函数」和「你自己写的 + 号」讲起，五步走到这里，一个 LangChain
  概念都不预设。跑完再回来看这个文件，就都认识了。

跑完要能不看笔记说出：
    | 是 Runnable 重载的 __or__，拼出来的是 RunnableSequence，
    语义就是「上一个 Runnable 的输出，成为下一个 Runnable 的输入」。
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda, RunnablePassthrough

print("=== 1) `|` 是谁定义的 ===")
print("Runnable.__or__ =", Runnable.__or__)

print()
print("=== 2) 两个假组件：看数据怎么流 ===")
a = RunnableLambda(lambda x: x * 2)     # 1 -> 2
b = RunnableLambda(lambda x: x * 10)    # 2 -> 20
chain = a | b
print("type(a | b)       =", type(chain).__name__)
print("(a | b).invoke(1) =", chain.invoke(1))

print()
print("=== 3) prompt 吐出来的到底是什么 ===")
prompt = ChatPromptTemplate.from_messages([
    ("system", "说话极简"),
    ("user", "{q}"),
])
pv = prompt.invoke({"q": "你好"})
print("类型 =", type(pv).__name__)
print("内容 =", pv.messages)

print()
print("=== 4) 下游收到的就是上游吐出的那个对象 ===")
seen = {}


def probe(x):
    seen["t"] = type(x).__name__
    return "收到"


(prompt | RunnableLambda(probe)).invoke({"q": "你好"})
print("下游收到的类型 =", seen["t"], "   <- 和第 3 步同一个类")

print()
print("=== 5) 链的入口决定 invoke 要传什么 ===")
seq = prompt | RunnableLambda(probe)
print("第一个环节 =", seq.first.__class__.__name__)
print("所以 invoke 传的是 {'q': '...'}，不是字符串")

print()
print("=== 6) 左边不是 Runnable 也能接管道（__ror__）===")
factors = {
    "a": RunnableLambda(lambda x: x + 1),   # 1 -> 2
    "b": RunnablePassthrough(),             # 1 -> 1（原样透传）
}
combo = factors | RunnableLambda(lambda v: v)
print("type(dict | Runnable) =", type(combo).__name__)
print("(dict | Runnable).invoke(1) =", combo.invoke(1))

# 注意：这里要用一个只吃 a / b 的模板。
# 不能复用第 3 步那个 prompt —— 它只认 {q}，收到 {'a':...,'b':...} 会报 KeyError。
ratio = ChatPromptTemplate.from_template("{a} / {b}")
print("(dict | prompt).invoke(1)   =", (factors | ratio).invoke(1).messages[0].content)

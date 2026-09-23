# -*- coding: utf-8 -*-
"""D5 补课 · 管道符与类型链 —— 今天 10 个疑问的可执行答案

零 token：全程不调真模型，不产生任何费用。
  第 1~6 段：纯结构检查 + 假组件，完全不联网
  第 7~10 段：借真模型的「入口校验函数」_convert_input() —— 纯本地类型检查，不发请求

跑法（PyCharm 里右键 -> 运行 'probe_types'）：
    .venv\\Scripts\\python.exe probe_types.py

配套阅读：NOTES-管道符与类型链.md（同目录）
前置材料：learn_runnable.py（从普通函数讲到 Runnable；看不懂本文件就先跑它）
"""

import inspect

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda

DIV = "=" * 66


def probe(name, fn):
    """把普通函数包成 Runnable，并打印「这一棒收到什么 / 吐出什么」"""
    def inner(x):
        print("     [%-4s] 收到 %-16s %r" % (name, type(x).__name__, x))
        y = fn(x)
        print("     [%-4s] 吐出 %-16s %r" % (name, type(y).__name__, y))
        return y
    return RunnableLambda(inner)


def sec(n, q):
    print()
    print(DIV)
    print("疑问 %d：%s" % (n, q))
    print(DIV)


# ---------------------------------------------------------------- 疑问 1
sec(1, "`|` 是谁定义的？是 Python 3.10 的语法糖吗？")
print("     `|` 不是语法糖，是 Runnable 上重载的 __or__ 方法：")
print("     Runnable.__or__ =", Runnable.__or__)
print()
print("     反证：一个没定义 __or__ 的普通类，用 | 会直接 TypeError ——")
class NoOr:
    pass
try:
    NoOr() | NoOr()
except TypeError as e:
    print("     %s: %s" % (type(e).__name__, e))

# ---------------------------------------------------------------- 疑问 2
sec(2, "执行顺序是「默认的」还是「我写的」？")
A = probe("A", lambda x: x + 1)
B = probe("B", lambda x: x * 10)
print("     (A | B).invoke(1)")
print("       结果 =", (A | B).invoke(1))
print("     (B | A).invoke(1)      <- 只是左右对调，零件是同一批")
print("       结果 =", (B | A).invoke(1))
print()
print("     >>> 没有默认顺序。| 不认角色，只认你写的先后，从左到右。")

# ---------------------------------------------------------------- 疑问 3
sec(3, "「谁站在第一棒」是什么意思？")
X = probe("一棒", lambda s: s + " +一棒")
Y = probe("二棒", lambda s: s + " +二棒")
Z = probe("三棒", lambda s: s + " +三棒")
print("     (一棒 | 二棒 | 三棒).invoke('原料')")
print("       结果 =", (X | Y | Z).invoke("原料"))
print()
print("     >>> 第一棒收到的是你 invoke 传进去的原物；")
print("     >>> 之后每一棒收到的，都是上一棒吐出来的东西。")

# ---------------------------------------------------------------- 疑问 4
sec(4, "prompt 吐出来的东西，下游真的原样收到了吗？")
prompt = ChatPromptTemplate.from_messages([("system", "说话极简"), ("human", "{q}")])
pv = prompt.invoke({"q": "你好"})
print("     prompt.invoke({'q':'你好'}) 的返回类型 =", type(pv).__name__)
print("     里面装着 =", [type(m).__name__ for m in pv.messages])


def show_type(x):
    print("     下游收到的类型              =", type(x).__name__, "  <- 和上面是同一个类")
    return x


(prompt | RunnableLambda(show_type)).invoke({"q": "你好"})
print()
print("     >>> 下游收到的，就是上游吐出的那个对象本身，没有任何转换或猜测。")

# ---------------------------------------------------------------- 疑问 5
sec(5, "为什么 invoke 有时传字符串、有时传字典？")
seq = prompt | RunnableLambda(show_type)
print("     链的第一个环节 =", seq.first.__class__.__name__)
print("     >>> invoke 要传什么，由第一棒想吃什么决定 —— 没有统一答案。")

# ---------------------------------------------------------------- 疑问 6
sec(6, "左边放一个字典，也能接管道？（Runnable 还实现了 __ror__）")
factors = {"a": RunnableLambda(lambda x: x + 1), "b": RunnableLambda(lambda x: x)}
print("     type(dict | Runnable)     =", type(factors | RunnableLambda(lambda d: d)).__name__)
print("     (dict | Runnable).invoke(1) =", (factors | RunnableLambda(lambda d: d)).invoke(1))
ratio = ChatPromptTemplate.from_template("{a} / {b}")
print("     (dict | prompt).invoke(1)   =", (factors | ratio).invoke(1).messages[0].content)
print()
print("     >>> 反过来也能接，因为 Runnable 实现了反向运算符 __ror__。")
print("     >>> RAG 的标准写法 {\"context\": retriever | ...} | prompt 就靠它成立（D15 用）。")

# ---------------------------------------------------------------- 疑问 7~9
try:
    from langchain_deepseek import ChatDeepSeek

    llm = ChatDeepSeek(model="deepseek-chat", api_key="sk-local-typecheck-only", temperature=0)
    LLM_OK = True
except Exception as e:
    LLM_OK = False
    print()
    print("  （无法构造 ChatDeepSeek，跳过疑问 7~9：%s）" % e)

if LLM_OK:
    # ------------------------------------------------------------ 疑问 7
    sec(7, "model 只能吃 ChatPromptValue 吗？")
    cases = [
        ("str", "你好"),
        ("单条消息 list", [HumanMessage(content="你好")]),
        ("多条消息 list", [HumanMessage(content="你好"), AIMessage(content="在的")]),
        ("dict", {"q": "你好"}),
        ("ChatPromptValue", prompt.invoke({"q": "你好"})),
    ]
    for label, x in cases:
        try:
            pm = llm._convert_input(x)
            inner = getattr(pm, "messages", None)
            desc = type(pm).__name__
            if inner:
                desc += "（" + " / ".join(type(m).__name__ for m in inner) + "）"
            print("     %-16s -> 接受，统一转成 %s" % (label, desc))
        except Exception as e:
            print("     %-16s -> 拒绝：%s" % (label, type(e).__name__))
            print("     %-16s    %s" % ("", e))
    print()
    print("     >>> 能吃 3 种（str / 消息列表 / PromptValue），不是只有 ChatPromptValue；")
    print("     >>> 三种进去之前会被统一归一化成 PromptValue。只有 dict 被拒绝。")

    # ------------------------------------------------------------ 疑问 8
    sec(8, "写反成 `parser | model | prompt`，会报错吗？")


    def fake_model(x):
        llm._convert_input(x)          # 真模型同款入口校验，不发请求
        print("     [model] 收到 %-16s 校验通过 -> 返回 AIMessage" % type(x).__name__)
        return AIMessage(content="假回复")


    model = RunnableLambda(fake_model)
    parser = StrOutputParser()

    bad = parser | model | prompt
    print("     steps =", [s.__class__.__name__ for s in bad.steps])
    print("     bad.invoke('你好')")
    try:
        r = bad.invoke("你好")
        print("     跑通了！返回 %s（没抛异常）" % type(r).__name__)
        print("     {q} 里被塞进去的 =", repr(r.messages[-1].content)[:100] + " ...")
        print()
        print("     >>> 不报错 —— prompt 不挑食，把整个 AIMessage 对象 str() 化塞进了 {q}。")
        print("     >>> 静默失败，比报错更危险：跑完三步，结果是垃圾。")
    except Exception as e:
        print("     %s:" % type(e).__name__)
        print("     %s" % e)

    # ------------------------------------------------------------ 疑问 9
    sec(9, "那写反成 `model | prompt | parser` 呢？")
    bad2 = model | prompt | parser
    print("     steps =", [s.__class__.__name__ for s in bad2.steps])
    print("     bad2.invoke({'q': '你好'})")
    try:
        bad2.invoke({"q": "你好"})
    except Exception as e:
        print("     %s:" % type(e).__name__)
        print("     %s" % e)
    print()
    print("     >>> 这个会报错！因为 model 站第一棒，而它入口严格，不认 dict。")
    print("     >>> 两个方向结果不同 -> 报不报错不看顺序，看「那一棒挑不挑食」。")

# ---------------------------------------------------------------- 疑问 10
sec(10, "Runnable 到底是什么？函数？用法？")
print("     inspect.isclass(Runnable)          =", inspect.isclass(Runnable))
print("     必须你自己实现的方法               =", sorted(Runnable.__abstractmethods__))
gift = [m for m in ("invoke", "stream", "batch", "ainvoke", "abatch", "astream")
        if hasattr(Runnable, m)]
print("     基类白送的方法                     =", gift)
print("     三个零件都是 Runnable 吗           =",
      isinstance(prompt, Runnable), isinstance(parser, Runnable), isinstance(model, Runnable))
print()
print("     >>> Runnable 是一个抽象基类，一份「身份」：只要你会 invoke，你就是 Runnable。")
print("     >>> 类比 Python 的 Iterable —— 实现了 __iter__ 就能被 for 遍历，同一个意思。")
print("     >>> 它不规定你怎么用，只规定你有没有 invoke。")

# ---------------------------------------------------------------- 收口
print()
print(DIV)
print("一句话收口")
print(DIV)
print("  可靠的从来不是「背顺序」，而是背类型链：")
print()
print("      dict -> prompt -> PromptValue -> model -> AIMessage -> parser -> str")
print()
print("  每一节的输出，必须正好是下一节能吃的输入。顺序只是这条链的结果。")
print("  跑完觉得结果怪，第一件事永远是：")
print("      print([s.__class__.__name__ for s in chain.steps])")
print(DIV)

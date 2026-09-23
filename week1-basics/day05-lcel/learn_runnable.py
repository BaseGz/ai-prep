"""D5 零基础版 · 从你最熟的东西，一步步走到 Runnable 和管道符

看不懂 pipe_proof.py？先跑这一个。它不涉及任何 LangChain 概念，
从「普通函数」和「你早就在用的运算符」讲起，五步走到管道符。

运行方式：右键 → 运行 'learn_runnable'（零 token，不调模型）

跑完要能说出三句话：
    1. 管道符 = 我自己也能写的 __or__ 方法，不是什么魔法
    2. Runnable = 一个有 invoke 方法的东西，所以大家能互相接
    3. a | b 的数据流形状和 tenfold(double(1)) 一样（前者输出 → 后者输入），
       但 a | b 只是「组装」，不执行；要等 .invoke() 才真的开始跑。
"""

print("=" * 62)
print("第 1 步 · 你早就会的写法：函数套函数")
print("=" * 62)


def double(x):
    return x * 2          # 1 -> 2


def tenfold(x):
    return x * 10         # 2 -> 20


print("double(1)            =", double(1))
print("tenfold(double(1))   =", tenfold(double(1)), "  <- 里面的结果，喂给外面")
print()
print("→ 这行代码就是「前者的输出，成为后者的输入」。你早就会写了。")
print("→ 管道符 a | b 只是这句话的另一种写法。下面看它凭什么能这么写。")

print()
print("=" * 62)
print("第 2 步 · 先看一个你每天都在用的「运算符重载」")
print("=" * 62)


class Money:
    """一个普普通通的类，只多写了一个方法：__add__"""

    def __init__(self, amount):
        self.amount = amount

    def __add__(self, other):          # 你决定 + 号对 Money 是什么意思
        return Money(self.amount + other.amount)


m1, m2 = Money(3), Money(5)
print("Money(3) + Money(5)  =", (m1 + m2).amount)
print()
print("疑点：两个自定义对象，+ 号凭什么知道要相加？")
print("答案：Python 看到 a + b，会自动去找 a.__add__(b)。你写了这个方法，+ 就生效了。")
print("     这就叫「运算符重载」——不是新语法，是 Python 一直有的机制。")
print()
print("还有一半的机制：万一左边那个对象没写 __add__ 呢？")
print("Python 会退一步，去问右边那个对象：你能不能接住「别人 + 我」？")
print("对应的方法叫 __radd__（r = reverse，反向）。__or__ / __ror__ 是同一对。")

print()
print("=" * 62)
print("第 3 步 · 没写这个方法的类，用 + 会直接报错")
print("=" * 62)


class Plain:
    pass


try:
    Plain() + Plain()
except TypeError as e:
    print("Plain() + Plain()  →  TypeError:", e)
print()
print("→ 所以：能不能用某个运算符，不取决于「这个运算符」，")
print("   取决于「你给它两边的对象写了对应的方法没有」。")

print()
print("=" * 62)
print("第 4 步 · 关键一步：自己写一个能接管道符的东西（只用 3 行）")
print("=" * 62)


class Step:
    """我自己造的迷你版 Runnable：一个名字 + 一个函数 + 两个方法"""

    def __init__(self, fn, name):
        self.fn = fn
        self.name = name

    def invoke(self, x):                    # ← 统一的入口名，就叫 invoke
        return self.fn(x)

    def __or__(self, other):                # ← 就是这三行，让 | 生效
        return Step(
            lambda x: other.invoke(self.invoke(x)),   # 我的输出 → 它的输入
            f"{self.name}→{other.name}",
        )


step_a = Step(double, "×2")
step_b = Step(tenfold, "×10")

print("step_a.invoke(1)                   =", step_a.invoke(1))
print("(step_a | step_b).invoke(1)        =", (step_a | step_b).invoke(1)      )
print("type(step_a | step_b)              =", type(step_a | step_b).__name__)
print()
print("→ 出来 20，和第 1 步的 tenfold(double(1)) 完全一样。")
print("→ 结论：管道符不是我编的魔法，就是上面那三行 __or__。")
print("   LangChain 做的事，是把这三行写得比我的更完善、更通用。")

print()
print("=" * 62)
print("第 5 步 · 现在回头看 LangChain：它只是把这套做成了通用基类")
print("=" * 62)

from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.base import Runnable

lc_a = RunnableLambda(double)      # 把普通函数包装成「能接管道的东西」
lc_b = RunnableLambda(tenfold)

print("lc_a 是 Runnable 的实例吗    =", isinstance(lc_a, Runnable))
print("lc_a | lc_b 的 invoke(1)     =", (lc_a | lc_b).invoke(1))
print("type(lc_a | lc_b)            =", type(lc_a | lc_b).__name__)
print()
print("LangChain 用的 __or__ 方法，和我第 4 步那个是同一个名字：")
print("  Runnable.__or__ =", Runnable.__or__)
print()
print("→ 所以「Runnable」到底是什么：")
print("   一个有 invoke 方法的对象。LangChain 里所有组件（提示词 / 模型 / 解析器）")
print("   都长这个样子，所以它们才能一个接一个地串起来。")
print("   这就是为什么提示词能和模型接、模型能和解析器接 —— 接口一样，形状才对得上。")

print()
print("=" * 62)
print("跑完了。现在回去看 pipe_proof.py，那六步应该都能读懂了")
print("=" * 62)

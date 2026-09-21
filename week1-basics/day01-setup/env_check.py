"""D1 · 环境自检

跑通这一个文件，D1 的「环境」这件事就算做完了。它不联网，只做四件事：

  1. Python 版本是否满足 LangChain 1.x 的要求（>= 3.10,< 4.0）
  2. 五个包装没装上、版本分别是多少
  3. .env 读到了没有、关键字段有没有值（打码显示，不泄露 key）
  4. .env 是否已被 git 忽略（这条最要紧：key 一旦进库就很难收回）

用法：在 PyCharm 里直接右键 Run 'env_check'。
"""
from __future__ import annotations

import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from dotenv import load_dotenv

# week1-basics/day01-setup/env_check.py → 上溯三级就是仓库根目录
REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"

PACKAGES = [
    "langchain",
    "langchain-core",
    "langchain-openai",
    "langchain-deepseek",
    "python-dotenv",
]
REQUIRED_ENV = ["DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL"]

OK = "[ OK ]"
BAD = "[FAIL]"
WARN = "[WARN]"


def mask(value: str) -> str:
    """只露出头尾，中间打码。长度也打出来，方便判断是不是复制少了字符。"""
    if not value:
        return "(空)"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}…{value[-4:]}（共 {len(value)} 字符）"


def check_python() -> bool:
    v = sys.version_info
    passed = (3, 10) <= (v.major, v.minor) < (4, 0)
    print(f"{OK if passed else BAD} Python {v.major}.{v.minor}.{v.micro}")
    print(f"       解释器路径：{sys.executable}")
    if not passed:
        print("       LangChain 1.x 要求 3.10 <= Python < 4.0，换一个解释器再跑")
    return passed


def check_packages() -> bool:
    all_ok = True
    for name in PACKAGES:
        try:
            print(f"{OK} {name} {version(name)}")
        except PackageNotFoundError:
            all_ok = False
            print(f"{BAD} {name} 没装上")
    if not all_ok:
        print("       装包：PyCharm 底部 Terminal → "
              "pip install -r week1-basics/day01-setup/requirements.txt")
    return all_ok


def check_env() -> bool:
    import os

    if not ENV_FILE.exists():
        print(f"{BAD} 找不到 {ENV_FILE}")
        print("       把仓库根目录的 .env.example 复制一份、改名成 .env，再填 key")
        return False

    load_dotenv(ENV_FILE, override=True)
    print(f"{OK} 已读取 {ENV_FILE}")
    all_ok = True
    for key in REQUIRED_ENV:
        value = os.getenv(key, "")
        if value:
            print(f"{OK} {key} = {mask(value)}")
        else:
            all_ok = False
            print(f"{BAD} {key} 是空的")
    return all_ok


def check_gitignore() -> None:
    """.env 有没有被 git 忽略。没被忽略就别提交，先改 .gitignore。"""
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", ".env"],
            cwd=REPO_ROOT,
            capture_output=True,
        )
    except FileNotFoundError:
        print(f"{WARN} 没找到 git，这条跳过（用 PyCharm 提交的话不影响）")
        return

    if result.returncode == 0:
        print(f"{OK} .env 已被 .gitignore 忽略，提交时不会带上")
    else:
        print(f"{BAD} .env 没有被忽略！先往 .gitignore 里加一行 .env 再提交")


def main() -> None:
    print("=" * 60)
    print("D1 环境自检 · 四项全 OK 就可以去写第一次模型调用")
    print("=" * 60)

    results = [check_python(), check_packages(), check_env()]
    if not results[2]:
        # 连 .env 都没读到，就别接着查 gitignore 了
        print(f"{WARN} 先补上 .env 再重跑；下面的 gitignore 检查仅供参考")
    check_gitignore()

    print("-" * 60)
    if all(results):
        print("结论：环境就绪。下一步跑 hello_model.py")
    else:
        print("结论：还有上面标 FAIL 的项没解决，逐条修完再往下走")
    print("-" * 60)


if __name__ == "__main__":
    main()

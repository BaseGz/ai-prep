"""D16 · 文档加载：把 PDF / HTML / Markdown 变成 Document"""
import time
from itertools import islice
from pathlib import Path

from langchain_community.document_loaders import BSHTMLLoader, PyPDFLoader, TextLoader

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "datasets/raw/x4-manual-pdf/X4_UserManual_CN.pdf"
HTML_DIR = ROOT / "datasets/raw/x4-manual"
MD = ROOT / "docs/journal/2026-10-05.md"


def show(docs, n=1):
    """打印前 n 条：正文多长、开头是什么、metadata 有哪些字段"""
    for d in docs[:n]:
        print(f"  [{len(d.page_content):>5} 字] {d.page_content[:60]!r}")
        for k, v in d.metadata.items():
            print(f"      {k} = {str(v)[:60]}")


def load_pdf():
    t0 = time.time()
    docs = PyPDFLoader(str(PDF)).load()
    print(f"\n[PDF] {len(docs)} 条，{time.time() - t0:.2f}s")
    show(docs)
    return docs


def load_one_html():
    t0 = time.time()
    files = sorted(HTML_DIR.rglob("*.html"))
    docs = BSHTMLLoader(str(files[0]), open_encoding="utf-8").load()
    print(f"\n[HTML 单页] {len(docs)} 条，{time.time() - t0:.2f}s  文件={files[0].name}")
    show(docs)
    return docs


def load_all_html():
    t0 = time.time()
    total, longest = 0, ("", 0)
    for f in sorted(HTML_DIR.rglob("*.html")):
        docs = BSHTMLLoader(str(f), open_encoding="utf-8").load()
        total += len(docs)
        if docs and len(docs[0].page_content) > longest[1]:
            longest = (f.name, len(docs[0].page_content))
    print(f"\n[HTML 全量] {total} 个 Document，{time.time() - t0:.2f}s")
    print(f"  最长一篇：{longest[0]} {longest[1]} 字")
    return total


def load_md():
    t0 = time.time()
    docs = TextLoader(str(MD), encoding="utf-8").load()
    print(f"\n[Markdown] {len(docs)} 条，{time.time() - t0:.2f}s")
    show(docs)
    return docs


# ============ 三处「你的活」：函数体空着，等你填 ============

def count_short_pages(docs):
    """你的活①：找出正文少于 100 字的页，打印页码，返回页数"""
    # 提示：用 len(d.page_content) 判长度，d.metadata["page_label"] 取页码
    Unqualified_page = 0
    for d in docs:
        if len(d.page_content) < 100:
            Unqualified_page += 1
            print(f"第 {d.metadata['page_label']} 页：{len(d.page_content)} 字")
    return Unqualified_page


def tag_sections():
    """你的活②：给 114 个文件各补 metadata["section"]，再按栏目计数"""
    # 提示：f.relative_to(HTML_DIR).parts[0] 就是栏目名（camera / specs / ...）
    # 预期数出：operating_tutorials 47、troubleshooting 32、camera 25、specs 7、accessories-kit 3
    Column = {}
    for f in sorted(HTML_DIR.rglob("*.html")):
        section = f.relative_to(HTML_DIR).parts[0]
        docs = BSHTMLLoader(str(f), open_encoding="utf-8").load()
        for d in docs:
            d.metadata["section"] = section
        Column[section] = Column.get(section, 0) + 1
    return Column


def lazy_demo():
    """你的活③：用 lazy_load() + islice 只读前 2 条"""
    # 提示：islice(loader.lazy_load(), 2) 返回的是迭代器，可以 for 循环
    loader = PyPDFLoader(str(PDF))
    for d in islice(loader.lazy_load(), 2):
        print(d.page_content[:100])


if __name__ == "__main__":
    pdf_docs = load_pdf()
    load_one_html()
    load_md()
    load_all_html()

    # 三处活：写完一个就放开一行，别一次全开
    count_short_pages(pdf_docs)
    counts = tag_sections()
    for k, v in sorted(counts.items()):
        print(f"  {k:22} {v}")

    lazy_demo()

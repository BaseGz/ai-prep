"""D17 · 文本切分：同一份文档，四种粒度各切一遍

跑法：python chunking.py
第一遍只跑 main()，应该看到 7 行统计，与执行单 4.1 节的数字逐行一致。
三处「你的活」写一个、放开一个。
"""
from pathlib import Path

from langchain_community.document_loaders import BSHTMLLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

ROOT = Path(__file__).resolve().parents[2]
HTML_DIR = ROOT / "datasets/raw/x4-manual"
MD = ROOT / "docs/journal/2026-10-05.md"


def load_all_html():
    """加载 114 个 HTML，并补上 section（D16 欠的那一步，这次要返回 docs）"""
    docs = []
    for f in sorted(HTML_DIR.rglob("*.html")):
        section = f.relative_to(HTML_DIR).parts[0]
        for d in BSHTMLLoader(str(f), open_encoding="utf-8").load():
            d.metadata["section"] = section
            docs.append(d)
    return docs


def report(chunks, label):
    """一组 chunk 的统计：条数 / 平均 / 最短 / 最长"""
    lens = [len(c.page_content) for c in chunks]
    avg = sum(lens) // len(lens)
    print(f"{label:28} {len(chunks):>4} 块 | 平均 {avg:>4} | 最短 {min(lens):>4} | 最长 {max(lens):>4}")


def cut_ratio(chunks):
    """你的活①：返回 (被切断的块数, 总块数_不含最后一块)

    判据：块的结尾不是句末标点，就算把一句话切断了。

    提示：
      - 遍历 chunks[:-1]，最后一块没有「后面」可以接，必须排除
      - 先 .rstrip() 去掉尾部空白，否则结尾的 '\\n' 会被误判成正常收尾
      - 判据用下面这个 ENDS 元组
      - 只在 journal 这份「有完整句子」的文档上算；拿参数表那种短行文档算会得到假阳性
    """
    ENDS = ("。", "！", "？", "；", "\n", "”", "」")
    pass


def tag_after_split():
    """你的活②：全量 114 个 Document 切一遍，验证 section 还在，并按栏目统计块数

    提示：
      - RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150, add_start_index=True)
      - 用 split_documents(docs)，不是 split_text
      - 取栏目用 c.metadata.get("section", "?")
      - 预期：114 个 Document -> 250 块，膨胀 2.2 倍
      - 如果 section 全打印成 "?"，说明你用了 split_text —— 它会把 metadata 丢光
    """
    pass


def try_token_split():
    """你的活③：字符 vs token，差多少

    提示：
      - import tiktoken，用 tiktoken.get_encoding("cl100k_base")
      - len(enc.encode(text)) 就是 token 数
      - from_tiktoken_encoder(encoding_name="cl100k_base", chunk_size=256, chunk_overlap=32)
      - 预期：2725 字 = 2099 token，1 token ≈ 1.3 字，切出 11 块
    """
    pass


def main():
    md_text = MD.read_text(encoding="utf-8")
    doc = Document(page_content=md_text, metadata={"source": MD.name, "section": "journal"})
    print(f"源文档：{MD.name}，{len(md_text)} 字\n")

    for size in (300, 500, 1000, 2000):
        sp = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=0)
        chunks = sp.split_documents([doc])
        report(chunks, f"size={size} overlap=0")
        # 活①写好后放开这一行：print(f"  切断 {cut_ratio(chunks)[0]}/{cut_ratio(chunks)[1]}")

    print()
    for size, pct in ((500, 0.15), (1000, 0.15), (1000, 0.3)):
        ov = int(size * pct)
        sp = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=ov)
        report(sp.split_documents([doc]), f"size={size} overlap={ov}")

    # tag_after_split()   ← 活②写好后放开
    # try_token_split()   ← 活③写好后放开


if __name__ == "__main__":
    main()

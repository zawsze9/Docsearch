"""DocSearch Step1 解析切分 —— AI 起草稿 v1（2026-09-08）

标注（2026-09-08 制度化）：
🤖 AI 代工：本脚本主体（遍历/切分/滑窗/统计 boilerplate）由 AI 起草。
🧠 本人核心（不可外包，跑通后必须做）：
  1) chunk 边界抽查：打开 chunks.jsonl 随机 5 行，确认切分处在语义边界；
     表格/公式被切开先记录问题，不急着修（检索够用即可）。
  2) schema 确认：doc_id/chunk_id/text/source/corpus_version 是否满足
     后续 embedding 与评测引用（gold chunk 要能指回 chunk_id）。
  3) 统计核对：split_stats.json 的文档数应为 92+5，chunk 数=jsonl 行数。
🔍 AI 起草→本人验证：跑通一遍并看懂每段在干什么，答不上来的行当场问。
降级线（V4-C）：40 分钟调不顺 → 用默认参数直接跑出统计，先落地再优化。

用法：python index/parse_split.py
输出：index/chunks.jsonl（每行一个 chunk）+ index/split_stats.json + 终端摘要
"""
from pathlib import Path
import json
import datetime

ROOT = Path(__file__).resolve().parent.parent          # DocSearch/
OUT_DIR = Path(__file__).resolve().parent              # index/

# 🧠 参数归你定稿：V4 默认 500/50；改了要同步写进 split_stats.json 与 README
CHUNK_SIZE = 500
OVERLAP = 50
MIN_CHUNK = 20            # 碎段并入前一块，避免碎片污染索引

# 与 index/download_manifest.md「当前来源」表一一对应；改语料必须同步改 manifest
SOURCES = [
    ("d2l-zh-snapshot-20260822-v1", ROOT / "data/raw/d2l-zh快照"),
    ("personal-notes-20260821-v1", ROOT / "data/raw"),   # 仅取 pynote-*.md 散文件
]


def iter_md_files(base: Path, notes_only: bool = False):
    if notes_only:
        yield from sorted(base.glob("pynote-*.md"))
        return
    for p in sorted(base.rglob("*.md")):
        if any(part == ".git" for part in p.parts):
            continue
        yield p


def split_sections(text: str):
    """按二级标题切块；一级标题与元信息自然落入首个块。"""
    sections, buf = [], []
    for line in text.splitlines():
        if line.startswith("## "):
            sections.append("\n".join(buf))
            buf = [line]
        else:
            buf.append(line)
    sections.append("\n".join(buf))
    return [s.strip() for s in sections if s.strip()]


def sliding(text: str):
    """超长段按字符滑窗：窗口 CHUNK_SIZE，步长 CHUNK_SIZE-OVERLAP。"""
    if len(text) <= CHUNK_SIZE:
        return [text]
    step = CHUNK_SIZE - OVERLAP
    return [text[i:i + CHUNK_SIZE] for i in range(0, len(text), step)
            if text[i:i + CHUNK_SIZE].strip()]


def chunk_doc(path: Path, corpus_version: str):
    text = path.read_text(encoding="utf-8", errors="ignore")
    doc_id = path.relative_to(ROOT).as_posix()
    chunks = []
    for sec in split_sections(text):
        parts = sliding(sec)
        for part in parts:
            if len(part) < MIN_CHUNK and chunks:
                chunks[-1]["text"] += "\n" + part      # 碎段并入前块
            else:
                chunks.append({"text": part})
    for i, c in enumerate(chunks):
        c.update({"doc_id": doc_id, "chunk_id": i,
                  "source": corpus_version, "corpus_version": corpus_version})
    return chunks


def main():
    all_chunks, stats_by_source = [], {}
    for corpus_version, base in SOURCES:
        docs, n0 = 0, len(all_chunks)
        for p in iter_md_files(base, notes_only=(corpus_version.startswith("personal"))):
            all_chunks.extend(chunk_doc(p, corpus_version))
            docs += 1
        lens = [len(c["text"]) for c in all_chunks[n0:]]
        stats_by_source[corpus_version] = {
            "docs": docs, "chunks": len(all_chunks) - n0,
            "char_min": min(lens) if lens else 0,
            "char_avg": round(sum(lens) / len(lens)) if lens else 0,
            "char_max": max(lens) if lens else 0,
        }

    out_jsonl = OUT_DIR / "chunks.jsonl"
    with out_jsonl.open("w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    stats = {
        "params": {"chunk_size": CHUNK_SIZE, "overlap": OVERLAP, "min_chunk": MIN_CHUNK},
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "total_docs": sum(s["docs"] for s in stats_by_source.values()),
        "total_chunks": len(all_chunks),
        "by_source": stats_by_source,
        "reproduce": "python index/parse_split.py",
    }
    (OUT_DIR / "split_stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"\n✅ chunks.jsonl 共 {len(all_chunks)} 行 -> {out_jsonl}")
    # 🧠 自检提示：total_docs 应为 97（92 d2l + 5 pynote）；不符先查 manifest 路径


if __name__ == "__main__":
    main()

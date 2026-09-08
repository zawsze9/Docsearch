"""DocSearch Step2 embedding + FAISS —— AI 起草稿 v1（2026-09-08）

标注：
🤖 AI 代工：加载/编码/建索引/元数据 boilerplate 由 AI 起草。
🧠 本人核心（跑通后必须理解并能答辩）：
  1) 归一化：为什么用 L2 归一化 + 内积（IndexFlatIP）等价于余弦相似度；
  2) 维度：bge-m3 输出 1024 维，meta.json 的 dim 必须与实测一致；
  3) 抽查：随机取 3 个 chunk 文本重新 encode，与库内向量算相似度应≈1.0；
  4) 语料版本：meta.json 的 corpus_version 必须与 chunks.jsonl / manifest 一致。
🔍 AI 起草→本人验证：先 --limit 20 小样本跑通，再全量 92+5 篇。
降级线（V4-C）：bge-m3 下载慢或显存/内存吃紧 → 换 BAAI/bge-small-zh-v1.5（512 维），
  只改 MODEL_NAME，README 注明模型可替换。

用法：
  python index/embed_faiss.py --limit 20     # 小样本冒烟
  python index/embed_faiss.py                # 全量
依赖：pip install sentence-transformers faiss-cpu numpy
输出：index/index.faiss + index/embed_meta.json
"""
import argparse
import datetime
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_DIR = Path(__file__).resolve().parent
MODEL_NAME = "BAAI/bge-m3"          # 🧠 降级换 "BAAI/bge-small-zh-v1.5"
BATCH_SIZE = 16                      # 6GB 显存不够就改 8 或转 CPU（自动回退）


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="只编码前 N 个 chunk（冒烟用）")
    args = ap.parse_args()

    chunks_path = INDEX_DIR / "chunks.jsonl"
    chunks = [json.loads(line) for line in chunks_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.limit:
        chunks = chunks[: args.limit]
    if not chunks:
        raise SystemExit("chunks.jsonl 为空：先跑 parse_split.py")

    model = SentenceTransformer(MODEL_NAME, device="cpu")  # 🧠 试过 GPU 再决定是否改 cuda
    texts = [c["text"] for c in chunks]
    vecs = model.encode(texts, batch_size=BATCH_SIZE, normalize_embeddings=True,
                        show_progress_bar=True)
    vecs = np.asarray(vecs, dtype="float32")

    index = faiss.IndexFlatIP(vecs.shape[1])   # 内积 + 已归一化 = 余弦
    index.add(vecs)
    faiss.write_index(index, str(INDEX_DIR / "index.faiss"))

    meta = {
        "model": MODEL_NAME,
        "dim": int(vecs.shape[1]),
        "normalized": True,
        "similarity": "cosine (L2-normalized inner product)",
        "corpus_version": sorted({c["corpus_version"] for c in chunks}),
        "num_chunks": len(chunks),
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "reproduce": f"python index/embed_faiss.py{' --limit ' + str(args.limit) if args.limit else ''}",
    }
    (INDEX_DIR / "embed_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"\n✅ index.faiss（{index.ntotal} 向量）+ embed_meta.json 已生成")
    # 🧠 抽查未实现：自己用 numpy 取 3 行算一遍相似度，确认≈1.0 后再进下一步


if __name__ == "__main__":
    main()

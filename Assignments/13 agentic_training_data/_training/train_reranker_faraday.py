"""
Tier 2 — Faraday-domain cross-encoder reranker fine-tuning.

Same labelled (concept-anchor, chunk) pos/hard-neg strategy as train_reranker.py,
but on Faraday data. Saves to _models/reranker_v1_faraday/.
"""
from __future__ import annotations
import json, random, re
from pathlib import Path
import torch

ROOT      = Path(__file__).resolve().parents[1]
DATA      = ROOT / "training_data"
OUT_DIR   = ROOT / "_models" / "reranker_v1_faraday"
BASE      = "cross-encoder/ms-marco-MiniLM-L-6-v2"
SEED      = 13
EPOCHS    = 1
BATCH     = 16
LR        = 2e-5
MAX_PAIRS = 6000
MAX_CONCEPTS_PER_CHUNK = 8

_STOP_CONCEPTS = {
    "a", "an", "the", "and", "or", "on", "in", "of", "to",
    "degree", "figure", "plate", "part", "section", "experiment",
}

random.seed(SEED); torch.manual_seed(SEED)

def load(name): return json.load(open(DATA / f"{name}.json", encoding="utf-8"))


def mine_examples():
    chunks   = load("faraday_rag_chunks")
    concepts = load("faraday_concept_graph")
    items = []
    for c in concepts:
        n = (c.get("concept") or "").strip()
        if len(n) < 4 or n.lower() in _STOP_CONCEPTS:
            continue
        items.append((n, c, re.compile(r"\b" + re.escape(n) + r"\b", re.I)))

    chunk_hits: list[set[str]] = []
    for ch in chunks:
        text = (ch.get("text") or "").strip()
        if len(text) < 80:
            chunk_hits.append(set())
            continue
        hits = set()
        for cname, _c, pat in items:
            if pat.search(text):
                hits.add(cname)
                if len(hits) >= MAX_CONCEPTS_PER_CHUNK:
                    break
        chunk_hits.append(hits)

    cdef_by_name = {n: c for n, c, _ in items}

    pos: list[tuple[str, str]] = []
    for ch, hits in zip(chunks, chunk_hits):
        text = (ch.get("text") or "").strip()
        if len(text) < 80:
            continue
        for cname in hits:
            cdef = cdef_by_name[cname]
            anchor = f"{cname}: {cdef.get('definition') or cname}"
            pos.append((anchor, text[:1000]))
    random.shuffle(pos)
    pos = pos[: MAX_PAIRS // 2]

    neg: list[tuple[str, str]] = []
    for anchor, _ in pos:
        cname = anchor.split(":", 1)[0].strip()
        for _ in range(8):
            j = random.randrange(len(chunks))
            if cname in chunk_hits[j]:
                continue
            t = (chunks[j].get("text") or "").strip()
            if len(t) >= 80:
                neg.append((anchor, t[:1000]))
                break

    pos_ex = [(a, b, 1.0) for a, b in pos]
    neg_ex = [(a, b, 0.0) for a, b in neg]
    examples = pos_ex + neg_ex
    random.shuffle(examples)
    return examples


def main() -> None:
    from sentence_transformers import CrossEncoder, InputExample
    from torch.utils.data import DataLoader

    rows = mine_examples()
    print(f"Faraday examples: {len(rows)} (pos+neg)")
    if len(rows) < 200:
        raise SystemExit("not enough Faraday examples; aborting.")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CrossEncoder(BASE, num_labels=1, max_length=512, device=device)
    print(f"device={device}  base={BASE}")

    train_examples = [InputExample(texts=[a, b], label=lbl) for a, b, lbl in rows]
    loader = DataLoader(train_examples, shuffle=True, batch_size=BATCH)

    OUT_DIR.parent.mkdir(parents=True, exist_ok=True)
    model.fit(
        train_dataloader=loader,
        epochs=EPOCHS,
        warmup_steps=int(0.1 * len(loader)),
        optimizer_params={"lr": LR},
        show_progress_bar=True,
        output_path=str(OUT_DIR),
    )
    # sentence-transformers v5: output_path only saves when an evaluator is
    # configured (save_best_model=True). Without one we must save explicitly.
    model.save(str(OUT_DIR))
    print(f"SAVED: {OUT_DIR}")


if __name__ == "__main__":
    main()

"""
Tier 2 — Fine-tune the cross-encoder reranker on labelled (query, chunk) pairs.

Mining strategy:
  - Positive (label=1.0): (concept + ': ' + definition, chunk.text)
                         when concept ∈ chunk.concepts.
  - Hard negative (label=0.0): same anchor, but a random *different* chunk
    that does NOT list this concept.
Output:
  IRTM-Admin/source/13 agentic_training_data/_models/reranker_v1/
"""
from __future__ import annotations
import json, random, re
from pathlib import Path
import torch

ROOT      = Path(__file__).resolve().parents[1]
DATA      = ROOT / "training_data"
OUT_DIR   = ROOT / "_models" / "reranker_v1"
BASE      = "cross-encoder/ms-marco-MiniLM-L-6-v2"
SEED      = 13
EPOCHS    = 1
BATCH     = 16
LR        = 2e-5
MAX_PAIRS = 6000   # half pos, half neg
MAX_CONCEPTS_PER_CHUNK = 8

_STOP_CONCEPTS = {
    "code", "server", "a server", "tool", "tools", "data", "system",
    "network", "protocol", "protocols", "configuration", "device",
    "user", "client", "computer", "file", "program", "process",
}

random.seed(SEED); torch.manual_seed(SEED)

def load(name): return json.load(open(DATA / f"{name}.json", encoding="utf-8"))


def mine_examples():
    """Substring-based positive + hard-negative mining.

    Positive: graph concept whose name appears as a whole word in the chunk text.
    Negative: same anchor paired with a random chunk whose text does NOT
              contain that concept name.
    """
    chunks   = load("cyber_rag_chunks")
    concepts = load("cyber_concept_graph")
    items = []
    for c in concepts:
        n = (c.get("concept") or "").strip()
        if len(n) < 4 or n.lower() in _STOP_CONCEPTS:
            continue
        items.append((n, c, re.compile(r"\b" + re.escape(n) + r"\b", re.I)))

    # Pre-compute, per chunk, which graph-concept names occur in its text.
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
    print(f"mined: {len(rows)} examples (pos+neg)")
    if len(rows) < 200:
        raise SystemExit("not enough examples; aborting.")

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

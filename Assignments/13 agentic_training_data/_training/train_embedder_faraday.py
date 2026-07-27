"""
Tier 2 — Faraday-domain bi-encoder fine-tuning.

Identical strategy to train_embedder.py, but mines positive pairs from
faraday_concept_graph.json × faraday_rag_chunks.json and saves to
_models/embedder_v1_faraday/. Train AFTER the cyber embedder if you want a
clean comparison; the two are independent.
"""
from __future__ import annotations
import json, random, re
from pathlib import Path
import torch

ROOT      = Path(__file__).resolve().parents[1]
DATA      = ROOT / "training_data"
OUT_DIR   = ROOT / "_models" / "embedder_v1_faraday"
BASE      = "sentence-transformers/all-MiniLM-L6-v2"
SEED      = 13
EPOCHS    = 1
BATCH     = 32
LR        = 2e-5
MAX_PAIRS = 8000
MAX_CONCEPTS_PER_CHUNK = 8

# Words that appear in almost every Faraday paragraph and would over-match.
_STOP_CONCEPTS = {
    "a", "an", "the", "and", "or", "on", "in", "of", "to",
    "degree", "figure", "plate", "part", "section", "experiment",
}

random.seed(SEED); torch.manual_seed(SEED)

def load(name): return json.load(open(DATA / f"{name}.json", encoding="utf-8"))


def mine_pairs() -> list[tuple[str, str]]:
    """Mine positives by whole-word substring match of graph concept names
    against chunk text. See train_embedder.py for the rationale.
    """
    chunks   = load("faraday_rag_chunks")
    concepts = load("faraday_concept_graph")
    items = []
    for c in concepts:
        n = (c.get("concept") or "").strip()
        if len(n) < 4 or n.lower() in _STOP_CONCEPTS:
            continue
        items.append((n, c, re.compile(r"\b" + re.escape(n) + r"\b", re.I)))
    pairs: list[tuple[str, str]] = []
    for ch in chunks:
        text = (ch.get("text") or "").strip()
        if len(text) < 80:
            continue
        seen = set()
        for cname, cdef, pat in items:
            if cname in seen or not pat.search(text):
                continue
            seen.add(cname)
            anchor = f"{cname}: {cdef.get('definition') or cname}"
            pairs.append((anchor, text[:1000]))
            if len(seen) >= MAX_CONCEPTS_PER_CHUNK:
                break
    random.shuffle(pairs)
    return pairs[:MAX_PAIRS]


def main() -> None:
    from sentence_transformers import SentenceTransformer, InputExample, losses
    from torch.utils.data import DataLoader

    pairs = mine_pairs()
    print(f"Faraday pairs: {len(pairs)}")
    if len(pairs) < 200:
        raise SystemExit("not enough Faraday pairs to train; aborting.")

    model = SentenceTransformer(BASE)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"device={device}  base={BASE}")

    train_examples = [InputExample(texts=[a, p]) for a, p in pairs]
    loader = DataLoader(train_examples, shuffle=True, batch_size=BATCH)
    loss   = losses.MultipleNegativesRankingLoss(model)

    OUT_DIR.parent.mkdir(parents=True, exist_ok=True)
    model.fit(
        train_objectives=[(loader, loss)],
        epochs=EPOCHS,
        warmup_steps=int(0.1 * len(loader)),
        optimizer_params={"lr": LR},
        show_progress_bar=True,
        output_path=str(OUT_DIR),
    )
    print(f"SAVED: {OUT_DIR}")


if __name__ == "__main__":
    main()

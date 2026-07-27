"""
Tier 2 — Fine-tune the bi-encoder (sentence-transformers) on cyber-domain
positive pairs mined from the concept graph + RAG chunks.

Mining strategy:
  - Pos pair: (concept + ': ' + definition,   chunk.text)  for every chunk that
    lists that concept in `chunk.concepts`.
  - In-batch negatives via MultipleNegativesRankingLoss.
Output:
  IRTM-Admin/source/13 agentic_training_data/_models/embedder_v1/
"""
from __future__ import annotations
import json, random, re
from pathlib import Path
import torch

ROOT      = Path(__file__).resolve().parents[1]
DATA      = ROOT / "training_data"
OUT_DIR   = ROOT / "_models" / "embedder_v1"
BASE      = "sentence-transformers/all-MiniLM-L6-v2"
SEED      = 13
EPOCHS    = 1
BATCH     = 32
LR        = 2e-5
MAX_PAIRS = 8000
MAX_CONCEPTS_PER_CHUNK = 8

# Generic / overly-short concept names that would over-match in cyber chunk text.
_STOP_CONCEPTS = {
    "code", "server", "a server", "tool", "tools", "data", "system",
    "network", "protocol", "protocols", "configuration", "device",
    "user", "client", "computer", "file", "program", "process",
}

random.seed(SEED); torch.manual_seed(SEED)

def load(name): return json.load(open(DATA / f"{name}.json", encoding="utf-8"))


def mine_pairs() -> list[tuple[str, str]]:
    """Mine (concept-anchor, chunk-text) positives by whole-word substring match
    of every graph concept name against every chunk text. The previous strategy
    (chunk.concepts ∩ graph) only found ~36 pairs because chunk.concepts is
    populated with section labels ("mitigation", "introduction") rather than
    graph terms.
    """
    chunks   = load("cyber_rag_chunks")
    concepts = load("cyber_concept_graph")
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
    print(f"mined pairs: {len(pairs)}")
    if len(pairs) < 200:
        raise SystemExit("not enough pairs to train; aborting.")

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

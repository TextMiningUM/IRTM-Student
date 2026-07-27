"""Run RAG and KG-RAG over the Cadzand booklet for the 15 eval questions.

Uses the EN_* artifacts (English) so prompts and grounding share one language:
  EN_cadzand_rag_chunks.jsonl       -> dense retrieval corpus
  EN_cadzand_knowledge_graph.json   -> KG augmentation
  EN_cadzand_eval_questions.json    -> questions + expected_points (English)

Two pipelines, both using gpt-4o-mini for the answer + an LLM-judge:
  RAG     : top-k cosine over OpenAI text-embedding-3-small chunk vectors.
  KG-RAG  : RAG hits + KG expansion (nodes mentioned in retrieved chunks via
            their `mentioned_in_chunks` provenance + entity-name lookup against
            the question text).

Outputs:
  cadzand_rag_results.json
  cadzand_kg_rag_results.json

Idempotent: skips a stage if its output file already exists.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

CAD = Path(__file__).resolve().parents[1] / "Cadzand"
ROOT = Path(__file__).resolve().parents[3]

try:
    from dotenv import load_dotenv
    for cand in [ROOT / "IRTM-Admin" / ".env", ROOT / ".env"]:
        if cand.is_file():
            load_dotenv(cand, override=False)
            break
except ImportError:
    pass

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("OPENAI_API_KEY not set.")

from openai import OpenAI

client = OpenAI()
ANS_MODEL = "gpt-4o-mini"
JUDGE_MODEL = "gpt-4o-mini"
EMBED_MODEL = "text-embedding-3-small"

QFILE = CAD / os.environ.get("CAD_QFILE", "EN_cadzand_eval_questions.json")
CHUNKS_FILE = CAD / os.environ.get("CAD_CHUNKS", "EN_cadzand_rag_chunks.jsonl")
KG_FILE = CAD / os.environ.get("CAD_KG", "EN_cadzand_knowledge_graph.json")
RAG_OUT = CAD / os.environ.get("CAD_RAG_OUT", "cadzand_rag_results.json")
KGRAG_OUT = CAD / os.environ.get("CAD_KGRAG_OUT", "cadzand_kg_rag_results.json")

ANSWER_SYS = (
    "You answer the user's question using ONLY the provided context. "
    "Be concrete: cite specific names, years, numbers from the context. "
    "If the context does not contain the answer, say 'I cannot find this in the source.' "
    "Do not invent facts."
)

JUDGE_SYS = (
    "You are a strict fact-checker. You receive a question, a model answer, "
    "and a list of expected facts (ground truth from a local source booklet). "
    "For each expected fact, decide HIT or MISS (spelling/phrasing variants count, "
    "but wrong names/years/numbers do NOT count as a hit). "
    "Then give one overall verdict: CORRECT (all facts hit), PARTIAL (>=1 hit, "
    ">=1 missing/wrong), WRONG (no hits but says 'don't know'), HALLUCINATED "
    "(no hits and invents plausible-sounding nonsense). "
    "Reply with JSON only: "
    '{"per_point":[{"point":"...","verdict":"HIT|MISS","reason":"short"}],'
    '"overall":"CORRECT|PARTIAL|WRONG|HALLUCINATED","note":"short"}'
)


def embed_batch(texts: list[str]) -> np.ndarray:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return np.array([d.embedding for d in resp.data], dtype=np.float32)


def cosine_topk(q: np.ndarray, M: np.ndarray, k: int) -> list[int]:
    qn = q / (np.linalg.norm(q) + 1e-9)
    Mn = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    sims = Mn @ qn
    return np.argsort(-sims)[:k].tolist()


def load_chunks() -> list[dict]:
    chunks = []
    for line in CHUNKS_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            chunks.append(json.loads(line))
    return chunks


def llm_judge(question: str, answer: str, expected: list[str]) -> dict:
    user = (
        f"Question: {question}\n\n"
        f"Model answer:\n{answer}\n\n"
        f"Expected facts:\n- " + "\n- ".join(expected) + "\n\n"
        "Return JSON per the system schema."
    )
    last = None
    for attempt in range(4):
        try:
            resp = client.chat.completions.create(
                model=JUDGE_MODEL, temperature=0.0,
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": JUDGE_SYS}, {"role": "user", "content": user}],
                timeout=60,
            )
            return json.loads(resp.choices[0].message.content or "{}")
        except Exception as e:
            last = e
            time.sleep(2 ** attempt)
    return {"error": str(last), "per_point": [], "overall": "ERROR"}


def answer_with_context(question: str, context: str) -> str:
    user = f"Context:\n{context}\n\nQuestion: {question}"
    last = None
    for attempt in range(4):
        try:
            resp = client.chat.completions.create(
                model=ANS_MODEL, temperature=0.0,
                messages=[{"role": "system", "content": ANSWER_SYS}, {"role": "user", "content": user}],
                timeout=60,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            last = e
            time.sleep(2 ** attempt)
    return f"<error: {last}>"


def embed_with_retry(texts: list[str]) -> np.ndarray:
    last = None
    for attempt in range(4):
        try:
            return embed_batch(texts)
        except Exception as e:
            last = e
            time.sleep(2 ** attempt)
    raise last


def kg_index(kg: dict) -> tuple[dict, dict]:
    """Return (node_by_id, chunk_to_nodes) maps."""
    node_by_id = {n["id"]: n for n in kg.get("nodes", [])}
    chunk_to_nodes: dict[str, list[str]] = {}
    for n in kg.get("nodes", []):
        for cid in n.get("chunks", []) or n.get("mentioned_in_chunks", []) or []:
            chunk_to_nodes.setdefault(cid, []).append(n["id"])
    return node_by_id, chunk_to_nodes


def kg_lookup_by_question(kg: dict, question: str) -> list[str]:
    """Find node ids whose name/aliases appear (case-insensitive) in the question."""
    q = question.lower()
    hits = []
    for n in kg.get("nodes", []):
        names = [n.get("label", ""), n.get("name", "")] + list(n.get("aliases", []) or [])
        for name in names:
            if name and len(name) >= 3 and name.lower() in q:
                hits.append(n["id"])
                break
    return hits


def edges_for_nodes(kg: dict, node_ids: set[str], cap: int = 12) -> list[dict]:
    out = []
    for e in kg.get("edges", []):
        if e.get("source") in node_ids or e.get("target") in node_ids:
            out.append(e)
            if len(out) >= cap:
                break
    return out


def format_kg_block(node_by_id: dict, node_ids: list[str], edges: list[dict]) -> str:
    lines = ["# Knowledge graph facts:"]
    seen = set()
    for nid in node_ids:
        if nid in seen:
            continue
        seen.add(nid)
        n = node_by_id.get(nid)
        if not n:
            continue
        nm = n.get("label") or n.get("name") or "?"
        bits = [f"- [{n.get('type','?')}] {nm}"]
        if n.get("description"):
            bits.append(f": {n['description']}")
        lines.append("".join(bits))
    if edges:
        lines.append("# Relations:")
        for e in edges:
            sn = node_by_id.get(e.get("source", ""), {})
            tn = node_by_id.get(e.get("target", ""), {})
            s = sn.get("label") or sn.get("name") or e.get("source", "?")
            t = tn.get("label") or tn.get("name") or e.get("target", "?")
            rel = e.get("relation") or e.get("type") or "RELATED_TO"
            extra = e.get("description") or e.get("note") or ""
            lines.append(f"- {s} —[{rel}]→ {t}" + (f" ({extra})" if extra else ""))
    return "\n".join(lines)


def _load_done(partial_path: Path) -> tuple[list[dict], set[str]]:
    rows = []
    done = set()
    if partial_path.exists():
        for line in partial_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                rows.append(r)
                done.add(r["id"])
    return rows, done


def _aggregate(rows: list[dict], n_questions: int, top_k: int, kind: str) -> dict:
    overall = {"CORRECT": 0, "PARTIAL": 0, "WRONG": 0, "HALLUCINATED": 0, "ERROR": 0}
    total_pts = 0
    judge_hits = 0
    for r in rows:
        v = r.get("judge_overall", "ERROR")
        overall[v] = overall.get(v, 0) + 1
        per = r.get("judge_per_point", []) or []
        total_pts += len(per)
        judge_hits += sum(1 for p in per if p.get("verdict") == "HIT")
    return {
        "kind": kind,
        "answer_model": ANS_MODEL, "judge_model": JUDGE_MODEL, "embed_model": EMBED_MODEL,
        "top_k": top_k,
        "summary": {"n_questions": n_questions, "n_points": total_pts,
                    "judge_hits": judge_hits, "overall": overall},
        "rows": rows,
    }


def run_rag(questions: list[dict], chunks: list[dict], chunk_emb: np.ndarray, top_k: int = 5) -> dict:
    partial = RAG_OUT.with_suffix(".partial.jsonl")
    rows, done = _load_done(partial)
    if done:
        print(f"[RAG] resuming, {len(done)} already done")
    with partial.open("a", encoding="utf-8") as fp:
        for q in questions:
            if q["id"] in done:
                continue
            q_emb = embed_with_retry([q["question"]])[0]
            idxs = cosine_topk(q_emb, chunk_emb, top_k)
            ctx_parts = [f"[{chunks[i]['id']}] {chunks[i].get('title','')}\n{chunks[i]['text']}" for i in idxs]
            ctx = "\n\n".join(ctx_parts)
            ans = answer_with_context(q["question"], ctx)
            judge = llm_judge(q["question"], ans, q["expected_points"])
            per = judge.get("per_point", []) or []
            hits = sum(1 for p in per if p.get("verdict") == "HIT")
            verdict = judge.get("overall", "ERROR")
            row = {
                "id": q["id"],
                "question": q["question"],
                "retrieved_ids": [chunks[i]["id"] for i in idxs],
                "answer": ans.strip(),
                "judge_per_point": per,
                "judge_overall": verdict,
                "judge_note": judge.get("note", ""),
            }
            rows.append(row)
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")
            fp.flush()
            print(f"[RAG  {q['id']}] hits {hits}/{len(q['expected_points'])}  {verdict}", flush=True)
    return _aggregate(rows, len(questions), top_k, "rag")


def run_kg_rag(questions: list[dict], chunks: list[dict], chunk_emb: np.ndarray,
               kg: dict, top_k: int = 5) -> dict:
    node_by_id, chunk_to_nodes = kg_index(kg)
    partial = KGRAG_OUT.with_suffix(".partial.jsonl")
    rows, done = _load_done(partial)
    if done:
        print(f"[KG-RAG] resuming, {len(done)} already done")
    with partial.open("a", encoding="utf-8") as fp:
        for q in questions:
            if q["id"] in done:
                continue
            q_emb = embed_with_retry([q["question"]])[0]
            idxs = cosine_topk(q_emb, chunk_emb, top_k)
            node_ids: list[str] = []
            node_set: set[str] = set()
            for nid in kg_lookup_by_question(kg, q["question"]):
                if nid not in node_set:
                    node_ids.append(nid); node_set.add(nid)
            for i in idxs:
                for nid in chunk_to_nodes.get(chunks[i]["id"], []):
                    if nid not in node_set:
                        node_ids.append(nid); node_set.add(nid)
            edges = edges_for_nodes(kg, node_set, cap=15)
            kg_block = format_kg_block(node_by_id, node_ids, edges)
            ctx_parts = [f"[{chunks[i]['id']}] {chunks[i].get('title','')}\n{chunks[i]['text']}" for i in idxs]
            ctx = "\n\n".join(ctx_parts) + "\n\n" + kg_block
            ans = answer_with_context(q["question"], ctx)
            judge = llm_judge(q["question"], ans, q["expected_points"])
            per = judge.get("per_point", []) or []
            hits = sum(1 for p in per if p.get("verdict") == "HIT")
            verdict = judge.get("overall", "ERROR")
            row = {
                "id": q["id"],
                "question": q["question"],
                "retrieved_ids": [chunks[i]["id"] for i in idxs],
                "kg_node_ids": node_ids,
                "kg_edge_count": len(edges),
                "answer": ans.strip(),
                "judge_per_point": per,
                "judge_overall": verdict,
                "judge_note": judge.get("note", ""),
            }
            rows.append(row)
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")
            fp.flush()
            print(f"[KGRAG {q['id']}] hits {hits}/{len(q['expected_points'])}  {verdict}  "
                  f"(nodes={len(node_ids)}, edges={len(edges)})", flush=True)
    return _aggregate(rows, len(questions), top_k, "kg_rag")


def main():
    questions = json.loads(QFILE.read_text(encoding="utf-8"))
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks, {len(questions)} questions")

    print("Embedding chunks...")
    texts = [(c.get("title", "") + "\n" + c.get("text", "")).strip() for c in chunks]
    # Batch in pieces of 64
    embs = []
    for i in range(0, len(texts), 64):
        embs.append(embed_batch(texts[i:i+64]))
    chunk_emb = np.vstack(embs)
    print(f"chunk_emb shape: {chunk_emb.shape}")

    if RAG_OUT.exists() and RAG_OUT.stat().st_size > 100:
        print(f"[RAG] cached: {RAG_OUT.name}")
    else:
        rag = run_rag(questions, chunks, chunk_emb, top_k=5)
        RAG_OUT.write_text(json.dumps(rag, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[RAG] wrote {RAG_OUT.name}: {rag['summary']}")

    if KGRAG_OUT.exists() and KGRAG_OUT.stat().st_size > 100:
        print(f"[KG-RAG] cached: {KGRAG_OUT.name}")
    else:
        kg = json.loads(KG_FILE.read_text(encoding="utf-8"))
        kgrag = run_kg_rag(questions, chunks, chunk_emb, kg, top_k=5)
        KGRAG_OUT.write_text(json.dumps(kgrag, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[KG-RAG] wrote {KGRAG_OUT.name}: {kgrag['summary']}")


if __name__ == "__main__":
    main()

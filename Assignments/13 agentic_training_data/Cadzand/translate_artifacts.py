"""Translate all Dutch Cadzand artifacts to English and cache as EN_*.

Sources & targets (in IRTM-Admin/source/13 agentic_training_data/Cadzand/):
  cadzand_booklet.txt           -> EN_cadzand_booklet.txt           (free text)
  cadzand_eval_questions.json   -> EN_cadzand_eval_questions.json   (per-field translation)
  cadzand_rag_chunks.jsonl      -> EN_cadzand_rag_chunks.jsonl      (per-chunk translation)
  cadzand_knowledge_graph.json  -> EN_cadzand_knowledge_graph.json  (per-node/edge translation)

Idempotent: skips a target if it already exists and is non-trivial in size.
Proper names, dates, place names, IDs are preserved verbatim by the prompt.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CAD = Path(__file__).resolve().parents[1] / "Cadzand"

try:
    from dotenv import load_dotenv
    for cand in [ROOT / "IRTM-Admin-2025-2026" / ".env", ROOT / ".env"]:
        if cand.is_file():
            load_dotenv(cand, override=False)
            break
except ImportError:
    pass

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("OPENAI_API_KEY not set.")

from openai import OpenAI

client = OpenAI()
MODEL = "gpt-4o-mini"

TRANSLATE_SYS = (
    "You are a careful Dutch->English translator. "
    "Preserve all proper names, place names, person names, dates, years, numbers, "
    "and identifiers exactly as they appear (e.g. Cadzand, Sint-Lambertustoren, "
    "St-Baafsabdij, Maximiliaan van Oostenrijk, 1492, 1809). "
    "Where 17th-century Dutch with archaic spelling appears, render it in readable "
    "modern English without losing factual content. "
    "Do not summarise. Do not add commentary. Do not omit details."
)


def translate_text(text: str) -> str:
    if not text or not text.strip():
        return text
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0.0,
        messages=[
            {"role": "system", "content": TRANSLATE_SYS},
            {"role": "user", "content": text},
        ],
    )
    return resp.choices[0].message.content or ""


def translate_json_string_field(s: str) -> str:
    """Translate a single string. Empty/None pass-through."""
    if not isinstance(s, str) or not s.strip():
        return s
    return translate_text(s)


# ──────────────────────────────────────────────────────────────────────────────
# 1. Booklet plain text (already cached previously, but redo if missing).
# ──────────────────────────────────────────────────────────────────────────────
def do_booklet():
    src = CAD / "cadzand_booklet.txt"
    dst = CAD / "EN_cadzand_booklet.txt"
    if dst.exists() and dst.stat().st_size > 100:
        print(f"[booklet] cached: {dst.name}")
        return
    print(f"[booklet] translating {src.name}...")
    out = translate_text(src.read_text(encoding="utf-8"))
    dst.write_text(out, encoding="utf-8")
    print(f"[booklet] wrote {dst.name} ({len(out)} chars)")


# ──────────────────────────────────────────────────────────────────────────────
# 2. Eval questions (translate question + each expected_point; keep id).
# ──────────────────────────────────────────────────────────────────────────────
def do_questions():
    src = CAD / "cadzand_eval_questions.json"
    dst = CAD / "EN_cadzand_eval_questions.json"
    if dst.exists() and dst.stat().st_size > 100:
        print(f"[questions] cached: {dst.name}")
        return
    print(f"[questions] translating {src.name}...")
    qs = json.loads(src.read_text(encoding="utf-8"))
    out = []
    for q in qs:
        out.append({
            "id": q["id"],
            "question": translate_json_string_field(q.get("question", "")),
            "expected_points": [translate_json_string_field(p) for p in q.get("expected_points", [])],
        })
        print(f"  - {q['id']} done")
    dst.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[questions] wrote {dst.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 3. RAG chunks JSONL (translate `text` + `title` per chunk; keep metadata as-is).
# ──────────────────────────────────────────────────────────────────────────────
def do_chunks():
    src = CAD / "cadzand_rag_chunks.jsonl"
    dst = CAD / "EN_cadzand_rag_chunks.jsonl"
    if dst.exists() and dst.stat().st_size > 100:
        print(f"[chunks] cached: {dst.name}")
        return
    print(f"[chunks] translating {src.name}...")
    lines = src.read_text(encoding="utf-8").splitlines()
    out_lines = []
    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue
        rec = json.loads(line)
        rec["title"] = translate_json_string_field(rec.get("title", ""))
        rec["text"] = translate_json_string_field(rec.get("text", ""))
        out_lines.append(json.dumps(rec, ensure_ascii=False))
        print(f"  - chunk {i}/{len(lines)} ({rec.get('id','?')})")
    dst.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"[chunks] wrote {dst.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 4. Knowledge graph (translate node `name`/`label`/`description`, edge `description`).
# ──────────────────────────────────────────────────────────────────────────────
def do_kg():
    src = CAD / "cadzand_knowledge_graph.json"
    dst = CAD / "EN_cadzand_knowledge_graph.json"
    if dst.exists() and dst.stat().st_size > 100:
        print(f"[kg] cached: {dst.name}")
        return
    print(f"[kg] translating {src.name}...")
    kg = json.loads(src.read_text(encoding="utf-8"))

    if "description" in kg and isinstance(kg["description"], str):
        kg["description"] = translate_json_string_field(kg["description"])

    # Translate likely free-text fields on each node, keep ids/types/refs.
    free_text_keys = {"name", "label", "description", "definition", "summary", "alias", "alt_name"}
    nodes = kg.get("nodes", [])
    for i, n in enumerate(nodes, 1):
        for k in list(n.keys()):
            if k in free_text_keys and isinstance(n[k], str):
                n[k] = translate_json_string_field(n[k])
            elif k == "aliases" and isinstance(n[k], list):
                n[k] = [translate_json_string_field(a) for a in n[k]]
        if i % 5 == 0 or i == len(nodes):
            print(f"  - nodes {i}/{len(nodes)}")

    edges = kg.get("edges", [])
    for i, e in enumerate(edges, 1):
        for k in list(e.keys()):
            if k in {"description", "label", "note"} and isinstance(e[k], str):
                e[k] = translate_json_string_field(e[k])
        if i % 10 == 0 or i == len(edges):
            print(f"  - edges {i}/{len(edges)}")

    dst.write_text(json.dumps(kg, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[kg] wrote {dst.name}")


def main():
    do_booklet()
    do_questions()
    do_chunks()
    do_kg()
    print("\nAll EN_* artifacts ready in", CAD)


if __name__ == "__main__":
    main()

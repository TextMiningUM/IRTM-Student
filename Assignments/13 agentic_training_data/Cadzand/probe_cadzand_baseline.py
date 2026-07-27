"""Probe whether vanilla GPT-4o-mini answers the Cadzand eval questions
WITHOUT any RAG context. For each question:

  1. Ask the question raw (no context).
  2. Substring-check expected_points (cheap baseline).
  3. LLM-judge each expected_point semantically (verdict: HIT / MISS) and
     overall correctness (CORRECT / PARTIAL / WRONG / HALLUCINATED).

Outputs per-question detail + summary table.
"""
import json
import os
import re
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    sys.exit("openai package missing. pip install openai")

# Load OPENAI_API_KEY from .env (IRTM-Admin/.env, then repo root as fallback).
try:
    from dotenv import load_dotenv
    _here = Path(__file__).resolve()
    for _cand in [
        _here.parents[3] / ".env",   # IRTM-Admin-2025-2026/.env
        _here.parents[4] / ".env",   # repo root /.env
    ]:
        if _cand.is_file():
            load_dotenv(_cand, override=False)
            break
except ImportError:
    pass  # dotenv optional; OPENAI_API_KEY may already be in env

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("OPENAI_API_KEY not set (checked .env and process env).")

_CAD = Path(__file__).resolve().parents[1] / "Cadzand"
QFILE = _CAD / os.environ.get("CAD_QFILE", "cadzand_eval_questions.json")
BOOKLET = _CAD / os.environ.get("CAD_BOOKLET", "cadzand_booklet.txt")
OUT_FILE = _CAD / os.environ.get("CAD_BASELINE_OUT", "cadzand_baseline_no_rag.json")
LANG = os.environ.get("CAD_LANG", "nl").lower()  # 'nl' or 'en'
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
JUDGE_MODEL = os.environ.get("OPENAI_JUDGE_MODEL", "gpt-4o-mini")

if LANG == "en":
    SYSTEM = (
        "Answer the question as precisely as possible in English. "
        "Give concrete names, years and numbers. "
        "If you are not sure, say so explicitly — do not invent anything."
    )
    JUDGE_SYSTEM = (
        "You are a strict fact-checker. You receive a question, the model's answer, "
        "and a list of expected facts (ground truth from a local source booklet). "
        "For each expected fact decide whether it appears correctly in the answer "
        "(spelling/phrasing variants count, but wrong names/years/numbers do NOT count as hit). "
        "Then give one overall verdict: CORRECT (all facts correct), PARTIAL (>=1 correct, "
        ">=1 wrong/missing), WRONG (no facts correct but politely says 'I don't know'), or "
        "HALLUCINATED (no facts correct AND fabricated plausible-sounding nonsense). "
        "Reply with JSON only: "
        '{"per_point":[{"point":"...","verdict":"HIT|MISS","reason":"short"}],'
        '"overall":"CORRECT|PARTIAL|WRONG|HALLUCINATED","note":"short"}'
    )
else:
    SYSTEM = (
        "Beantwoord de vraag zo precies mogelijk in het Nederlands. "
        "Geef concrete namen, jaartallen en getallen. "
        "Als je het niet zeker weet, zeg dat dan expliciet — verzin niets."
    )
    JUDGE_SYSTEM = (
        "Je bent een strenge feiten-rechter. Je krijgt een vraag, het modelantwoord "
        "en een lijst van verwachte feiten (ground-truth uit een lokaal bronboekje). "
        "Beoordeel per verwacht feit of het correct in het antwoord voorkomt "
        "(spellingvariaties en gelijkwaardige formuleringen tellen mee, maar verkeerde "
        "namen/jaartallen/getallen tellen NIET als hit). "
        "Geef daarna één eindoordeel: CORRECT (alle feiten goed), PARTIAL (≥1 goed, "
        "≥1 fout/ontbrekend), WRONG (geen feiten goed maar netjes 'weet niet'), of "
        "HALLUCINATED (geen feiten goed én verzonnen plausibele onzin). "
        "Antwoord uitsluitend in JSON: "
        '{"per_point":[{"point":"...","verdict":"HIT|MISS","reason":"kort"}],'
        '"overall":"CORRECT|PARTIAL|WRONG|HALLUCINATED","note":"kort"}'
    )


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def point_hit(answer: str, point: str) -> bool:
    a = norm(answer)
    # Split point on spaces and require ALL non-trivial tokens to appear.
    tokens = [t for t in norm(point).split() if len(t) >= 3 and t not in {"van", "een", "het", "der", "tot", "met", "uit"}]
    return all(t in a for t in tokens) if tokens else False


def llm_judge(client: "OpenAI", question: str, answer: str, expected: list[str]) -> dict:
    """Ask the judge model to verify each expected_point semantically."""
    user = (
        f"Vraag: {question}\n\n"
        f"Antwoord van model:\n{answer}\n\n"
        f"Verwachte feiten:\n- " + "\n- ".join(expected) + "\n\n"
        "Geef je oordeel als JSON volgens het schema in de systeem-instructie."
    )
    try:
        resp = client.chat.completions.create(
            model=JUDGE_MODEL,
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM},
                {"role": "user", "content": user},
            ],
        )
        return json.loads(resp.choices[0].message.content or "{}")
    except Exception as e:
        return {"error": str(e), "per_point": [], "overall": "ERROR"}


def main() -> int:
    questions = json.loads(QFILE.read_text(encoding="utf-8"))
    client = OpenAI()

    rows = []
    total_pts = 0
    total_hits_sub = 0
    total_hits_judge = 0
    overall_counts = {"CORRECT": 0, "PARTIAL": 0, "WRONG": 0, "HALLUCINATED": 0, "ERROR": 0}
    print(f"Probing {len(questions)} Cadzand questions against {MODEL} (no RAG)")
    print(f"Judge: {JUDGE_MODEL}\n")
    for q in questions:
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": q["question"]},
                ],
            )
            ans = resp.choices[0].message.content or ""
        except Exception as e:
            ans = f"<error: {e}>"

        pts = q.get("expected_points", [])
        sub_hits = [p for p in pts if point_hit(ans, p)]
        judge = llm_judge(client, q["question"], ans, pts)
        judge_per = judge.get("per_point", []) or []
        judge_hits = [pp.get("point", "") for pp in judge_per if pp.get("verdict") == "HIT"]
        overall = judge.get("overall", "ERROR")
        overall_counts[overall] = overall_counts.get(overall, 0) + 1

        total_pts += len(pts)
        total_hits_sub += len(sub_hits)
        total_hits_judge += len(judge_hits)
        rows.append({
            "id": q["id"],
            "question": q["question"],
            "answer": ans.strip(),
            "expected_points": pts,
            "substring_hits": sub_hits,
            "judge_per_point": judge_per,
            "judge_overall": overall,
            "judge_note": judge.get("note", ""),
        })

        print(f"[{q['id']}] sub {len(sub_hits)}/{len(pts)}  judge {len(judge_hits)}/{len(pts)}  overall={overall}")
        print(f"  Q: {q['question']}")
        print(f"  A: {ans.strip()[:240]}{'…' if len(ans) > 240 else ''}")
        for pp in judge_per:
            mark = "✓" if pp.get("verdict") == "HIT" else "✗"
            print(f"    {mark} {pp.get('point','')[:80]}  — {pp.get('reason','')[:120]}")
        if judge.get("note"):
            print(f"  judge note: {judge['note'][:160]}")
        print()

    print("─" * 78)
    print(f"Substring hits : {total_hits_sub}/{total_pts}  ({total_hits_sub / max(total_pts,1):.1%})")
    print(f"Judge hits     : {total_hits_judge}/{total_pts}  ({total_hits_judge / max(total_pts,1):.1%})")
    print("Overall verdicts:")
    for k in ("CORRECT", "PARTIAL", "WRONG", "HALLUCINATED", "ERROR"):
        if overall_counts.get(k):
            print(f"  {k:13s} {overall_counts[k]}/{len(questions)}")

    out = OUT_FILE
    out.write_text(
        json.dumps(
            {"answer_model": MODEL, "judge_model": JUDGE_MODEL,
             "summary": {"n_questions": len(questions), "n_points": total_pts,
                         "substring_hits": total_hits_sub, "judge_hits": total_hits_judge,
                         "overall": overall_counts},
             "rows": rows},
            indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nWrote per-question detail to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

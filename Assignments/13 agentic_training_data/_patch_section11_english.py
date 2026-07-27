"""Patch §11 cells to display English questions throughout."""
import json
from pathlib import Path

NB = Path(r"C:\Users\jcsch\Documents\Python\UM-Courses\IRTM\IRTM-Admin\source\13 agentic_training_data\13_IRTM_From_Text_to_Agentic_Training_Data_2026_2027.ipynb")
nb = json.loads(NB.read_text(encoding="utf-8"))
cells = nb["cells"]

# --- Cell 97: eval-set DataFrame — show only English question.
NEW_97 = '''import json
import pandas as pd

questions_nl = json.loads((CAD_DIR / 'cadzand_eval_questions.json').read_text(encoding='utf-8'))
questions_en = json.loads((CAD_DIR / 'EN_cadzand_eval_questions.json').read_text(encoding='utf-8'))
en_by_id = {q['id']: q for q in questions_en}

rows = []
for q in questions_nl:
    rows.append({
        'id': q['id'],
        'question': en_by_id.get(q['id'], {}).get('question', q['question']),
        'expected facts': ' | '.join(q['expected_points']),
    })
df_q = pd.DataFrame(rows)
print(f'Total: {len(df_q)} questions, {sum(len(q["expected_points"]) for q in questions_nl)} expected facts.')
print('Note: questions are shown in English here for readability; the model was probed with the original Dutch wording (see Cadzand/cadzand_eval_questions.json).')
with pd.option_context('display.max_colwidth', 220):
    display(df_q)
'''

# --- Cell 99: show_run helper — replace question column with English lookup by id.
NEW_99 = '''baseline = json.loads((CAD_DIR / 'cadzand_baseline_no_rag.json').read_text(encoding='utf-8'))
print('Baseline summary:', baseline['summary'])

VERDICT_COLOR = {
    'CORRECT': '#c8e6c9',
    'PARTIAL': '#fff59d',
    'WRONG': '#ffcc80',
    'HALLUCINATED': '#ef9a9a',
}

def show_run(run, title):
    rows = []
    for r in run['rows']:
        per = r.get('judge_per_point', []) or []
        n_hits = sum(1 for p in per if p.get('verdict') == 'HIT')
        q_en = en_by_id.get(r['id'], {}).get('question', r['question'])
        rows.append({
            'id': r['id'],
            'verdict': r['judge_overall'],
            'fact hits': f"{n_hits}/{len(per)}",
            'question (EN)': q_en[:110],
            'answer (model — Dutch)': r['answer'][:180].replace('\\n', ' '),
        })
    df = pd.DataFrame(rows)
    styled = df.style.set_caption(title).map(
        lambda v: f'background-color:{VERDICT_COLOR.get(v,"")}', subset=['verdict']
    )
    display(styled)
    return df

df_baseline = show_run(baseline, 'Baseline — GPT-4o-mini, no retrieval')
'''

def set_source(cell, code):
    cell["source"] = code.splitlines(keepends=True)

# Sanity: verify we are patching the right cells.
src97 = "".join(cells[97].get("source", []))
src99 = "".join(cells[99].get("source", []))
assert "questions_nl = json.loads" in src97, f"cell 97 unexpected: {src97[:80]}"
assert "VERDICT_COLOR" in src99, f"cell 99 unexpected: {src99[:80]}"

set_source(cells[97], NEW_97)
set_source(cells[99], NEW_99)

NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("Patched cells 97 (eval table) and 99 (show_run helper) to English-only display.")

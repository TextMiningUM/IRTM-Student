"""Rewrite the §10.7d markdown cell to be unambiguous about Faraday-only components,
and de-duplicate the 'How to push Tier-2 further' checklist (keep it only in §10.7e).
"""
import json
from pathlib import Path

NB = Path(r"C:\Users\jcsch\Documents\Python\UM-Courses\IRTM\IRTM-Admin\source\13 agentic_training_data\13_IRTM_From_Text_to_Agentic_Training_Data_2026_2027.ipynb")
nb = json.loads(NB.read_text(encoding="utf-8"))
cells = nb["cells"]

NEW_10_7D = '''### 10.7d  Tier 2 — Critic + safety on the Faraday DPO policy (Agent-T2)

Wraps the **Faraday-trained** DPO policy (the `dpo_qwen15b_lora_faraday` adapter built in §10.7c) with the same *shape* of critic + safety pipeline as §9.7d. To be precise about what is and is not Faraday-specific in this stage:

- **Draft answer.** Comes from `faraday_results['RLHF-T2']`, i.e. the Faraday-DPO generator on top of Faraday-T2 retrieval. No cyber-trained model is in this step.
- **Critic.** `critic_review()` is `gpt-4o-mini` acting as a devil's-advocate judge against the question's own `expected_points`. The judge is a general-purpose LLM call (no Faraday weights, no cyber weights) — the *content* it judges (Faraday questions, Faraday expected facts, Faraday context) is fully Faraday.
- **Reflect-and-revise.** `reflect_and_revise()` rewrites the draft using the critic's notes and the Faraday retrieval context already attached to `RLHF-T2[i]['context']`.
- **Safety guardrail.** `safety_guardrail()` is a cyber-themed regex (`malware`, `exploit`, …) reused verbatim from §9.7. On Faraday it should rarely fire — that asymmetry is a deliberate *precision* check on the guardrail (a well-targeted filter does **not** misfire on physics text), not a leakage of cyber-trained components into the Faraday pipeline.

So §10.7d on Faraday = **Faraday-DPO output → LLM-as-critic → (mostly inert) safety regex**. The Faraday-DPO adapter is the only *learned* model in this stage and it was trained exclusively on the Faraday SFT/DPO datasets generated in §10.7b–c.

<!-- t2-expectations -->

**Expected lift (Agent-T2 vs RLHF-T2 on Faraday).** Cover/Correct +1 to +3 pp. The cyber-themed safety regex should rarely fire on Faraday — that is a *precision* signal, not a defect. Critic/reflect can recover a couple of points where the policy under-cited.

> The "How to push Tier-2 further" checklist is given once at the end of §10.7e (Full-T2) so it covers the entire Tier-2 stack rather than being repeated for each sub-stage.
'''

def find_cell_starting_with(text):
    for i, c in enumerate(cells):
        if c["cell_type"] == "markdown" and "".join(c.get("source", [])).startswith(text):
            return i
    return None

idx = find_cell_starting_with("### 10.7d")
if idx is None:
    raise SystemExit("§10.7d cell not found")

old = "".join(cells[idx].get("source", []))
print(f"Replacing cell {idx}, old length={len(old)} chars")
cells[idx]["source"] = NEW_10_7D.splitlines(keepends=True)
print(f"New length={len(NEW_10_7D)} chars")

NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("Done.")

"""Fix cell 18: add proper 8.6 Pipeline Evaluation Metrics, rename old 8.6 to 8.7."""
import json

NB = "13_IRTM_From_Text_to_Agentic_Training_Data_2025_2026.ipynb"

with open(NB, encoding="utf-8") as f:
    nb = json.load(f)
cells = nb["cells"]

# Reconstruct cell 18 cleanly from scratch up to 8.5, then add 8.6 and 8.7
SECTION_8 = """\
---

## 8. Evaluating Agentic Training Data

Generating training data is only half the challenge. Ensuring its **quality** determines whether the fine-tuned components will actually improve agent performance. Each dataset type requires its own evaluation criteria and metrics.

### 8.1 RAG Chunk Quality

| Criterion | Check |
|-----------|-------|
| Semantic coherence | Each chunk covers a single, complete concept |
| Context completeness | The chunk is understandable in isolation |
| Deduplication | Near-duplicate chunks do not dominate the index |
| Coverage | The full knowledge domain is represented |

**Metrics:** chunk overlap ratio, cosine similarity distribution, retrieval hit rate R@k

### 8.2 Reranker Triplet Quality

| Criterion | Check |
|-----------|-------|
| Hard negative difficulty | Negatives are topically similar but factually wrong |
| Positive correctness | The positive genuinely answers the query |
| Balance | Approximately equal positives and negatives per query |

**Metrics:** Mean Reciprocal Rank (MRR), NDCG@k, Precision@1

### 8.3 SFT Trajectory Quality

| Criterion | Check |
|-----------|-------|
| Step completeness | Every step has observation, thought, action, and expected result |
| Logical ordering | Steps are in the correct causal sequence |
| Tool correctness | The tool invoked is appropriate for the action |
| Diversity | Trajectories cover a wide range of scenarios and edge cases |

**Metrics:** task completion rate, step accuracy, tool selection accuracy

### 8.4 RLHF Preference Pair Quality

| Criterion | Check |
|-----------|-------|
| Clear contrast | Chosen and rejected actions are meaningfully different |
| Reasoning quality | Reasoning explains *why* the chosen action is better |
| Category balance | Security, ethical, and operational categories are balanced |
| No sycophancy | Chosen actions are correct, not just agreeable |

**Metrics:** inter-annotator agreement (Cohen's κ), reward model accuracy, policy win rate

### 8.5 Knowledge Graph Quality

| Criterion | Check |
|-----------|-------|
| Definition accuracy | Definitions are precise and domain-specific |
| Relationship completeness | Edges capture all meaningful connections |
| Category correctness | Nodes are correctly classified (tool, technique, attack, term) |

**Metrics:** node coverage, edge precision, alias recall

### 8.6  Pipeline Evaluation Metrics — How We Score Each Stage

The live demo in Sections 9 and 10 evaluates every pipeline stage with five complementary metrics.
Together they form the per-stage `score` that drives the overview table.

| Metric | Function | What it measures |
|---|---|---|
| **Faithfulness** | `faithfulness(answer, context)` | Token-overlap fraction: how much of the answer is grounded in retrieved evidence |
| **Answer relevance** | `answer_relevance(question, answer)` | Token-overlap fraction: how directly the answer addresses the question |
| **Safety score** | `safety_check(answer)` | Penalises offensive or policy-violating phrasing (1.0 = fully safe) |
| **Expected-point coverage** | `coverage_with_alternatives(answer, points)` | Fraction of gold benchmark points present in the answer |
| **LLM-as-a-judge** | `llm_judge(question, answer)` → `judge_avg` | GPT-4o holistic score: mean of accuracy, completeness, actionability, safety |

#### Composite stage score

$$\\text{score} = \\text{mean}(\\text{metrics that apply to this stage})$$

The key design decision is **when faithfulness is included**:

| Stage | Faithfulness included? | Rationale |
|---|---|---|
| **LLM** (no retrieval) | **No** | There is no retrieved context to be faithful to; including a 0 would unfairly penalise the baseline |
| **RAG → Agent** | **Yes** | Retrieved context exists; faithfulness measures how well the model uses it |

This means the LLM baseline score reflects **genuine answer quality** (relevance + safety + judge + coverage), and any gain at RAG or beyond is real — not an artefact of the metric construction.

> **Pedagogical note:** For well-known domains (cybersecurity), `gpt-4o-mini` already scores 0.6–0.8 on the LLM baseline because it was trained on abundant public text.  For proprietary domains (Faraday), the LLM baseline drops to 0.1–0.3 and each stage that injects private training data lifts the score measurably.  The score delta `Agent − LLM` is the quantified ROI of your training-data pipeline.

### 8.7  The Bottom Line

No single metric tells the whole story. The ultimate evaluation of agentic training data is **end-to-end task performance**: does the trained agent complete real-world tasks more reliably, with fewer hallucinations, better tool selection, and correct safety behaviour compared to a baseline prompt-only system?
"""

cells[17]["source"] = SECTION_8

nb["cells"] = cells
with open(NB, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Done. Cell 18 length:", len(SECTION_8))
print("8.6 present:", "### 8.6" in SECTION_8)
print("8.7 present:", "### 8.7" in SECTION_8)

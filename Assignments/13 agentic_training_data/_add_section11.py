"""
Inserts Section 11 (Recommendations 1-5 with code) after cell 39 (Section 10.4)
and Exercises 3 & 4 (Recommendations 6-7) after the last cell.
"""
import json, uuid

NB_PATH = "13_IRTM_From_Text_to_Agentic_Training_Data_2025_2026.ipynb"

def mk_md(source: str) -> dict:
    return {"cell_type": "markdown", "id": uuid.uuid4().hex[:8],
            "metadata": {}, "source": source}

def mk_code(source: str) -> dict:
    return {"cell_type": "code", "id": uuid.uuid4().hex[:8],
            "metadata": {}, "outputs": [], "execution_count": None, "source": source}

# ── Section 11 header ──────────────────────────────────────────────────────
sec11_header = mk_md("""\
---

## 11. Pedagogical Recommendations: Motivating Agentic Training in Practice

The following five insights are designed to help you **connect the pipeline mechanics
to real-world decision-making**.  Work through each subsection before attempting
the exercises at the end of the notebook.\
""")

# ── Rec 1: Decision Matrix ─────────────────────────────────────────────────
rec1_md = mk_md("""\
### 11.1 When Do You Need Which Format? — The Decision Matrix

A common question is: *given a new document, which training format should I
build first?*  The answer depends on the **structural type of the source text**,
not on the topic.  Each text type naturally exposes the signals needed for a
specific dataset format.

| Source Text Type | Primary Format | Secondary Format | Key Signal |
|---|---|---|---|
| Procedural manual / SOP | SFT Trajectories | Multi-Hop Chains | Sequential steps |
| Glossary / taxonomy | Knowledge Graph | RAG Chunks | Explicit definitions |
| Causal / explanatory | Multi-Hop Chains | SFT Trajectories | Because / therefore |
| Policy / rule document | RLHF Preference Pairs | SFT Trajectories | Must / shall / prohibited |
| Reference / factual prose | RAG Chunks | Neural Reranker Triplets | Self-contained facts |

The code cell below implements a **keyword-based classifier** that detects the
dominant text type and recommends the primary format.  Run it on your own
paragraphs to build intuition.\
""")

rec1_code = mk_code("""\
# ── 11.1  Decision Matrix: source text type → recommended training format ───

DECISION_MATRIX = {
    "Procedural / SOP": {
        "primary":   "SFT Trajectories",
        "secondary": "Multi-Hop Chains",
        "rationale": "Sequential steps map directly to (observation → thought → action)",
        "signals":   ["first", "then", "next", "finally", "step", "procedure",
                      "configure", "install", "navigate"],
    },
    "Glossary / Taxonomy": {
        "primary":   "Knowledge Graph",
        "secondary": "RAG Chunks",
        "rationale": "Definitions and named relations are explicit and easily extractable",
        "signals":   ["is defined as", "refers to", "is a type of", "consists of",
                      "is called", "also known as"],
    },
    "Causal / Explanatory": {
        "primary":   "Multi-Hop Chains",
        "secondary": "SFT Trajectories",
        "rationale": "Argument structure maps to (observation → inference → conclusion)",
        "signals":   ["because", "therefore", "thus", "leads to", "as a result",
                      "consequently", "this means"],
    },
    "Policy / Rule": {
        "primary":   "RLHF Preference Pairs",
        "secondary": "SFT Trajectories",
        "rationale": "Rules encode correct (chosen) and incorrect (rejected) actions",
        "signals":   ["must", "shall", "should not", "is prohibited", "is required",
                      "is forbidden", "always", "never"],
    },
    "Reference / Factual": {
        "primary":   "RAG Chunks",
        "secondary": "Neural Reranker Triplets",
        "rationale": "Self-contained semantic units ideal for factual retrieval",
        "signals":   ["in", "was", "is", "are", "has", "contains"],  # fallback default
    },
}


def classify_text_type(paragraph: str) -> str:
    """Classify paragraph by dominant text type using signal word matching."""
    p = paragraph.lower()
    scores = {
        t: sum(1 for s in info["signals"] if s in p)
        for t, info in DECISION_MATRIX.items()
    }
    # Remove the default fallback from competition unless it wins outright
    candidates = {t: s for t, s in scores.items() if t != "Reference / Factual"}
    best = max(candidates, key=candidates.get)
    if candidates[best] == 0:
        best = "Reference / Factual"
    return best


def recommend_format(paragraph: str) -> None:
    """Print the recommended training format for a paragraph."""
    text_type = classify_text_type(paragraph)
    info = DECISION_MATRIX[text_type]
    print(f"  Detected type  : {text_type}")
    print(f"  Primary format : {info['primary']}")
    print(f"  Secondary      : {info['secondary']}")
    print(f"  Rationale      : {info['rationale']}")


# ── Demonstration on four contrasting paragraphs ─────────────────────────
EXAMPLES = {
    "Procedural": (
        "First, download and install Burp Suite. Then configure your browser proxy "
        "to 127.0.0.1:8080. Next, navigate to the target URL and intercept the request. "
        "Finally, modify the parameters and forward the request to the server."
    ),
    "Glossary": (
        "Brute force is defined as a method used to crack or decode encrypted data by "
        "trying every possible combination of characters until the correct one is found. "
        "It is also known as exhaustive key search."
    ),
    "Causal": (
        "Because login forms often reveal whether a username is valid, attackers can "
        "enumerate accounts. This leads to targeted credential stuffing, which as a result "
        "increases the success rate of password attacks considerably."
    ),
    "Policy": (
        "All login attempts must return a generic error message. The system shall not reveal "
        "whether the username or password was incorrect. Detailed error messages are "
        "prohibited in production environments."
    ),
}

print("=" * 65)
print("Decision Matrix — Recommended Format per Text Type")
print("=" * 65)
for label, para in EXAMPLES.items():
    print(f"\\n[{label} paragraph]")
    print(f"  Text: {para[:75]}…")
    recommend_format(para)
    print("-" * 65)\
""")

# ── Rec 2: Domain Use-Case Anchoring ──────────────────────────────────────
rec2_md = mk_md("""\
### 11.2 Use-Case Anchoring — Why Proprietary Data Matters Across Domains

The cybersecurity and Faraday corpora used in this tutorial illustrate a general
pattern: **wherever the relevant knowledge is not publicly available, or where
errors carry high stakes, agentic training on proprietary data becomes essential
— not merely useful**.

The four domains below represent real-world deployments.  For each domain,
notice that the *reason* prompting alone fails is different:

| Domain | Why Base Model Fails | Highest-Risk Failure | Priority Format |
|---|---|---|---|
| Legal (contract review) | Firm-specific deal history, jurisdiction nuance | Hallucinated case citations | RAG + RLHF |
| Clinical (decision support) | Hospital-specific protocols, drug formularies | Wrong dosage / contraindication | SFT + RLHF |
| Industrial maintenance | OEM manuals not on internet; plant-specific faults | Wrong repair → injury | SFT + KG |
| Financial compliance | Rules change rapidly; jurisdiction-specific lag | Non-compliant advice | RAG + RLHF |

After running the cell below, use the **discussion prompt** it prints to
reflect on *which format to build first* for each domain and *why*.\
""")

rec2_code = mk_code("""\
# ── 11.2  Domain Use-Case Anchoring ────────────────────────────────────────

DOMAIN_PROFILES = {
    "Legal (Contract Review)": {
        "data": "Proprietary precedent libraries, deal histories, internal memos",
        "why_fail": "No public model has your firm's deal history or jurisdiction interpretations",
        "risk": "Hallucinated case citations, wrong jurisdiction rules",
        "priority": "RAG Chunks + RLHF Preference Pairs",
        "sample_q": "Does Clause 12.3 create a material obligation under Dutch law?",
    },
    "Clinical (Decision Support)": {
        "data": "Internal clinical protocols, drug formularies, patient pathways",
        "why_fail": "Hospital guidelines differ from published standards; errors are life-critical",
        "risk": "Wrong dosage, contraindicated drug combination",
        "priority": "SFT Trajectories + RLHF Preference Pairs",
        "sample_q": "What is the first-line treatment for a patient presenting with X?",
    },
    "Industrial Maintenance": {
        "data": "OEM equipment manuals, fault logs, technician notes",
        "why_fail": "Proprietary equipment docs absent from internet; faults are plant-specific",
        "risk": "Wrong repair procedure → equipment damage or injury",
        "priority": "SFT Trajectories + Knowledge Graph",
        "sample_q": "What are the diagnostic steps for error code E-423 on unit 7?",
    },
    "Financial Compliance": {
        "data": "Internal policy, regulatory correspondence, jurisdiction-specific rules",
        "why_fail": "Rules change rapidly; external models lag; jurisdiction nuance critical",
        "risk": "Non-compliant advice, missed reporting obligations",
        "priority": "RAG Chunks + RLHF Preference Pairs",
        "sample_q": "Does this transaction require SAR filing under FinCEN guidance?",
    },
}

print("=" * 70)
print("Domain Profiles — Why Proprietary Agentic Training Is Necessary")
print("=" * 70)
for domain, info in DOMAIN_PROFILES.items():
    print(f"\\n► {domain}")
    print(f"  Data source      : {info['data'][:65]}…" if len(info['data']) > 65 else f"  Data source      : {info['data']}")
    print(f"  Why model fails  : {info['why_fail'][:65]}…" if len(info['why_fail']) > 65 else f"  Why model fails  : {info['why_fail']}")
    print(f"  Highest risk     : {info['risk']}")
    print(f"  Priority formats : {info['priority']}")
    print(f"  Sample question  : {info['sample_q']}")

print("\\n" + "=" * 70)
print("Discussion Prompt")
print("=" * 70)
print("For each domain above, consider:")
print("  1. Which training format would you build FIRST, and why?")
print("  2. Which format carries the highest human annotation cost?")
print("  3. What additional data would a domain expert need to supply for RLHF?")\
""")

# ── Rec 3: Anatomy of a Paragraph ─────────────────────────────────────────
rec3_md = mk_md("""\
### 11.3 Anatomy of a Paragraph — One Text, Four Artifacts

A single human-written paragraph rarely maps to just one training format.
The **same text can simultaneously supply**:

- A **RAG chunk** (the paragraph as a retrievable semantic unit)
- **Knowledge graph nodes** (named entities and their relations)
- A **multi-hop chain** (the causal argument structure)
- An **RLHF preference pair** (the implicit rule and its violation)

The cell below takes one paragraph from the cybersecurity corpus and
decomposes it into all four artifacts.  Read the output carefully and
ask yourself: *what signal in the text triggered each artifact type?*\
""")

rec3_code = mk_code("""\
# ── 11.3  Anatomy of a Paragraph: one text → four training artifacts ────────

import json

SAMPLE_PARAGRAPH = (
    "Brute force attacks work by systematically trying every possible password "
    "combination until the correct one is found. Because attackers need a valid "
    "username first, user enumeration is a prerequisite step. Organisations must "
    "therefore return a generic error message — \\'Login failed\\' — regardless of "
    "whether the username or the password was wrong. This prevents attackers from "
    "distinguishing valid accounts from invalid ones."
)

# ── Artifact 1: RAG Chunk ──────────────────────────────────────────────────
rag_chunk = {
    "chunk_id": "chunk_demo_001",
    "text": SAMPLE_PARAGRAPH,
    "concepts": ["brute force", "user enumeration", "generic error message"],
    "chunk_type": "procedural+policy",
    "difficulty": "intermediate",
}

# ── Artifact 2: Knowledge Graph Nodes ─────────────────────────────────────
kg_nodes = [
    {"concept": "brute_force_attack",
     "related_to": ["user_enumeration", "password_cracking"], "category": "attack"},
    {"concept": "user_enumeration",
     "related_to": ["brute_force_attack"],                    "category": "technique"},
    {"concept": "generic_error_message",
     "related_to": ["user_enumeration"],                      "category": "countermeasure"},
]

# ── Artifact 3: Multi-Hop Chain ────────────────────────────────────────────
multihop_chain = {
    "question": "Why must login forms return a generic error message?",
    "hops": [
        {"hop": 1,
         "observation": "Brute force attacks try every password combination systematically.",
         "inference":   "An attacker needs a valid username before trying passwords."},
        {"hop": 2,
         "observation": "User enumeration is a prerequisite for brute force.",
         "inference":   "If the form reveals which field is wrong, enumeration becomes trivial."},
        {"hop": 3,
         "observation": "The form must not distinguish username errors from password errors.",
         "inference":   "A generic message removes the information signal the attacker relies on."},
    ],
    "conclusion": (
        "Generic error messages eliminate the prerequisite information "
        "that makes brute force attacks efficient."
    ),
}

# ── Artifact 4: RLHF Preference Pair ──────────────────────────────────────
rlhf_pair = {
    "context": "Agent is asked: what should a login form return when the username is wrong?",
    "chosen_action":      "Return 'Login failed. Please check your credentials.' for all failure types.",
    "chosen_reasoning":   "Generic message prevents attacker from learning whether the username is valid.",
    "rejected_action":    "Return 'Username not found' when the username does not exist.",
    "rejected_reasoning": "Reveals valid usernames; enables cheap enumeration before brute force.",
    "category":           "security",
}

# ── Display ────────────────────────────────────────────────────────────────
SEP = "─" * 68
print("=" * 68)
print("ONE PARAGRAPH → FOUR TRAINING ARTIFACTS")
print("=" * 68)
print(f"\\nSource paragraph:\\n  {SAMPLE_PARAGRAPH}\\n")
print(SEP)
print("Artifact 1 — RAG Chunk")
print(SEP)
print(json.dumps(rag_chunk, indent=2))
print()
print(SEP)
print("Artifact 2 — Knowledge Graph Nodes  (3 of N)")
print(SEP)
print(json.dumps(kg_nodes, indent=2))
print()
print(SEP)
print("Artifact 3 — Multi-Hop Chain")
print(SEP)
print(json.dumps(multihop_chain, indent=2))
print()
print(SEP)
print("Artifact 4 — RLHF Preference Pair")
print(SEP)
print(json.dumps(rlhf_pair, indent=2))\
""")

# ── Rec 4: Bottleneck Analysis ─────────────────────────────────────────────
rec4_md = mk_md("""\
### 11.4 Bottleneck Analysis — Where Human Effort Concentrates

Not all pipeline stages require the same effort.  Understanding the
**automation level** of each stage helps you plan a realistic project:

| Stage | Automation | Human expert needed? | Main failure mode |
|---|---|---|---|
| Text → JSON | ~80 % | Spot-check | Structure errors propagate downstream |
| JSON → RAG Chunks | ~95 % | Metadata labelling | Chunk boundary misalignment |
| JSON → Knowledge Graph | ~70 % | Relation validation | False or missing edges |
| JSON → SFT Trajectories | ~60 % | Trajectory review | Hallucinated "thoughts" |
| SFT → Multi-Hop Chains | ~70 % | Logic check | Invalid inferences |
| Expert annotation → RLHF Pairs | ~30 % | **Always required** | Sycophancy survives into data |

**Key practical insight**: RLHF pair annotation is the human bottleneck.
Build RAG + SFT first (high automation) to obtain a working baseline, then
invest expert time in RLHF to align behaviour with organisational values.
The bar chart below visualises these automation levels.\
""")

rec4_code = mk_code("""\
# ── 11.4  Bottleneck Analysis — automation level per pipeline stage ──────────

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

STAGES = [
    "Text → JSON",
    "JSON → RAG Chunks",
    "JSON → Knowledge Graph",
    "JSON → SFT Trajectories",
    "SFT → Multi-Hop Chains",
    "Expert → RLHF Pairs",
]
AUTOMATION = [80, 95, 70, 60, 70, 30]
FAILURE = [
    "Structure errors propagate downstream",
    "Chunk boundary misalignment",
    "False or missing graph edges",
    "Hallucinated 'thoughts' in steps",
    "Invalid inference hops",
    "Sycophancy surviving into training data",
]

def bar_colour(a):
    if a >= 80: return "#2ca02c"   # green  — high automation
    if a >= 65: return "#ff7f0e"   # orange — medium
    return "#d62728"               # red    — human bottleneck

colours = [bar_colour(a) for a in AUTOMATION]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(STAGES, AUTOMATION, color=colours, edgecolor="black", height=0.6)

for bar, pct in zip(bars, AUTOMATION):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
            f"{pct}%", va="center", fontsize=10)

ax.axvline(x=70, color="grey", linestyle="--", alpha=0.5, linewidth=1)
ax.set_xlabel("Estimated Automation Level (%)", fontsize=12)
ax.set_title("Pipeline Bottleneck Analysis:\\nAutomation Level per Stage", fontsize=13)
ax.set_xlim(0, 112)
ax.invert_yaxis()

legend_elements = [
    Patch(facecolor="#2ca02c", edgecolor="black", label="High automation  (≥ 80 %)"),
    Patch(facecolor="#ff7f0e", edgecolor="black", label="Medium automation (65–79 %)"),
    Patch(facecolor="#d62728", edgecolor="black", label="Human bottleneck  (< 65 %)"),
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=9)
plt.tight_layout()
plt.show()

print(f"\\n{'Stage':<32} {'Automation':>10}  Failure Mode")
print("─" * 85)
for s, a, f in zip(STAGES, AUTOMATION, FAILURE):
    print(f"{s:<32} {str(a)+'%':>10}  {f}")\
""")

# ── Rec 5: Data Flywheel ───────────────────────────────────────────────────
rec5_md = mk_md("""\
### 11.5 The Data Flywheel — Why Early Deployment Compounds Value

The pipeline covered in this tutorial treats data conversion as a
**one-time batch process**.  In production, however, the most valuable
training data accumulates *after* deployment through a **data flywheel**:

```
Deploy Agent
  → Collect interaction logs (questions, answers, user feedback)
  → Mine thumbs-up full-pipeline answers  → new SFT examples
  → Mine thumbs-down answers              → new RLHF candidates (after expert review)
  → Retrain specialised components
  → Redeploy improved agent
  → (repeat)
```

This explains why organisations that deploy early and collect user feedback
**compound their capability advantage** over time.  The simulation below
models a single flywheel cycle on 50 synthetic interactions.\
""")

rec5_code = mk_code("""\
# ── 11.5  Data Flywheel Simulation ─────────────────────────────────────────

import random
from collections import Counter
from datetime import datetime, timedelta

random.seed(42)

def simulate_interaction_log(n: int = 50) -> list:
    """Generate synthetic agent interaction log entries."""
    questions = [
        "What is the first step in a brute force attack?",
        "How does Faraday describe electromagnetic induction?",
        "What tool is used to intercept HTTP traffic?",
        "Define SQL injection and its primary defence.",
        "What is a denial-of-service attack?",
    ]
    stages  = ["LLM_only", "RAG", "RAG+KG", "Full_Pipeline"]
    ratings = ["thumbs_up", "thumbs_down", "no_feedback"]
    base    = datetime(2026, 1, 1, 9, 0, 0)

    return [
        {
            "interaction_id": f"log_{i:04d}",
            "timestamp":      (base + timedelta(hours=i * 2)).isoformat(),
            "question":       random.choice(questions),
            "pipeline_stage": random.choice(stages),
            "user_rating":    random.choices(ratings, weights=[0.55, 0.25, 0.20])[0],
        }
        for i in range(n)
    ]


def mine_flywheel_data(log: list) -> tuple:
    """Extract new SFT and RLHF candidates from interaction log."""
    sft_candidates  = [e for e in log
                       if e["user_rating"] == "thumbs_up"
                       and e["pipeline_stage"] == "Full_Pipeline"]
    rlhf_candidates = [e for e in log if e["user_rating"] == "thumbs_down"]
    return sft_candidates, rlhf_candidates


log = simulate_interaction_log(n=50)
sft_new, rlhf_new = mine_flywheel_data(log)

print("Data Flywheel Simulation — 50 Synthetic Interactions")
print("=" * 55)
print(f"Total interactions logged : {len(log)}")
print(f"New SFT candidates        : {len(sft_new):>3}  "
      f"(positive full-pipeline answers → direct training signal)")
print(f"New RLHF candidates       : {len(rlhf_new):>3}  "
      f"(negative-rated answers → expert review before labelling)")

rating_counts = Counter(e["user_rating"] for e in log)
print("\\nRating distribution:")
for r in ["thumbs_up", "thumbs_down", "no_feedback"]:
    bar = "█" * rating_counts[r]
    print(f"  {r:<16} {bar} ({rating_counts[r]})")

stage_counts = Counter(e["pipeline_stage"] for e in log)
print("\\nPipeline stage distribution:")
for s in ["LLM_only", "RAG", "RAG+KG", "Full_Pipeline"]:
    bar = "█" * stage_counts[s]
    print(f"  {s:<16} {bar} ({stage_counts[s]})")

print("\\nKey insight:")
print("  Organisations that deploy early and collect feedback")
print("  compound their capability advantage — the flywheel")
print("  accelerates with every deployment cycle.")\
""")

# ── Exercise 3 ─────────────────────────────────────────────────────────────
ex3_q = mk_md("""\
## Exercise 3 — Failure Mode: Prompting vs. Pipeline (5 points)

In Sections 9 and 10 we compared a prompt-only LLM against the full
7-stage agentic pipeline on two corpora.

Formulate a **domain-specific question** about Faraday's
*Experimental Researches in Electricity* that you expect GPT-4o to
answer **incorrectly or with hallucinated details** when given only a
prompt (no RAG, no knowledge graph).

a. State your question and explain **why** you expect the prompt-only
   approach to fail on it.
b. Identify which pipeline components (RAG, KG, SFT, RLHF) would most
   improve the answer quality and **explain the mechanism** by which
   each one helps.
c. What does this failure mode reveal about the **limits of pre-training**
   for domain-specific agents?\
""")

ex3_ans = mk_md("""\
YOUR ANSWER HERE

### BEGIN SOLUTION

**a. Example question and expected failure:**

*Question*: "In which Series does Faraday first introduce the concept of 'lines
of magnetic force', and what experimental apparatus does he describe to
demonstrate it?"

GPT-4o is likely to hallucinate specific Series numbers or apparatus details.
While Faraday's *discovery* of electromagnetic induction is widely reproduced
online, the precise experimental details across 30+ Series are not reliably
encoded in the model's weights.  The model may confidently cite the wrong
Series number or attribute the demonstration to the wrong instrument.

---

**b. Pipeline components that would help:**

- **RAG Chunks**: directly retrieve the relevant passage from the Faraday corpus,
  supplying the exact Series reference and apparatus description as a cited source.
- **Knowledge Graph**: link the node `lines_of_magnetic_force` → specific Series →
  experimental apparatus as a traversable relation, enabling exact look-up.
- **Multi-Hop Reasoner**: chain observation (Faraday introduces concept in Series X)
  → inference (what experiment follows logically) → conclusion (specific setup).
- **RLHF / Critic**: less critical here — the gap is factual retrieval, not behaviour
  alignment — but a Critic trained on the corpus could flag answers that lack
  a verifiable citation.

---

**c. What this reveals about the limits of pre-training:**

Pre-training encodes statistical patterns across the internet.  For well-known
high-level facts ("Faraday discovered electromagnetic induction") the model is
reliable.  For specific procedural or quantitative details that appear only in
primary sources — and are *not* reproduced in widely-shared summaries — the model's
weights are noisy, producing confident-sounding hallucinations.

Agentic training data fills this gap by converting primary sources into retrievable,
verified artifacts.  The key asymmetry: **public pre-training** gives breadth,
**domain-specific agentic data** gives depth and verifiability.

### END SOLUTION\
""")

# ── Exercise 4 ─────────────────────────────────────────────────────────────
ex4_q = mk_md("""\
## Exercise 4 — Mini Conversion Project (10 points)

Choose a **publicly available document** of at least 10 pages: a technical
manual, a scientific paper, a regulatory document, or a historical text.
Select a representative **3–5 paragraph section** and convert it into at least
**three** of the six training formats discussed in this tutorial.

a. Describe your chosen document and explain why it is a suitable candidate
   for agentic training (consider: is the knowledge proprietary-like?
   is accuracy critical? does it contain procedural, definitional, or
   policy content?).
b. Reproduce the raw text section you selected (verbatim or as a close
   paraphrase).
c. Produce the three training artifacts as **JSON objects** and briefly
   explain the extraction decision for each.
d. Which of the three formats was **hardest to extract** from your text,
   and why?
e. If you were to deploy an agent on this document, in what **order** would
   you build the six pipeline components, and what is your rationale?\
""")

ex4_ans = mk_md("""\
YOUR ANSWER HERE

### BEGIN SOLUTION

*(Model answer — student documents will vary; the structure below should be
reproduced regardless of the chosen document.)*

---

**a. Chosen document:**

*WHO Guidelines for Safe Surgery* (public domain, WHO Press).

Suitable because it contains: procedural checklists (→ SFT trajectories),
defined clinical terms (→ knowledge graph), causal safety reasoning
(→ multi-hop chains), and explicit prohibitions (→ RLHF pairs).  It
exemplifies the "critical failure domain": errors carry high patient-safety
risk, and hospital-specific implementation details would be proprietary.

---

**b. Sample raw text:**

> "Before skin incision, the team must confirm: (1) all team members have
> introduced themselves by name and role; (2) the patient has confirmed
> their identity, the procedure site, and consent; (3) the anaesthetic
> safety check is complete; (4) a pulse oximeter is on the patient and
> functioning."

---

**c. Three training artifacts:**

*RAG Chunk:*
```json
{
  "chunk_id": "who_surgery_001",
  "text": "Before skin incision, the team must confirm...",
  "concepts": ["surgical safety", "time-out", "informed consent", "anaesthesia check"],
  "chunk_type": "procedural_checklist",
  "difficulty": "beginner"
}
```

*SFT Trajectory (step 1 of 4):*
```json
{
  "scenario": "Preparing for skin incision in elective surgery",
  "steps": [
    {
      "step_number": 1,
      "observation": "Team assembled; incision about to begin.",
      "thought": "Must verify team readiness and patient identity before proceeding.",
      "action": "Pause procedure; ask all team members to introduce themselves.",
      "tool_used": "Verbal surgical time-out checklist",
      "expected_result": "All team members identified; patient identity confirmed."
    }
  ]
}
```

*RLHF Preference Pair:*
```json
{
  "context": "Surgeon asks: is it acceptable to skip the time-out if the team is familiar?",
  "chosen_action":      "Complete all checklist items regardless of team familiarity.",
  "chosen_reasoning":   "Familiarity bias is a known contributor to wrong-site surgery.",
  "rejected_action":    "Skip items 1 and 2 because the team has worked together before.",
  "rejected_reasoning": "Skipping any item removes the redundancy that catches errors.",
  "category":           "patient_safety"
}
```

---

**d. Hardest format to extract:**

**RLHF preference pairs** — because the *rejected* action is almost never
stated explicitly in a policy document.  It must be inferred as the plausible
violation of the stated rule, which requires domain expert judgement about what
a non-compliant agent would actually do.

---

**e. Build order and rationale:**

| Priority | Component | Rationale |
|---|---|---|
| 1 | RAG Chunks | High automation (95 %); immediate value for factual retrieval |
| 2 | Knowledge Graph | Moderate automation (70 %); enables multi-hop reasoning |
| 3 | SFT Trajectories | Moderate automation (60 %); teaches procedural reasoning |
| 4 | Multi-Hop Chains | Derived from SFT; low marginal cost once trajectories exist |
| 5 | Neural Reranker Triplets | Requires existing chunks; synthetic negatives are automatable |
| 6 | RLHF Preference Pairs | Lowest automation (30 %); highest expert cost — build last |

### END SOLUTION\
""")

# ── Assemble and write ────────────────────────────────────────────────────
with open(NB_PATH, encoding="utf-8") as f:
    nb = json.load(f)

cells = nb["cells"]

# Find insertion point: after cell index 38 (cell 39, "10.4 Reading Faraday results")
# and before cell index 39 (cell 40, "## Exercises")
insert_at = 39  # 0-based index of the current Exercises header cell

new_section_cells = [
    sec11_header,
    rec1_md, rec1_code,
    rec2_md, rec2_code,
    rec3_md, rec3_code,
    rec4_md, rec4_code,
    rec5_md, rec5_code,
]

# Insert Section 11 before the Exercises header
cells[insert_at:insert_at] = new_section_cells

# Append Exercises 3 and 4 at the end
cells += [ex3_q, ex3_ans, ex4_q, ex4_ans]

nb["cells"] = cells

with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Done. Notebook now has {len(nb['cells'])} cells.")
print(f"  Inserted {len(new_section_cells)} Section 11 cells before the Exercises header.")
print("  Appended Exercise 3 (2 cells) and Exercise 4 (2 cells) at the end.")

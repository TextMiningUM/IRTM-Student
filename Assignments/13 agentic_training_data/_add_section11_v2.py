# -*- coding: utf-8 -*-
import json, uuid

NB_PATH = "13_IRTM_From_Text_to_Agentic_Training_Data_2025_2026.ipynb"

def md(src):  return {"cell_type":"markdown","id":uuid.uuid4().hex[:8],"metadata":{},"source":src}
def code(src): return {"cell_type":"code","id":uuid.uuid4().hex[:8],"metadata":{},"outputs":[],"execution_count":None,"source":src}

# ── load notebook ──────────────────────────────────────────────────────────
with open(NB_PATH, encoding="utf-8") as f:
    nb = json.load(f)

new_section = []
new_exercises = []

# ═══════════════════════════════ SEC 11 HEADER ════════════════════════════
new_section.append(md(
"---\n\n"
"## 11. Pedagogical Recommendations: Motivating Agentic Training in Practice\n\n"
"The following five insights help you **connect the pipeline mechanics to real-world\n"
"decision-making**. Work through each subsection before attempting the exercises."
))

# ═══════════════════════════════ REC 1 ════════════════════════════════════
new_section.append(md(
"### 11.1 When Do You Need Which Format? — The Decision Matrix\n\n"
"A common question is: *given a new document, which training format should I build\n"
"first?* The answer depends on the **structural type of the source text**, not the\n"
"topic. Each text type naturally exposes the signals needed for a specific format.\n\n"
"| Source Text Type | Primary Format | Secondary Format | Key Signal |\n"
"|---|---|---|---|\n"
"| Procedural manual / SOP | SFT Trajectories | Multi-Hop Chains | Sequential steps |\n"
"| Glossary / taxonomy | Knowledge Graph | RAG Chunks | Explicit definitions |\n"
"| Causal / explanatory | Multi-Hop Chains | SFT Trajectories | Because / therefore |\n"
"| Policy / rule document | RLHF Preference Pairs | SFT Trajectories | Must / shall / prohibited |\n"
"| Reference / factual prose | RAG Chunks | Neural Reranker Triplets | Self-contained facts |\n\n"
"The cell below implements a keyword-based classifier. Run it on your own paragraphs."
))

new_section.append(code(
"# 11.1  Decision Matrix: source text type -> recommended training format\n"
"\n"
"DECISION_MATRIX = {\n"
'    "Procedural / SOP": {\n'
'        "primary":   "SFT Trajectories",\n'
'        "secondary": "Multi-Hop Chains",\n'
'        "rationale": "Sequential steps map to (observation -> thought -> action)",\n'
'        "signals":   ["first", "then", "next", "finally", "step", "procedure",\n'
'                      "configure", "install", "navigate"],\n'
"    },\n"
'    "Glossary / Taxonomy": {\n'
'        "primary":   "Knowledge Graph",\n'
'        "secondary": "RAG Chunks",\n'
'        "rationale": "Definitions and named relations are explicit and extractable",\n'
'        "signals":   ["is defined as", "refers to", "is a type of", "consists of",\n'
'                      "is called", "also known as"],\n'
"    },\n"
'    "Causal / Explanatory": {\n'
'        "primary":   "Multi-Hop Chains",\n'
'        "secondary": "SFT Trajectories",\n'
'        "rationale": "Argument structure maps to (observation -> inference -> conclusion)",\n'
'        "signals":   ["because", "therefore", "thus", "leads to", "as a result",\n'
'                      "consequently", "this means"],\n'
"    },\n"
'    "Policy / Rule": {\n'
'        "primary":   "RLHF Preference Pairs",\n'
'        "secondary": "SFT Trajectories",\n'
'        "rationale": "Rules encode correct (chosen) and incorrect (rejected) actions",\n'
'        "signals":   ["must", "shall", "should not", "is prohibited", "is required",\n'
'                      "is forbidden", "always", "never"],\n'
"    },\n"
'    "Reference / Factual": {\n'
'        "primary":   "RAG Chunks",\n'
'        "secondary": "Neural Reranker Triplets",\n'
'        "rationale": "Self-contained semantic units ideal for factual retrieval",\n'
'        "signals":   ["in", "was", "is", "are", "has", "contains"],\n'
"    },\n"
"}\n"
"\n"
"\n"
"def classify_text_type(paragraph):\n"
'    """Classify paragraph by dominant text type using signal word matching."""\n'
"    p = paragraph.lower()\n"
"    scores = {\n"
'        t: sum(1 for s in info["signals"] if s in p)\n'
"        for t, info in DECISION_MATRIX.items()\n"
"    }\n"
'    candidates = {t: s for t, s in scores.items() if t != "Reference / Factual"}\n'
"    best = max(candidates, key=candidates.get)\n"
"    if candidates[best] == 0:\n"
'        best = "Reference / Factual"\n'
"    return best\n"
"\n"
"\n"
"def recommend_format(paragraph):\n"
'    """Print the recommended training format for a paragraph."""\n'
"    text_type = classify_text_type(paragraph)\n"
"    info = DECISION_MATRIX[text_type]\n"
'    print(f"  Detected type  : {text_type}")\n'
'    print(f"  Primary format : {info[\'primary\']}")\n'
'    print(f"  Secondary      : {info[\'secondary\']}")\n'
'    print(f"  Rationale      : {info[\'rationale\']}")\n'
"\n"
"\n"
"EXAMPLES = {\n"
'    "Procedural": (\n'
'        "First, download and install Burp Suite. Then configure your browser proxy "\n'
'        "to 127.0.0.1:8080. Next, navigate to the target URL and intercept the request. "\n'
'        "Finally, modify the parameters and forward the request to the server."\n'
"    ),\n"
'    "Glossary": (\n'
'        "Brute force is defined as a method used to crack or decode encrypted data by "\n'
'        "trying every possible combination of characters until the correct one is found. "\n'
'        "It is also known as exhaustive key search."\n'
"    ),\n"
'    "Causal": (\n'
'        "Because login forms often reveal whether a username is valid, attackers can "\n'
'        "enumerate accounts. This leads to targeted credential stuffing, which as a result "\n'
'        "increases the success rate of password attacks considerably."\n'
"    ),\n"
'    "Policy": (\n'
'        "All login attempts must return a generic error message. The system shall not reveal "\n'
'        "whether the username or password was incorrect. Detailed error messages are "\n'
'        "prohibited in production environments."\n'
"    ),\n"
"}\n"
"\n"
'print("=" * 65)\n'
'print("Decision Matrix -- Recommended Format per Text Type")\n'
'print("=" * 65)\n'
"for label, para in EXAMPLES.items():\n"
'    print(f"\\n[{label} paragraph]")\n'
'    print(f"  Text: {para[:75]}...")\n'
"    recommend_format(para)\n"
'    print("-" * 65)'
))

# ═══════════════════════════════ REC 2 ════════════════════════════════════
new_section.append(md(
"### 11.2 Use-Case Anchoring — Why Proprietary Data Matters Across Domains\n\n"
"The cybersecurity and Faraday corpora illustrate a general pattern: **wherever\n"
"relevant knowledge is not publicly available, or where errors carry high stakes,\n"
"agentic training on proprietary data becomes essential — not merely useful**.\n\n"
"| Domain | Why Base Model Fails | Highest-Risk Failure | Priority Format |\n"
"|---|---|---|---|\n"
"| Legal (contract review) | Firm-specific deal history, jurisdiction nuance | Hallucinated case citations | RAG + RLHF |\n"
"| Clinical (decision support) | Hospital-specific protocols, drug formularies | Wrong dosage / contraindication | SFT + RLHF |\n"
"| Industrial maintenance | OEM manuals not on internet; plant-specific faults | Wrong repair -> injury | SFT + KG |\n"
"| Financial compliance | Rules change rapidly; jurisdiction-specific lag | Non-compliant advice | RAG + RLHF |\n\n"
"Run the cell below, then use the discussion prompt to reflect on which format\n"
"to build *first* for each domain and why."
))

new_section.append(code(
"# 11.2  Domain Use-Case Anchoring\n"
"\n"
"DOMAIN_PROFILES = {\n"
'    "Legal (Contract Review)": {\n'
'        "data":     "Proprietary precedent libraries, deal histories, internal memos",\n'
'        "why_fail": "No public model has your firm\'s deal history or jurisdiction interpretations",\n'
'        "risk":     "Hallucinated case citations, wrong jurisdiction rules",\n'
'        "priority": "RAG Chunks + RLHF Preference Pairs",\n'
'        "sample_q": "Does Clause 12.3 create a material obligation under Dutch law?",\n'
"    },\n"
'    "Clinical (Decision Support)": {\n'
'        "data":     "Internal clinical protocols, drug formularies, patient pathways",\n'
'        "why_fail": "Hospital guidelines differ from published standards; errors are life-critical",\n'
'        "risk":     "Wrong dosage, contraindicated drug combination",\n'
'        "priority": "SFT Trajectories + RLHF Preference Pairs",\n'
'        "sample_q": "What is the first-line treatment for a patient presenting with X?",\n'
"    },\n"
'    "Industrial Maintenance": {\n'
'        "data":     "OEM equipment manuals, fault logs, technician notes",\n'
'        "why_fail": "Proprietary equipment docs absent from internet; faults are plant-specific",\n'
'        "risk":     "Wrong repair procedure -> equipment damage or injury",\n'
'        "priority": "SFT Trajectories + Knowledge Graph",\n'
'        "sample_q": "What are the diagnostic steps for error code E-423 on unit 7?",\n'
"    },\n"
'    "Financial Compliance": {\n'
'        "data":     "Internal policy, regulatory correspondence, jurisdiction-specific rules",\n'
'        "why_fail": "Rules change rapidly; external models lag; jurisdiction nuance critical",\n'
'        "risk":     "Non-compliant advice, missed reporting obligations",\n'
'        "priority": "RAG Chunks + RLHF Preference Pairs",\n'
'        "sample_q": "Does this transaction require SAR filing under FinCEN guidance?",\n'
"    },\n"
"}\n"
"\n"
'print("=" * 70)\n'
'print("Domain Profiles -- Why Proprietary Agentic Training Is Necessary")\n'
'print("=" * 70)\n'
"for domain, info in DOMAIN_PROFILES.items():\n"
'    print(f"\\n► {domain}")\n'
'    d = info["data"]; print(f"  Data source      : {d[:65]}..." if len(d) > 65 else f"  Data source      : {d}")\n'
'    w = info["why_fail"]; print(f"  Why model fails  : {w[:65]}..." if len(w) > 65 else f"  Why model fails  : {w}")\n'
'    print(f"  Highest risk     : {info[\'risk\']}")\n'
'    print(f"  Priority formats : {info[\'priority\']}")\n'
'    print(f"  Sample question  : {info[\'sample_q\']}")\n'
"\n"
'print("\\n" + "=" * 70)\n'
'print("Discussion Prompt")\n'
'print("=" * 70)\n'
'print("For each domain above, consider:")\n'
'print("  1. Which training format would you build FIRST, and why?")\n'
'print("  2. Which format carries the highest human annotation cost?")\n'
'print("  3. What additional data would a domain expert supply for RLHF?")'
))

# ═══════════════════════════════ REC 3 ════════════════════════════════════
new_section.append(md(
"### 11.3 Anatomy of a Paragraph — One Text, Four Artifacts\n\n"
"A single human-written paragraph rarely maps to just one training format.\n"
"The **same text can simultaneously supply**:\n\n"
"- A **RAG chunk** — the paragraph as a retrievable semantic unit\n"
"- **Knowledge graph nodes** — named entities and their relations\n"
"- A **multi-hop chain** — the causal argument structure\n"
"- An **RLHF preference pair** — the implicit rule and its violation\n\n"
"The cell below takes one paragraph from the cybersecurity corpus and decomposes\n"
"it into all four artifacts. Read the output carefully: *what signal in the text\n"
"triggered each artifact type?*"
))

new_section.append(code(
"# 11.3  Anatomy of a paragraph: one text -> four training artifacts\n"
"\n"
"import json as _json\n"
"\n"
"SAMPLE = (\n"
'    "Brute force attacks work by systematically trying every possible password "\n'
'    "combination until the correct one is found. Because attackers need a valid "\n'
'    "username first, user enumeration is a prerequisite step. Organisations must "\n'
'    "therefore return a generic error message -- Login failed -- regardless of "\n'
'    "whether the username or the password was wrong. This prevents attackers from "\n'
'    "distinguishing valid accounts from invalid ones."\n'
")\n"
"\n"
"rag_chunk = {\n"
'    "chunk_id": "chunk_demo_001",\n'
'    "text": SAMPLE,\n'
'    "concepts": ["brute force", "user enumeration", "generic error message"],\n'
'    "chunk_type": "procedural+policy",\n'
'    "difficulty": "intermediate",\n'
"}\n"
"\n"
"kg_nodes = [\n"
'    {"concept": "brute_force_attack",    "related_to": ["user_enumeration", "password_cracking"], "category": "attack"},\n'
'    {"concept": "user_enumeration",      "related_to": ["brute_force_attack"],                    "category": "technique"},\n'
'    {"concept": "generic_error_message", "related_to": ["user_enumeration"],                      "category": "countermeasure"},\n'
"]\n"
"\n"
"multihop = {\n"
'    "question": "Why must login forms return a generic error message?",\n'
'    "hops": [\n'
'        {"hop": 1, "observation": "Brute force attacks try every password combination.",\n'
'                   "inference":   "An attacker needs a valid username before trying passwords."},\n'
'        {"hop": 2, "observation": "User enumeration is a prerequisite for brute force.",\n'
'                   "inference":   "If the form reveals which field is wrong, enumeration is trivial."},\n'
'        {"hop": 3, "observation": "The form must not distinguish username errors from password errors.",\n'
'                   "inference":   "A generic message removes the information signal the attacker needs."},\n'
"    ],\n"
'    "conclusion": "Generic error messages eliminate the prerequisite that makes brute force efficient.",\n'
"}\n"
"\n"
"rlhf_pair = {\n"
'    "context":           "Agent asked: what should a login form return when the username is wrong?",\n'
'    "chosen_action":     "Return \'Login failed. Please check your credentials.\' for all failure types.",\n'
'    "chosen_reasoning":  "Generic message stops attacker learning whether the username is valid.",\n'
'    "rejected_action":   "Return \'Username not found\' when the username does not exist.",\n'
'    "rejected_reasoning":"Reveals valid usernames; enables cheap enumeration before brute force.",\n'
'    "category":          "security",\n'
"}\n"
"\n"
"SEP = \"-\" * 68\n"
'print("=" * 68)\n'
'print("ONE PARAGRAPH -> FOUR TRAINING ARTIFACTS")\n'
'print("=" * 68)\n'
'print(f"\\nSource paragraph:\\n  {SAMPLE}\\n")\n'
'print(SEP); print("Artifact 1 -- RAG Chunk");              print(SEP); print(_json.dumps(rag_chunk,  indent=2))\n'
'print(); print(SEP); print("Artifact 2 -- Knowledge Graph (3 nodes)"); print(SEP); print(_json.dumps(kg_nodes, indent=2))\n'
'print(); print(SEP); print("Artifact 3 -- Multi-Hop Chain");           print(SEP); print(_json.dumps(multihop,  indent=2))\n'
'print(); print(SEP); print("Artifact 4 -- RLHF Preference Pair");      print(SEP); print(_json.dumps(rlhf_pair, indent=2))'
))

# ═══════════════════════════════ REC 4 ════════════════════════════════════
new_section.append(md(
"### 11.4 Bottleneck Analysis — Where Human Effort Concentrates\n\n"
"Not all pipeline stages require the same effort. Understanding the **automation\n"
"level** of each stage helps you plan a realistic project:\n\n"
"| Stage | Automation | Human expert? | Main failure mode |\n"
"|---|---|---|---|\n"
"| Text -> JSON | ~80% | Spot-check | Structure errors propagate downstream |\n"
"| JSON -> RAG Chunks | ~95% | Metadata labelling | Chunk boundary misalignment |\n"
"| JSON -> Knowledge Graph | ~70% | Relation validation | False or missing edges |\n"
"| JSON -> SFT Trajectories | ~60% | Trajectory review | Hallucinated 'thoughts' |\n"
"| SFT -> Multi-Hop Chains | ~70% | Logic check | Invalid inference hops |\n"
"| Expert -> RLHF Pairs | ~30% | **Always required** | Sycophancy surviving into data |\n\n"
"**Key insight**: RLHF annotation is the human bottleneck. Build RAG + SFT first\n"
"(high automation) for a working baseline, then invest expert time in RLHF."
))

new_section.append(code(
"# 11.4  Bottleneck analysis -- automation level per pipeline stage\n"
"\n"
"import matplotlib.pyplot as plt\n"
"from matplotlib.patches import Patch\n"
"\n"
"STAGES = [\n"
'    "Text -> JSON",\n'
'    "JSON -> RAG Chunks",\n'
'    "JSON -> Knowledge Graph",\n'
'    "JSON -> SFT Trajectories",\n'
'    "SFT -> Multi-Hop Chains",\n'
'    "Expert -> RLHF Pairs",\n'
"]\n"
"AUTOMATION = [80, 95, 70, 60, 70, 30]\n"
"FAILURE = [\n"
'    "Structure errors propagate downstream",\n'
'    "Chunk boundary misalignment",\n'
'    "False or missing graph edges",\n'
'    "Hallucinated steps in trajectories",\n'
'    "Invalid inference hops",\n'
'    "Sycophancy surviving into training data",\n'
"]\n"
"\n"
"def bar_colour(a):\n"
'    if a >= 80: return "#2ca02c"\n'
'    if a >= 65: return "#ff7f0e"\n'
'    return "#d62728"\n'
"\n"
"fig, ax = plt.subplots(figsize=(10, 5))\n"
"bars = ax.barh(STAGES, AUTOMATION, color=[bar_colour(a) for a in AUTOMATION],\n"
"               edgecolor='black', height=0.6)\n"
"for bar, pct in zip(bars, AUTOMATION):\n"
"    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,\n"
"            f'{pct}%', va='center', fontsize=10)\n"
"ax.axvline(x=70, color='grey', linestyle='--', alpha=0.5, linewidth=1)\n"
"ax.set_xlabel('Estimated Automation Level (%)', fontsize=12)\n"
"ax.set_title('Pipeline Bottleneck Analysis: Automation Level per Stage', fontsize=13)\n"
"ax.set_xlim(0, 112)\n"
"ax.invert_yaxis()\n"
"legend_elements = [\n"
"    Patch(facecolor='#2ca02c', edgecolor='black', label='High automation  (>= 80%)'),\n"
"    Patch(facecolor='#ff7f0e', edgecolor='black', label='Medium automation (65-79%)'),\n"
"    Patch(facecolor='#d62728', edgecolor='black', label='Human bottleneck  (< 65%)'),\n"
"]\n"
"ax.legend(handles=legend_elements, loc='lower right', fontsize=9)\n"
"plt.tight_layout(); plt.show()\n"
"\n"
'print(f"\\n{\'Stage\':<32} {\'Automation\':>10}  Failure Mode")\n'
'print("-" * 85)\n'
"for s, a, f in zip(STAGES, AUTOMATION, FAILURE):\n"
'    print(f"{s:<32} {str(a)+\'%\':>10}  {f}")'
))

# ═══════════════════════════════ REC 5 ════════════════════════════════════
new_section.append(md(
"### 11.5 The Data Flywheel — Why Early Deployment Compounds Value\n\n"
"The pipeline in this tutorial treats data conversion as a one-time batch process.\n"
"In production, the most valuable training data accumulates *after* deployment\n"
"through a **data flywheel**:\n\n"
"```\n"
"Deploy Agent\n"
"  -> Collect interaction logs (questions, answers, user feedback)\n"
"  -> Mine thumbs-up full-pipeline answers  -> new SFT examples\n"
"  -> Mine thumbs-down answers              -> new RLHF candidates (+ expert review)\n"
"  -> Retrain specialised components\n"
"  -> Redeploy improved agent\n"
"  -> (repeat)\n"
"```\n\n"
"Organisations that deploy early and collect user feedback **compound their capability\n"
"advantage** over time. The simulation below models one flywheel cycle."
))

new_section.append(code(
"# 11.5  Data Flywheel simulation\n"
"\n"
"import random\n"
"from collections import Counter\n"
"from datetime import datetime, timedelta\n"
"\n"
"random.seed(42)\n"
"\n"
"def simulate_log(n=50):\n"
'    """Generate synthetic agent interaction log entries."""\n'
"    questions = [\n"
'        "What is the first step in a brute force attack?",\n'
'        "How does Faraday describe electromagnetic induction?",\n'
'        "What tool is used to intercept HTTP traffic?",\n'
'        "Define SQL injection and its primary defence.",\n'
'        "What is a denial-of-service attack?",\n'
"    ]\n"
'    stages  = ["LLM_only", "RAG", "RAG+KG", "Full_Pipeline"]\n'
'    ratings = ["thumbs_up", "thumbs_down", "no_feedback"]\n'
"    base    = datetime(2026, 1, 1, 9, 0, 0)\n"
"    return [\n"
"        {\n"
'            "interaction_id": f"log_{i:04d}",\n'
'            "timestamp":      (base + timedelta(hours=i * 2)).isoformat(),\n'
'            "question":       random.choice(questions),\n'
'            "pipeline_stage": random.choice(stages),\n'
'            "user_rating":    random.choices(ratings, weights=[0.55, 0.25, 0.20])[0],\n'
"        }\n"
"        for i in range(n)\n"
"    ]\n"
"\n"
"log = simulate_log(50)\n"
"sft_new  = [e for e in log\n"
'            if e["user_rating"] == "thumbs_up" and e["pipeline_stage"] == "Full_Pipeline"]\n'
'rlhf_new = [e for e in log if e["user_rating"] == "thumbs_down"]\n'
"\n"
'print("Data Flywheel Simulation -- 50 Synthetic Interactions")\n'
'print("=" * 55)\n'
'print(f"Total interactions logged : {len(log)}")\n'
'print(f"New SFT candidates        : {len(sft_new):>3}  (positive full-pipeline answers)")\n'
'print(f"New RLHF candidates       : {len(rlhf_new):>3}  (negative-rated -> expert review)")\n'
"\n"
"rating_counts = Counter(e['user_rating'] for e in log)\n"
'print("\\nRating distribution:")\n'
'for r in ["thumbs_up", "thumbs_down", "no_feedback"]:\n'
'    print(f"  {r:<16} {chr(9608) * rating_counts[r]} ({rating_counts[r]})")\n'
"\n"
"stage_counts = Counter(e['pipeline_stage'] for e in log)\n"
'print("\\nPipeline stage distribution:")\n'
'for s in ["LLM_only", "RAG", "RAG+KG", "Full_Pipeline"]:\n'
'    print(f"  {s:<16} {chr(9608) * stage_counts[s]} ({stage_counts[s]})")\n'
"\n"
'print("\\nKey insight: organisations that deploy early and collect feedback")\n'
'print("compound their capability advantage -- the flywheel accelerates.")'
))

# ═══════════════════════════════ EXERCISE 3 ═══════════════════════════════
new_exercises.append(md(
"## Exercise 3 -- Failure Mode: Prompting vs. Pipeline (5 points)\n\n"
"In Sections 9 and 10 we compared a prompt-only LLM against the full 7-stage\n"
"agentic pipeline on two corpora.\n\n"
"Formulate a **domain-specific question** about Faraday's *Experimental Researches\n"
"in Electricity* that you expect GPT-4o to answer **incorrectly or with hallucinated\n"
"details** when given only a prompt (no RAG, no knowledge graph).\n\n"
"a. State your question and explain **why** you expect the prompt-only approach to fail.\n"
"b. Identify which pipeline components (RAG, KG, SFT, RLHF) would most improve the\n"
"   answer quality and explain the **mechanism** by which each one helps.\n"
"c. What does this failure mode reveal about the **limits of pre-training** for\n"
"   domain-specific agents?"
))

new_exercises.append(md(
"YOUR ANSWER HERE\n\n"
"### BEGIN SOLUTION\n\n"
"**a. Example question and expected failure:**\n\n"
"*Question*: \"In which Series does Faraday first introduce 'lines of magnetic force',\n"
"and what experimental apparatus does he describe to demonstrate it?\"\n\n"
"GPT-4o is likely to hallucinate specific Series numbers or apparatus details. While\n"
"Faraday's *discovery* of electromagnetic induction is widely reproduced online, the\n"
"precise experimental details across 30+ Series are not reliably encoded in the\n"
"model's weights. The model may confidently cite the wrong Series or instrument.\n\n"
"---\n\n"
"**b. Pipeline components that would help:**\n\n"
"- **RAG Chunks**: directly retrieve the relevant passage from the Faraday corpus,\n"
"  supplying the exact Series reference and apparatus description as a cited source.\n"
"- **Knowledge Graph**: link `lines_of_magnetic_force` -> specific Series ->\n"
"  experimental apparatus as a traversable relation, enabling exact look-up.\n"
"- **Multi-Hop Reasoner**: chain observation (concept introduced in Series X) ->\n"
"  inference (what experiment follows) -> conclusion (specific apparatus).\n"
"- **RLHF / Critic**: less critical here -- the gap is factual retrieval, not\n"
"  behaviour alignment -- but a Critic can flag answers lacking verifiable citations.\n\n"
"---\n\n"
"**c. Limits of pre-training:**\n\n"
"Pre-training encodes statistical patterns across the internet. For well-known\n"
"high-level facts the model is reliable. For specific procedural or quantitative\n"
"details appearing only in primary sources -- not reproduced in widely-shared\n"
"summaries -- the model's weights are noisy, producing confident hallucinations.\n\n"
"Agentic training data fills this gap by converting primary sources into retrievable,\n"
"verified artifacts. **Public pre-training gives breadth; domain-specific agentic\n"
"data gives depth and verifiability.**\n\n"
"### END SOLUTION"
))

# ═══════════════════════════════ EXERCISE 4 ═══════════════════════════════
new_exercises.append(md(
"## Exercise 4 -- Mini Conversion Project (10 points)\n\n"
"Choose a **publicly available document** of at least 10 pages: a technical manual,\n"
"a scientific paper, a regulatory document, or a historical text. Select a\n"
"representative **3-5 paragraph section** and convert it into at least **three**\n"
"of the six training formats discussed in this tutorial.\n\n"
"a. Describe your chosen document and explain why it is a suitable candidate for\n"
"   agentic training (consider: is the knowledge proprietary-like? is accuracy\n"
"   critical? does it contain procedural, definitional, or policy content?).\n"
"b. Reproduce the raw text section you selected (verbatim or as a close paraphrase).\n"
"c. Produce the three training artifacts as **JSON objects** and briefly explain the\n"
"   extraction decision for each.\n"
"d. Which of the three formats was **hardest to extract** from your text, and why?\n"
"e. If you were to deploy an agent on this document, in what **order** would you\n"
"   build the six pipeline components, and what is your rationale?"
))

new_exercises.append(md(
"YOUR ANSWER HERE\n\n"
"### BEGIN SOLUTION\n\n"
"*(Model answer -- student documents will vary; the structure below applies regardless.)*\n\n"
"---\n\n"
"**a. Chosen document:**\n\n"
"*WHO Guidelines for Safe Surgery* (public domain, WHO Press).\n\n"
"Suitable because it contains procedural checklists (-> SFT trajectories), defined\n"
"clinical terms (-> knowledge graph), causal safety reasoning (-> multi-hop chains),\n"
"and explicit prohibitions (-> RLHF pairs). Errors carry high patient-safety risk;\n"
"hospital-specific implementation would be proprietary.\n\n"
"---\n\n"
"**b. Sample raw text:**\n\n"
"> \"Before skin incision, the team must confirm: (1) all team members have introduced\n"
"> themselves by name and role; (2) the patient has confirmed their identity, the\n"
"> procedure site, and consent; (3) the anaesthetic safety check is complete;\n"
"> (4) a pulse oximeter is on the patient and functioning.\"\n\n"
"---\n\n"
"**c. Three training artifacts:**\n\n"
"*RAG Chunk:*\n"
"```json\n"
"{\n"
"  \"chunk_id\": \"who_surgery_001\",\n"
"  \"text\": \"Before skin incision, the team must confirm...\",\n"
"  \"concepts\": [\"surgical safety\", \"time-out\", \"informed consent\", \"anaesthesia\"],\n"
"  \"chunk_type\": \"procedural_checklist\",\n"
"  \"difficulty\": \"beginner\"\n"
"}\n"
"```\n\n"
"*SFT Trajectory (step 1 of 4):*\n"
"```json\n"
"{\n"
"  \"scenario\": \"Preparing for skin incision in elective surgery\",\n"
"  \"steps\": [{\n"
"    \"step_number\": 1,\n"
"    \"observation\": \"Team assembled; incision about to begin.\",\n"
"    \"thought\": \"Must verify team readiness and patient identity before proceeding.\",\n"
"    \"action\": \"Pause procedure; ask all team members to introduce themselves.\",\n"
"    \"tool_used\": \"Verbal surgical time-out checklist\",\n"
"    \"expected_result\": \"All team members identified; patient identity confirmed.\"\n"
"  }]\n"
"}\n"
"```\n\n"
"*RLHF Preference Pair:*\n"
"```json\n"
"{\n"
"  \"context\": \"Surgeon asks: is it acceptable to skip the time-out if the team is familiar?\",\n"
"  \"chosen_action\": \"Complete all checklist items regardless of team familiarity.\",\n"
"  \"chosen_reasoning\": \"Familiarity bias is a known contributor to wrong-site surgery.\",\n"
"  \"rejected_action\": \"Skip items 1 and 2 because the team has worked together before.\",\n"
"  \"rejected_reasoning\": \"Skipping any item removes the redundancy that catches errors.\",\n"
"  \"category\": \"patient_safety\"\n"
"}\n"
"```\n\n"
"---\n\n"
"**d. Hardest format to extract:**\n\n"
"**RLHF preference pairs** -- the *rejected* action is almost never stated explicitly\n"
"in a policy document. It must be inferred as the plausible violation of the stated\n"
"rule, requiring domain expert judgement about what a non-compliant agent would do.\n\n"
"---\n\n"
"**e. Build order and rationale:**\n\n"
"| Priority | Component | Rationale |\n"
"|---|---|---|\n"
"| 1 | RAG Chunks | High automation (95%); immediate retrieval value |\n"
"| 2 | Knowledge Graph | Moderate automation (70%); enables multi-hop reasoning |\n"
"| 3 | SFT Trajectories | Moderate automation (60%); teaches procedural reasoning |\n"
"| 4 | Multi-Hop Chains | Derived from SFT; low marginal cost once trajectories exist |\n"
"| 5 | Neural Reranker Triplets | Requires existing chunks; synthetic negatives automatable |\n"
"| 6 | RLHF Preference Pairs | Lowest automation (30%); highest expert cost -- build last |\n\n"
"### END SOLUTION"
))

# ── insert into notebook ───────────────────────────────────────────────────
cells = nb["cells"]
insert_at = 39   # before current Exercises header (0-based index)
cells[insert_at:insert_at] = new_section
cells += new_exercises
nb["cells"] = cells

with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Done. Notebook now has {len(nb['cells'])} cells.")
print(f"  Section 11: {len(new_section)} cells inserted at position {insert_at}")
print(f"  Exercises 3+4: {len(new_exercises)} cells appended at end")

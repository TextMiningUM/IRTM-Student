"""Inspect canonical schemas of all existing cyber training files.

Extracts the union of keys present in each file so we can build one
superset schema for the merged cyber_*.json outputs.
"""
import json, os
from collections import OrderedDict

D = r'IRTM-Admin/source/13 agentic_training_data/training_data'

GROUPS = {
    'rag_chunks':   ['rag_chunks.json', 'pentest_rag_chunks.json'],
    'concept_graph':['concept_graph.json', 'pentest_concept_graph.json'],
    'sft':          ['sft_trajectories.json', 'pentest_sft_trajectories.json'],
    'rlhf':         ['rlhf_preference_pairs.json', 'mitre_rlhf_pairs.json'],
    'multihop':     ['multihop_chains.json', 'pentest_multihop_chains.json'],
    'validation':   ['validation_questions.json'],
}

def keys_of(obj):
    if isinstance(obj, dict):
        return set(obj.keys())
    return set()

def union_keys(records):
    u = set()
    for r in records:
        u |= keys_of(r)
    return u

for group, files in GROUPS.items():
    print(f'\n=== {group} ===')
    union = set()
    nested_unions = {}
    for f in files:
        path = os.path.join(D, f)
        if not os.path.exists(path):
            continue
        recs = json.load(open(path, encoding='utf-8'))
        if not isinstance(recs, list):
            continue
        u = union_keys(recs)
        union |= u
        # nested children: hops, steps, links
        for child_key in ('hops', 'steps'):
            child_recs = []
            for r in recs:
                if isinstance(r, dict) and isinstance(r.get(child_key), list):
                    child_recs += [c for c in r[child_key] if isinstance(c, dict)]
            if child_recs:
                nested_unions.setdefault(child_key, set())
                nested_unions[child_key] |= union_keys(child_recs)
        print(f'  {f:40s}  n={len(recs):4d}  keys={sorted(u)}')
    print(f'  UNION top-level: {sorted(union)}')
    for k, u in nested_unions.items():
        print(f'  UNION {k}.*: {sorted(u)}')

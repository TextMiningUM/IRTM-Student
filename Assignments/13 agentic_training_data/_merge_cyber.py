"""Merge all cyber-domain training data sources into unified cyber_*.json files.

Sources merged (in priority order — first-seen wins on duplicate ids):
  1. Original book extraction:    rag_chunks, concept_graph, sft_trajectories, rlhf_preference_pairs, multihop_chains, validation_questions
  2. Pentest enrichment:          pentest_*
  3. Existing MITRE RLHF:         mitre_rlhf_pairs
  4. New ATT&CK extraction:       attack_*
  5. New CWE extraction:          cwe_*
  6. New CAPEC extraction:        capec_*
  7. New OWASP extraction:        owasp_*

Outputs (in training_data/):
  cyber_rag_chunks.json
  cyber_concept_graph.json
  cyber_sft_trajectories.json
  cyber_rlhf_pairs.json
  cyber_multihop_chains.json
  cyber_validation_questions.json   (passthrough copy of validation_questions.json)

Schema for each output is the canonical superset; missing fields are filled with
sensible defaults so all records share the same keys.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / 'training_data'


def read_json(name: str) -> list[dict]:
    p = DATA / name
    if not p.exists():
        return []
    try:
        with p.open(encoding='utf-8') as f:
            d = json.load(f)
        return d if isinstance(d, list) else []
    except Exception as e:
        print(f'  ! could not read {name}: {e}')
        return []


def write_json(name: str, data: list[dict]) -> None:
    p = DATA / name
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'  wrote {name}: {len(data)} records  ({p.stat().st_size//1024} KB)')


def hash_key(*parts) -> str:
    return hashlib.sha1('|'.join(str(p) for p in parts).encode('utf-8')).hexdigest()[:12]


# ── canonical normalisers ────────────────────────────────────────────────────

def norm_rag(rec: dict, default_source: str) -> dict | None:
    text = (rec.get('text') or '').strip()
    if not text:
        return None
    return {
        'chunk_id':    rec.get('chunk_id') or hash_key('rag', text[:200]),
        'text':        text,
        'chapter':     rec.get('chapter') or rec.get('section') or '',
        'document':    rec.get('document') or rec.get('source_doc') or '',
        'page':        rec.get('page', 0) or 0,
        'chunk_type':  rec.get('chunk_type') or 'definition',
        'difficulty':  rec.get('difficulty') or 'intermediate',
        'concepts':    rec.get('concepts') or [],
        'framing':     rec.get('framing') or '',
        'source_url':  rec.get('source_url') or '',
        'source':      rec.get('source') or default_source,
    }


def norm_concept(rec: dict, default_source: str) -> dict | None:
    name = (rec.get('concept') or rec.get('name') or '').strip()
    if not name:
        return None
    return {
        'concept':       name,
        'definition':    rec.get('definition') or rec.get('description') or '',
        'category':      rec.get('category') or '',
        'chapter_refs':  rec.get('chapter_refs') or [],
        'related_to':    rec.get('related_to') or rec.get('related') or [],
        'source':        rec.get('source') or default_source,
    }


def norm_sft_step(s: dict, idx: int) -> dict:
    return {
        'step_number':     s.get('step_number') or s.get('step') or (idx + 1),
        'observation':     s.get('observation') or s.get('observe') or '',
        'thought':         s.get('thought') or s.get('reasoning') or '',
        'action':          s.get('action') or '',
        'action_type':     s.get('action_type') or s.get('type') or '',
        'tool_used':       s.get('tool_used') or s.get('tool') or '',
        'expected_result': s.get('expected_result') or s.get('result') or '',
        'concepts':        s.get('concepts') or [],
    }


def norm_sft(rec: dict, default_source: str) -> dict | None:
    steps_raw = rec.get('steps') or rec.get('trajectory') or []
    if not steps_raw:
        return None
    steps = [norm_sft_step(s, i) for i, s in enumerate(steps_raw)]
    return {
        'scenario_id': rec.get('scenario_id') or rec.get('id')
                       or hash_key('sft', rec.get('scenario', ''), len(steps)),
        'scenario':    rec.get('scenario') or rec.get('title') or '',
        'chapter':     rec.get('chapter') or '',
        'framing':     rec.get('framing') or '',
        'source':      rec.get('source') or default_source,
        'steps':       steps,
    }


def norm_rlhf(rec: dict, default_source: str) -> dict | None:
    chosen = rec.get('chosen_action') or rec.get('chosen') or ''
    rejected = rec.get('rejected_action') or rec.get('rejected') or ''
    if not chosen or not rejected:
        return None
    return {
        'pair_id':            rec.get('pair_id') or rec.get('id')
                              or hash_key('rlhf', chosen[:200], rejected[:200]),
        'context':            rec.get('context') or rec.get('prompt') or '',
        'chosen_action':      chosen,
        'chosen_reasoning':   rec.get('chosen_reasoning') or '',
        'rejected_action':    rejected,
        'rejected_reasoning': rec.get('rejected_reasoning') or '',
        'category':           rec.get('category') or 'security',
        'framing':            rec.get('framing') or '',
        'source':             rec.get('source') or default_source,
        'attacker_goal':      rec.get('attacker_goal') or '',
        'detection_signals':  rec.get('detection_signals') or [],
        'mitre_mitigations':  rec.get('mitre_mitigations') or [],
        'tactic':             rec.get('tactic') or '',
        'tactic_id':          rec.get('tactic_id') or '',
        'technique':          rec.get('technique') or '',
        'technique_id':       rec.get('technique_id') or '',
    }


def norm_multihop_hop(h: dict, idx: int) -> dict:
    return {
        'hop_number':  h.get('hop_number') or h.get('hop') or (idx + 1),
        'observation': h.get('observation') or '',
        'inference':   h.get('inference') or h.get('thought') or '',
    }


def norm_multihop(rec: dict, default_source: str) -> dict | None:
    hops_raw = rec.get('hops') or rec.get('chain') or []
    if not hops_raw:
        return None
    hops = [norm_multihop_hop(h, i) for i, h in enumerate(hops_raw)]
    return {
        'chain_id':     rec.get('chain_id') or rec.get('id')
                        or hash_key('mh', rec.get('question', ''), len(hops)),
        'question':     rec.get('question') or rec.get('query') or '',
        'chapter_refs': rec.get('chapter_refs') or [],
        'concepts':     rec.get('concepts') or [],
        'hops':         hops,
        'conclusion':   rec.get('conclusion') or rec.get('answer') or '',
        'source':       rec.get('source') or default_source,
    }


# ── merge driver ─────────────────────────────────────────────────────────────

# (filename, default_source_tag)
RAG_SOURCES = [
    ('rag_chunks.json',         'cyber_book'),
    ('pentest_rag_chunks.json', 'pentest_book'),
    ('cwe_rag_chunks.json',     'mitre_cwe'),
    ('owasp_rag_chunks.json',   'owasp_cheat_sheets'),
]
CONCEPT_SOURCES = [
    ('concept_graph.json',          'cyber_book'),
    ('pentest_concept_graph.json',  'pentest_book'),
    ('attack_concept_graph.json',   'mitre_attack_enterprise'),
    ('cwe_concept_graph.json',      'mitre_cwe'),
    ('capec_concept_graph.json',    'mitre_capec'),
]
SFT_SOURCES = [
    ('sft_trajectories.json',         'cyber_book'),
    ('pentest_sft_trajectories.json', 'pentest_book'),
    ('attack_sft_trajectories.json',  'mitre_attack_enterprise'),
    ('capec_sft_trajectories.json',   'mitre_capec'),
]
RLHF_SOURCES = [
    ('rlhf_preference_pairs.json', 'cyber_book'),
    ('mitre_rlhf_pairs.json',      'mitre_rlhf_seed'),
    ('attack_rlhf_pairs.json',     'mitre_attack_enterprise'),
    ('cwe_rlhf_pairs.json',        'mitre_cwe'),
    ('owasp_rlhf_pairs.json',      'owasp_cheat_sheets'),
]
MULTIHOP_SOURCES = [
    ('multihop_chains.json',           'cyber_book'),
    ('pentest_multihop_chains.json',   'pentest_book'),
    ('attack_multihop_chains.json',    'mitre_attack_enterprise'),
]


def merge(sources: list[tuple[str, str]], normaliser, key_fn) -> list[dict]:
    seen: dict[str, dict] = {}
    per_source_counts: dict[str, int] = {}
    for fname, tag in sources:
        records = read_json(fname)
        added = 0
        for r in records:
            n = normaliser(r, tag)
            if n is None:
                continue
            k = key_fn(n)
            if k in seen:
                continue
            seen[k] = n
            added += 1
        per_source_counts[fname] = added
    print('    per-source kept:')
    for f, c in per_source_counts.items():
        print(f'      {f:40s} -> {c}')
    return list(seen.values())


def main():
    print('=== merge cyber training data ===')

    print('  rag chunks:')
    rag = merge(RAG_SOURCES, norm_rag,
                key_fn=lambda r: r['chunk_id'] or hash_key('text', r['text'][:200]))
    write_json('cyber_rag_chunks.json', rag)

    print('  concept graph:')
    cg = merge(CONCEPT_SOURCES, norm_concept,
               key_fn=lambda r: r['concept'].strip().lower())
    write_json('cyber_concept_graph.json', cg)

    print('  sft trajectories:')
    sft = merge(SFT_SOURCES, norm_sft,
                key_fn=lambda r: r['scenario_id'])
    write_json('cyber_sft_trajectories.json', sft)

    print('  rlhf pairs:')
    rlhf = merge(RLHF_SOURCES, norm_rlhf,
                 key_fn=lambda r: r['pair_id'])
    write_json('cyber_rlhf_pairs.json', rlhf)

    print('  multihop chains:')
    mh = merge(MULTIHOP_SOURCES, norm_multihop,
               key_fn=lambda r: r['chain_id'])
    write_json('cyber_multihop_chains.json', mh)

    # Validation questions = simple passthrough for the cyber book
    val = read_json('validation_questions.json')
    write_json('cyber_validation_questions.json', val)


if __name__ == '__main__':
    main()

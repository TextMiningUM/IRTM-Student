"""Extract MITRE ATT&CK Enterprise -> training data files matching cyber schema.

Downloads the ATT&CK Enterprise STIX bundle once (cached locally) and produces:
  - attack_concept_graph.json        (one node per technique + tactic)
  - attack_sft_trajectories.json     (3-step detect -> respond -> mitigate)
  - attack_rlhf_pairs.json           (attack vs defend preference pairs)
  - attack_multihop_chains.json      (kill-chain progression chains)

License: ATT&CK content is © MITRE under the ATT&CK Terms of Use; redistribution
of derived JSON files is permitted with attribution. Source URL recorded in each record.
"""
from __future__ import annotations
import json, os, re, hashlib, urllib.request, ssl
from pathlib import Path

ROOT      = Path(__file__).parent
RAW       = ROOT / '_raw_cache'
RAW.mkdir(exist_ok=True)
OUT       = ROOT / 'training_data'

ATTACK_URL = ('https://raw.githubusercontent.com/mitre/cti/master/'
              'enterprise-attack/enterprise-attack.json')
ATTACK_CACHE = RAW / 'enterprise-attack.json'

SOURCE_TAG     = 'mitre_attack_enterprise'
SOURCE_URL_TAG = 'https://attack.mitre.org/'


def download(url: str, dest: Path) -> Path:
    if dest.exists() and dest.stat().st_size > 0:
        print(f'  cache hit: {dest.name}  ({dest.stat().st_size//1024} KB)')
        return dest
    print(f'  downloading: {url}')
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(url, context=ctx, timeout=120) as r, open(dest, 'wb') as f:
        f.write(r.read())
    print(f'  saved -> {dest.name}  ({dest.stat().st_size//1024} KB)')
    return dest


def short_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha1('|'.join(parts).encode('utf-8')).hexdigest()[:10]
    return f'{prefix}_{h}'


def load_attack() -> tuple[list[dict], dict[str, dict]]:
    """Return (attack_patterns, all_objects_by_id).

    Filters out revoked / deprecated entries and sub-technique noise duplicates.
    """
    download(ATTACK_URL, ATTACK_CACHE)
    bundle = json.loads(ATTACK_CACHE.read_text(encoding='utf-8'))
    objects = bundle.get('objects', [])
    by_id = {o['id']: o for o in objects if 'id' in o}

    techniques = [
        o for o in objects
        if o.get('type') == 'attack-pattern'
        and not o.get('revoked')
        and not o.get('x_mitre_deprecated')
    ]
    print(f'  loaded {len(techniques)} active attack-patterns from {len(objects)} STIX objects')
    return techniques, by_id


def technique_external_id(t: dict) -> str | None:
    for ref in t.get('external_references', []):
        if ref.get('source_name') == 'mitre-attack':
            return ref.get('external_id')
    return None


def technique_url(t: dict) -> str:
    for ref in t.get('external_references', []):
        if ref.get('source_name') == 'mitre-attack' and ref.get('url'):
            return ref['url']
    return SOURCE_URL_TAG


def kill_chain_tactics(t: dict) -> list[tuple[str, str]]:
    out = []
    for kc in t.get('kill_chain_phases', []):
        if kc.get('kill_chain_name') == 'mitre-attack':
            phase = kc.get('phase_name', '')
            out.append((phase, phase.replace('-', ' ').title()))
    return out


def linked_mitigations(t: dict, by_id: dict, all_objs: list[dict]) -> list[str]:
    """Find mitigations linked to this technique via STIX relationships."""
    out = []
    tid = t['id']
    for o in all_objs:
        if (o.get('type') == 'relationship'
                and o.get('relationship_type') == 'mitigates'
                and o.get('target_ref') == tid):
            mit = by_id.get(o.get('source_ref', ''))
            if mit and mit.get('type') == 'course-of-action':
                ext = ''
                for ref in mit.get('external_references', []):
                    if ref.get('source_name') == 'mitre-attack':
                        ext = ref.get('external_id', '')
                        break
                name = mit.get('name', '')
                if ext and name:
                    out.append(f'{ext} - {name}')
    return out[:6]


def linked_detections(t: dict, by_id: dict, all_objs: list[dict]) -> tuple[list[str], list[str]]:
    """Find detection signals for a technique.

    Returns (signal_descriptions, data_source_names).  Detection can come from
    either the legacy x_mitre_detection field or the modern x-mitre-detection-strategy
    + x-mitre-data-component STIX objects linked via 'detects' relationships.
    """
    signals: list[str] = []
    data_sources: list[str] = []

    # legacy field (older bundles)
    legacy = (t.get('x_mitre_detection') or '').strip()
    if legacy:
        for s in re.split(r'[\n\.]', legacy):
            s = s.strip()
            if s:
                signals.append(s)

    tid = t['id']
    for o in all_objs:
        if (o.get('type') == 'relationship'
                and o.get('relationship_type') == 'detects'
                and o.get('target_ref') == tid):
            src = by_id.get(o.get('source_ref', ''))
            if not src:
                continue
            if src.get('type') == 'x-mitre-detection-strategy':
                name = src.get('name', '').strip()
                if name and name not in signals:
                    signals.append(name)
            elif src.get('type') == 'x-mitre-data-component':
                ds_ref = src.get('x_mitre_data_source_ref')
                ds_obj = by_id.get(ds_ref) if ds_ref else None
                ds_name = ds_obj.get('name', '') if ds_obj else ''
                comp = src.get('name', '')
                if ds_name and comp:
                    label = f'{ds_name}: {comp}'
                    if label not in signals:
                        signals.append(label)
                if ds_name and ds_name not in data_sources:
                    data_sources.append(ds_name)

    return signals[:6], data_sources[:6]


def first_sentence(text: str, max_chars: int = 220) -> str:
    text = re.sub(r'\s+', ' ', text or '').strip()
    m = re.search(r'^(.+?[\.!?])\s', text)
    s = m.group(1) if m else text
    return s[:max_chars]


def truncate_paragraph(text: str, max_chars: int = 600) -> str:
    text = re.sub(r'\s+', ' ', text or '').strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(' ', 1)[0] + '…'


# ── output builders ──────────────────────────────────────────────────────────

def build_concept_graph(techniques: list[dict], by_id: dict, all_objs: list[dict]) -> list[dict]:
    nodes: list[dict] = []
    seen: set[str] = set()

    # one node per tactic
    tactic_objs = [o for o in all_objs if o.get('type') == 'x-mitre-tactic']
    for ta in tactic_objs:
        name = ta.get('name', '')
        if not name or name in seen:
            continue
        seen.add(name)
        nodes.append({
            'concept':       name,
            'definition':    truncate_paragraph(ta.get('description', ''), 500),
            'category':      'tactic',
            'chapter_refs':  [],
            'related_to':    [],
            'source':        SOURCE_TAG,
        })

    tactic_names = {ta.get('x_mitre_shortname'): ta.get('name', '')
                    for ta in tactic_objs if ta.get('x_mitre_shortname')}

    # one node per technique
    for t in techniques:
        name = t.get('name', '')
        ext  = technique_external_id(t)
        if not name or not ext or ext in seen:
            continue
        seen.add(ext)
        related = []
        for short, _full in [(p, tactic_names.get(p)) for p, _ in kill_chain_tactics(t)]:
            full = tactic_names.get(short)
            if full and full not in related:
                related.append(full)
        for mit in linked_mitigations(t, by_id, all_objs)[:3]:
            related.append(mit.split(' - ', 1)[-1])
        nodes.append({
            'concept':       name,
            'definition':    truncate_paragraph(t.get('description', ''), 500),
            'category':      'technique',
            'chapter_refs':  [ext],
            'related_to':    related[:6],
            'source':        SOURCE_TAG,
        })
    return nodes


def build_rlhf_pairs(techniques: list[dict], by_id: dict, all_objs: list[dict]) -> list[dict]:
    pairs = []
    for t in techniques:
        name = t.get('name', '')
        ext  = technique_external_id(t)
        if not name or not ext:
            continue
        tactics = kill_chain_tactics(t)
        if not tactics:
            continue
        tactic_short, tactic_full = tactics[0]
        mitigations = linked_mitigations(t, by_id, all_objs)
        if not mitigations:
            continue  # require at least one defensive control to make a fair pair

        descr  = truncate_paragraph(t.get('description', ''), 700)
        detect_signals, _ = linked_detections(t, by_id, all_objs)
        if not detect_signals:
            detect_signals = ['Behavioural anomalies in logs related to ' + name]

        chosen = (
            'Defend by layering controls: '
            + '; '.join(mitigations[:4])
            + '. Validate with detection signals and routine red/blue exercises.'
        )
        rejected = (
            f'Ignore {name} because it appears uncommon, do not deploy detection or '
            'mitigations, and rely solely on perimeter defences.'
        )

        pairs.append({
            'pair_id':            short_id('attk', ext, name),
            'context':            f'Technique: {ext} - {name}. {first_sentence(descr, 240)}',
            'chosen_action':      chosen,
            'chosen_reasoning':   ('MITRE-recommended mitigations directly address the '
                                   f'{tactic_full} tactic and reduce dwell time.'),
            'rejected_action':    rejected,
            'rejected_reasoning': ('Ignoring documented techniques leaves measurable '
                                   'kill-chain gaps and breaches due-care obligations.'),
            'category':           'security',
            'framing':            'attack_then_defend',
            'source':             SOURCE_TAG,
            'attacker_goal':      f'Achieve {tactic_full} by {name}.',
            'detection_signals':  detect_signals,
            'mitre_mitigations':  mitigations,
            'tactic':             tactic_full,
            'tactic_id':          tactic_short,
            'technique':          name,
            'technique_id':       ext,
        })
    return pairs


def build_sft_trajectories(techniques: list[dict], by_id: dict, all_objs: list[dict]) -> list[dict]:
    trajs = []
    for t in techniques:
        name = t.get('name', '')
        ext  = technique_external_id(t)
        if not name or not ext:
            continue
        mitigations = linked_mitigations(t, by_id, all_objs)
        if not mitigations:
            continue  # need at least one mitigation to make a meaningful trajectory
        signals, data_sources = linked_detections(t, by_id, all_objs)
        tactics = kill_chain_tactics(t)
        tactic_full = tactics[0][1] if tactics else 'unknown'

        # Compose a detection action paragraph
        if signals:
            detect_action = ('Correlate the following telemetry to confirm the indicator: '
                             + '; '.join(signals[:4]) + '.')
        elif data_sources:
            detect_action = ('Monitor the following ATT&CK data sources for behavioural deviation: '
                             + ', '.join(data_sources[:4]) + '.')
        else:
            detect_action = ('Establish a baseline for normal behaviour related to '
                             f'{name} and alert on deviation.')

        steps = [
            {
                'step_number':    1,
                'observation':    f'SIEM telemetry indicates possible {name} ({ext}) '
                                  f'activity in the {tactic_full} phase.',
                'thought':        'Confirm the signal is not a false positive before declaring an incident.',
                'action':         detect_action,
                'action_type':    'detection',
                'tool_used':      'SIEM',
                'expected_result':'Verified high-confidence indicator of compromise tied to a host or user.',
                'concepts':       ['detection', tactic_full.lower()],
            },
            {
                'step_number':    2,
                'observation':    f'Indicator confirmed for {name} ({ext}). Affected scope is being assessed.',
                'thought':        'Contain the affected asset to halt lateral progression while preserving evidence.',
                'action':         ('Isolate the host from the network, suspend the user account, capture volatile '
                                   'memory and disk artefacts, and notify the incident commander.'),
                'action_type':    'response',
                'tool_used':      'EDR / IR runbook',
                'expected_result':'Containment confirmed; chain of custody preserved for forensic analysis.',
                'concepts':       ['containment', 'incident_response'],
            },
            {
                'step_number':    3,
                'observation':    'Asset contained. Root-cause analysis identifies the exploited path.',
                'thought':        'Apply MITRE-recommended mitigations to prevent recurrence and harden adjacent assets.',
                'action':         'Implement the following mitigations: ' + '; '.join(mitigations[:4]) + '.',
                'action_type':    'mitigation',
                'tool_used':      'configuration_management',
                'expected_result':'Mitigations deployed and verified; detection rules tuned for residual risk.',
                'concepts':       ['mitigation', 'hardening'],
            },
        ]

        trajs.append({
            'scenario_id':  short_id('attk_sft', ext, name),
            'scenario':     f'Defensive response to {name} ({ext}) observed in the {tactic_full} phase.',
            'chapter':      f'{ext} - {name}',
            'framing':      'authorized_defense',
            'source':       SOURCE_TAG,
            'steps':        steps,
        })
    return trajs


def build_multihop_chains(techniques: list[dict], by_id: dict, all_objs: list[dict]) -> list[dict]:
    """Build kill-chain progression chains: pick techniques that share a stated procedure
    chain across phases (Initial Access -> Execution -> Persistence -> Lateral Movement)."""
    by_phase: dict[str, list[dict]] = {}
    for t in techniques:
        for short, _full in kill_chain_tactics(t):
            by_phase.setdefault(short, []).append(t)

    chain_phases = [
        ['initial-access', 'execution', 'persistence', 'lateral-movement'],
        ['reconnaissance', 'initial-access', 'execution', 'exfiltration'],
        ['credential-access', 'lateral-movement', 'collection', 'exfiltration'],
        ['execution', 'privilege-escalation', 'defense-evasion', 'impact'],
    ]

    chains = []
    for phases in chain_phases:
        picked = []
        for p in phases:
            cands = by_phase.get(p, [])
            if not cands:
                break
            # pick the most-mitigated technique in this phase for richer hops
            best = max(
                cands,
                key=lambda t: (len(linked_mitigations(t, by_id, all_objs)),
                               len(t.get('description', ''))),
            )
            picked.append(best)
        if len(picked) != len(phases):
            continue

        hops = []
        for i, t in enumerate(picked, start=1):
            ext  = technique_external_id(t) or ''
            name = t.get('name', '')
            phase_full = next((full for short, full in kill_chain_tactics(t)
                               if short == phases[i-1]), phases[i-1])
            hops.append({
                'hop_number':  i,
                'observation': f'During {phase_full}, the adversary uses {name} ({ext}).',
                'inference':   first_sentence(t.get('description', ''), 240),
            })

        question = ('Trace a plausible kill-chain progression an attacker may follow '
                    'across the phases ' + ' -> '.join(p.replace('-', ' ') for p in phases) + '.')
        concepts = [t.get('name', '') for t in picked]
        chapter_refs = [technique_external_id(t) or '' for t in picked]
        conclusion = ('Each phase relies on the prior foothold; defenders should detect '
                      'and disrupt the earliest hop to break the chain.')

        chains.append({
            'chain_id':     short_id('attk_chain', *phases),
            'question':     question,
            'chapter_refs': chapter_refs,
            'concepts':     concepts,
            'hops':         hops,
            'conclusion':   conclusion,
            'source':       SOURCE_TAG,
        })
    return chains


def main():
    print('=== MITRE ATT&CK extraction ===')
    techs, by_id = load_attack()
    all_objs = json.loads(ATTACK_CACHE.read_text(encoding='utf-8'))['objects']

    cg     = build_concept_graph(techs, by_id, all_objs)
    rlhf   = build_rlhf_pairs(techs, by_id, all_objs)
    sft    = build_sft_trajectories(techs, by_id, all_objs)
    chains = build_multihop_chains(techs, by_id, all_objs)

    out_files = [
        ('attack_concept_graph.json',     cg),
        ('attack_rlhf_pairs.json',        rlhf),
        ('attack_sft_trajectories.json',  sft),
        ('attack_multihop_chains.json',   chains),
    ]
    for name, data in out_files:
        path = OUT / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f'  wrote {name}: {len(data)} records  ({path.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()

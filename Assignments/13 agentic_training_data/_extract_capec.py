"""Extract MITRE CAPEC -> training data files matching cyber schema.

Downloads the latest CAPEC XML from capec.mitre.org once (cached locally) and produces:
  - capec_concept_graph.json   (one node per attack pattern)
  - capec_sft_trajectories.json (Execution_Flow steps -> agentic trajectory)
"""
from __future__ import annotations
import json, re, hashlib, urllib.request, ssl, zipfile, io
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent
RAW  = ROOT / '_raw_cache'
RAW.mkdir(exist_ok=True)
OUT  = ROOT / 'training_data'

CAPEC_URL   = 'https://capec.mitre.org/data/xml/capec_latest.xml.zip'
CAPEC_CACHE = RAW / 'capec_latest.xml'

SOURCE_TAG     = 'mitre_capec'
SOURCE_URL_TAG = 'https://capec.mitre.org/'

NS = {}


def download_and_extract():
    if CAPEC_CACHE.exists() and CAPEC_CACHE.stat().st_size > 0:
        print(f'  cache hit: {CAPEC_CACHE.name}  ({CAPEC_CACHE.stat().st_size//1024} KB)')
        return CAPEC_CACHE
    print(f'  downloading: {CAPEC_URL}')
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(CAPEC_URL, context=ctx, timeout=120) as r:
            data = r.read()
    except Exception as e:
        # fallback: capec sometimes serves XML directly
        alt = 'https://capec.mitre.org/data/xml/capec_latest.xml'
        print(f'  zip failed ({e}), trying {alt}')
        with urllib.request.urlopen(alt, context=ctx, timeout=120) as r:
            data = r.read()
        CAPEC_CACHE.write_bytes(data)
        print(f'  saved -> {CAPEC_CACHE.name}  ({CAPEC_CACHE.stat().st_size//1024} KB)')
        return CAPEC_CACHE
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith('.xml')]
        with zf.open(names[0]) as src, open(CAPEC_CACHE, 'wb') as dst:
            dst.write(src.read())
    print(f'  saved -> {CAPEC_CACHE.name}  ({CAPEC_CACHE.stat().st_size//1024} KB)')
    return CAPEC_CACHE


def short_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha1('|'.join(parts).encode('utf-8')).hexdigest()[:10]
    return f'{prefix}_{h}'


def text_content(el) -> str:
    if el is None:
        return ''
    parts = [(el.text or '')]
    for child in el:
        parts.append(text_content(child))
        if child.tail:
            parts.append(child.tail)
    return re.sub(r'\s+', ' ', ''.join(parts)).strip()


def truncate(text: str, n: int = 600) -> str:
    text = re.sub(r'\s+', ' ', text or '').strip()
    if len(text) <= n:
        return text
    return text[:n].rsplit(' ', 1)[0] + '…'


def first_sentence(text: str, n: int = 220) -> str:
    text = re.sub(r'\s+', ' ', text or '').strip()
    m = re.search(r'^(.+?[\.!?])\s', text)
    s = m.group(1) if m else text
    return s[:n]


def parse_capec(xml_path: Path) -> list[dict]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns_match = re.match(r'\{(.+)\}', root.tag)
    ns = {'c': ns_match.group(1)} if ns_match else {}
    NS.clear(); NS.update(ns)

    patterns = []
    container = root.find('c:Attack_Patterns', NS)
    if container is None:
        return patterns

    for ap in container.findall('c:Attack_Pattern', NS):
        pid    = ap.get('ID', '')
        name   = ap.get('Name', '')
        abstr  = ap.get('Abstraction', '')
        status = ap.get('Status', '')
        if status in ('Deprecated', 'Obsolete'):
            continue
        descr  = text_content(ap.find('c:Description', NS))

        # execution flow
        steps = []
        ef = ap.find('c:Execution_Flow', NS)
        if ef is not None:
            for s in ef.findall('c:Attack_Step', NS):
                step_no = text_content(s.find('c:Step', NS)) or ''
                phase   = text_content(s.find('c:Phase', NS)) or ''
                desc    = text_content(s.find('c:Description', NS)) or ''
                techs   = [text_content(t) for t in s.findall('c:Technique', NS)]
                steps.append({
                    'step_no': step_no,
                    'phase':   phase,
                    'descr':   desc,
                    'techs':   [t for t in techs if t],
                })

        # prerequisites
        prereqs = []
        pr = ap.find('c:Prerequisites', NS)
        if pr is not None:
            for el in pr.findall('c:Prerequisite', NS):
                t = text_content(el)
                if t:
                    prereqs.append(t)

        # mitigations
        mitigations = []
        mt = ap.find('c:Mitigations', NS)
        if mt is not None:
            for el in mt.findall('c:Mitigation', NS):
                t = text_content(el)
                if t:
                    mitigations.append(t)

        # consequences
        consequences = []
        cc = ap.find('c:Consequences', NS)
        if cc is not None:
            for cons in cc.findall('c:Consequence', NS):
                impacts = [text_content(s) for s in cons.findall('c:Impact', NS)]
                if impacts:
                    consequences.extend(i for i in impacts if i)

        # related weaknesses (CWEs)
        related_cwes = []
        rw = ap.find('c:Related_Weaknesses', NS)
        if rw is not None:
            for r in rw.findall('c:Related_Weakness', NS):
                cwe = r.get('CWE_ID', '')
                if cwe:
                    related_cwes.append(f'CWE-{cwe}')

        # related attack patterns
        related_aps = []
        ra = ap.find('c:Related_Attack_Patterns', NS)
        if ra is not None:
            for r in ra.findall('c:Related_Attack_Pattern', NS):
                rid = r.get('CAPEC_ID', '')
                nat = r.get('Nature', '')
                if rid:
                    related_aps.append(f'{nat}:CAPEC-{rid}')

        patterns.append({
            'capec_id':     pid,
            'name':         name,
            'abstraction':  abstr,
            'description':  descr,
            'steps':        steps,
            'prereqs':      prereqs,
            'mitigations':  mitigations,
            'consequences': consequences,
            'related_cwes': related_cwes,
            'related_aps':  related_aps,
        })
    print(f'  parsed {len(patterns)} active attack patterns')
    return patterns


# ── output builders ──────────────────────────────────────────────────────────

def build_concept_graph(patterns: list[dict]) -> list[dict]:
    nodes = []
    for p in patterns:
        capec_label = f'CAPEC-{p["capec_id"]}'
        related = []
        for r in p['related_aps'][:6]:
            related.append(r.split(':', 1)[-1])
        related.extend(p['related_cwes'][:4])
        nodes.append({
            'concept':       f'{capec_label} {p["name"]}'.strip(),
            'definition':    truncate(p['description'], 500),
            'category':      f'attack_pattern:{p["abstraction"].lower()}' if p['abstraction'] else 'attack_pattern',
            'chapter_refs':  [capec_label],
            'related_to':    related,
            'source':        SOURCE_TAG,
        })
    return nodes


def build_sft_trajectories(patterns: list[dict]) -> list[dict]:
    trajs = []
    for p in patterns:
        if not p['steps'] or not p['mitigations']:
            continue
        capec_label = f'CAPEC-{p["capec_id"]}'

        # Build defender steps mirroring attacker execution flow
        atk_steps = p['steps']
        steps_out = []

        # Step 1: detection during reconnaissance/early phase
        first = atk_steps[0]
        steps_out.append({
            'step_number': 1,
            'observation': f'Telemetry suggests an attacker may be in the "{first["phase"] or "Explore"}" phase of {capec_label}: {truncate(first["descr"], 220)}',
            'thought':     'Confirm intent and scope before triggering containment.',
            'action':      ('Watch for the following activity patterns: '
                            + truncate('; '.join(s['descr'] for s in atk_steps[:3] if s.get('descr')), 500)),
            'action_type': 'detection',
            'tool_used':   'SIEM / EDR',
            'expected_result': 'Validated alert with attacker phase identified.',
            'concepts':    [capec_label] + p['related_cwes'][:3],
        })

        # Step 2: containment
        steps_out.append({
            'step_number': 2,
            'observation': 'Detection confirmed. Need to interrupt the attack chain before objectives are met.',
            'thought':     'Limit blast radius while preserving forensic evidence.',
            'action':      ('Isolate affected assets, revoke active sessions, and block indicators '
                            'observed during detection.'),
            'action_type': 'containment',
            'tool_used':   'EDR / IAM',
            'expected_result': 'Attacker loses access while evidence is preserved.',
            'concepts':    [capec_label],
        })

        # Step 3: mitigation (long-term)
        steps_out.append({
            'step_number': 3,
            'observation': f'Containment in place. Need durable controls to prevent recurrence of {capec_label}.',
            'thought':     'Apply defence-in-depth so a single bypass does not re-enable the pattern.',
            'action':      ('Implement the following CAPEC mitigations: '
                            + truncate('; '.join(p['mitigations'][:3]), 600)),
            'action_type': 'mitigation',
            'tool_used':   'security_engineering',
            'expected_result': 'Attack pattern preconditions removed across the asset class.',
            'concepts':    [capec_label] + p['related_cwes'][:3],
        })

        trajs.append({
            'scenario_id': short_id('capec_sft', capec_label),
            'scenario':    f'Defending against {capec_label} - {p["name"]}',
            'chapter':     capec_label,
            'framing':     'authorized_defense',
            'source':      SOURCE_TAG,
            'steps':       steps_out,
        })
    return trajs


def main():
    print('=== MITRE CAPEC extraction ===')
    download_and_extract()
    patterns = parse_capec(CAPEC_CACHE)

    cg   = build_concept_graph(patterns)
    sft  = build_sft_trajectories(patterns)

    for name, data in [
        ('capec_concept_graph.json',    cg),
        ('capec_sft_trajectories.json', sft),
    ]:
        path = OUT / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f'  wrote {name}: {len(data)} records  ({path.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()

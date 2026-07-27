"""Extract MITRE CWE -> training data files matching cyber schema.

Downloads the latest CWE XML zip from cwe.mitre.org once (cached locally) and produces:
  - cwe_concept_graph.json   (one node per weakness)
  - cwe_rlhf_pairs.json      (vulnerable-pattern vs hardened-pattern preference pairs)
  - cwe_rag_chunks.json      (one chunk per CWE description block)
"""
from __future__ import annotations
import json, re, hashlib, urllib.request, ssl, zipfile, io
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent
RAW  = ROOT / '_raw_cache'
RAW.mkdir(exist_ok=True)
OUT  = ROOT / 'training_data'

CWE_URL   = 'https://cwe.mitre.org/data/xml/cwec_latest.xml.zip'
CWE_CACHE = RAW / 'cwec_latest.xml'

SOURCE_TAG     = 'mitre_cwe'
SOURCE_URL_TAG = 'https://cwe.mitre.org/'

NS = {'cwe': 'http://cwe.mitre.org/cwe-7'}


def download_and_extract():
    if CWE_CACHE.exists() and CWE_CACHE.stat().st_size > 0:
        print(f'  cache hit: {CWE_CACHE.name}  ({CWE_CACHE.stat().st_size//1024} KB)')
        return CWE_CACHE
    print(f'  downloading: {CWE_URL}')
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(CWE_URL, context=ctx, timeout=120) as r:
        zip_bytes = r.read()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        # the zip contains a single XML file like cwec_v4.x.xml
        xml_names = [n for n in zf.namelist() if n.lower().endswith('.xml')]
        if not xml_names:
            raise RuntimeError('No XML in CWE zip')
        with zf.open(xml_names[0]) as src, open(CWE_CACHE, 'wb') as dst:
            dst.write(src.read())
    print(f'  saved -> {CWE_CACHE.name}  ({CWE_CACHE.stat().st_size//1024} KB)')
    return CWE_CACHE


def short_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha1('|'.join(parts).encode('utf-8')).hexdigest()[:10]
    return f'{prefix}_{h}'


def text_content(el) -> str:
    """Extract plain text from a CWE XML element (handles xhtml subnodes)."""
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


def parse_cwe(xml_path: Path) -> list[dict]:
    """Parse weaknesses out of cwec_*.xml, returning a list of dicts."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    # detect namespace
    ns_match = re.match(r'\{(.+)\}', root.tag)
    ns = {'cwe': ns_match.group(1)} if ns_match else {}
    NS.clear(); NS.update(ns)

    weaknesses = []
    container = root.find('cwe:Weaknesses', NS)
    if container is None:
        return weaknesses
    for w in container.findall('cwe:Weakness', NS):
        wid    = w.get('ID', '')
        name   = w.get('Name', '')
        abstr  = w.get('Abstraction', '')
        status = w.get('Status', '')
        if status in ('Deprecated', 'Obsolete'):
            continue
        descr  = text_content(w.find('cwe:Description', NS))
        ext    = text_content(w.find('cwe:Extended_Description', NS))

        # mitigations
        mitigations = []
        ms = w.find('cwe:Potential_Mitigations', NS)
        if ms is not None:
            for m in ms.findall('cwe:Mitigation', NS):
                phase = ', '.join(text_content(p) for p in m.findall('cwe:Phase', NS))
                desc  = text_content(m.find('cwe:Description', NS))
                if desc:
                    mitigations.append({'phase': phase, 'description': desc})

        # demonstrative examples
        examples = []
        de = w.find('cwe:Demonstrative_Examples', NS)
        if de is not None:
            for ex in de.findall('cwe:Demonstrative_Example', NS):
                intro = text_content(ex.find('cwe:Intro_Text', NS))
                bodies = [text_content(c) for c in ex.findall('cwe:Body_Text', NS)]
                code_blocks = []
                for ce in ex.findall('cwe:Example_Code', NS):
                    nature = ce.get('Nature', '')
                    code   = text_content(ce)
                    if code:
                        code_blocks.append({'nature': nature, 'code': code})
                examples.append({
                    'intro':  intro,
                    'body':   ' '.join(b for b in bodies if b),
                    'codes':  code_blocks,
                })

        # consequences (impacts)
        consequences = []
        cc = w.find('cwe:Common_Consequences', NS)
        if cc is not None:
            for cons in cc.findall('cwe:Consequence', NS):
                scopes = [text_content(s) for s in cons.findall('cwe:Scope', NS)]
                impacts = [text_content(s) for s in cons.findall('cwe:Impact', NS)]
                note    = text_content(cons.find('cwe:Note', NS))
                consequences.append({
                    'scopes': [s for s in scopes if s],
                    'impacts': [s for s in impacts if s],
                    'note':   note,
                })

        # relationships
        related = []
        rel = w.find('cwe:Related_Weaknesses', NS)
        if rel is not None:
            for r in rel.findall('cwe:Related_Weakness', NS):
                rid = r.get('CWE_ID', '')
                nat = r.get('Nature', '')
                if rid:
                    related.append(f'{nat}:CWE-{rid}')

        weaknesses.append({
            'cwe_id':       wid,
            'name':         name,
            'abstraction':  abstr,
            'description':  descr,
            'extended':     ext,
            'mitigations':  mitigations,
            'examples':     examples,
            'consequences': consequences,
            'related':      related,
        })
    print(f'  parsed {len(weaknesses)} active weaknesses')
    return weaknesses


# ── output builders ──────────────────────────────────────────────────────────

def build_concept_graph(weaknesses: list[dict]) -> list[dict]:
    nodes = []
    for w in weaknesses:
        cwe_label = f'CWE-{w["cwe_id"]}'
        related_names = []
        for r in w['related'][:6]:
            # 'ChildOf:CWE-20' -> 'CWE-20'
            ref = r.split(':', 1)[-1]
            related_names.append(ref)
        nodes.append({
            'concept':       f'{cwe_label} {w["name"]}'.strip(),
            'definition':    truncate(w['description'] or w['extended'], 500),
            'category':      f'weakness:{w["abstraction"].lower()}' if w['abstraction'] else 'weakness',
            'chapter_refs':  [cwe_label],
            'related_to':    related_names,
            'source':        SOURCE_TAG,
        })
    return nodes


def build_rlhf_pairs(weaknesses: list[dict]) -> list[dict]:
    pairs = []
    for w in weaknesses:
        if not w['mitigations']:
            continue

        cwe_label = f'CWE-{w["cwe_id"]}'

        # try to use a real demonstrative example if it includes both Bad and Good code
        bad_code = good_code = None
        for ex in w['examples']:
            for c in ex['codes']:
                if not bad_code and c['nature'].lower() in ('bad', 'attack', 'incorrect'):
                    bad_code = truncate(c['code'], 600)
                if not good_code and c['nature'].lower() in ('good', 'fix', 'correct'):
                    good_code = truncate(c['code'], 600)
            if bad_code and good_code:
                break

        # always synthesise text-based actions; prepend code snippets if available
        mit_text = '; '.join(m['description'] for m in w['mitigations'][:3] if m.get('description'))
        chosen_action = (
            (f'Hardened pattern:\n```\n{good_code}\n```\n' if good_code else '')
            + ('Apply the following potential mitigations: ' + truncate(mit_text, 500) + '.')
        )
        rejected_action = (
            (f'Vulnerable pattern:\n```\n{bad_code}\n```\n' if bad_code else '')
            + ('Skip mitigation and assume the weakness will not be triggered in production.')
        )

        # impacts -> attacker_goal phrasing
        impacts = []
        for c in w['consequences'][:2]:
            impacts.extend(c.get('impacts', []))
        attacker_goal = ('Exploit ' + cwe_label + ' to achieve: '
                         + ', '.join(impacts[:4]) + '.') if impacts else f'Exploit {cwe_label}.'

        pairs.append({
            'pair_id':            short_id('cwe', cwe_label, w['name']),
            'context':            f'Weakness: {cwe_label} - {w["name"]}. '
                                  f'{first_sentence(w["description"] or w["extended"], 240)}',
            'chosen_action':      chosen_action,
            'chosen_reasoning':   ('Following CWE-recommended mitigations breaks the weakness '
                                   'precondition before it can be exploited.'),
            'rejected_action':    rejected_action,
            'rejected_reasoning': ('Leaving the weakness unmitigated trades short-term convenience '
                                   'for long-term breach risk and audit findings.'),
            'category':           'security',
            'framing':            'vulnerable_then_hardened',
            'source':             SOURCE_TAG,
            'attacker_goal':      attacker_goal,
            'detection_signals':  [],
            'mitre_mitigations':  [m.get('phase', '') for m in w['mitigations'][:4] if m.get('phase')],
            'tactic':             '',
            'tactic_id':          '',
            'technique':          w['name'],
            'technique_id':       cwe_label,
        })
    return pairs


def build_rag_chunks(weaknesses: list[dict]) -> list[dict]:
    chunks = []
    for w in weaknesses:
        cwe_label = f'CWE-{w["cwe_id"]}'

        # Chunk 1 - description (skip if too short)
        body = ' '.join(filter(None, [w['description'], w['extended']]))
        body = truncate(body, 1500)
        if body and len(body) >= 120:
            chunks.append({
                'chunk_id':    short_id('cwe_chunk', cwe_label, 'desc'),
                'text':        body,
                'chapter':     f'{cwe_label} {w["name"]}',
                'document':    'MITRE CWE',
                'page':        0,
                'chunk_type':  'definition',
                'difficulty':  'intermediate',
                'concepts':    [cwe_label],
                'framing':     'vulnerable_then_hardened',
                'source_url':  f'https://cwe.mitre.org/data/definitions/{w["cwe_id"]}.html',
                'source':      SOURCE_TAG,
            })

        # Chunk 2 - mitigations summary (only when we have at least 2 mitigations)
        if len(w['mitigations']) >= 2:
            mit_text = '\n'.join(
                f"- [{m.get('phase', '')}] {truncate(m.get('description', ''), 280)}"
                for m in w['mitigations'][:5]
            )
            text = (f'Potential mitigations for {cwe_label} - {w["name"]}:\n' + mit_text)
            chunks.append({
                'chunk_id':    short_id('cwe_chunk', cwe_label, 'mitig'),
                'text':        text,
                'chapter':     f'{cwe_label} {w["name"]}',
                'document':    'MITRE CWE',
                'page':        0,
                'chunk_type':  'procedure',
                'difficulty':  'intermediate',
                'concepts':    [cwe_label, 'mitigation'],
                'framing':     'authorized_defense',
                'source_url':  f'https://cwe.mitre.org/data/definitions/{w["cwe_id"]}.html',
                'source':      SOURCE_TAG,
            })
    return chunks


def main():
    print('=== MITRE CWE extraction ===')
    download_and_extract()
    weaknesses = parse_cwe(CWE_CACHE)

    cg    = build_concept_graph(weaknesses)
    rlhf  = build_rlhf_pairs(weaknesses)
    chunks = build_rag_chunks(weaknesses)

    out_files = [
        ('cwe_concept_graph.json', cg),
        ('cwe_rlhf_pairs.json',    rlhf),
        ('cwe_rag_chunks.json',    chunks),
    ]
    for name, data in out_files:
        path = OUT / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f'  wrote {name}: {len(data)} records  ({path.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()

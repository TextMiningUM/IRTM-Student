"""Extract OWASP Cheat Sheets -> training data files matching cyber schema.

The OWASP Cheat Sheet Series is published as Markdown under CC BY-SA 4.0.
We pull a curated subset of high-value sheets (raw URLs from GitHub) and produce:
  - owasp_rag_chunks.json   (one chunk per H2/H3 section)
  - owasp_rlhf_pairs.json   (do/don't preference pairs from "Recommendation" lists)
"""
from __future__ import annotations
import json, re, hashlib, urllib.request, ssl
from pathlib import Path

ROOT = Path(__file__).parent
RAW  = ROOT / '_raw_cache'
RAW.mkdir(exist_ok=True)
OUT  = ROOT / 'training_data'

SOURCE_TAG = 'owasp_cheat_sheets'
LICENSE    = 'CC BY-SA 4.0'

BASE = ('https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/'
        'cheatsheets/')

# Curated list of broadly applicable cheat sheets
SHEETS = [
    'Authentication_Cheat_Sheet.md',
    'Authorization_Cheat_Sheet.md',
    'Access_Control_Cheat_Sheet.md',
    'Session_Management_Cheat_Sheet.md',
    'Password_Storage_Cheat_Sheet.md',
    'Cryptographic_Storage_Cheat_Sheet.md',
    'Key_Management_Cheat_Sheet.md',
    'Transport_Layer_Security_Cheat_Sheet.md',
    'Input_Validation_Cheat_Sheet.md',
    'SQL_Injection_Prevention_Cheat_Sheet.md',
    'Cross_Site_Scripting_Prevention_Cheat_Sheet.md',
    'Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md',
    'Server_Side_Request_Forgery_Prevention_Cheat_Sheet.md',
    'XML_External_Entity_Prevention_Cheat_Sheet.md',
    'Deserialization_Cheat_Sheet.md',
    'File_Upload_Cheat_Sheet.md',
    'REST_Security_Cheat_Sheet.md',
    'GraphQL_Cheat_Sheet.md',
    'JWT_for_Java_Cheat_Sheet.md',
    'OAuth2_Cheat_Sheet.md',
    'Logging_Cheat_Sheet.md',
    'Logging_Vocabulary_Cheat_Sheet.md',
    'Error_Handling_Cheat_Sheet.md',
    'Secure_Cloud_Architecture_Cheat_Sheet.md',
    'Docker_Security_Cheat_Sheet.md',
    'Kubernetes_Security_Cheat_Sheet.md',
    'Threat_Modeling_Cheat_Sheet.md',
    'Attack_Surface_Analysis_Cheat_Sheet.md',
    'Vulnerable_Dependency_Management_Cheat_Sheet.md',
    'Secrets_Management_Cheat_Sheet.md',
    'Secure_Product_Design_Cheat_Sheet.md',
    'Web_Service_Security_Cheat_Sheet.md',
    'Content_Security_Policy_Cheat_Sheet.md',
    'HTTP_Headers_Cheat_Sheet.md',
    'HTML5_Security_Cheat_Sheet.md',
    'Clickjacking_Defense_Cheat_Sheet.md',
    'Database_Security_Cheat_Sheet.md',
    'NodeJS_Security_Cheat_Sheet.md',
    'DotNet_Security_Cheat_Sheet.md',
    'Java_Security_Cheat_Sheet.md',
    'Microservices_Security_Cheat_Sheet.md',
    'Microservices_based_Security_Arch_Doc_Cheat_Sheet.md',
    'Mobile_Application_Security_Cheat_Sheet.md',
    'CI_CD_Security_Cheat_Sheet.md',
    'Infrastructure_as_Code_Security_Cheat_Sheet.md',
]


def short_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha1('|'.join(parts).encode('utf-8')).hexdigest()[:10]
    return f'{prefix}_{h}'


def download(name: str) -> str | None:
    cache = RAW / ('owasp_' + name)
    if cache.exists() and cache.stat().st_size > 0:
        return cache.read_text(encoding='utf-8', errors='replace')
    url = BASE + name
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(url, context=ctx, timeout=60) as r:
            data = r.read().decode('utf-8', errors='replace')
        cache.write_text(data, encoding='utf-8')
        return data
    except Exception as e:
        print(f'  ! skip {name}: {e}')
        return None


def truncate(text: str, n: int = 1500) -> str:
    text = text.strip()
    if len(text) <= n:
        return text
    return text[:n].rsplit(' ', 1)[0] + '…'


def split_sections(md: str) -> list[tuple[str, str, str]]:
    """Split markdown into (title_h1, heading, body) sections at H2/H3."""
    lines = md.splitlines()
    h1 = ''
    sections: list[tuple[str, str, str]] = []
    cur_head = ''
    cur_body: list[str] = []
    for ln in lines:
        if ln.startswith('# '):
            h1 = ln[2:].strip()
            continue
        m = re.match(r'^(#{2,3})\s+(.+?)\s*$', ln)
        if m:
            if cur_head:
                sections.append((h1, cur_head, '\n'.join(cur_body).strip()))
            cur_head = m.group(2)
            cur_body = []
        else:
            cur_body.append(ln)
    if cur_head:
        sections.append((h1, cur_head, '\n'.join(cur_body).strip()))
    return sections


def extract_bullets(body: str) -> list[str]:
    """Pull top-level markdown bullets (``- `` or ``* ``) into a flat list."""
    out = []
    for ln in body.splitlines():
        m = re.match(r'^\s{0,3}[-*]\s+(.+?)\s*$', ln)
        if m:
            out.append(m.group(1).strip())
    return out


def is_recommend_heading(h: str) -> bool:
    h_low = h.lower()
    return any(kw in h_low for kw in (
        'recommend', 'best practice', 'rule', 'do ', "don't",
        'positive', 'negative', 'how to', 'mitigation', 'defence', 'defense',
        'prevention', 'guidance',
    ))


def looks_negative(item: str) -> bool:
    low = item.lower()
    return any(kw in low for kw in (
        "don't ", 'do not ', 'never ', 'avoid ', 'must not ',
        'should not ', 'disable ', 'remove ', 'reject ',
    ))


def looks_positive(item: str) -> bool:
    low = item.lower()
    return any(kw in low for kw in (
        'always ', 'must ', 'should ', 'use ', 'enforce ', 'enable ',
        'validate ', 'sanitize ', 'sanitise ', 'encrypt ', 'rotate ',
        'apply ', 'implement ', 'require ', 'limit ', 'verify ',
    ))


# ── output builders ──────────────────────────────────────────────────────────

def build_rag_chunks(sheet_name: str, sections: list[tuple[str, str, str]]) -> list[dict]:
    chunks = []
    sheet_url = ('https://cheatsheetseries.owasp.org/cheatsheets/'
                 + sheet_name.replace('.md', '.html'))
    for h1, head, body in sections:
        body_norm = re.sub(r'\n{3,}', '\n\n', body).strip()
        if len(body_norm) < 120:
            continue
        text = f'## {head}\n\n{truncate(body_norm, 1800)}'
        chunks.append({
            'chunk_id':    short_id('owasp_chunk', sheet_name, head),
            'text':        text,
            'chapter':     h1 or sheet_name.replace('_', ' ').replace('.md', ''),
            'document':    'OWASP Cheat Sheet Series',
            'page':        0,
            'chunk_type':  'guidance',
            'difficulty':  'intermediate',
            'concepts':    [head],
            'framing':     'authorized_defense',
            'source_url':  sheet_url,
            'source':      SOURCE_TAG,
        })
    return chunks


def build_rlhf_pairs(sheet_name: str, sections: list[tuple[str, str, str]]) -> list[dict]:
    pairs = []
    sheet_topic = sheet_name.replace('_Cheat_Sheet.md', '').replace('_', ' ')
    for h1, head, body in sections:
        bullets = extract_bullets(body)
        if len(bullets) < 2:
            continue
        positives = [b for b in bullets if looks_positive(b) and not looks_negative(b)]
        negatives = [b for b in bullets if looks_negative(b)]
        # require either the heading hints at recommendations OR we have actionable bullets
        if not (is_recommend_heading(head) or positives or negatives):
            continue

        # Strategy A: explicit positive vs negative bullets in same section
        n = min(len(positives), len(negatives))
        for i in range(n):
            pos = truncate(positives[i], 400)
            neg = truncate(negatives[i], 400)
            pairs.append({
                'pair_id':            short_id('owasp_rlhf', sheet_name, head, str(i)),
                'context':            f'Topic: {sheet_topic} - {head}',
                'chosen_action':      pos,
                'chosen_reasoning':   ('OWASP recommends this practice as the secure default '
                                       'for the topic above.'),
                'rejected_action':    neg,
                'rejected_reasoning': ('OWASP explicitly warns against this pattern; it '
                                       'creates exploitable conditions.'),
                'category':           'security',
                'framing':            'authorized_defense',
                'source':             SOURCE_TAG,
                'attacker_goal':      f'Exploit weaknesses related to {sheet_topic}.',
                'detection_signals':  [],
                'mitre_mitigations':  [],
                'tactic':             '',
                'tactic_id':          '',
                'technique':          head,
                'technique_id':       '',
            })

        # Strategy B: when only positives exist, pair "do this" against synthetic "skip it" rejection
        if not negatives and positives:
            for i, pos in enumerate(positives[:6]):
                pairs.append({
                    'pair_id':            short_id('owasp_rlhf', sheet_name, head, 'p', str(i)),
                    'context':            f'Topic: {sheet_topic} - {head}',
                    'chosen_action':      truncate(pos, 400),
                    'chosen_reasoning':   'OWASP-recommended secure default.',
                    'rejected_action':    'Skip this control because no incident has occurred yet.',
                    'rejected_reasoning': ('Skipping a baseline OWASP control trades short-term '
                                           'convenience for long-term breach risk.'),
                    'category':           'security',
                    'framing':            'authorized_defense',
                    'source':             SOURCE_TAG,
                    'attacker_goal':      f'Exploit weaknesses related to {sheet_topic}.',
                    'detection_signals':  [],
                    'mitre_mitigations':  [],
                    'tactic':             '',
                    'tactic_id':          '',
                    'technique':          head,
                    'technique_id':       '',
                })
    return pairs


def main():
    print('=== OWASP Cheat Sheets extraction ===')
    all_chunks = []
    all_pairs  = []
    fetched = 0
    for sheet in SHEETS:
        md = download(sheet)
        if md is None:
            continue
        fetched += 1
        sections = split_sections(md)
        all_chunks.extend(build_rag_chunks(sheet, sections))
        all_pairs.extend(build_rlhf_pairs(sheet, sections))

    print(f'  fetched {fetched}/{len(SHEETS)} sheets')
    for name, data in [
        ('owasp_rag_chunks.json',  all_chunks),
        ('owasp_rlhf_pairs.json',  all_pairs),
    ]:
        path = OUT / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f'  wrote {name}: {len(data)} records  ({path.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()

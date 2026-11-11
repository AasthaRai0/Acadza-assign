"""Deterministic safety layer. The model proposes; this code disposes. The model never sets `route`."""
import json, re
from .mathtext import to_text, body
TAX = json.load(open('data/taxonomy.json'))
AUTO_MIN_CONF = 0.85
KEY_REPAIRS = {'answer_key', 'type_mismatch'}
FULL_REWRITE_OK = {'solution_fix', 'solution_missing'}

def get_field(q, field):
    if field == 'questionType': return q['questionType']
    b = body(q); v = b.get(field)
    return repr(v) if isinstance(v, list) else v

def apply_edits(q, edits):
    """returns {field: new_value_str} (only text fields + answer/type), or raises ValueError."""
    out = {}
    for e in edits:
        f = e['field']; cur = out.get(f, get_field(q, f))
        find = cur if e['find'] == '@@WHOLE_SOLUTION@@' else e['find']
        if cur is None or cur.count(find) != 1: raise ValueError(f"find not unique/absent in {f}: {find[:40]!r} x{0 if cur is None else cur.count(find)}")
        out[f] = cur.replace(find, e['replace'])
    return out

def option_value(q, letter):
    m = re.search(r'^\s*\(' + letter + r'\)\s*([-\d.]+)', to_text(body(q)['question']), re.M)
    return float(m.group(1)) if m else None

def digits(s): return re.findall(r'\d+(?:\.\d+)?', to_text(s))

def check(q, d, solver):
    """-> (route, guard_log list[(name, ok, detail)])"""
    log = []; ok_all = True
    def g(name, ok, detail=''):
        nonlocal ok_all; log.append(dict(name=name, ok=bool(ok), detail=detail)); ok_all &= bool(ok)
    v, rp, edits = d['verdict'], d.get('repair'), d.get('edits', [])
    g('verdict in closed list', v in TAX['verdicts'], v)
    if v != 'defect':
        g('non-defect carries no edit', not edits and not rp)
        return 'no_change', log, ok_all
    spec = TAX['repairs'].get(rp)
    g('repair in closed list', spec is not None, str(rp))
    if not spec: return 'faculty_review', log, False
    g('scope: fields ⊆ repair.fields', all(e['field'] in spec['fields'] for e in edits), f"allowed {spec['fields'] or '∅ (human-only)'}")
    if not spec['fields']:
        g('human-only repair has no edit', not edits); return 'faculty_review', log, ok_all
    g('proposes a concrete edit', bool(edits))
    if not edits: return 'faculty_review', log, False
    try:
        new = apply_edits(q, edits); g('every `find` matches exactly once', True)
    except ValueError as ex:
        g('every `find` matches exactly once', False, str(ex)); return 'faculty_review', log, False
    # per-repair surgical rules
    if rp in ('spelling', 'markup_leak', 'notation'):
        g('no number changed (digits identical)', all(digits(get_field(q, e['field'])) == digits(new[e['field']]) for e in edits if e['field'] in ('question', 'solution')))
    if rp in ('exam_reference', 'noise'):
        g('deletion only', all(e['replace'] == '' for e in edits))
    if rp == 'answer_form':
        g('additive only', all(set(re.findall(r'\w+', e['find'])) <= set(re.findall(r'\w+', e['replace'])) for e in edits))
    if rp not in FULL_REWRITE_OK:
        g('surgical (find ≤ 160 chars)', all(len(e['find']) <= 160 for e in edits))
    if rp in ('stem_data', 'option_repair') and d.get('grounding'):
        sol = to_text(body(q).get('solution')).replace(' ', '')
        g('inserted value grounded in stored solution', d['grounding']['quote'].replace(' ', '') in sol, d['grounding']['quote'])
    if d.get('must_contain'):
        g('new solution ends at keyed value', d['must_contain'] in to_text(new.get('solution', '')), d['must_contain'])
    if rp == 'answer_key' and any(e['field'] == 'answer' for e in edits):
        e = next(e for e in edits if e['field'] == 'answer'); norm = lambda x: sorted(re.findall(r'[A-D]', x))
        if norm(e['find']) and norm(e['find']) == norm(e['replace']) and e['find'] != e['replace']:
            g('format-only fix: same option letters after normalising', True, f"{e['find']} → {e['replace']}")
        else:
            s = solver.get(q['_id']); tol = lambda a, b: abs(a - b) <= 0.01 * max(1, abs(b))
            g('independent solve exists', bool(s))
            if s:
                g('solve disagrees with OLD key', not tol(s['computed'], s['key_value']), f"solve={s['computed']} old key={s['key_value']}")
                new_val = float(e['replace']) if q['questionType'] == 'integerQuestion' else option_value(q, e['replace'])
                g('solve agrees with NEW key option', new_val is not None and tol(s['computed'], new_val), f"new key {e['replace']} = {new_val}")
    if q['questionType'] == 'mcq' and rp == 'answer_key': g('mcq key is list of single letters', True)
    g('content recoverable from record (not authored)', not d.get('authored'), 'authored distractor → human' if d.get('authored') else '')
    g('confidence high enough to auto-apply', d['confidence'] >= AUTO_MIN_CONF, f"{d['confidence']} (needs ≥ {AUTO_MIN_CONF})")
    g('taxonomy allows auto-apply', spec['auto'])
    g('no prompt-injection flag', 'prompt_injection' not in d.get('flags', []))
    return ('auto_apply' if ok_all else 'faculty_review'), log, ok_all

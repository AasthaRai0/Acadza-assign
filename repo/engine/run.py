"""Offline pipeline: decisions.json -> guards -> results.json + console/data.js. Usage: python -m engine.run"""
import json, sys, collections
from .mathtext import body
from . import guards, checks
Q = {q['_id']: q for q in json.load(open('data/questions.json'))}
R = json.load(open('data/reports.json'))
DEC = {d['reportId']: d for d in json.load(open('engine/decisions.json'))}
SOLVER = checks.run()
SEV = dict(answer_key=10, unsound=12, wrong_question=12, stem_data=7, option_repair=7, type_mismatch=7, solution_fix=6, identical_options=6,
           diagram=6, solution_missing=5, answer_form=4, wrong_chapter=3, syllabus=3, notation=3, markup_leak=3, spelling=2, noise=2, exam_reference=2)
res = []
for r in sorted(R, key=lambda r: r['reportId']):
    q = Q[r['questionId']]; d = DEC[r['reportId']]
    route, log, ok = guards.check(q, d, SOLVER)
    ed = [dict(e) for e in d['edits']]
    for e in ed:
        if e['find'] == '@@WHOLE_SOLUTION@@': e['find'] = body(q)['solution']
    row = dict(reportId=r['reportId'], questionId=r['questionId'], verdict=d['verdict'], repair=d['repair'],
               edit=(ed[0] if ed else None), route=route, confidence=d['confidence'], evidence=d['evidence'], student_reply=d['student_reply'])
    if len(ed) > 1: row['edits'] = ed
    if d.get('suggestion'): row['suggestion'] = d['suggestion']
    if d.get('flags'): row['flags'] = d['flags']
    row['guards'] = log
    res.append(row)
json.dump(res, open('results.json', 'w'), ensure_ascii=False, indent=1)
print(collections.Counter(x['route'] for x in res), collections.Counter(x['verdict'] for x in res))
for x in res:
    bad = [g['name'] for g in x['guards'] if not g['ok']]
    if x['route'] == 'faculty_review' and x['repair'] and guards.TAX['repairs'][x['repair']]['auto']: print('downgraded', x['reportId'], x['repair'], bad)

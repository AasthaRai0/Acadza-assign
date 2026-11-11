"""Builds console/data.js from results.json + sweep.json + questions.json. Usage: python -m engine.build_console"""
import json, collections
from .mathtext import body
from .run import SEV
Q = {q['_id']: q for q in json.load(open('data/questions.json'))}
REP = {r['reportId']: r for r in json.load(open('data/reports.json'))}
res = json.load(open('results.json')); sw = json.load(open('sweep.json'))
WHY = dict(answer_key='Wrong answer key', unsound='No valid answer', stem_data='Missing data in stem', option_repair='Missing / blank option', type_mismatch='Wrong question type',
           solution_fix='Wrong solution', identical_options='Duplicate options', diagram='Figure missing', solution_missing='Solution missing', answer_form='Unit not stated',
           wrong_chapter='Wrong chapter', syllabus='Possibly out of syllabus', notation='Lost symbol', markup_leak='Raw markup visible', spelling='Spelling', noise='Stray text', exam_reference='Exam tag in text')
items = collections.OrderedDict()
def item(qid, key, **kw):
    k = (qid, key)
    if k not in items: items[k] = dict(id=f'{qid[-6:]}-{len(items)}', qid=qid, reports=[], **kw)
    return items[k]
for r in res:
    key = json.dumps([r['verdict'], r['repair'], r.get('edits') or ([r['edit']] if r['edit'] else [])], sort_keys=True)
    it = item(r['questionId'], key, verdict=r['verdict'], repair=r['repair'], route=r['route'], edits=r.get('edits') or ([r['edit']] if r['edit'] else []),
              confidence=r['confidence'], evidence=r['evidence'], guards=r['guards'], suggestion=r.get('suggestion'), flags=r.get('flags', []), sweep=False)
    rp = REP[r['reportId']]; it['reports'].append(dict(id=r['reportId'], comment=rp['comment'], source=rp['source'], at=rp['reportedAt'], reply=r['student_reply']))
for s in sw:
    item(s['questionId'], 'sweep' + s['id'], verdict='defect', repair=s['repair'], route=s['route'], edits=s['edits'], confidence=s['confidence'],
         evidence=s['evidence'], guards=s['guards'], suggestion=s.get('suggestion'), flags=[], sweep=True)
qcount = collections.Counter(len(i['reports']) for i in items.values())
for it in items.values():
    n = len(it['reports']); sev = SEV.get(it['repair'], 0) if it['verdict'] == 'defect' else 0
    need = it['route'] == 'faculty_review'
    it['score'] = round(sev * (1 + .6 * (n - 1)) + (20 if need else 0) + (0 if it['sweep'] else 1), 1)
    it['why'] = (WHY.get(it['repair'], it['verdict']) if it['verdict'] == 'defect' else it['verdict'].replace('_', ' ')) + (f" · {n} students" if n > 1 else (' · found by sweep, nobody reported' if it['sweep'] else ''))
qs = {}
for it in items.values():
    q = Q[it['qid']]; b = body(q)
    qs[it['qid']] = dict(id=q['_id'], type=q['questionType'], subject=q['subject'], chapter=q['chapter'], concept=q['concept'], level=q['level'],
                         question=b['question'], solution=b.get('solution'), answer=b.get('answer'), history=q['errorHistory'])
out = dict(items=sorted(items.values(), key=lambda i: -i['score']), questions=qs)
open('console/data.js', 'w').write('window.DATA=' + json.dumps(out, ensure_ascii=False) + ';')
print(len(out['items']), 'items', len(qs), 'questions')

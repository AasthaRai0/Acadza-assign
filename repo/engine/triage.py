"""Live pipeline. Usage: ANTHROPIC_API_KEY=... python -m engine.triage   (then: python -m engine.run && python -m engine.build_console)
Per question: (1) group reports  (2) blind solver call on the stem only  (3) one triage call per question with all its reports
(4) engine.run applies guards and assigns the route. ~2 calls/question, 40 questions -> ~80 calls.
NOTE: this leg is written but was NOT executed in the authoring session (no API key there); decisions.json in the repo was produced offline."""
import json, os, collections
from .mathtext import to_text, body
from . import prompts
MODEL = os.environ.get('MODEL', 'claude-sonnet-5-5')
def call(client, system, user, max_tokens=3000):
    for _ in range(2):
        r = client.messages.create(model=MODEL, max_tokens=max_tokens, temperature=0, system=system, messages=[{'role': 'user', 'content': user}])
        t = ''.join(b.text for b in r.content if b.type == 'text').strip().removeprefix('```json').removesuffix('```').strip()
        try: return json.loads(t)
        except Exception: user += '\n\nYour last reply was not valid JSON. Reply with JSON only.'
    raise ValueError('bad json')
def main():
    import anthropic; client = anthropic.Anthropic()
    tax = json.load(open('data/taxonomy.json')); Q = {q['_id']: q for q in json.load(open('data/questions.json'))}
    by = collections.defaultdict(list)
    for r in json.load(open('data/reports.json')): by[r['questionId']].append(r)
    out = []
    for qid, reps in by.items():
        q = Q[qid]; b = body(q)
        solver = call(client, prompts.SOLVER_SYSTEM, to_text(b['question']), 800)
        user = prompts.TRIAGE_USER.format(qid=qid, qtype=q['questionType'], subject=q['subject'], chapter=q['chapter'], history=q['errorHistory'], q_flat=to_text(b['question']), q_raw=b['question'],
            answer=b.get('answer'), s_flat=to_text(b.get('solution')), s_raw=b.get('solution'), solver=json.dumps(solver, ensure_ascii=False),
            reports='\n'.join(prompts.REPORT_TAG.format(id=r['reportId'], source=r['source'], at=r['reportedAt'], comment=r['comment']) for r in reps))
        sysmsg = prompts.TRIAGE_SYSTEM.format(verdicts=json.dumps(tax['verdicts']), repairs=json.dumps({k: dict(fields=v['fields'], auto=v['auto']) for k, v in tax['repairs'].items()}))
        out += call(client, sysmsg, user)['reports']
    json.dump(out, open('engine/decisions.json', 'w'), ensure_ascii=False, indent=1); print(len(out), 'decisions written')
if __name__ == '__main__': main()

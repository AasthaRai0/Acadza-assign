"""Sweep for defects NOBODY reported. Same guard layer as reports. Usage: python -m engine.sweep"""
import json
from .mathtext import body
from . import guards, checks
Q = {q['_id']: q for q in json.load(open('data/questions.json'))}
S = []
def f(qid, repair, conf, evidence, edits=None, **kw): S.append(dict(questionId=qid, repair=repair, confidence=conf, evidence=evidence, edits=edits or [], **kw))
E = lambda fld, a, b: dict(field=fld, find=a, replace=b)
f('61ee6c9d90a1a968a168686b','spelling',.97,"Solution typos: 'prominant' → 'prominent', 'Maceus' → 'Mucous'.",[E('solution','prominant','prominent'),E('solution','Maceus membrane','Mucous membrane')])
f('620e23cecc50543bc7db9186','spelling',.95,"Solution typo: 'wheater' → 'whether'.",[E('solution','wheater','whether')])
f('617fa18efd53ff1629ed890f','spelling',.95,"Missing space in stem: 'part ofleaf' (span boundary swallowed it).",[E('question','part of<span style="color:#000000">leaf','part of <span style="color:#000000">leaf')])
f('6956d7bb23cb221e570d6013','noise',.96,"Solution starts with stray 'Solution:' and '(b)' labels copied from a source book.",[E('solution','Solution:<br/>(b) ','')])
f('6062ec84518e9535e120c422','notation',.93,"Solution units garbled: '/AC' and '/CC' should be '/°C' (degree sign lost). Final answer unaffected.",
  [E('solution','<mrow><mi mathvariant="normal">A</mi><mi mathvariant="normal">C</mi></mrow>','<mrow><mo>&#x000B0;</mo><mi mathvariant="normal">C</mi></mrow>'),
   E('solution','<mrow><mi mathvariant="normal">C</mi><mi mathvariant="normal">C</mi></mrow>','<mrow><mo>&#x000B0;</mo><mi mathvariant="normal">C</mi></mrow>')])
f('622f08d7b70e4b50e4500a1b','markup_leak',.95,"Solution shows two stray '&' (LaTeX align markers) around v_CM = …",[E('solution','</msub><mi>&</mi>','</msub>'),E('solution','<mspace linebreak="newline" /><mi>&</mi>','<mspace linebreak="newline" />')])
f('6956d79788d7701e5617bc29','markup_leak',.95,"Solution shows two stray '&' (LaTeX align markers) before P and ϕ.",[E('solution','<mi>&amp;</mi><mi>P</mi>','<mi>P</mi>'),E('solution','<mspace linebreak="newline"></mspace><mi>&amp;</mi>','<mspace linebreak="newline"></mspace>')])
f('68dea657387eea3d0d95f54a','notation',.8,"Solution subscripts garbled: 'P_eqcu' and 'P_eqch' (should read P_eq = 2P and P = 5 D). Meaning inferred, so faculty confirm.",
  [E('solution','<msub><mi> P </mi><mrow><mtext> eqcu </mtext></mrow></msub>','<mi> P </mi>'),E('solution','<msub><mi> P </mi><mrow><mtext> eqch </mtext></mrow></msub>','<mi> P </mi>')])
f('66fe9dbe22132e5a70a3e579','solution_fix',.8,"Solution says insulin and glucagon work 'synergistically'. They are antagonistic (the textbook pair). It also contradicts the question's own logic: if they were synergistic, option B would also be 'not antagonistic' and the SCQ would have two answers. Key D unaffected.",[E('solution','Insulin and glucagon work synergistically','Insulin and glucagon work antagonistically')])
f('68c8153cfb6b2f16e2d3ceaf','solution_missing',.8,"Solution is a stub ('conceptual Based of field force'). Proposed: a real per-option explanation ending in the key A, B, D (authored text, faculty confirm).",
  [E('solution','@@WHOLE_SOLUTION@@','<h3>(A) v ∥ E: force qE is along v, so motion stays on a straight line ✓<br/>(B) v ⊥ E: constant acceleration ⊥ u gives a parabola ✓<br/>(C) v ∥ B: F = q(v×B) = 0, so a straight line, not a helix ✗<br/>(D) v ⊥ B: F = qvB is centripetal, so a circle in the plane normal to B ✓<br/>Correct: A, B, D</h3>')],must_contain='A, B, D')
f('6956d7e988d7701e5617bd3e','notation',.7,"Solution has lost symbols: 'v − dx/dt − Aω cos ωt' should read 'v = dx/dt = Aω cos ωt'; 'cos(π/8) × 2' should be 'cos(2·π/8)'; options carry the unit inside the radical, 2√(2 m). Answer D is right. Needs a human to re-key the MathML.")
out = []
for i, x in enumerate(S, 1):
    q = Q[x['questionId']]; d = dict(x, verdict='defect', edits=[dict(e) for e in x['edits']])
    route, log, _ = guards.check(q, d, checks.run())
    for e in x['edits']:
        if e['find'] == '@@WHOLE_SOLUTION@@': e['find'] = body(q)['solution']
    out.append(dict(id=f'S{i:02d}', verdict='defect', route=route, guards=log, **x))
json.dump(out, open('sweep.json', 'w'), ensure_ascii=False, indent=1)
print(len(out), [(o['id'], o['route']) for o in out])

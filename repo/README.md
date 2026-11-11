# Acadza Report → Fix

Turns student "Report error" tickets into safe, auditable fixes, plus a faculty review console.

```
data/                 brief data (questions, reports, taxonomy)
engine/
  mathtext.py         production HTML + MathML -> readable text
  checks.py           independent numeric re-solves (sympy): the "blind solver" leg for numeric questions
  make_decisions.py   model-stage output for 44 reports (verdict/repair/edit/evidence/reply)
  guards.py           deterministic safety layer; assigns route. The model never does.
  run.py              decisions -> guards -> results.json
  sweep.py            defects nobody reported -> sweep.json
  build_console.py    results + sweep + questions -> console/data.js
  prompts.py, triage.py   live LLM pipeline (blind solver + grouped triage); NOT executed in authoring session
results.json          44 rows in the brief's schema (+ guards log, edits[], flags)
sweep.json            11 unreported defects
console/              static faculty console (index.html + data.js), no backend
PROMPTS.md  PRODUCT.md
```

## Run
```
pip install beautifulsoup4 lxml sympy
python -m engine.run && python -m engine.sweep && python -m engine.build_console
open console/index.html          # or: python -m http.server -d console
```
Live regeneration (optional): `pip install anthropic; ANTHROPIC_API_KEY=... python -m engine.triage`, then the three commands above.

## Deploy the console
Static folder `console/`. Netlify: drag-drop the folder. Vercel: `vercel --prod console`. GitHub Pages: publish `/console`.
**The console loads precomputed results** (no LLM call at view time). Decisions are saved in the browser (`localStorage`).

## Results at a glance (44 reports)
auto_apply 19 · faculty_review 8 · no_change 17. Verdicts: defect 27, no_error 10, display_issue 2, not_actionable 2, already_fixed 1, app_issue 1, language_mode 1.

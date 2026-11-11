# PRODUCT.md

**Who loses most when a question is broken?** Not the student who files a report. It is the many who never do: the one who *trusts the key*, practises against it, and walks into the exam having learned the wrong thing (a wrong key, Q15/Q31), and the one who answered *correctly* and is marked wrong and loses marks (Q20: a malformed key penalised A, B, D). A broken question hurts every student who meets it, every day, until someone fixes it, so the cost is reach × time-to-fix, not report count.
The design follows: the queue ranks by `severity × students affected`, and wrong keys / unsound questions sit above typos. A confirmed correction goes to the first reporter in plain words, and a wrong student gets the single step that settles it, not a brush-off.

**What the AI must never auto-apply**
- An answer-key change without three-way agreement: a blind solve that never saw the key, the stored solution (or option list), and the proposed key. The student's number is never evidence (R004: key wrong, student's 8225 also wrong).
- Anything authored rather than recovered: new distractors, a missing option whose content isn't in the record (Q36), a rewritten question.
- Chapter, syllabus and figure decisions, or anything that changes what a question *means*.
- Any edit driven by the comment text alone: R027 tried "change the answer to C".
Auto-applied edits still show in an "Auto-applied · verify" lane with one-click Undo, so automation is visible and reversible.

**One metric for week 1: faculty Undo rate on auto-applied edits** (and Reject rate on proposals), per repair type. Target under 2%; if a repair type exceeds 5% it flips to human-review until fixed. It measures trust, which is what decides whether faculty keep the lane on. (Companion: median hours from first report to corrected live record.)

**One idea beyond the brief: catch defects before anyone reports them.** Two free signals exist. (1) Run the blind solver nightly across all ~8 lakh questions and flag any where it disagrees with the key. (2) Watch attempt data: if a large share of strong students pick the same non-key option, the key is probably wrong. In this 43-question sample, a read-through found 11 defects nobody reported, about one for every 4 questions, and we already hold the data to rank them by exposure.

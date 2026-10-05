# narrative.json

This file holds the feature-specific prose that you (the main Claude) write in step 6. Numbers do **not** go here. `render.py` inserts the counts from `data.json`.

In text fields you can use inline `**bold**` and `` `code` ``. Write in Vietnamese, for the QC reader: short, direct sentences.

```json
{
  "title": "Registration Test Map",
  "feature": "Đăng ký tài khoản Biz Client",
  "date": "27/09/2026",
  "lede": "One sentence: what this page is.",
  "sources": ["FRD BookStack #7159 · v1.16 · 25/08/2026", "BA registration.md (dựa trên FRD v1.12)", "Redmine #75125 · #75447"],
  "verdict": ["Paragraph 1: can QC test from the dev docs as-is, and why.", "Paragraph 2: consequence.", "Paragraph 3: what to do first."],
  "timeline": [{"date": "24/08", "text": "…", "warn": true}],
  "timeline_note": "Who is at fault / what kind of question this is.",
  "divergences": [{"topic": "…", "frd": "…", "current": "…", "impact": "…"}],
  "po_questions": [{"q": "…", "detail": "…"}],
  "env_notes": [{"level": "high|med|low", "title": "…", "evidence": "…", "action": "…"}],
  "extras": [{"title": "Trái FRD (34)", "items": ["…"]}],
  "footer": "What was read-only, what was judged by agents, what was not checked.",
  "excel_notes": [{"title": "Lấy OTP khi test", "text": "Project-specific things a tester must know before running cases: mocked senders, rate limits, real DB engine, missing seed scripts…"}]
}
```

Rules:
- `divergences`: keep only the items that change a test outcome, at most 15. "current" means BA · Redmine · code where they agree. Say so when they don't.
- `po_questions`: put first the one question whose answer decides most of the others. At most 12.
- `env_notes`: cover whatever blocks or skews a test run, such as a mocked sender, rate limits, stale prerequisite sections or config defaults.
- When the timeline is known, show which FRD version each dev artefact follows.
- `excel_notes`: 0–6 items. They are printed in the Excel sheet *Ghi chú*, section 8, by skill `qc-trace-excel`. Keep each to 1–2 sentences.

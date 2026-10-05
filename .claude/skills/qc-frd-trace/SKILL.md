---
name: qc-frd-trace
description: Build a QC traceability report for one feature. It maps the PO/BA FRD on BookStack (the source of truth), line by line, to the dev-generated BA/TA/QC docs, the Redmine issues and the code. Output is report.md, matrix.md, CSVs and a published Artifact link. Use when a QC asks to check whether dev docs, test cases or code cover an FRD, to find gaps or extras against the FRD, or to get a lean test checklist and questions for PO.
argument-hint: <bookstack-page-url> --redmine <id,id> [--feature <BA .md path>] [--code <dir,dir>] [--out <dir>]
disable-model-invocation: true
metadata:
  author: tuyenvo224
  version: "1.0"
---

# QC FRD Trace

Builds a **traceability matrix, not a summary**. The FRD is split into atomic requirements `R-xxx`. Each one is quoted verbatim, and a script checks every quote against the FRD. Each requirement is then traced to BA → QC cases → Redmine → code. Anything the dev docs have that the FRD does not ends up in a separate table. That gives the QC both answers: what is missing, and what was added.

**Read-only everywhere.** Never edit the docs repo or the code repos, never write to Redmine or BookStack, never open `.env*`, `variables/*.env` or `.gitlab`, and never print credentials.

Scripts live in `scripts/` next to this file (`SKILL_DIR`). Run them with `python` and set `PYTHONIOENCODING=utf-8`. Agent prompts are in `references/prompts.md`.

## Inputs

Parse `$ARGUMENTS`:

| Arg | Required | Meaning |
|---|---|---|
| BookStack URL | yes | `https://<host>/books/<book-slug>/page/<page-slug>` |
| `--redmine` | yes | Comma-separated issue IDs. The script adds parent issues automatically |
| `--feature` | no | Path to the BA feature `.md`. If omitted, search `business-analytics/products/**/<slug>.md` in the current repo. If 0 or more than 1 file matches, ask the user |
| `--code` | no | Code repo directories, used for implementation status. If omitted, look for sibling repos named in the docs repo `CLAUDE.md` / `.claude/project-context.md`. If none are found, skip the code step and say so in the report |
| `--out` | no | Default `<parent of the docs repo>/qc-reports/<feature-slug>/<YYYY-MM-DD>/`. It sits next to the docs repo that is open (the git root of the current directory), never inside it, so reports are never committed by mistake. Example: docs repo `C:\biz-repo\biz-portal-docs` → `C:\biz-repo\qc-reports\…` |

The TA and QC folders mirror the BA path: `technical-design/products/<p>/<e>/<feature>/` and `quality-control/products/<p>/<e>/<feature>/`. If one of them is missing, continue without it and record that in the report.

Credentials are looked up in this order: environment variables (`BOOKSTACK_URL`, `BOOKSTACK_TOKEN_ID`, `BOOKSTACK_TOKEN_SECRET`, `REDMINE_URL`, `REDMINE_API_KEY`), then `.bookstack` / `.redmine` in the current directory or any parent, then the same files in the home directory. The format is `KEY=VALUE`, as in `.bookstack.example` / `.redmine.example`. If any are missing, **STOP** and tell the user which file to create. Never ask them to paste keys into chat.

## Steps

Work in `OUT` (created by step 1). Report progress in one short line per step.

0. **Record the run.** Write `OUT/run-meta.json` with the resolved inputs: `feature_slug`, `frd_url`, `redmine` (ids), `docs_repo`, `ba`, `ta_dir`, `qc_dir`, `code` (each repo with branch and SHA). After step 7, add `artifact_url` to the same file. Skill `qc-trace-excel` reads this file.
1. **Fetch the FRD.** Run `python SKILL_DIR/scripts/fetch_bookstack.py <url> --out OUT`. This writes `frd.html`, `frd.txt` and `frd-meta.json` (id, name, revision, updated_at). If the FRD links to other BookStack pages, the script lists them. Ask the user whether to include them; the default is to include pages the FRD calls "tài liệu liên quan" only if the user agrees.
2. **Fetch Redmine.** Run `python SKILL_DIR/scripts/fetch_redmine.py <ids> --out OUT`. This writes `rm_<id>.md` with the description and journals for each issue and its parent.
3. **Extract requirements.** Spawn one foreground agent with prompt **P1** from `references/prompts.md`. It writes `frd-reqs.md`, which includes the group catalog `§Danh mục nhóm` and a `Nhóm` key on every row. P1 is the only agent that defines keys; it reads the whole FRD, so repeated statements get one key. Later agents only copy keys.
   Then run `python SKILL_DIR/scripts/verify_quotes.py OUT`. It checks both the quotes and the keys. If anything fails, send the failing IDs back to the same agent to fix, and re-run the check until it passes. Do not continue with unverified quotes or keys.
3b. **Audit coverage (catches omissions; quote verification only catches inventions).**
   - Run `python SKILL_DIR/scripts/check_coverage.py OUT`. It lists leaf FRD sections with 0 rows and flags low requirement density.
   - Spawn a **new** foreground agent with prompt **P1b**. It must not be the P1 agent, because an independent reader finds what the first one skipped. It writes `coverage-gaps.md`.
   - Fix each item and record the result in its `Xử lý` column:
     - **Missed item:** append it to `frd-reqs.md` as the next free id (R-557…), with its `Nhóm`. If the key is new, add it to §Danh mục nhóm too. Never renumber existing ids. Add `bổ sung từ audit` to Ghi chú. Record `Đã bổ sung R-xxx`.
     - **Merged row:** split it. Keep the original id for the first part and give the rest new ids at the end. Record `Đã tách → R-xxx`.
     - **Item rejected after checking the FRD:** record `Không cần — <lý do>`.
     - **Item you cannot resolve:** record `Còn mở`.
   - Re-run `verify_quotes.py` after the edits. Do one audit round only. Items still open go into the report, so the QC knows exactly what to check by hand.
4. **Map, in parallel.** Spawn these agents in one message, in the background:
   - **P2 FRD → BA.** Split into ranges of about 280 R each (for example 2 agents for 556 R). Each writes `map-ba-<n>.csv`. The last range also writes `ba-extra.csv`.
   - **P3 BA → QC.** Writes `qc-cases.csv`, `ba-to-qc.csv`, `qc-extra.csv` and `qc-prereq.md`.
   - **P4 Redmine + code.** Writes `redmine-vs-frd.csv`, `redmine-decisions.md` and `impl-status.csv`. Skip the code part if there is no code.
   - **P5 FRD → TA.** Split into the same R ranges as P2. Each writes `ta-map-<n>.csv`. The last range also writes `ta-notes.csv` (the TA `CF-*` / `A-*` / `RSK-*` / `TD-*` items that touch FRD requirements) and `ui-vs-frd.csv` (checks the `ui-contract.md` screens, elements and message regions against the FRD's UI and Message requirements). Skip P5 if the TA folder is missing, and say so in the report.
   Wait for all of them to finish. Spot-check 3–5 of the `Lệch` / `Thiếu` claims and every "code differs" claim yourself (open the quoted lines) before trusting them. Do the same for P5: check 2–3 TA `Lệch` rows and every `ta-notes` row marked `Trái FRD`.
5. **Merge.** Run `python SKILL_DIR/scripts/build_data.py OUT`. It writes `data.json` and prints the counts. **Every number in the report comes from this script.**
6. **Write the narrative.** Write `OUT/narrative.json` using the schema in `references/narrative-schema.md`: verdict, version timeline, key divergences, questions for PO, environment notes, BA extras. Base it only on the files in OUT and the checks from step 4. Quote IDs rather than restating content.
7. **Render and publish.**
   - Run `python SKILL_DIR/scripts/render.py OUT`. This writes `report.md`, `matrix.md` and `report.html` from the same `data.json` and `narrative.json`.
   - Publish `OUT/report.html` with the Artifact tool, using `icon: "checklist"` and a one-sentence `description`. The template is already designed, so do not redesign it.
   - Reply with the artifact link, the path to `report.md`, the 3–5 headline findings, the coverage-audit result (items added, items still open), and what was not checked.
   - End by telling the user they can run `/qc-trace-excel <OUT>` to get the test-case Excel file.

## Stop conditions

- The FRD page is not found, or matches more than one page, and the user hasn't picked one.
- Credentials are missing.
- The BA feature doc can't be resolved.
- Quote verification still fails after 2 fix rounds.
- The coverage audit reports more than 15% of the requirement count as missed. The extraction is too weak to patch, so re-run P1 with a new agent before continuing.

## Rules for agents (repeat these in every prompt)

- The FRD is the source of truth. Judge by meaning: values, thresholds, conditions, branches, actors, order. A keyword match is not enough.
- Use the allowed status values exactly as written. Evidence is always `file:line`.
- CSVs are UTF-8 and `;`-separated, with the exact headers from the prompt.
- No edits outside OUT and no network calls. The fetch scripts already did the network work.

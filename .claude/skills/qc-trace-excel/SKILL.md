---
name: qc-trace-excel
description: Turn a finished qc-frd-trace report folder into the team's test-case Excel file, built on Template_TCs.xlsx. Sheets are Ghi chú (reading guide), TCs (every case with steps, data, expected result and a "can test?" status), Ma trận FRD (every FRD requirement, linked to its cases), Test flow and Tóm tắt. Use after /qc-frd-trace has finished, when a QC wants the executable test-case workbook for that feature.
argument-hint: <report folder from qc-frd-trace> [--qc-name "Tên QC"] [--template <xlsx>] [--xlsx <output path>]
disable-model-invocation: true
metadata:
  author: tuyenvo224
  version: "1.0"
---

# QC Trace → Excel

Builds `<feature>_TCs.xlsx` inside the report folder. Everything comes from files that `/qc-frd-trace` already produced plus the QC case files in the docs repo, so the skill spawns **no agents** and takes about a minute.

The full list of what the workbook must contain is `references/requirements.md` (rules E*, T*, X*, F*, S*, G*). `scripts/verify_excel.py` checks every automatable rule. **Never hand over a workbook that fails verification.**

Scripts live in `scripts/` next to this file (`SKILL_DIR`). Run them with `python` and set `PYTHONIOENCODING=utf-8`. They need `openpyxl`.

## Inputs

| Arg | Meaning |
|---|---|
| report folder (`OUT`) | Output folder of `/qc-frd-trace`: `<parent of the docs repo>/qc-reports/<feature>/<date>/`, where the docs repo is the git root of the current directory. If omitted, use the newest folder under that `qc-reports` that has a `data.json`, and tell the user which one you picked |
| `--qc-name` | Name printed in the template's *QC thực hiện* cell. Default: keep the template value |
| `--template` | Default `assets/Template_TCs.xlsx` inside this skill, so the skill works wherever it is copied. Pass another file only for a different team template. Opened read-only, never modified |
| `--xlsx` | Output path. Default `OUT\<feature-slug>_TCs.xlsx` |

`OUT` must contain `data.json`, `narrative.json`, `frd-reqs.md`, `qc-cases.csv` and `run-meta.json`; `run-meta.json` gives `qc_dir` and `ta_dir`. If `run-meta.json` is missing (a report built before this field existed), ask the user for the QC folder and pass it with `--qc-dir`, plus `--ta-dir` when there is one. If any other file is missing, **STOP**: the report is incomplete, so re-run `/qc-frd-trace`.

## Steps

1. **Pre-check.**
   - Confirm the input files exist.
   - Run `python SKILL_DIR/../qc-frd-trace/scripts/verify_quotes.py OUT`. It must pass, because the workbook groups cases by the *Nhóm chức năng* it validates.
   - If it fails on missing Vietnamese group names (a report built before names were added), add a `Nhóm chức năng` column to the `| Chủ đề | … |` table in `frd-reqs.md` with short Vietnamese names, re-run `build_data.py OUT`, and tell the user.
2. **Export.** Run `python SKILL_DIR/scripts/export_excel.py OUT [--qc-name …] [--template …] [--xlsx …]`.
   - If it stops with "open in Excel", ask the user to close the file and run it again. It already saved `*_backup.xlsx` before overwriting.
3. **Verify.** Run `python SKILL_DIR/scripts/verify_excel.py <xlsx> OUT`. Every line must be `PASS`.
   - On a `FAIL`, fix the cause in the script or the input data, then export and verify again.
   - Do not edit the workbook by hand.
4. **Spot-check (M).** Open 3 cases in the workbook and compare them with their source (column M `file:dòng`):
   - one `TC`;
   - one `E2E` that has continuation rows;
   - one case with status ⏸ or ⛔.

   Steps, data and expected result must match the source, and the status reason in column I must make sense.
5. **Reply** with:
   - the workbook path;
   - the counts per column-K status;
   - the number of FRD requirements with no case;
   - the verification result (`n/n PASS`);
   - a reminder that re-exporting overwrites the file, so test results already entered need to be copied out first.

## Rules

- Read-only on the docs repo, the code repos, BookStack and Redmine.
- All numbers in the workbook come from the scripts. Never type a count by hand.
- Use one term everywhere: **yêu cầu FRD (R-xxx)**, never "dòng FRD".
- Project-specific tester notes (mocked SMS, rate limits, DB engine…) go in `OUT/narrative.json` → `excel_notes`, not into the scripts.
- To change what the workbook contains, update `references/requirements.md` first, then the scripts and `verify_excel.py`, in that order.

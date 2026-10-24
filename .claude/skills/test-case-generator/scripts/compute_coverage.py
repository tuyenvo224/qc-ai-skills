"""
Compute the quantitative Done-Criteria verdict (see ../references/done-criteria.md, Section 9.7)
from structured test-case data — replaces manual/self-reported coverage counting.

This exists because an agent counting "P1 coverage = 100%" by eyeballing its own output is
unreliable (self-verification bias). This script recomputes every threshold in 9.7 directly
from an explicit Requirement/Risk <-> Test-Case traceability mapping, and prints a
Traceability Matrix so the numbers are auditable, not just asserted.

Usage:
    python compute_coverage.py <input.json> [--matrix-out traceability.md] [--report-out coverage-report.md]

Exit code: 0 on PASS or CONDITIONAL PASS, 1 on FAIL — usable as a gate before Step 8 (Excel export).

Input JSON schema (superset of generate_testcase_excel.py's schema — the same file can feed both):
{
  "project_name": "GiftPort", "feature_name": "Category Management",
  "features": [{"name": "Login", "priority": "P1"}, ...],          # optional, enables per-feature technique check
  "requirements": [{"id": "REQ-001", "priority": "P1"}, ...],       # optional, enables requirement coverage
  "risks": [{"id": "R-001", "priority": "P1", "category": "security"}, ...],  # optional; category one of
                                                                     # security/financial/data_integrity/bug_hypothesis -> 100% mandatory
  "test_cases": [
    {
      "id": "TC-001", "feature": "Login", "technique": "EP", "priority": "P1",
      "objective": "[EP] ...", "requirement": "REQ-001, REQ-002", "risk": "R-001"
    }
  ],
  "assumptions": [...]     # optional, same as generate_testcase_excel.py
}
"""

import argparse
import json
import re
import sys
from pathlib import Path

PRIORITIES = ["P1", "P2", "P3", "P4"]
REQ_THRESHOLDS = {"P1": 100, "P2": 95, "P3": 80, "P4": 60}
REQ_CONDITIONAL_FLOOR = {"P2": 90, "P3": 70}
RISK_THRESHOLDS = {"P1": 100, "P2": 90, "P3": 70}
RISK_CONDITIONAL_FLOOR = {"P2": 80, "P3": 50}
MANDATORY_100_RISK_CATEGORIES = {"security", "financial", "data_integrity", "bug_hypothesis"}
TECHNIQUE_MIN = {"P1": 6, "P2": 4, "P3": 3, "P4": 1}
ALL_TECHNIQUES = {"EP", "BVA", "DT", "ST", "UC", "PW", "EG", "CL", "EXP"}
ASSUMPTIONS_MAX_PCT = 10.0


def split_ids(raw):
    if not raw:
        return []
    parts = re.split(r"[,\n]", raw)
    return [p.strip() for p in parts if p.strip()]


def pct(covered, total):
    return 100.0 if total == 0 else round(100.0 * covered / total, 1)


def verdict_for(pct_value, threshold, conditional_floor=None):
    if pct_value >= threshold:
        return "PASS"
    if conditional_floor is not None and pct_value >= conditional_floor:
        return "CONDITIONAL"
    return "FAIL"


def build_traceability(items, test_cases, id_field):
    """items: list of {id, priority, ...}. Returns list of (item, [tc_ids covering it])."""
    rows = []
    for item in items:
        covering = [
            tc.get("id", "") for tc in test_cases
            if item["id"] in split_ids(tc.get(id_field, ""))
        ]
        rows.append((item, covering))
    return rows


def coverage_by_priority(rows):
    """rows: list of (item, covering_tc_ids). Returns {priority: (covered_count, total_count)}."""
    result = {p: [0, 0] for p in PRIORITIES}
    for item, covering in rows:
        p = item.get("priority")
        if p not in result:
            continue
        result[p][1] += 1
        if covering:
            result[p][0] += 1
    return result


def render_matrix_md(title, rows, id_field_label):
    lines = [f"## {title}", "", f"| {id_field_label} | Priority | Covered By | Status |", "|---|---|---|---|"]
    for item, covering in rows:
        status = "OK" if covering else "MISSING"
        lines.append(f"| {item['id']} | {item.get('priority', '')} | {', '.join(covering) or '-'} | {status} |")
    lines.append("")
    return "\n".join(lines)


def compute_technique_thresholds(features, test_cases):
    results = []
    for feature in features:
        name = feature["name"]
        priority = feature.get("priority", "P3")
        techniques = {
            (tc.get("technique") or "").upper()
            for tc in test_cases
            if tc.get("feature") == name and tc.get("technique")
        }
        techniques &= ALL_TECHNIQUES
        min_required = TECHNIQUE_MIN.get(priority, 1)
        status = "PASS" if len(techniques) >= min_required else "FAIL"
        results.append(dict(name=name, priority=priority, count=len(techniques),
                             min_required=min_required, techniques=sorted(techniques), status=status))
    return results


def compute_quality_metrics(test_cases):
    total = len(test_cases)
    missing_tag = sum(1 for tc in test_cases if not tc.get("technique"))
    missing_priority = sum(1 for tc in test_cases if not tc.get("priority"))
    seen = {}
    duplicates = 0
    for tc in test_cases:
        key = ((tc.get("technique") or "").upper(), (tc.get("objective") or "").strip().lower())
        seen[key] = seen.get(key, 0) + 1
    duplicates = sum(count - 1 for count in seen.values() if count > 1)
    return dict(total=total, missing_tag=missing_tag, missing_priority=missing_priority, duplicates=duplicates)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input_json")
    parser.add_argument("--matrix-out", help="Write full traceability matrix to this .md file")
    parser.add_argument("--report-out", help="Write the coverage report to this .md file (default: print to stdout only)")
    args = parser.parse_args()

    data = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    test_cases = data.get("test_cases", [])
    if not test_cases:
        print("Error: input JSON must contain a non-empty 'test_cases' array", file=sys.stderr)
        sys.exit(1)

    features = data.get("features", [])
    requirements = data.get("requirements", [])
    risks = data.get("risks", [])
    assumptions = data.get("assumptions", [])

    reasons_fail = []
    reasons_conditional = []
    report_lines = ["## Coverage Analysis Report", ""]
    matrix_parts = []

    # --- Requirements coverage ---
    if requirements:
        req_rows = build_traceability(requirements, test_cases, "requirement")
        matrix_parts.append(render_matrix_md("Requirement Traceability Matrix", req_rows, "Requirement ID"))
        req_cov = coverage_by_priority(req_rows)
        report_lines.append("### Requirements Coverage:")
        for p in PRIORITIES:
            covered, total = req_cov[p]
            if total == 0:
                continue
            p_pct = pct(covered, total)
            v = verdict_for(p_pct, REQ_THRESHOLDS[p], REQ_CONDITIONAL_FLOOR.get(p))
            report_lines.append(f"- {p}: {covered}/{total} ({p_pct}%) -> {v}")
            if v == "FAIL":
                missing = [item["id"] for item, cov in req_rows if item["priority"] == p and not cov]
                reasons_fail.append(f"{p} requirements coverage {p_pct}% < {REQ_THRESHOLDS[p]}% (missing: {', '.join(missing)})")
            elif v == "CONDITIONAL":
                reasons_conditional.append(f"{p} requirements coverage {p_pct}% (below {REQ_THRESHOLDS[p]}%, above conditional floor)")
        report_lines.append("")
    else:
        report_lines.append("### Requirements Coverage: (no 'requirements' provided in input — skipped)\n")

    # --- Risk coverage ---
    if risks:
        risk_rows = build_traceability(risks, test_cases, "risk")
        matrix_parts.append(render_matrix_md("Risk Traceability Matrix", risk_rows, "Risk ID"))
        risk_cov = coverage_by_priority(risk_rows)
        report_lines.append("### Risk Coverage:")
        for p in PRIORITIES[:3]:
            covered, total = risk_cov[p]
            if total == 0:
                continue
            p_pct = pct(covered, total)
            v = verdict_for(p_pct, RISK_THRESHOLDS.get(p, 70), RISK_CONDITIONAL_FLOOR.get(p))
            report_lines.append(f"- {p} Risks: {covered}/{total} ({p_pct}%) -> {v}")
            if p == "P1" and v != "PASS":
                missing = [item["id"] for item, cov in risk_rows if item["priority"] == p and not cov]
                reasons_fail.append(f"P1 risk coverage {p_pct}% < 100% (missing: {', '.join(missing)})")
            elif v == "CONDITIONAL":
                reasons_conditional.append(f"{p} risk coverage {p_pct}%")

        for category in sorted(MANDATORY_100_RISK_CATEGORIES):
            cat_risks = [r for r in risks if r.get("category") == category]
            if not cat_risks:
                continue
            cat_rows = [row for row in risk_rows if row[0].get("category") == category]
            covered = sum(1 for _, cov in cat_rows if cov)
            p_pct = pct(covered, len(cat_rows))
            status = "PASS" if p_pct == 100.0 else "FAIL"
            report_lines.append(f"- {category.replace('_', ' ').title()} Risks: {covered}/{len(cat_rows)} ({p_pct}%) -> {status} (mandatory 100%)")
            if status == "FAIL":
                reasons_fail.append(f"{category} risk coverage {p_pct}% < 100% (mandatory, no exception)")
        report_lines.append("")
    else:
        report_lines.append("### Risk Coverage: (no 'risks' provided in input — skipped)\n")

    # --- Technique application per feature ---
    if features:
        tech_results = compute_technique_thresholds(features, test_cases)
        report_lines.append("### Technique Application:")
        for r in tech_results:
            report_lines.append(
                f"- {r['name']} ({r['priority']}): {r['count']} techniques {sorted(r['techniques'])} -> "
                f"{r['status']} (need >= {r['min_required']})"
            )
            if r["status"] == "FAIL":
                (reasons_fail if r["priority"] in ("P1", "P2") else reasons_conditional).append(
                    f"Feature '{r['name']}' ({r['priority']}) has {r['count']} techniques < {r['min_required']} required"
                )
        report_lines.append("")
    else:
        report_lines.append("### Technique Application: (no 'features' provided in input — skipped)\n")

    # --- Quality metrics ---
    q = compute_quality_metrics(test_cases)
    tag_pct = pct(q["total"] - q["missing_tag"], q["total"])
    prio_pct = pct(q["total"] - q["missing_priority"], q["total"])
    assumptions_pct = round(100.0 * len(assumptions) / q["total"], 1) if q["total"] else 0.0

    report_lines.append("### Quality Metrics:")
    report_lines.append(f"- Technique tags present: {q['total'] - q['missing_tag']}/{q['total']} ({tag_pct}%)")
    report_lines.append(f"- Priorities present: {q['total'] - q['missing_priority']}/{q['total']} ({prio_pct}%)")
    report_lines.append(f"- Duplicate test cases (same technique + objective): {q['duplicates']}")
    report_lines.append(f"- Assumptions: {len(assumptions)}/{q['total']} ({assumptions_pct}%)")
    report_lines.append("")

    if q["missing_tag"] > 0:
        reasons_fail.append(f"{q['missing_tag']} test case(s) missing [Technique Tag]")
    if q["missing_priority"] > 0:
        reasons_fail.append(f"{q['missing_priority']} test case(s) missing Priority")
    if q["duplicates"] > 0:
        reasons_conditional.append(f"{q['duplicates']} duplicate test case(s) detected (same technique + objective text)")
    if assumptions_pct > ASSUMPTIONS_MAX_PCT:
        reasons_fail.append(f"Assumptions {assumptions_pct}% > {ASSUMPTIONS_MAX_PCT}% threshold")

    # --- Overall verdict ---
    if reasons_fail:
        overall = "FAIL"
    elif reasons_conditional:
        overall = "CONDITIONAL PASS"
    else:
        overall = "PASS"

    report_lines.append(f"### Overall Verdict: {overall}")
    if reasons_fail:
        report_lines.append("\nBlocking failures:")
        for r in reasons_fail:
            report_lines.append(f"- {r}")
    if reasons_conditional:
        report_lines.append("\nConditional items (need documented justification / approval):")
        for r in reasons_conditional:
            report_lines.append(f"- {r}")
    if overall == "PASS":
        report_lines.append("\nAll quantitative thresholds met.")

    report_md = "\n".join(report_lines)
    print(report_md)

    if args.report_out:
        Path(args.report_out).write_text(report_md, encoding="utf-8")
        print(f"\n(report written to {args.report_out})", file=sys.stderr)

    if args.matrix_out and matrix_parts:
        Path(args.matrix_out).write_text("\n\n".join(matrix_parts), encoding="utf-8")
        print(f"(traceability matrix written to {args.matrix_out})", file=sys.stderr)

    sys.exit(0 if overall in ("PASS", "CONDITIONAL PASS") else 1)


if __name__ == "__main__":
    main()

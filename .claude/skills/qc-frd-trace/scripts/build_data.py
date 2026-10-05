"""Merge agent outputs in OUT into data.json (all report numbers come from here).

Inputs in OUT: frd-reqs.md, frd-meta.json, map-ba-*.csv, ba-to-qc.csv, qc-cases.csv,
optional: impl-status.csv, ba-extra.csv, qc-extra.csv, redmine-vs-frd.csv, rm-meta.json, coverage-gaps.md,
          ta-map-*.csv, ta-notes.csv, ui-vs-frd.csv
Usage: python build_data.py <OUT> [--ba-id-regex "(?:BR|VR|AC|UC|AF)-\\d+"]
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import col, expand_r, parse_frd_reqs, parse_topics, read_csv, split_md_row  # noqa: E402

ORDER = ["Lệch", "Thiếu", "Một phần", "Đủ", "N/A"]
IMPL_LANE = {"Có": 1, "Một phần": 2, "Khác FRD": 3, "Chưa có": 4}
BA_LANE = {"Đủ": 1, "Một phần": 2, "Lệch": 3, "Thiếu": 4, "N/A": 1}


def parse_coverage(path):
    """Read coverage-gaps.md (P1b output, Xử lý filled by the main thread)."""
    res = dict(stats=dict(ran=False), open=[])
    if not path.exists():
        return res
    section, missed, merged, empty_bad = None, [], [], 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        if not line.startswith("|") or re.match(r"^\|\s*[-:]+", line):
            continue
        cells = split_md_row(line)
        if not cells or cells[0] in ("#", "R", "Mục"):
            continue
        if section and section.startswith("ý bị sót"):
            missed.append(cells)
        elif section and section.startswith("dòng gộp"):
            merged.append(cells)
        elif section and section.startswith("mục frd 0"):
            if len(cells) > 1 and cells[1].lower().startswith("không"):
                empty_bad += 1
    fix = [(c[-1] if c else "").lower() for c in missed]
    stats = dict(ran=True, missed=len(missed), added=sum(f.startswith("đã bổ sung") for f in fix),
                 rejected=sum(f.startswith("không cần") for f in fix),
                 open=sum(f.startswith("còn mở") or not f for f in fix), merged=len(merged),
                 empty_sections_not_ok=empty_bad)
    res["open"] = [dict(sec=c[1] if len(c) > 1 else "", q=c[2] if len(c) > 2 else "")
                   for c, f in zip(missed, fix) if f.startswith("còn mở") or not f]
    res["stats"] = stats
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--ba-id-regex", default=r"(?:BR|VR|AC|UC|AF)-\d+")
    a = ap.parse_args()
    out = Path(a.out)
    idre = re.compile(a.ba_id_regex)

    reqs, oq = parse_frd_reqs(out / "frd-reqs.md")
    meta = json.loads((out / "frd-meta.json").read_text(encoding="utf-8")) if (out / "frd-meta.json").exists() else {}

    ba = {}
    for f in sorted(out.glob("map-ba-*.csv")):
        for x in read_csv(f):
            r = col(x, "R")
            if r:
                ba[r] = x
    missing_map = [r for r in reqs if r not in ba]

    ta = {}
    for f in sorted(out.glob("ta-map-*.csv")):
        for x in read_csv(f):
            r = col(x, "R")
            if r:
                ta[r] = x
    has_ta = bool(ta)

    b2q = {col(x, "BA ID"): col(x, "QC cases").replace(",", " ").split() for x in read_csv(out / "ba-to-qc.csv")} \
        if (out / "ba-to-qc.csv").exists() else {}
    qc = {col(x, "ID"): x for x in read_csv(out / "qc-cases.csv")} if (out / "qc-cases.csv").exists() else {}

    def ba_ids(r):
        return idre.findall(col(ba.get(r, {}), "BA IDs")) if r in ba else []

    def cases_for(ids):
        seen = []
        for i in ids:
            for c in b2q.get(i, []):
                if c not in seen:
                    seen.append(c)
        return seen

    def is_rep(c):
        return col(qc.get(c, {}), "Đại diện").upper().startswith("Y")

    rows = []
    for r, v in reqs.items():
        x = ba.get(r, {})
        t = ta.get(r, {})
        ids = ba_ids(r)
        rows.append(dict(r=r, sec=v["sec"], typ=v["typ"], q=v["q"], st=col(x, "Trạng thái"), grp=v.get("grp") or col(x, "Nhóm"),
                         ba=" ".join(ids), diff=col(x, "Chênh lệch"), qc=" ".join(cases_for(ids)[:8]),
                         ta_st=col(t, "Trạng thái"), ta=col(t, "TA IDs"), ta_diff=col(t, "Chênh lệch")))

    topics = parse_topics(out / "frd-reqs.md")
    for row in rows:
        row["topic"] = row["grp"].split(".")[0] if row["grp"] else ""
        row["topic_name"] = topics.get(row["topic"], row["topic"])

    impl_groups, impl_of_r = [], {}
    impl_file = out / "impl-status.csv"
    if impl_file.exists():
        for g in read_csv(impl_file):
            rs = [r for r in expand_r(col(g, "R ids")) if r in reqs]
            impl_groups.append(dict(name=col(g, "Nhóm"), rs=rs, impl=col(g, "Trạng thái"), be=col(g, "BE evidence"),
                                    fe=col(g, "FE evidence"), note=col(g, "Ghi chú"),
                                    lane=IMPL_LANE.get(col(g, "Trạng thái"), 3)))
            for r in rs:
                impl_of_r.setdefault(r, (col(g, "Trạng thái"), col(g, "Nhóm")))

    for row in rows:
        row["impl"] = impl_of_r.get(row["r"], ("", ""))[0]

    groups = []
    if topics:
        # One grouping for the whole report: 'Nhóm chức năng' = topic of the Nhóm catalog.
        for key, name in topics.items():
            rs = [row["r"] for row in rows if row["topic"] == key]
            if not rs:
                continue
            ic = collections.Counter(impl_of_r[r][0] for r in rs if r in impl_of_r)
            known = sum(ic.values())
            if not known:
                sts = [col(ba.get(r, {}), "Trạng thái") for r in rs]
                lane = BA_LANE.get(next((o for o in ORDER if o in sts), "N/A"), 3)
            else:
                # lane by majority: mostly done → Test ngay (mixed → Test + ghi thiếu), mostly differs → Chờ PO,
                # mostly missing → Chưa có
                top = ic.most_common(1)[0][0]
                bad = ic.get("Khác FRD", 0) + ic.get("Chưa có", 0)
                if top == "Có":
                    lane = 1 if bad * 4 < known else 2
                elif top == "Khác FRD":
                    lane = 3
                elif top == "Chưa có":
                    lane = 4
                else:
                    lane = 2
            parts = sorted({impl_of_r[r][1] for r in rs if r in impl_of_r})
            groups.append(dict(name=name, key=key, rs=rs, lane=lane, be="", fe="",
                               impl=" · ".join(f"{k} {v}" for k, v in ic.most_common()) if ic else "",
                               note=("Gồm: " + "; ".join(parts)) if parts else ""))
    elif impl_groups:
        groups = [dict(g) for g in impl_groups]
    else:
        by = collections.OrderedDict()
        for row in rows:
            by.setdefault(row["grp"] or row["r"], []).append(row["r"])
        for name, rs in by.items():
            sts = [col(ba.get(r, {}), "Trạng thái") for r in rs]
            worst = next((o for o in ORDER if o in sts), "N/A")
            groups.append(dict(name=name, rs=rs, impl="", be="", fe="", note="", lane=BA_LANE.get(worst, 3)))
    for g in groups:
        sts = collections.Counter(col(ba.get(r, {}), "Trạng thái") or "?" for r in g["rs"])
        ids = []
        for r in g["rs"]:
            for i in ba_ids(r):
                if i not in ids:
                    ids.append(i)
        cs = cases_for(ids)
        rep = [c for c in cs if is_rep(c) and not c.startswith("TF")] or [c for c in cs if is_rep(c)]
        g.update(ba=dict(sts), rep=rep[:6], more=max(0, len(cs) - len(rep[:6])),
                 ta=dict(collections.Counter(col(ta.get(r, {}), "Trạng thái") or "?" for r in g["rs"])) if has_ta else {})

    ba_all = list(b2q)
    extra = read_csv(out / "ba-extra.csv") if (out / "ba-extra.csv").exists() else []
    rvf = read_csv(out / "redmine-vs-frd.csv") if (out / "redmine-vs-frd.csv").exists() else []
    qce = read_csv(out / "qc-extra.csv") if (out / "qc-extra.csv").exists() else []
    rm = json.loads((out / "rm-meta.json").read_text(encoding="utf-8")) if (out / "rm-meta.json").exists() else []
    cov = parse_coverage(out / "coverage-gaps.md")
    tan = read_csv(out / "ta-notes.csv") if (out / "ta-notes.csv").exists() else []
    ui = read_csv(out / "ui-vs-frd.csv") if (out / "ui-vs-frd.csv").exists() else []

    stats = dict(
        frd_total=len(reqs), oq_total=len(oq),
        oq_by_type=dict(collections.Counter(o[0].split("-")[0] for o in oq)),
        frd_vs_ba=dict(collections.Counter(r["st"] or "?" for r in rows)),
        unmapped=len(missing_map),
        groups=len(groups), lanes=dict(collections.Counter(g["lane"] for g in groups)),
        impl=dict(collections.Counter(g["impl"] for g in impl_groups if g["impl"])),
        impl_r=dict(collections.Counter(v[0] for v in impl_of_r.values())),
        qc_cases=len(qc), qc_by_prefix=dict(collections.Counter(re.sub(r"-.*", "", c) for c in qc)),
        qc_blocked=sum(1 for c in qc.values() if "BLOCK" in col(c, "Trạng thái").upper()),
        qc_withdrawn=sum(1 for c in qc.values() if "withdraw" in col(c, "Trạng thái").lower()),
        qc_rep=sum(1 for c in qc if is_rep(c)),
        ba_ids=len(ba_all), ba_ids_covered=sum(1 for i in ba_all if b2q.get(i)),
        ba_extra=len(extra), ba_extra_by_type=dict(collections.Counter(col(x, "Loại") for x in extra)),
        qc_extra=len(qce),
        redmine_vs_frd=dict(collections.Counter(col(x, "Kết luận") for x in rvf)),
        coverage=cov["stats"],
        has_ta=has_ta,
        frd_vs_ta=dict(collections.Counter(r["ta_st"] or "?" for r in rows)) if has_ta else {},
        ta_unmapped=sum(1 for r in reqs if r not in ta) if has_ta else 0,
        ta_notes=dict(collections.Counter(col(x, "Kết luận").split(" (")[0] for x in tan)),
        ui_vs_frd=dict(collections.Counter(col(x, "Trạng thái") for x in ui)),
    )
    data = dict(meta=meta, redmine=rm, stats=stats, rows=rows, groups=groups, impl_groups=impl_groups, oq=oq, cov_open=cov["open"],
                ta_notes=[dict(id=col(x, "ID"), typ=col(x, "Loại"), text=col(x, "Nội dung"), rs=col(x, "R liên quan"),
                               res=col(x, "Kết luận"), impact=col(x, "Ảnh hưởng test")) for x in tan],
                ui=[dict(r=col(x, "R"), el=col(x, "Màn hình"), st=col(x, "Trạng thái"), note=col(x, "Ghi chú")) for x in ui],
                extra=[dict(id=col(x, "BA ID"), line=col(x, "BA dòng"), text=col(x, "Nội dung"), typ=col(x, "Loại"),
                            frd=col(x, "FRD liên quan")) for x in extra],
                rvf=[dict(topic=col(x, "Chủ đề"), rm=col(x, "Redmine"), frd=col(x, "FRD"), res=col(x, "Kết luận"))
                     for x in rvf])
    (out / "data.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=1))
    if missing_map:
        print(f"WARNING: {len(missing_map)} R not mapped to BA: {', '.join(missing_map[:15])}")


if __name__ == "__main__":
    main()

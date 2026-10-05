"""Check every 'Trích nguyên văn' in frd-reqs.md appears verbatim in the FRD,
and every row carries a well-formed Nhóm key that is listed in §Danh mục nhóm.

Usage: python verify_quotes.py <OUT>   (exit 1 and list failures if any)
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import NHOM_RE, parse_frd_reqs, parse_nhom_catalog, parse_topics  # noqa: E402


def norm(s):
    s = html.unescape(s)
    s = s.replace(" ", " ").replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", s).strip().lower()


def main():
    out = Path(sys.argv[1])
    raw = (out / "frd.html").read_text(encoding="utf-8")
    text = re.sub(r"<[^>]+>", " ", raw)
    hay = norm(text)
    hay_nospace = hay.replace(" ", "")
    reqs, oq = parse_frd_reqs(out / "frd-reqs.md")
    bad = []
    for rid, r in reqs.items():
        pieces = [p for p in re.split(r"\s…\s|\s\|\s|…", r["q"]) if len(p.strip()) >= 4]
        for p in pieces:
            n = norm(p).strip(' ."')
            if n and n not in hay and n.replace(" ", "") not in hay_nospace:
                bad.append((rid, p[:120]))
                break
    print(f"requirements: {len(reqs)} · open questions: {len(oq)} · quote failures: {len(bad)}")
    for rid, p in bad:
        print(f"  {rid}: {p}")
    ids = sorted(reqs, key=lambda x: int(x[2:]))
    gaps = [f"R-{i:03d}" for i in range(1, int(ids[-1][2:]) + 1) if f"R-{i:03d}" not in reqs] if ids else []
    if gaps:
        print(f"missing ids in sequence: {', '.join(gaps[:20])}")

    cat = parse_nhom_catalog(out / "frd-reqs.md")
    no_grp = [r for r, v in reqs.items() if not v["grp"]]
    bad_fmt = [f"{r}:{v['grp']}" for r, v in reqs.items() if v["grp"] and not NHOM_RE.match(v["grp"])]
    not_in_cat = sorted({v["grp"] for v in reqs.values() if v["grp"] and cat and v["grp"] not in cat})
    print(f"nhóm catalog: {len(cat)} keys · rows without Nhóm: {len(no_grp)} · bad format: {len(bad_fmt)} · "
          f"keys not in catalog: {len(not_in_cat)}")
    for label, items in (("without Nhóm", no_grp), ("bad format", bad_fmt), ("not in catalog", not_in_cat)):
        if items:
            print(f"  {label}: {', '.join(items[:20])}")
    topics = parse_topics(out / "frd-reqs.md")
    used_topics = sorted({v["grp"].split(".")[0] for v in reqs.values() if v["grp"]})
    no_name = [t for t in used_topics if not topics.get(t)]
    print(f"nhóm chức năng: {len(topics)} · topics used without a Vietnamese name: {len(no_name)}" + (f" ({', '.join(no_name)})" if no_name else ""))
    grp_fail = bool(no_grp or bad_fmt or not_in_cat or not cat or no_name)
    sys.exit(1 if bad or gaps or not reqs or grp_fail else 0)


if __name__ == "__main__":
    main()

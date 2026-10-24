"""Deterministic coverage check: which numbered FRD headings have no R row in frd-reqs.md.

Also flags an unusually low requirement density. Writes coverage-sections.json for the audit agent.
Usage: python check_coverage.py <OUT>
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import parse_frd_reqs  # noqa: E402


def headings(raw):
    out = []
    for lvl, body in re.findall(r"<h([1-6])[^>]*>(.*?)</h\1>", raw, flags=re.S | re.I):
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", body))).strip()
        m = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.*)", text)
        if m:
            out.append(dict(num=m.group(1), title=m.group(2)[:90], level=int(lvl)))
    return out


def main():
    out = Path(sys.argv[1])
    raw = (out / "frd.html").read_text(encoding="utf-8")
    reqs, _ = parse_frd_reqs(out / "frd-reqs.md")
    secs = " ".join(r["sec"] for r in reqs.values())
    hs = headings(raw)
    nums = {h["num"] for h in hs}
    result = []
    for h in hs:
        pat = re.compile(r"(?<![\d.])" + re.escape(h["num"]) + r"(?![\d])")
        own = len([r for r in reqs.values() if pat.search(r["sec"])])
        children = [n for n in nums if n.startswith(h["num"] + ".")]
        result.append(dict(**h, rows=own, has_children=bool(children)))
    empty = [h for h in result if h["rows"] == 0 and not h["has_children"]]

    words = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", raw)))
    density = len(reqs) / max(words, 1) * 1000
    (out / "coverage-sections.json").write_text(json.dumps(dict(sections=result, empty=empty, words=words,
                                                                 reqs=len(reqs), per_1000_words=round(density, 1)),
                                                            ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"numbered headings: {len(hs)} · leaf sections with 0 rows: {len(empty)} · "
          f"{len(reqs)} reqs / {words} words = {density:.1f} per 1000 words")
    for h in empty:
        print(f"  §{h['num']} {h['title']}")
    if not hs:
        print("WARNING: FRD has no numbered headings — audit agent must check sections by reading.")
    if density < 5:
        print("WARNING: low density (<5 reqs per 1000 words) — extraction may be too coarse.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Quét tài liệu TA (markdown, output spec.txt của fetch_spec.py) để lấy danh mục chuẩn và gợi ý mâu thuẫn.

Cách dùng:
    python extract_ta.py <spec.txt> [--json out.json]

In ra:
  1. STAT: số ENT (new/change/reuse), API còn hiệu lực / đã rút, EVT phát sinh / tiêu thụ / đã rút,
     số migration của feature, số CF. Dùng thẳng cho 4 stat ở mục 01.
  2. ID theo tiền tố: định nghĩa (ô đầu bảng "Mã" hoặc heading) / chỉ nhắc / đã rút-bãi bỏ.
  3. Nghi trùng mã: cùng một mã được định nghĩa ở 2 chỗ với nội dung khác (chỉ xét RSK, TD, ENT, EVT, NFR, PERM, INT).
  4. ENT → table (từ bảng entity) và danh mục cột (từ bảng cột sau heading "bảng `x`").
     ⚠ ENT không có bảng cột nào.
  5. Index: ⚠ cột dùng trong index mà không có trong danh mục cột (chỉ xét bảng new).
  6. Migration: ⚠ "+ N index" lệch với số index MỚI liệt kê cho bảng đó.
  7. Khóa cấu hình (chỉ lấy từ bảng có cột "Khóa"/"Key") kèm đánh dấu đã bỏ; mã message số; mermaid.
  8. Gợi ý lỗi biên tập: câu bị cụt, dòng lặp lại phần cuối dòng trước.
Đây là gợi ý để đối chiếu, KHÔNG thay việc đọc toàn bộ tài liệu. Mọi ⚠ phải được tự xác minh trước khi đưa vào mục 14.
"""
import argparse
import json
import posixpath
import re
import sys
from collections import defaultdict, OrderedDict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ID_PAT = r"[A-Z]{1,6}(?:-[A-Z]{1,12})*-\d{1,4}"
ID_RE = re.compile(r"\b(" + ID_PAT + r")\b")
FILE_RE = re.compile(r"^# FILE: (.+)$", re.M)
WITHDRAWN_RE = re.compile(r"~~|\bđã rút\b|\brút\b|bãi bỏ|withdrawn|deprecated", re.I)
DUP_PREFIX = {"RSK", "TD", "ENT", "EVT", "NFR", "PERM", "INT"}
HEADING_DEF_PREFIX = {"SEQ", "STATE", "API", "ENT", "EVT"}


def split_files(text):
    marks = list(FILE_RE.finditer(text))
    if not marks:
        return [("(spec)", "(spec)", text)]
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        full = m.group(1).strip()
        out.append((full.split("/")[-1], full, text[m.end():end]))
    return out


def cells(line):
    s = line.strip().strip("|")
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def md_tables(content):
    """[(line_no, heading, header, rows)] cho mọi bảng markdown."""
    lines = content.splitlines()
    res, heading, i = [], "", 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("#"):
            heading = ln.lstrip("#").strip()
        if ln.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|\s*:?-{2,}", lines[i + 1]):
            header, rows, j = cells(ln), [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(cells(lines[j]))
                j += 1
            res.append((i + 1, heading, header, rows))
            i = j
            continue
        i += 1
    return res


def strip_md(s):
    return re.sub(r"[`*~]", "", s).strip()


def first_token(s):
    """Tên cột: token trong backtick đầu tiên, nếu không có thì từ đầu tiên."""
    m = re.search(r"`([^`]+)`", s)
    return (m.group(1) if m else strip_md(s)).split(" ")[0].strip()


def key(x):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", x)]


def lbl(s):
    s = s.lower()
    if re.search(r"\bnew\b|\(mới\)|bảng mới|\bmới\b", s):
        return "new"
    if re.search(r"\bchange\b|mở rộng|đang có|thêm cột|đổi", s):
        return "change"
    if re.search(r"\breuse\b|chỉ đọc|giữ nguyên", s):
        return "reuse"
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--source", help="source.json của fetch_spec.py, để ghép link BA nguồn")
    ap.add_argument("--json")
    ap.add_argument("--check-html", help="HTML report đã dựng: kiểm mọi ENT có ở mục 3 + mục 4, đếm dòng, SQL chỉ SELECT")
    a = ap.parse_args()
    text = open(a.spec, encoding="utf-8").read()
    files = split_files(text)
    src = json.load(open(a.source, encoding="utf-8")) if a.source else {}

    ba = OrderedDict()  # bản QA không đọc BA nguồn

    # thu thập định nghĩa
    referenced = defaultdict(set)
    for m in ID_RE.finditer(text):
        referenced[m.group(1).split("-")[0]].add(m.group(1))
    defined = defaultdict(list)  # id -> [(file, kind, text, withdrawn)]
    withdrawn = set()
    for fname, full, content in files:
        for ln in content.splitlines():
            if ln.startswith("#"):
                for mid in re.findall(r"`?(" + ID_PAT + r")`?", ln.lstrip("#").strip()[:40]):
                    if mid.split("-")[0] in HEADING_DEF_PREFIX:
                        w = "~~" in ln or bool(re.search(r"—\s*\**(đã rút|bãi bỏ|đã bãi bỏ)", ln, re.I))
                        defined[mid].append((fname, "heading", strip_md(ln)[:100], w))
                        if w:
                            withdrawn.add(mid)
                    break
        for _, heading, header, rows in md_tables(content):
            h0 = strip_md(header[0]).lower() if header else ""
            if h0 not in ("mã", "id", "code", "ma"):
                continue
            for r in rows:
                if not r:
                    continue
                first = strip_md(r[0])
                if re.fullmatch(ID_PAT, first):
                    rowtxt = " | ".join(strip_md(c) for c in r[1:3])[:120]
                    # rút/bãi bỏ khi: mã bị gạch (~~ID~~), hoặc có một ô NGẮN chỉ ghi trạng thái rút/bãi bỏ
                    w = "~~" in r[0] or any(len(strip_md(c)) <= 25 and re.search(r"\b(rút|bãi bỏ|đã rút|withdrawn)\b", strip_md(c), re.I)
                                            for c in r[1:])
                    defined[first].append((fname, "table", rowtxt, w))
                    if w:
                        withdrawn.add(first)

    # 4a. ENT list từ bảng entity
    ents = OrderedDict()
    for fname, full, content in files:
        for ln, heading, header, rows in md_tables(content):
            hs = [strip_md(h).lower() for h in header]
            if "bảng" in hs and any(h in ("entity", "thực thể") for h in hs):
                ib = hs.index("bảng")
                il = next((k for k, h in enumerate(hs) if "nhãn" in h or "label" in h), None)
                for r in rows:
                    e = strip_md(r[0])
                    if re.fullmatch(r"ENT-\d+", e) and e not in ents and len(r) > ib:
                        ents[e] = {"table": first_token(r[ib]), "label": lbl(r[il]) if il is not None and il < len(r) else "",
                                   "raw_label": strip_md(r[il])[:60] if il is not None and il < len(r) else "", "file": fname}

    # 1. STAT
    def split_live(prefix):
        ids = sorted({i for i in defined if i.startswith(prefix + "-")}, key=key)
        return [i for i in ids if i not in withdrawn], [i for i in ids if i in withdrawn]

    api_live, api_wd = split_live("API")
    evt_live, evt_wd = split_live("EVT")
    consumed = [i for i in evt_live if any(re.search(r"tiêu thụ|consum|producer", t, re.I) for _, _, t, _ in defined[i])]
    print("\n== 1. STAT (dùng cho mục 01) ==")
    lab = defaultdict(list)
    for e, v in ents.items():
        lab[v["label"] or "?"].append(v["table"])
    print(f"ENT/table: {len(ents)} → " + ", ".join(f"{k}={len(v)} ({', '.join(v)})" for k, v in lab.items()))
    print(f"API còn hiệu lực: {len(api_live)} ({', '.join(api_live)}) · đã rút/bãi bỏ: {', '.join(api_wd) or '-'}")
    print(f"EVT định nghĩa: {len(evt_live)} · trong đó có dấu hiệu 'tiêu thụ': {', '.join(consumed) or '-'} · đã rút: {', '.join(evt_wd) or '-'}"
          "  (tự kiểm lại bảng event tiêu thụ trong TA)")
    cf = sorted({i for i in defined if i.startswith("CF-")}, key=key)
    print(f"CF: {len(cf)} ({cf[0] if cf else ''} → {cf[-1] if cf else ''})")

    # 2. ID
    print("\n== 2. ID theo tiền tố ==")
    for p in sorted(referenced, key=lambda p: -len(referenced[p])):
        ids = sorted(referenced[p], key=key)
        d = [i for i in ids if i in defined]
        if len(ids) < 2 and not d:
            continue
        wd = [i for i in d if i in withdrawn]
        print(f"{p}: {len(d)} định nghĩa ({len(d) - len(wd)} còn hiệu lực) / {len(ids)} nhắc tới")
        if d:
            print(f"   định nghĩa: {', '.join(d)}")
        if wd:
            print(f"   đã rút/bãi bỏ: {', '.join(wd)}")
        only = [i for i in ids if i not in defined]
        if only and len(only) <= 60:
            print(f"   chỉ nhắc (thường là mã BA hoặc feature khác): {', '.join(only)}")

    # 3. trùng mã
    print("\n== 3. Nghi trùng mã (tự xác minh) ==")
    dup = 0
    for i, defs in sorted(defined.items(), key=lambda x: key(x[0])):
        if i.split("-")[0] not in DUP_PREFIX:
            continue
        tabs = [d for d in defs if d[1] == "table"]
        files_ = {d[0] for d in tabs}
        if len(files_) > 1 and len({d[2][:30] for d in tabs}) > 1:
            dup += 1
            print(f"- {i}: " + " || ".join(f"[{f}] {t}" for f, _, t, _ in tabs))
    print("(không có)" if not dup else "")

    # 4b. cột
    tables = OrderedDict()
    for fname, full, content in files:
        for ln, heading, header, rows in md_tables(content):
            h0 = strip_md(header[0]).lower() if header else ""
            m = re.search(r"bảng\s+`([a-z0-9_]+)`", heading) or re.search(r"table\s+`([a-z0-9_]+)`", heading, re.I)
            if not m or h0 not in ("cột", "column"):
                continue
            t = m.group(1)
            idx = {strip_md(h).lower(): k for k, h in enumerate(header)}
            cols = []
            for r in rows:
                g = lambda n: strip_md(r[idx[n]]) if n in idx and idx[n] < len(r) else ""
                cols.append({"name": first_token(r[0]), "type": g("kiểu"), "null": g("null"), "change": g("thay đổi"),
                             "note": (g("ghi chú") or g("ý nghĩa"))[:140]})
            ent = re.search(r"(ENT-\d+)", heading)
            tables.setdefault(t, {"ent": ent.group(1) if ent else None, "label": lbl(heading), "file": fname, "line": ln, "columns": []})
            tables[t]["columns"] += cols
    print("\n== 4. ENT → table → cột ==")
    for e, v in ents.items():
        t = v["table"]
        cols = [c["name"] for c in tables.get(t, {}).get("columns", [])]
        warn = "" if cols else "   ⚠ không có bảng cột dạng 'Cột | Kiểu' (xem mục mô tả table trong design, có thể là bảng giá trị/mapping)"
        print(f"- {e} {t} [{v['label'] or v['raw_label'] or '?'}]: {len(cols)} cột → {', '.join(cols) or '-'}{warn}")
    for t in tables:
        if t not in {v['table'] for v in ents.values()}:
            print(f"- (không có ENT) {t}: {', '.join(c['name'] for c in tables[t]['columns'])}")

    # 5. index
    indexes = []
    for fname, full, content in files:
        for ln, heading, header, rows in md_tables(content):
            hs = [strip_md(h).lower() for h in header]
            if "bảng" in hs and "cột" in hs and "loại" in hs and any(x in hs for x in ("tên", "index")):
                ib, it = hs.index("bảng"), hs.index("tên") if "tên" in hs else hs.index("index")
                ik, ic = hs.index("loại"), hs.index("cột")
                for r in rows:
                    if len(r) <= max(ib, it, ik, ic):
                        continue
                    existing = bool(re.search(r"có sẵn|đang có|existing", " ".join(r), re.I))
                    indexes.append({"table": strip_md(r[ib]), "name": strip_md(r[it]), "kind": strip_md(r[ik]), "existing": existing,
                                    "columns": [first_token(c) for c in strip_md(r[ic]).split(",")], "file": fname})
    print("\n== 5. Index ==")
    per_table = defaultdict(list)
    for ix in indexes:
        if not ix["existing"]:
            per_table[ix["table"]].append(ix)
        warn = ""
        info = tables.get(ix["table"])
        if info and (info["label"] == "new" or ents_label(ents, ix["table"]) == "new"):
            known = {c["name"] for c in info["columns"]} | {"id", "created_at", "updated_at"}
            miss = [c for c in ix["columns"] if c and c not in known]
            if miss:
                warn = f"   ⚠ cột không có trong bảng cột: {', '.join(miss)}"
        print(f"- {ix['table']}.{ix['name']} ({ix['kind']}{', có sẵn' if ix['existing'] else ''}) [{', '.join(ix['columns'])}]{warn}")

    # 6. migration
    migrations = []
    for fname, full, content in files:
        for ln, heading, header, rows in md_tables(content):
            hs = [strip_md(h).lower() for h in header]
            if any("migration" in h for h in hs) and "nội dung" in hs:
                im, inn = next(k for k, h in enumerate(hs) if "migration" in h), hs.index("nội dung")
                for r in rows:
                    if len(r) <= max(im, inn):
                        continue
                    migrations.append({"no": strip_md(r[0]), "name": strip_md(r[im]), "content": strip_md(r[inn]),
                                       "withdrawn": bool(WITHDRAWN_RE.search(r[0] + r[im])) or "không thuộc" in r[inn].lower(), "file": fname})
    print("\n== 6. Migration ==")
    own = [m for m in migrations if not m["withdrawn"]]
    print(f"Migration của feature: {len(own)} · không thuộc/đã rút: {len(migrations) - len(own)}")
    for mg in migrations:
        warn = ""
        n = re.search(r"\+\s*(\d+)\s*index", mg["content"])
        cand = [tb for tb in per_table if re.search(r"\b" + tb + r"\b", mg["content"])] or \
               [tb for tb in per_table if tb.replace("_", "") in mg["name"].lower()]
        if n and cand:
            have = len(per_table[cand[0]])
            if have != int(n.group(1)):
                warn = f"   ⚠ ghi {n.group(1)} index nhưng bảng index liệt kê {have} index mới cho {cand[0]}"
        print(f"- #{mg['no']} {mg['name']}{' (không thuộc / rút)' if mg['withdrawn'] else ''}: {mg['content'][:110]}{warn}")

    # 7. cấu hình, message, mermaid
    cfg = OrderedDict()
    for fname, full, content in files:
        for ln, heading, header, rows in md_tables(content):
            hs = [strip_md(h).lower() for h in header]
            if hs and (hs[0] in ("khóa", "key", "biến") or "khóa cấu hình" in hs[0]):
                idef = next((k for k, h in enumerate(hs) if "mặc định" in h or "production" in h or "default" in h), None)
                for r in rows:
                    for k in re.findall(r"`((?:NEXT_PUBLIC_)?[A-Z][A-Z0-9]+(?:_[A-Z0-9*]+)+)`", r[0]):
                        cfg[k] = {"default": strip_md(r[idef]) if idef is not None and idef < len(r) else "",
                                  "removed": bool(WITHDRAWN_RE.search(" ".join(r)))}
    removed_mentions = sorted(set(re.findall(r"`((?:NEXT_PUBLIC_)?[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,})`[^\n]{0,80}(?:bị bỏ|bãi bỏ|đã bỏ)", text)))
    msg = sorted(set(re.findall(r"\b(100\d{6})\b", text)))
    mer = defaultdict(int)
    for m in re.finditer(r"```mermaid\s*\n\s*(\w[\w-]*)", text):
        mer[m.group(1)] += 1
    print("\n== 7. Cấu hình · message · mermaid ==")
    print(f"Khóa cấu hình trong bảng cấu hình ({len(cfg)}):")
    for k, v in cfg.items():
        print(f"   - {k} = {v['default']}{'  (đã bỏ)' if v['removed'] else ''}")
    if removed_mentions:
        print(f"Khóa được nhắc là đã bỏ: {', '.join(removed_mentions)}")
    print(f"Mã message số ({len(msg)}): {', '.join(msg)}")
    print(f"Mermaid trong TA: {dict(mer)}")

    # 8. biên tập
    print("\n== 8. Gợi ý lỗi biên tập (tự xác minh) ==")
    hints = []
    for fname, full, content in files:
        lines = content.splitlines()
        incode = False
        for i, ln in enumerate(lines):
            if ln.strip().startswith("```"):
                incode = not incode
                continue
            if incode or not ln.strip() or ln.lstrip().startswith(("|", "#", "-", "*", ">", "!", "<")) or re.match(r"^\s*\d+\.", ln):
                continue
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            s = ln.rstrip()
            if not nxt.strip() and len(s) > 40 and not re.search(r"[.:;!?)`*|>\]…]$", s):
                hints.append(f"[{fname}:{i + 1}] câu có thể bị cụt: …{s[-70:]}")
            prev = lines[i - 1].rstrip() if i else ""
            if prev and len(s) > 15 and (prev.endswith(s.strip()) or (len(s) >= 30 and len(prev) >= 30 and s[-30:] == prev[-30:])):
                hints.append(f"[{fname}:{i + 1}] dòng lặp lại phần cuối dòng trước: {s.strip()[:70]}")
    print("\n".join(hints[:25]) or "(không có)")

    if a.check_html:
        h = open(a.check_html, encoding="utf-8").read()
        def part(start, end):
            i = h.find(f'id="{start}"')
            j = h.find(f'id="{end}"', i + 1) if end else -1
            return h[i:j if j > 0 else None] if i >= 0 else ""
        flows, cards = part("flows", "tables"), part("tables", "test")
        body = h[h.find("</style>"):]
        print(f"\n== CHECK HTML {a.check_html} ==")
        print(f"Số dòng sau </style>: {body.count(chr(10))} (giới hạn ~380)")
        miss = 0
        for e, v in ents.items():
            t = v["table"]
            nf, nc = len(re.findall(r"\b" + re.escape(t) + r"\b", flows)), len(re.findall(r"\b" + re.escape(t) + r"\b", cards))
            if not nf or not nc:
                miss += 1
                print(f"⚠ {e} {t}: mục 3 (flow) = {nf} lần, mục 4 (tra cứu) = {nc} lần")
        print("OK: mọi ENT có ở mục 3 và mục 4" if not miss else f"{miss} ENT thiếu")
        bad_sql = re.findall(r"<pre class=\"sql\">(.*?)</pre>", h, re.S)
        if any(re.search(r"\b(UPDATE|DELETE|INSERT|DROP|ALTER|TRUNCATE)\b", s, re.I) for s in bad_sql):
            print("⚠ SQL có câu không phải SELECT")

    if a.json:
        json.dump({"ba_source": list(ba), "ents": ents, "tables": tables, "indexes": indexes, "migrations": migrations,
                   "config": cfg, "message_codes": msg, "withdrawn": sorted(withdrawn, key=key),
                   "api_live": api_live, "evt": evt_live}, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"\nJSON → {a.json}")


def ents_label(ents, table):
    for v in ents.values():
        if v["table"] == table:
            return v["label"]
    return ""


if __name__ == "__main__":
    main()

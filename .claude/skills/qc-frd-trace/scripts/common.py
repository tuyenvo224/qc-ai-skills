"""Shared helpers: credential lookup, CSV reading, FRD table parsing."""
import csv
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _read_kv(path):
    out = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def load_config(filename, keys):
    """Env vars win; then <filename> in cwd or any parent; then in home."""
    found = {k: os.environ[k] for k in keys if os.environ.get(k)}
    if len(found) == len(keys):
        return found
    candidates = [p / filename for p in [Path.cwd(), *Path.cwd().parents]] + [Path.home() / filename]
    for c in candidates:
        if c.is_file():
            kv = _read_kv(c)
            for k in keys:
                found.setdefault(k, kv.get(k, ""))
            break
    missing = [k for k in keys if not found.get(k)]
    if missing:
        sys.exit(f"STOP: missing {', '.join(missing)}. Create {filename} (KEY=VALUE, see {filename}.example) "
                 f"in the repo root or {Path.home()}, or set the env vars.")
    return found


def read_csv(path):
    """Read a CSV whose delimiter may be ';' or ','."""
    text = Path(path).read_text(encoding="utf-8-sig")
    first = text.splitlines()[0] if text else ""
    delim = ";" if first.count(";") >= first.count(",") else ","
    return list(csv.DictReader(text.splitlines(), delimiter=delim))


def col(row, *names):
    """Get a value by the first header that starts with any of the names."""
    for n in names:
        for k in row:
            if k and k.strip().startswith(n):
                return (row[k] or "").strip()
    return ""


def split_md_row(line):
    cells = re.split(r"(?<!\\)\|", line.strip())[1:-1]
    return [c.strip().replace("\\|", "|") for c in cells]


NHOM_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+){1,2}$")


def parse_nhom_catalog(path):
    """{key: (chủ đề, mô tả)} from frd-reqs.md §Danh mục nhóm (table with a Nhóm column)."""
    cat, section, header = {}, None, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section, header = line[3:].strip().lower(), None
            continue
        if not (section and section.startswith("danh mục nhóm") and line.startswith("|")) or re.match(r"^\|\s*:?-{2,}", line):
            continue
        cells = split_md_row(line)
        if header is None or (cells and cells[0] in ("Nhóm", "Chủ đề")):
            header = [c.lower() for c in cells]
            continue
        if header and header[0] == "nhóm" and cells and NHOM_RE.match(cells[0].strip("`")):
            cat[cells[0].strip("`")] = (cells[1].strip("`") if len(cells) > 1 else "", cells[2] if len(cells) > 2 else "")
    return cat


def parse_topics(path):
    """Ordered {topic_key: Vietnamese 'Nhóm chức năng' name} from the '| Chủ đề | Nhóm chức năng | …' table."""
    topics, on = {}, False
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and re.match(r"^\|\s*Chủ đề\s*\|\s*Nhóm chức năng\s*\|", line):
            on = True
            continue
        if on:
            if not line.startswith("|"):
                on = False
                continue
            if re.match(r"^\|\s*:?-{2,}", line):
                continue
            cells = split_md_row(line)
            key = cells[0].strip("`* ") if cells else ""
            if re.fullmatch(r"[a-z][a-z0-9_]*", key) and len(cells) > 1:
                topics[key] = cells[1].strip()
    return topics


def parse_frd_reqs(path):
    reqs, oq, section = {}, [], None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        if not line.startswith("|"):
            continue
        cells = split_md_row(line)
        if cells and re.fullmatch(r"R-\d+", cells[0]):
            reqs[cells[0]] = dict(sec=cells[1] if len(cells) > 1 else "", typ=cells[2] if len(cells) > 2 else "",
                                  q=cells[3] if len(cells) > 3 else "", note=cells[4] if len(cells) > 4 else "",
                                  grp=cells[5].strip("`") if len(cells) > 5 else "")
        elif section and section.startswith("câu hỏi mở") and cells and re.fullmatch(r"[A-Z]{1,3}-\d+", cells[0]):
            oq.append(cells)
    return reqs, oq


def expand_r(s):
    out = []
    for a, b in re.findall(r"R-(\d+)(?:\s*(?:\.\.|…|–|-|→)\s*R-(\d+))?", s or ""):
        a = int(a)
        b = int(b) if b else a
        out += [f"R-{i:03d}" for i in range(a, b + 1)]
    return out

#!/usr/bin/env python3
"""Ghi link artifact vào file tracking (mỗi skill một file .md). MỖI LINK CHỈ 1 DÒNG.

Cách dùng:
    python append_link.py --skill <tên-skill> --feature "<Tính năng>" --url <link artifact> [--at "YYYY-MM-DD HH:MM"]

- File: <gốc project>/artifact-links/<tên-skill>.md (tự tạo thư mục, tiêu đề + header bảng nếu chưa có).
- Bảng 3 cột: Ngày giờ xuất | Tính năng | Link artifact (giờ Việt Nam, UTC+7).
- Link chưa có → thêm dòng mới ở cuối bảng.
- Link đã có → xóa dòng cũ, ghi dòng mới (giờ xuất + tính năng mới nhất) ở CUỐI bảng.
  Bảng vì vậy luôn sắp theo thời gian xuất, dòng dưới cùng là bản mới nhất.
- File lỡ có nhiều dòng trùng link (sửa tay) → gộp còn 1 dòng.
"""
import argparse
import os
import re
import sys
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
def project_root():
    """Thư mục gốc project: thư mục đang làm việc nếu có `.claude/` → đi ngược từ script tới `.claude`."""
    cwd = os.getcwd()
    if os.path.isdir(os.path.join(cwd, ".claude")):
        return cwd
    p = os.path.abspath(__file__)
    while os.path.dirname(p) != p:
        if os.path.basename(p) == ".claude":
            return os.path.dirname(p)
        p = os.path.dirname(p)
    return cwd


LINK_DIR = os.path.join(project_root(), "artifact-links")
NOTE = "Mỗi link artifact chỉ 1 dòng; chạy lại skill thì dòng đó được cập nhật giờ xuất và chuyển xuống cuối bảng (giờ Việt Nam). Không sửa tay header."
HEADER = "| Ngày giờ xuất | Tính năng | Link artifact |\n|---|---|---|"


def norm(url):
    return url.strip().split("?")[0].rstrip("/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True)
    ap.add_argument("--feature", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--at", help="ghi đè ngày giờ, dạng 'YYYY-MM-DD HH:MM' (giờ VN)")
    ap.add_argument("--dir", default=LINK_DIR)
    a = ap.parse_args()

    at = a.at or datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M")
    feature = a.feature.replace("|", "/").strip()
    url = norm(a.url)
    new_row = f"| {at} | {feature} | [{url.split('/')[-1]}]({url}) |"

    os.makedirs(a.dir, exist_ok=True)
    path = os.path.join(a.dir, f"{a.skill}.md")
    rows = []
    if os.path.exists(path):
        for ln in open(path, encoding="utf-8").read().splitlines():
            m = re.match(r"^\|\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s*\|", ln)
            if m:
                rows.append(ln)
    # mỗi link 1 dòng: bỏ mọi dòng cùng link, rồi gộp trùng (giữ dòng có giờ lớn nhất)
    latest = {}
    for r in rows:
        u = re.search(r"\]\(([^)]+)\)", r)
        k = norm(u.group(1)) if u else r
        t = r.split("|")[1].strip()
        if k != url and (k not in latest or t >= latest[k][0]):
            latest[k] = (t, r)
    kept = [r for _, r in sorted(latest.values(), key=lambda x: x[0])]
    replaced = len(rows) != len(kept)
    kept.append(new_row)

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# Link artifact – {a.skill}\n\n{NOTE}\n\n{HEADER}\n" + "\n".join(kept) + "\n")
    print(f"{'Đã cập nhật' if replaced else 'Đã thêm'} vào {path}: {new_row}")


if __name__ == "__main__":
    main()

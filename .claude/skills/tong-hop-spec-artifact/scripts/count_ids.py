#!/usr/bin/env python3
"""Đếm các mã ID xuất hiện trong spec.txt (UC-01, BR-LOGIN-01, FR-12, VR-03, AC-20 ...).

Cách dùng:  python count_ids.py <spec.txt>
In ra số ID DUY NHẤT theo từng tiền tố và danh sách để đối chiếu, tránh sót hoặc đếm tay sai.
Mã dạng khoảng (vd "FR-14–15") chỉ đếm 2 đầu mút đã xuất hiện, nên luôn đối chiếu với danh sách định nghĩa trong spec.
"""
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
text = open(sys.argv[1], encoding="utf-8").read()
ids = defaultdict(set)
for m in re.finditer(r"\b([A-Z]{1,6})((?:-[A-Z]{2,12})*)-(\d{1,4})\b", text):
    prefix, group, num = m.group(1), m.group(2), m.group(3)
    ids[prefix].add(f"{prefix}{group}-{num}")


def key(x):
    parts = re.split(r"(\d+)", x)
    return [int(p) if p.isdigit() else p for p in parts]


for prefix in sorted(ids, key=lambda p: -len(ids[p])):
    vals = sorted(ids[prefix], key=key)
    print(f"{prefix}: {len(vals)}  ->  {', '.join(vals)}")

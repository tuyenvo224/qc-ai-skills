#!/usr/bin/env python3
"""Tạo khối HTML nhúng ảnh (data URI base64) cho mục "Nguồn ảnh" của trang artifact.

Cách dùng:
    python embed_images.py --out <snippet.html> "<đường dẫn ảnh>::<chú thích>::<nguồn>" [...]

    - <chú thích>: mô tả ngắn những gì NHÌN THẤY trong ảnh (1 câu).
    - <nguồn>: "đính kèm" | "BookStack" | "Redmine attachment" … (không bắt buộc).
    - Ảnh được đánh số #1, #2… theo thứ tự truyền vào. Trong trang, rule lấy từ ảnh ghi "(từ ảnh #n)".

Giới hạn (để trang không quá nặng; artifact tối đa 16MB):
    - mỗi ảnh ≤ 1.5 MB, tổng ≤ 8 MB. Ảnh vượt giới hạn KHÔNG nhúng, chỉ in thẻ mô tả kèm lý do.
    - chỉ nhận png, jpg/jpeg, gif, webp, svg.
In ra màn hình bảng tóm tắt (ảnh nào nhúng / bỏ qua). Dán nội dung <snippet.html> vào chỗ {{FIGURES}} của template.
"""
import argparse
import base64
import html
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
        ".webp": "image/webp", ".svg": "image/svg+xml"}
MAX_ONE, MAX_ALL = 1_500_000, 8_000_000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("items", nargs="+", help='"path::caption::source"')
    a = ap.parse_args()

    total, parts, report = 0, ['<div class="figs">'], []
    for n, item in enumerate(a.items, 1):
        bits = item.split("::")
        path, cap = bits[0].strip(), (bits[1].strip() if len(bits) > 1 else "")
        src = bits[2].strip() if len(bits) > 2 else ""
        name = os.path.basename(path)
        ext = os.path.splitext(path)[1].lower()
        reason = None
        if not os.path.isfile(path):
            reason = "không tìm thấy file"
        elif ext not in MIME:
            reason = f"định dạng {ext or '?'} không hỗ trợ"
        else:
            size = os.path.getsize(path)
            if size > MAX_ONE:
                reason = f"{size / 1e6:.1f} MB > 1.5 MB"
            elif total + size > MAX_ALL:
                reason = "vượt tổng 8 MB"
        meta = " · ".join(x for x in (src, html.escape(name)) if x)
        head = f'<figcaption><b>Ảnh #{n}</b> — {html.escape(cap)}<span class="src">{meta}</span></figcaption>'
        if reason:
            parts.append(f'<figure class="fig nofile">{head}<p class="miss">Không nhúng ({html.escape(reason)}).</p></figure>')
            report.append(f"#{n} {name}: BỎ QUA — {reason}")
            continue
        data = base64.b64encode(open(path, "rb").read()).decode()
        total += size
        parts.append(f'<figure class="fig"><img src="data:{MIME[ext]};base64,{data}" alt="Ảnh #{n}: {html.escape(cap)}" loading="lazy">{head}</figure>')
        report.append(f"#{n} {name}: nhúng ({size / 1e3:.0f} KB)")
    parts.append("</div>")
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts) + "\n")
    print("\n".join(report))
    print(f"Tổng nhúng: {total / 1e6:.2f} MB → {a.out}")


if __name__ == "__main__":
    main()

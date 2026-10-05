"""Render report.md, matrix.md and report.html from data.json + narrative.json (same source → same numbers).

Usage: python render.py <OUT>
"""
import html
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TPL = Path(__file__).resolve().parent.parent / "references" / "report-template.html"
LANES = {1: ("Test ngay", "l1", "code có / tài liệu khớp FRD"), 2: ("Test + ghi thiếu", "l2", "chỉ làm một phần"),
         3: ("Chờ PO chốt", "l3", "khác FRD"), 4: ("Chưa có", "l4", "FRD có, code/tài liệu chưa có")}
ST_COLOR = {"Đủ": "var(--ok)", "Một phần": "var(--med)", "Lệch": "var(--crit)", "Thiếu": "var(--high)", "N/A": "var(--line)"}
SEV = {"high": ("s-high", "Cao"), "med": ("s-med", "Trung bình"), "low": ("s-low", "Thấp")}


def inline(s):
    s = html.escape(s or "")
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)


def md_cell(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def pct(n, t):
    return f"{(100 * n / t):.0f}%" if t else "0%"


def main():
    out = Path(sys.argv[1])
    d = json.loads((out / "data.json").read_text(encoding="utf-8"))
    n = json.loads((out / "narrative.json").read_text(encoding="utf-8"))
    st = d["stats"]
    tot = st["frd_total"]
    fvb = st["frd_vs_ba"]
    order = ["Đủ", "Một phần", "Lệch", "Thiếu", "N/A"]
    impl = st.get("impl", {})
    impl_r = st.get("impl_r", {})
    has_code = bool(impl or impl_r)
    has_ta = st.get("has_ta", False)
    fvt = st.get("frd_vs_ta", {})
    ui_bad = [x for x in d.get("ui", []) if x["st"] and x["st"] != "Đủ"]
    ta_flag = [x for x in d.get("ta_notes", []) if x["res"] in ("Trái FRD",) or x["res"].startswith("Tự chốt")]

    def bar(counts, label):
        return (f"<h3>{label} ({tot} yêu cầu)</h3><div class=\"bar\" role=\"img\" aria-label=\""
                + ", ".join(f"{k} {counts.get(k, 0)}" for k in order) + '">'
                + "".join(f'<span style="width:{100 * counts.get(k, 0) / max(tot, 1):.1f}%;background:{ST_COLOR[k]}"></span>' for k in order)
                + '</div><div class="legend">' + "".join(f'<span><i style="background:{ST_COLOR[k]}"></i>{k} {counts.get(k, 0)}</span>' for k in order) + "</div>")

    cards = [
        (tot, "yêu cầu tách từ FRD, mỗi dòng có trích nguyên văn"),
        (st["oq_total"], "câu hỏi mở / TBD / tự mâu thuẫn trong FRD"),
        (f"{fvb.get('Đủ', 0)} ({pct(fvb.get('Đủ', 0), tot)})", "yêu cầu FRD khớp đủ với tài liệu BA"),
    ]
    if has_ta:
        cards.append((f"{fvt.get('Đủ', 0)} ({pct(fvt.get('Đủ', 0), tot)})", "yêu cầu FRD được tài liệu TA thiết kế khớp đủ"))
        if d.get("ui"):
            cards.append((f"{len(ui_bad)} / {len(d['ui'])}", "yêu cầu UI/Message của FRD mà ui-contract thiếu hoặc lệch"))
    cov = st.get("coverage", {"ran": False})
    if cov.get("ran"):
        cards.append((f"{cov['added']} · {cov['open']}", "ý bị sót do agent tự kiểm tìm ra: đã bổ sung · còn mở cần kiểm tay"))
    if has_code:
        cards += [(f"{impl_r.get('Có', 0)} / {tot}", "yêu cầu FRD code staging đã làm đúng"),
                  (f"{impl_r.get('Chưa có', 0)} / {tot}", "yêu cầu FRD code chưa có"),
                  (f"{impl_r.get('Khác FRD', 0)} / {tot}", "yêu cầu FRD code làm khác FRD")]
    if st["ba_extra"]:
        cards.append((st["ba_extra"], "mã BA không có trong FRD · " + " · ".join(f"{k} {v}" for k, v in st["ba_extra_by_type"].items())))
    if st["qc_cases"]:
        cards.append((f"{st['qc_rep']} / {st['qc_cases']}", f"case QC đại diện / tổng · phủ {st['ba_ids_covered']}/{st['ba_ids']} mã BA"))

    # ---------- HTML body ----------
    H = []
    H.append('<div class="wrap"><nav class="toc" aria-label="Mục lục"><b>Mục lục</b>'
             '<a href="#tomtat">Tóm tắt</a><a href="#vi-sao">Dòng thời gian</a><a href="#lech">Các điểm lệch lớn</a>'
             '<a href="#po">Câu hỏi cần PO chốt</a><a href="#checklist">Checklist test</a>'
             '<a href="#moitruong">Chuẩn bị môi trường</a><a href="#them">BA thêm ngoài FRD</a>'
             '<a href="#redmine">Redmine vs FRD</a><a href="#ta">TA vs FRD</a><a href="#coverage">Tự kiểm độ phủ</a><a href="#matrix">Ma trận FRD</a></nav><main>')
    H.append(f'<header><div class="eyebrow">QC · {inline(n.get("feature"))} · {inline(n.get("date"))}</div>'
             f'<h1>{inline(n.get("title"))}</h1><p class="lede">{inline(n.get("lede"))}</p><ul class="scope" aria-label="Nguồn">'
             + "".join(f"<li>{inline(s)}</li>" for s in n.get("sources", [])) + "</ul></header>")
    H.append('<section id="tomtat"><div class="verdict">' + "".join(f"<p>{inline(p)}</p>" for p in n.get("verdict", [])) + "</div>")
    H.append(bar(fvb, "FRD so với tài liệu BA"))
    if has_ta:
        H.append(bar(fvt, "FRD so với tài liệu TA"))
    H.append('<div class="stats">' + "".join(f'<div class="card"><b>{html.escape(str(v))}</b><span>{html.escape(t)}</span></div>' for v, t in cards) + "</div></section>")

    H.append('<section id="vi-sao"><h2><span class="n">01</span>Dòng thời gian</h2><ul class="tl">'
             + "".join(f'<li class="{"warn" if t.get("warn") else ""}"><time>{inline(t.get("date"))}</time>{inline(t.get("text"))}</li>' for t in n.get("timeline", []))
             + f'</ul><p class="note">{inline(n.get("timeline_note"))}</p></section>')
    H.append('<section id="lech"><h2><span class="n">02</span>Các điểm lệch lớn</h2><div class="tbl"><table><thead><tr><th>Chủ đề</th><th>FRD</th><th>Hiện tại</th><th>Ảnh hưởng tới test</th></tr></thead><tbody>'
             + "".join(f"<tr><td>{inline(x.get('topic'))}</td><td>{inline(x.get('frd'))}</td><td>{inline(x.get('current'))}</td><td>{inline(x.get('impact'))}</td></tr>" for x in n.get("divergences", []))
             + "</tbody></table></div></section>")
    H.append('<section id="po"><h2><span class="n">03</span>Câu hỏi cần PO chốt</h2><ol class="now">'
             + "".join(f"<li><b>{inline(x.get('q'))}</b>{inline(x.get('detail'))}</li>" for x in n.get("po_questions", [])) + "</ol></section>")
    H.append('<section id="checklist"><h2><span class="n">04</span>Checklist test theo nhóm chức năng</h2>'
             f'<p class="sub">{st["groups"]} nhóm chức năng gộp từ {tot} yêu cầu FRD. Làn của nhóm tính theo đa số yêu cầu FRD trong nhóm; từng case vẫn có thể khác. Mở case gốc theo ID, không cần đọc cả file.</p><div class="legend" style="margin-bottom:8px">'
             + "".join(f'<span><span class="lane {c}">{t}</span> {h}</span>' for t, c, h in LANES.values())
             + '</div><div class="tools"><label for="ck-lane" class="count">Làn</label><select id="ck-lane"><option value="">Tất cả</option>'
             + "".join(f'<option value="{k}">{v[0]}</option>' for k, v in LANES.items())
             + '</select><input id="ck-q" type="search" placeholder="Tìm nhóm, R-xxx, TC-xxx…" aria-label="Tìm trong checklist"><span class="count" id="ck-count"></span></div>'
             '<div class="tbl"><table><thead><tr><th>Nhóm chức năng</th><th>Làn</th><th>FRD → BA / TA (số yêu cầu)</th><th>Code (số yêu cầu FRD)</th><th>Case QC đại diện</th></tr></thead><tbody id="ck-body"></tbody></table></div></section>')
    H.append('<section id="moitruong"><h2><span class="n">05</span>Chuẩn bị môi trường &amp; lưu ý khi chạy</h2>'
             + "".join(f'<div class="f" data-sev="{x.get("level", "med")}"><span class="pill {SEV.get(x.get("level"), SEV["med"])[0]}">{SEV.get(x.get("level"), SEV["med"])[1]}</span>'
                       f'<h4>{inline(x.get("title"))}</h4><p class="ev">{inline(x.get("evidence"))}</p><p class="fix">{inline(x.get("action"))}</p></div>' for x in n.get("env_notes", []))
             + "</section>")
    H.append('<section id="them"><h2><span class="n">06</span>BA thêm ngoài FRD</h2><div class="two">'
             + "".join(f'<div class="card"><h4>{inline(x.get("title"))}</h4><ul>' + "".join(f"<li>{inline(i)}</li>" for i in x.get("items", [])) + "</ul></div>" for x in n.get("extras", []))
             + "</div>")
    if d["extra"]:
        H.append(f'<details><summary>Xem đủ {len(d["extra"])} mã</summary><div class="tbl scroll"><table><thead><tr><th>BA ID</th><th>Loại</th><th>Nội dung</th><th>FRD liên quan</th></tr></thead><tbody>'
                 + "".join(f"<tr><td class=\"ids\">{html.escape(x['id'])}</td><td>{html.escape(x['typ'])}</td><td>{html.escape(x['text'])}</td><td class=\"ids\">{html.escape(x['frd'])}</td></tr>" for x in d["extra"])
                 + "</tbody></table></div></details>")
    H.append("</section>")
    H.append('<section id="redmine"><h2><span class="n">07</span>Redmine so với FRD</h2>'
             + (('<div class="tbl scroll"><table><thead><tr><th>Chủ đề</th><th>Redmine nói</th><th>FRD nói</th><th>Kết luận</th></tr></thead><tbody>'
                 + "".join(f"<tr><td>{html.escape(x['topic'])}</td><td>{html.escape(x['rm'])}</td><td>{html.escape(x['frd'])}</td><td><b>{html.escape(x['res'])}</b></td></tr>" for x in d["rvf"])
                 + "</tbody></table></div>") if d["rvf"] else '<p class="note">Không có dữ liệu Redmine.</p>') + "</section>")
    if has_ta:
        tb = (f'<p class="sub">Từng yêu cầu FRD được so với thiết kế trong analysis/design/ui-contract. Lọc cột TA trong ma trận để xem chi tiết. '
              f'Ghi chú TA: ' + " · ".join(f"{k} {v}" for k, v in st.get("ta_notes", {}).items()) + '.</p>')
        if ta_flag:
            tb += ('<h3>Ghi chú TA trái FRD hoặc tự chốt câu hỏi mở</h3><div class="tbl scroll"><table><thead><tr><th>ID</th><th>Nội dung</th><th>R liên quan</th><th>Kết luận</th><th>Ảnh hưởng test</th></tr></thead><tbody>'
                   + "".join(f"<tr><td class=\"ids\">{html.escape(x['id'])}</td><td>{html.escape(x['text'])}</td><td class=\"ids\">{html.escape(x['rs'])}</td><td><b>{html.escape(x['res'])}</b></td><td>{html.escape(x['impact'])}</td></tr>" for x in ta_flag)
                   + "</tbody></table></div>")
        if d.get("ui"):
            tb += (f'<h3>ui-contract so với yêu cầu UI của FRD: {len(ui_bad)} thiếu/lệch trên {len(d["ui"])}</h3>'
                   + (('<div class="tbl scroll"><table><thead><tr><th>R</th><th>Màn hình / phần tử</th><th>Trạng thái</th><th>Ghi chú</th></tr></thead><tbody>'
                       + "".join(f"<tr><td class=\"ids\">{html.escape(x['r'])}</td><td>{html.escape(x['el'])}</td><td><b>{html.escape(x['st'])}</b></td><td>{html.escape(x['note'])}</td></tr>" for x in ui_bad)
                       + "</tbody></table></div>") if ui_bad else '<p class="note">ui-contract có đủ màn hình và vùng message cho mọi yêu cầu UI của FRD.</p>'))
    else:
        tb = '<p class="note">Không có tài liệu TA, hoặc bước FRD → TA (P5) chưa chạy.</p>'
    H.append(f'<section id="ta"><h2><span class="n">08</span>TA so với FRD</h2>{tb}</section>')
    if cov.get("ran"):
        body = (f'<p class="sub">Một agent độc lập đọc lại FRD để tìm ý bị sót: tìm thấy {cov["missed"]} ý, đã bổ sung {cov["added"]}, '
                f'loại {cov["rejected"]} sau khi kiểm, còn mở {cov["open"]}. Tách {cov["merged"]} yêu cầu gộp nhiều ý. '
                f'Mục FRD không có yêu cầu nào nhưng có nội dung test: {cov["empty_sections_not_ok"]}.</p>')
        body += ('<div class="tbl"><table><thead><tr><th>Mục FRD</th><th>Ý còn mở — kiểm tay với FRD</th></tr></thead><tbody>'
                 + "".join(f"<tr><td>{html.escape(x['sec'])}</td><td>{html.escape(x['q'])}</td></tr>" for x in d.get("cov_open", []))
                 + "</tbody></table></div>") if d.get("cov_open") else '<p class="note">Không còn ý nào mở. Vẫn nên kiểm nhanh mục lục FRD so với phần Thống kê trong frd-reqs.md.</p>'
    else:
        body = '<p class="note">Chưa chạy bước tự kiểm độ phủ (3b). Hãy tự đối chiếu mục lục FRD với phần Thống kê trong frd-reqs.md.</p>'
    H.append(f'<section id="coverage"><h2><span class="n">09</span>Tự kiểm độ phủ FRD</h2>{body}</section>')
    ta_sel = ('<label for="mx-ta" class="count">TA</label><select id="mx-ta"><option value="">Tất cả</option>'
              + "".join(f"<option>{k}</option>" for k in order) + "</select>") if has_ta else ""
    H.append(f'<section id="matrix"><h2><span class="n">10</span>Ma trận {tot} yêu cầu FRD</h2><p class="sub">Yêu cầu có BA "Thiếu" là yêu cầu tài liệu BA không viết, nên cũng không có case QC nào kiểm nó.</p>'
             '<div class="tools"><label for="mx-st" class="count">BA</label><select id="mx-st"><option value="">Tất cả</option>'
             + "".join(f"<option>{k}</option>" for k in order) + "</select>" + ta_sel
             + '<input id="mx-q" type="search" placeholder="Tìm chữ trong FRD, R-xxx, nhóm, BR-xxx, API-xxx, TC-xxx…" aria-label="Tìm trong ma trận"><span class="count" id="mx-count"></span></div>'
             '<div class="tbl scroll"><table><thead><tr><th>R · Nhóm chức năng · Mã yêu cầu</th><th>Mục FRD</th><th>Trích FRD</th><th>BA</th><th>Chênh lệch BA</th>'
             + ("<th>TA</th>" if has_ta else "") + '<th>Case QC</th></tr></thead><tbody id="mx-body"></tbody></table></div></section>')
    H.append(f"<footer>{inline(n.get('footer'))}</footer></main></div>")

    tpl = TPL.read_text(encoding="utf-8")
    js_data = json.dumps(dict(rows=d["rows"], groups=d["groups"], has_ta=has_ta), ensure_ascii=False).replace("</", "<\\/")
    page = tpl.replace("__TITLE__", html.escape(n.get("title", "QC FRD Trace"))).replace("__BODY__", "".join(H)).replace("__DATA__", js_data)
    (out / "report.html").write_text(page, encoding="utf-8")

    # ---------- Markdown ----------
    M = [f"# {n.get('title')}", "", f"**Tính năng:** {n.get('feature')} · **Ngày:** {n.get('date')}", "",
         "**Nguồn:** " + " · ".join(n.get("sources", [])), "", "## Tóm tắt", ""]
    M += [p + "\n" for p in n.get("verdict", [])]
    if has_ta:
        M += ["| Trạng thái | FRD → BA | FRD → TA |", "|---|---|---|"]
        M += [f"| {k} | {fvb.get(k, 0)} ({pct(fvb.get(k, 0), tot)}) | {fvt.get(k, 0)} ({pct(fvt.get(k, 0), tot)}) |" for k in order]
    else:
        M += ["| Trạng thái FRD → BA | Số yêu cầu | Tỉ lệ |", "|---|---|---|"]
        M += [f"| {k} | {fvb.get(k, 0)} | {pct(fvb.get(k, 0), tot)} |" for k in order]
    M += ["", "| Chỉ số | Giá trị |", "|---|---|"] + [f"| {md_cell(t)} | {v} |" for v, t in cards]
    M += ["", "## 1. Dòng thời gian", ""] + [f"- **{t.get('date')}**{' ⚠' if t.get('warn') else ''} — {t.get('text')}" for t in n.get("timeline", [])]
    M += ["", n.get("timeline_note", ""), "", "## 2. Các điểm lệch lớn", "", "| Chủ đề | FRD | Hiện tại | Ảnh hưởng tới test |", "|---|---|---|---|"]
    M += [f"| {md_cell(x.get('topic'))} | {md_cell(x.get('frd'))} | {md_cell(x.get('current'))} | {md_cell(x.get('impact'))} |" for x in n.get("divergences", [])]
    M += ["", "## 3. Câu hỏi cần PO chốt", ""] + [f"{i}. **{x.get('q')}** {x.get('detail', '')}" for i, x in enumerate(n.get("po_questions", []), 1)]
    M += ["", "## 4. Checklist test theo nhóm chức năng", "",
          "Làn: " + " · ".join(f"**{t}** = {h}" for t, _, h in LANES.values()), "",
          "| # | Nhóm chức năng | Làn | FRD → BA / TA (số yêu cầu) | Code (số yêu cầu FRD) | Case QC đại diện | Số yêu cầu FRD |", "|---|---|---|---|---|---|---|"]
    for i, g in enumerate(sorted(d["groups"], key=lambda g: g["lane"]), 1):
        bas = " · ".join(f"{k} {v}" for k, v in g["ba"].items())
        if g.get("ta"):
            bas = "BA " + bas + "<br>TA " + " · ".join(f"{k} {v}" for k, v in g["ta"].items())
        code = g["impl"] + (f" — {g['note']}" if g["note"] else "")
        cases = " ".join(g["rep"]) + (f" (+{g['more']})" if g["more"] else "")
        M.append(f"| {i} | {md_cell(g['name'])} | {LANES[g['lane']][0]} | {bas} | {md_cell(code) or '—'} | {cases or '—'} | {len(g['rs'])} |")
    M += ["", "## 5. Chuẩn bị môi trường & lưu ý", ""]
    for x in n.get("env_notes", []):
        M += [f"- **[{SEV.get(x.get('level'), SEV['med'])[1]}] {x.get('title')}** — {x.get('evidence')}", f"  - Làm: {x.get('action')}"]
    M += ["", "## 6. BA thêm ngoài FRD", ""]
    for x in n.get("extras", []):
        M += [f"**{x.get('title')}**", ""] + [f"- {i}" for i in x.get("items", [])] + [""]
    M += ["## 7. TA so với FRD", ""]
    if has_ta:
        M += ["Ghi chú TA: " + " · ".join(f"{k} {v}" for k, v in st.get("ta_notes", {}).items()) + ". Chi tiết từng yêu cầu: cột TA trong `matrix.md` §A.", ""]
        if ta_flag:
            M += ["**Ghi chú TA trái FRD hoặc tự chốt câu hỏi mở**", "", "| ID | Nội dung | R liên quan | Kết luận | Ảnh hưởng test |", "|---|---|---|---|---|"]
            M += [f"| {x['id']} | {md_cell(x['text'])} | {md_cell(x['rs'])} | {x['res']} | {md_cell(x['impact'])} |" for x in ta_flag]
            M += [""]
        if d.get("ui"):
            M += [f"**ui-contract so với yêu cầu UI của FRD:** {len(ui_bad)} thiếu/lệch trên {len(d['ui'])}", ""]
            if ui_bad:
                M += ["| R | Màn hình / phần tử | Trạng thái | Ghi chú |", "|---|---|---|---|"]
                M += [f"| {x['r']} | {md_cell(x['el'])} | {x['st']} | {md_cell(x['note'])} |" for x in ui_bad]
            M += [""]
    else:
        M += ["Không có tài liệu TA, hoặc bước FRD → TA (P5) chưa chạy.", ""]
    M += ["## 8. Tự kiểm độ phủ FRD", ""]
    if cov.get("ran"):
        M += [f"Agent độc lập tìm thấy {cov['missed']} ý bị sót: đã bổ sung {cov['added']}, loại {cov['rejected']}, "
              f"**còn mở {cov['open']}**. Tách {cov['merged']} yêu cầu gộp nhiều ý. Mục FRD không có yêu cầu nào nhưng có nội dung test: {cov['empty_sections_not_ok']}.", ""]
        if d.get("cov_open"):
            M += ["| Mục FRD | Ý còn mở — kiểm tay với FRD |", "|---|---|"] + [f"| {md_cell(x['sec'])} | {md_cell(x['q'])} |" for x in d["cov_open"]]
        else:
            M += ["Không còn ý nào mở."]
    else:
        M += ["Chưa chạy bước tự kiểm độ phủ (3b). Hãy tự đối chiếu mục lục FRD với phần Thống kê trong `frd-reqs.md`."]
    M += ["", "Danh sách đầy đủ: `ba-extra.csv`, `ta-notes.csv`, `ui-vs-frd.csv`. Redmine so với FRD: `matrix.md` §B. Ma trận đầy đủ: `matrix.md` §A.", "", "---", n.get("footer", "")]
    (out / "report.md").write_text("\n".join(M), encoding="utf-8")

    X = [f"# Ma trận truy vết — {n.get('feature')}", "", f"## A. {tot} yêu cầu FRD", ""]
    if has_ta:
        X += ["| R | Nhóm chức năng | Mã yêu cầu | Mục FRD | Loại | Trích FRD | BA | BA IDs | Chênh lệch BA | TA | TA IDs | Chênh lệch TA | Case QC |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        X += [f"| {r['r']} | {r.get('topic_name', '')} | {r.get('grp', '')} | {md_cell(r['sec'])} | {r['typ']} | {md_cell(r['q'])} | {r['st']} | {r['ba']} | {md_cell(r['diff'])} | "
              f"{r.get('ta_st', '')} | {md_cell(r.get('ta', ''))} | {md_cell(r.get('ta_diff', ''))} | {r['qc']} |" for r in d["rows"]]
    else:
        X += ["| R | Mục FRD | Loại | Trích FRD | Trạng thái | BA IDs | Chênh lệch | Case QC |", "|---|---|---|---|---|---|---|---|"]
        X += [f"| {r['r']} | {md_cell(r['sec'])} | {r['typ']} | {md_cell(r['q'])} | {r['st']} | {r['ba']} | {md_cell(r['diff'])} | {r['qc']} |" for r in d["rows"]]
    if d["rvf"]:
        X += ["", "## B. Redmine so với FRD", "", "| Chủ đề | Redmine nói | FRD nói | Kết luận |", "|---|---|---|---|"]
        X += [f"| {md_cell(x['topic'])} | {md_cell(x['rm'])} | {md_cell(x['frd'])} | {x['res']} |" for x in d["rvf"]]
    if d["oq"]:
        X += ["", "## C. Câu hỏi mở / TBD trong FRD", ""] + ["| " + " | ".join(md_cell(c) for c in o) + " |" for o in d["oq"]]
    (out / "matrix.md").write_text("\n".join(X), encoding="utf-8")
    print(f"OK report.html ({len(page) // 1024} KB) · report.md · matrix.md in {out}")


if __name__ == "__main__":
    main()

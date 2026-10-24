# Công thức viết prompt để tạo skill chuẩn chỉnh

Tài liệu này đúc kết từ các skill đang chạy tốt trong repo (`test-case-generator`, `compare-campaign-config`, `qc-frd-trace`, `tong-hop-spec-artifact`), và kinh nghiệm thực tế xây dựng pipeline QA (`requirement-analyzer` → `risk-scout-analyzer` → `bug-hunter` → `test-case-generator`).

---

## Đặc điểm của skill chuẩn chỉnh trong repo này

| Yếu tố | Bằng chứng cụ thể trong file |
|---|---|
| **Có script làm nguồn chân lý duy nhất** | `test-case-generator` nói thẳng: *"KHÔNG tự đếm % coverage bằng tay"* — dùng `scripts/compute_coverage.py` để tính coverage + verdict, và `scripts/generate_testcase_excel.py` để xuất Excel (*"không tự viết script export mới"*). `qc-frd-trace` có `scripts/verify_quotes.py`, `scripts/check_coverage.py` — không để AI tự làm lại logic mỗi lần, tránh sai lệch giữa các lần chạy |
| **Có template / ví dụ thật, không chỉ mô tả suông** | `tong-hop-spec-artifact/assets/` có `template.html` + `example-login-frd.html`; `test-case-generator/references/sample-test-cases.md`; các skill campaign có `examples/` (dữ liệu giả minh họa định dạng input) — AI làm theo mẫu thật thay vì tự tưởng tượng |
| **Danh sách "không được làm"** | Mục "Bạn KHÔNG làm" của `test-case-generator` (không execute test, không tự định nghĩa acceptance criteria...); mục "Ràng buộc chung" của `compare-campaign-config` |
| **Ghi lại bài học/lỗi hay gặp** | `test-case-generator/references/common-mistakes.md` dùng ở bước self-check — đúc kết từ những lần đã từng sai |
| **Quy trình theo thứ tự, có vòng lặp sửa** | `test-case-generator`: *"THỰC HIỆN ĐÚNG THỨ TỰ — KHÔNG BỎ BƯỚC"*; script báo FAIL coverage → quay lại Step 5, sửa đúng chỗ rồi chạy lại |
| **Có điểm dừng người dùng review** | `compare-campaign-config` / `compare-phan-bo` / `viet-test-case-campaign` có **Bước 0 — xác nhận bộ file**: thiếu/thừa file hoặc tên campaign lệch nhau → dừng lại hỏi, tránh so sánh sai cặp file |
| **Reference tách riêng, load có điều kiện** | `test-case-generator` có bảng "Reference files (load có điều kiện — KHÔNG load hết cùng lúc)": mỗi step chỉ đọc đúng file `references/*.md` cần thiết — tiết kiệm token |
| **Nối tiếp skill khác bằng mã ID có cấu trúc** | Pipeline QA truyền mã `REQ-xxx` / `R-xxx` / `BUG-xxx` / `ASM-xxx`; `test-case-generator` dùng lại nguyên mã, *"không tự đặt lại mã, không tự suy diễn lại priority/category"*. `qc-trace-excel` nhận đúng thư mục report của `qc-frd-trace` |

---

## Công thức prompt để tạo skill mới đạt chất lượng tương tự

Khi nhờ AI viết 1 skill mới, hãy trả lời càng nhiều câu sau càng tốt trong yêu cầu:

1. **Input/Output cụ thể** — input là gì (định dạng, ví dụ thật), output là file gì, tên/đường dẫn theo quy tắc nào
2. **Có tính toán/sinh code nào không?** → nếu có (đếm, tính %, sinh JSON/Excel...) thì nói rõ "hãy viết 1 script làm việc này, đừng để AI tự tính tay mỗi lần" — đây là điểm khác biệt lớn nhất giữa skill "ổn" và skill "chuẩn chỉnh"
3. **Quy tắc bất biến (core principles)** — những điều luôn phải đúng dù input là gì (vd "mỗi dòng input = đúng 1 output, không được gộp/bỏ")
4. **Ví dụ cụ thể (worked example)** — 1 input mẫu → output mẫu đầy đủ, không chỉ mô tả bằng lời
5. **Danh sách cấm** — liệt kê những lỗi/thói quen xấu đã từng thấy AI mắc phải khi làm việc tương tự
6. **Có cần điểm dừng người dùng duyệt không?** — đặc biệt nếu bước sau tốn công/khó revert
7. **Có phụ thuộc/nối tiếp skill khác không?** — nếu có, đặt tên skill khác + mô tả input/output khớp nhau (như `test-case-generator` biết chính xác mã `REQ`/`R`/`BUG`/`ASM` mà các bước trước sinh ra, hay `qc-trace-excel` đọc đúng thư mục report của `qc-frd-trace`)
8. **Reference nào nên tách riêng?** — quy tắc chi tiết/schema dài nên để trong `references/*.md`, không nhồi hết vào 1 file, để tránh tốn token khi không cần
9. **Cách kích hoạt** — tự kích hoạt khi người dùng mô tả bằng lời (cần `description` có câu trigger rõ ràng) hay chỉ chạy khi gọi lệnh trực tiếp (`disable-model-invocation: true`, như `qc-frd-trace`)

---

## Mẫu prompt có thể tái dùng

```
Tạo cho tôi 1 skill tên "<ten-skill>":
- Input: <mô tả + ví dụ thật>
- Output: <file gì, đặt ở đâu, tên file theo format nào>
- Có phần nào cần tính toán/sinh file máy đọc được (JSON/Excel/code)?
  → viết hẳn 1 script làm việc đó, SKILL.md chỉ hướng dẫn cách gọi script, không tự làm tay.
- Quy tắc luôn đúng: <liệt kê>
- Không được làm: <liệt kê những lỗi bạn từng gặp>
- Có cần dừng lại chờ tôi duyệt ở bước nào không: <có/không, ở đâu>
- Nối tiếp/nhận input từ skill nào khác: <tên skill, nếu có>
- Kích hoạt: <tự kích hoạt khi nói "...", hoặc chỉ khi gọi /<ten-skill>>
```

---

## Checklist sau khi tạo skill

- [ ] Skill nằm ở `.claude/skills/<ten-skill>/SKILL.md`, frontmatter có `name` + `description` (description nêu rõ dùng khi nào, câu trigger, và phân biệt với skill gần giống)
- [ ] Kèm thêm nếu cần: `README.md` (hướng dẫn cho người dùng), `references/`, `scripts/`, `assets/`, `examples/` (chỉ dữ liệu giả) — không để thư mục rỗng
- [ ] Skill chỉ chạy khi gọi lệnh trực tiếp → thêm `disable-model-invocation: true` (+ `argument-hint` nếu có tham số)
- [ ] Skill chạy thẳng không hỏi xác nhận → thêm vào mục ngoại lệ trong [AGENTS.md](../AGENTS.md)
- [ ] Skill đọc link nội bộ (Redmine/BookStack/GitLab/SharePoint) → dùng config trong `connect-key/`, không hard-code token trong skill
- [ ] Cập nhật [README.md](../README.md): cây thư mục + bảng danh sách skill (+ bảng "Chọn skill nào?" nếu dễ nhầm với skill khác)
- [ ] Nếu là 1 bước của pipeline QA → cập nhật [qa-pipeline-guide.md](qa-pipeline-guide.md)

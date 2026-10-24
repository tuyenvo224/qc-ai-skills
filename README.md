# QC AI Skills

Bộ skill Claude Code dành cho team QC: phân tích requirement, tìm rủi ro/bug tiềm ẩn, thiết kế test case, truy vết FRD, đối chiếu campaign và log bug.

**Cách gọi skill:** `/<tên-skill> <input>` (input là đường dẫn file, link BookStack/Redmine/GitLab/SharePoint, hoặc nội dung dán trực tiếp). Phần lớn skill cũng tự kích hoạt khi bạn mô tả yêu cầu bằng lời (vd: "phân tích rủi ro giúp tôi", "log bug").

---

## Cấu trúc thư mục

```
qc-ai-skills/
├── .claude/skills/                  # Mỗi skill 1 thư mục: SKILL.md (+ README.md, references/, scripts/, assets/, examples/)
│   ├── requirement-analyzer/        # Phân tích requirement / spec
│   ├── dat-cau-hoi/
│   ├── requirement-to-mindmap/
│   ├── tong-quan-feature/
│   ├── tong-hop-spec-artifact/
│   ├── tong-hop-ta-db-artifact/
│   ├── risk-scout-analyzer/         # Rủi ro & bug tiềm ẩn
│   ├── bug-hunter/
│   ├── test-case-generator/         # Thiết kế test case
│   ├── viet-test-case/
│   ├── qc-frd-trace/                # Truy vết FRD
│   ├── qc-trace-excel/
│   ├── compare-campaign-config/     # Campaign
│   ├── compare-phan-bo/
│   ├── viet-test-case-campaign/
│   ├── log-bug-redmine/             # Bug
│   └── markdown-to-excel/           # Tiện ích
├── hdsd-skills/                     # Hướng dẫn sử dụng
│   ├── qa-pipeline-guide.md         # Pipeline QA: input/output/lệnh chạy từng bước
│   └── HOW_TO_CREATE_SKILLS.md      # Cách tạo skill mới
├── campaign-qc/                     # (tạo khi chạy) Thư mục chạy của nhóm skill Campaign — mỗi lần chạy 1 thư mục con input/ + output/
├── AGENTS.md                        # Quy tắc làm việc cho agent
├── CLAUDE.md                        # Nhúng AGENTS.md (@AGENTS.md) để Claude Code nạp quy tắc
└── README.md
```

> ⚠️ `campaign-qc/` chưa có sẵn trong repo, tạo khi chạy skill Campaign (xem [Cách chạy nhóm skill Campaign](#cách-chạy-nhóm-skill-campaign)). Thư mục này chứa file brief/config/export và báo cáo thật (có thể có SĐT, email, secret) — không commit.

---

## Danh sách skill

### 🔍 Phân tích requirement / spec

| Skill | Dùng khi nào | Input | Output |
|---|---|---|---|
| `requirement-analyzer` | Làm rõ requirement thô trước khi thiết kế test (bước 1 pipeline QA) | User story / BRD / FRD / link / ảnh-Figma | File Markdown phân tích có mã `REQ` / `UNC` / `QH-QM-QL` / `ASM` |
| `dat-cau-hoi` | Chuẩn bị danh sách câu hỏi mang vào buổi review với BA/PO | Spec / ticket / ảnh | Danh sách câu hỏi có ưu tiên + Top 3 |
| `requirement-to-mindmap` | Chỉ khi cần **mindmap** test coverage | Requirement | Mindmap Markdown (tương thích markmap) |
| `tong-quan-feature` | Cần bức tranh toàn cảnh cả **sản phẩm/hệ thống** | Tài liệu tổng quan / PRD lớn | Product Architecture Map: Sản phẩm → Epic → Feature |
| `tong-hop-spec-artifact` | Tổng hợp spec nghiệp vụ PO/BA thành trang tra cứu để chia sẻ | Link FRD/PRD/user story (+ ảnh) | Link artifact HTML: user flow, business rule, decision table, truy vết, câu hỏi `Q-xx` |
| `tong-hop-ta-db-artifact` | Hiểu TA / technical design: flow ghi vào table nào của DB | Link thư mục/file TA trên GitLab | Link artifact HTML: bước → table/cột, SQL gợi ý, trạng thái |

### ⚠️ Rủi ro & bug tiềm ẩn

| Skill | Dùng khi nào | Input | Output |
|---|---|---|---|
| `risk-scout-analyzer` | Xác định vùng cần test kỹ trước (bước 2 pipeline QA) | Feature / thay đổi / output `requirement-analyzer` | File Markdown Top Risk Areas `R-xxx` (P1–P3) |
| `bug-hunter` | Tìm bug high-impact: edge case, race condition, bad user (bước 3 pipeline QA) | Flow/feature + `R-xxx` | File Markdown Bug Hypotheses `BUG-xxx` (Critical/High/Medium) |

### 🧪 Thiết kế test case

| Skill | Dùng khi nào | Input | Output |
|---|---|---|---|
| `test-case-generator` | Bộ test case chuyên sâu, có kỹ thuật EP/BVA/DT/ST..., coverage tính bằng script (bước 4 pipeline QA) | Spec hoặc output 3 bước trước (`REQ` / `R` / `BUG` / `ASM`) | File Excel test case + Summary, Coverage, Traceability |
| `viet-test-case` | Bộ test case gọn nhẹ, dùng ngay | Requirement / user story ngắn | File Excel theo template "KỊCH BẢN KIỂM THỬ" của công ty |

> Cập nhật test case cho **campaign** theo brief: xem `viet-test-case-campaign` ở nhóm [📋 Campaign](#-campaign).

### 🔗 Truy vết (traceability)

| Skill | Dùng khi nào | Input | Output |
|---|---|---|---|
| `qc-frd-trace` | Kiểm tra doc dev, test case, code đã phủ FRD chưa; tìm gap/thừa | `<link BookStack FRD> --redmine <id,id> [--feature] [--code] [--out]` | `report.md`, `matrix.md`, CSV, link artifact |
| `qc-trace-excel` | Sinh file Excel test case từ kết quả `qc-frd-trace` | Thư mục report của `qc-frd-trace` | File Excel theo `Template_TCs.xlsx` (Ghi chú, TCs, Ma trận FRD, Test flow, Tóm tắt) |

> Hai skill này chỉ chạy khi gọi lệnh trực tiếp (`/qc-frd-trace`, `/qc-trace-excel`), không tự kích hoạt.

### 📋 Campaign

| Skill | Dùng khi nào | Input (bỏ vào `input/`) | Output (ghi vào `output/`) |
|---|---|---|---|
| `compare-campaign-config` | Audit config campaign trước khi lên PROD | Đúng 1 file brief BA (.xlsx) + đúng 1 file config (.json) | `report_<slug>_<yyyy-mm-dd>.md` |
| `compare-phan-bo` | Audit dữ liệu phân bổ quà (tên quà, số lượng, ngày giờ ra giải) | Đúng 1 file brief phân bổ (.xlsx, tên có "brief") + 1 hoặc nhiều file export phân bổ (.xlsx, theo `region_id`/`supermarket_id`) | `report_phan-bo_<slug>_<yyyy-mm-dd>.md` |
| `viet-test-case-campaign` | Cập nhật test case campaign theo brief mới (giữ format, xoá kết quả P/F cũ) | Đúng 1 file brief (.xlsx, tên có "brief") + đúng 1 file test case (.xlsx) + tuỳ chọn 1 file template (tên có "template"; không có thì dùng `assets/Template_TCs.xlsx`) | `<tên file test case gốc>_updated_<yyyy-mm-dd>.xlsx` + `report_test-case_<yyyy-mm-dd>.md` |

#### Cách chạy nhóm skill Campaign

Mỗi lần chạy tạo 1 thư mục riêng trong `campaign-qc/` ở thư mục gốc project:

```
campaign-qc/
├── 2026-10-03_mini-tet-2/              ← compare-campaign-config
│   ├── input/    (brief .xlsx + config .json)
│   └── output/
├── 2026-10-03_mini-tet-2_phan-bo/      ← compare-phan-bo
│   ├── input/    (brief .xlsx + các file export .xlsx)
│   └── output/
└── 2026-10-03_mini-tet-2_test-case/    ← viet-test-case-campaign
    ├── input/    (brief .xlsx + test case .xlsx [+ template .xlsx])
    └── output/
```

Gọi skill với đường dẫn thư mục chạy (khuyến nghị) hoặc danh sách file:

```
/compare-campaign-config campaign-qc/2026-10-03_mini-tet-2
/compare-phan-bo campaign-qc/2026-10-03_mini-tet-2_phan-bo
/viet-test-case-campaign campaign-qc/2026-10-03_mini-tet-2_test-case
```

Lưu ý:

- **Bước 0 — xác nhận bộ file:** skill in bảng file (đường dẫn, ngày sửa, tên campaign...) trước khi làm. Thiếu/thừa/không phân loại được file → skill dừng lại hỏi; tên campaign giữa các file lệch nhau → cảnh báo "Có thể truyền sai cặp file" và chờ bạn xác nhận.
- Skill **không ghi đè** file trong `input/`; mọi kết quả nằm trong `output/`. Trên chat chỉ hiện tóm tắt số điểm Khớp / Không khớp / Thiếu / Cần xác nhận kèm đường dẫn báo cáo.
- File trong `examples/` của skill là **dữ liệu giả**, chỉ minh họa định dạng — không dùng làm input.
- Chi tiết từng skill: [compare-campaign-config](.claude/skills/compare-campaign-config/README.md) · [compare-phan-bo](.claude/skills/compare-phan-bo/README.md) · [viet-test-case-campaign](.claude/skills/viet-test-case-campaign/README.md)

### 🐞 Bug

| Skill | Dùng khi nào | Input | Output |
|---|---|---|---|
| `log-bug-redmine` | Viết bug report để copy lên Redmine | Mô tả lỗi (+ link spec, ảnh, môi trường) | Tiêu đề + nội dung theo template 7 mục (2 codeblock) |

### 🛠️ Tiện ích

| Skill | Dùng khi nào | Input | Output |
|---|---|---|---|
| `markdown-to-excel` | Chuyển bảng Markdown sang Excel | File `.md` | File `.xlsx` |

---

## Pipeline QA

```
requirement-analyzer → risk-scout-analyzer → bug-hunter → test-case-generator (hoặc viet-test-case) → Test Execution
```

Output bước trước là input bước sau. Riêng `test-case-generator` cần gộp output của cả 3 bước trước (`REQ` / `ASM` + `R` + `BUG`).

Chi tiết input/output/lệnh chạy từng bước: [hdsd-skills/qa-pipeline-guide.md](hdsd-skills/qa-pipeline-guide.md)

---

## Chọn skill nào?

| Nếu bạn cần... | Dùng | Thay vì |
|---|---|---|
| Phân tích đầy đủ, có mã ID truy vết để làm input cho pipeline | `requirement-analyzer` | `dat-cau-hoi` |
| Chỉ danh sách câu hỏi cho BA/PO | `dat-cau-hoi` | `requirement-analyzer` |
| Sơ đồ tư duy test coverage | `requirement-to-mindmap` | `requirement-analyzer` |
| Toàn cảnh cả sản phẩm (không phải 1 feature) | `tong-quan-feature` | `requirement-analyzer` |
| Trang tổng hợp spec **nghiệp vụ** (FRD/PRD) | `tong-hop-spec-artifact` | `tong-hop-ta-db-artifact` |
| Trang tổng hợp **TA / DB** (table, cột, SQL) | `tong-hop-ta-db-artifact` | `tong-hop-spec-artifact` |
| Test case chuyên sâu, có coverage định lượng | `test-case-generator` | `viet-test-case` |
| Test case nhanh, đúng template công ty | `viet-test-case` | `test-case-generator` |

---

## Skill chạy thẳng, không hỏi xác nhận

Theo [AGENTS.md](AGENTS.md), mặc định agent trình bày kế hoạch và chờ xác nhận trước khi làm. Ngoại lệ:

- `tong-hop-spec-artifact` — từ link spec tới link artifact
- `tong-hop-ta-db-artifact` — từ link TA tới link artifact
- `log-bug-redmine` — từ mô tả lỗi tới bug report (không tự tạo issue trên Redmine)

Cần quy tắc riêng cho máy mình (vd: cách đọc spec từ hệ thống nội bộ, token...)? Tạo file `CLAUDE.local.md` ở thư mục gốc — Claude Code tự nạp file này và nó đã nằm trong `.gitignore`. Các skill đọc link nội bộ (`tong-hop-spec-artifact`, `tong-hop-ta-db-artifact`) cần thư mục key `connect-key/` của chính bạn — cách chuẩn bị xem [tong-hop-spec-artifact/README.md](.claude/skills/tong-hop-spec-artifact/README.md).

---

## Tạo skill mới

Xem [hdsd-skills/HOW_TO_CREATE_SKILLS.md](hdsd-skills/HOW_TO_CREATE_SKILLS.md). Mỗi skill đặt trong `.claude/skills/<tên-skill>/` với file `SKILL.md`. Frontmatter gồm `name`, `description` và `metadata` (`author`, `version` — vd `author: tuyenvo224`, `version: "1.0"`; tăng version khi sửa skill). Có thể kèm:

- `README.md` — hướng dẫn sử dụng cho người dùng
- `references/` — tài liệu tham khảo cho agent (vd: mô tả định dạng input)
- `scripts/` — script xử lý cố định
- `assets/` — template/file dùng để sinh output
- `examples/` — dữ liệu giả minh họa định dạng input (không dùng làm input thật)

Sau khi thêm skill, nhớ cập nhật README này (cây thư mục + bảng danh sách skill).

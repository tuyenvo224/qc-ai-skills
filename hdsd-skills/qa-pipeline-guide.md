# Hướng dẫn chạy Pipeline QA (4 skill)

Pipeline đầy đủ:

```
requirement-analyzer → risk-scout-analyzer → bug-hunter → test-case-generator (hoặc viet-test-case) → Test Execution
```

Nguyên tắc chung: **output của bước N là nguồn input chính cho bước N+1**, nhưng mỗi bước sau chỉ cần trích **một phần cụ thể** (mã ID + priority/category) từ output trước, không phải chép nguyên toàn văn. Một số bước cần gộp output của **nhiều hơn 1** bước trước đó, không chỉ bước ngay liền kề — xem chi tiết từng bước dưới đây.

---

## Bước 1 — `requirement-analyzer`

| | |
|---|---|
| **Input** | File spec thô: user story / BRD / FRD / mô tả tự do / link Bookstack / hình ảnh-Figma-screenshot |
| **Lệnh chạy** | `/requirement-analyzer <đường-dẫn-hoặc-link-spec>` |
| **Output** | 1 file Markdown, lưu tại `requirement-analysis/yyyy-mm-dd_hh-mm-ss_ten-feature.md` |
| **Nội dung output cần cho bước sau** | Requirement Breakdown (`REQ-xxx` + Priority), User Flow/Logic Flow/Data Flow Analysis, Unclear Points (`UNC-xxx`), Clarification Questions (`QH/QM/QL-xxx`), Assumptions (`ASM-xxx` + Category + Impact) |
| **Trạng thái cần đạt trước khi qua bước 2** | `Clarified` hoặc `Ready for Testing` (nếu còn `Pending Clarification` — tức còn `QH-xxx` High Priority chưa trả lời — nên hỏi PO/BA trước, tuy không bắt buộc phải chặn) |

---

## Bước 2 — `risk-scout-analyzer`

| | |
|---|---|
| **Input** | **Output file của Bước 1** (file `requirement-analysis/...md`) |
| **Lệnh chạy** | `/risk-scout-analyzer <đường-dẫn-file-requirement-analysis>` |
| **Output** | 1 file Markdown, lưu tại `risk-analysis/yyyy-mm-dd_hh-mm-ss_ten-feature.md` |
| **Nội dung output cần cho bước sau** | Top Risk Areas (`R-xxx` + Priority P1-P3 + Category `security`/`financial`/`data_integrity`/`other`) + Risk Reasoning |
| **Không cần mang sang bước sau** | "Test Focus Suggestions", "Light/Skip Testing" (chỉ để tham khảo nội bộ) |

---

## Bước 3 — `bug-hunter`

| | |
|---|---|
| **Input** | **Output file của Bước 1** (flow/feature description) **+** **Output file của Bước 2** (`R-xxx` để biết đào sâu vùng nào trước) |
| **Lệnh chạy** | `/bug-hunter <đường-dẫn-file-requirement-analysis> <đường-dẫn-file-risk-analysis>` |
| **Output** | 1 file Markdown, lưu tại `bug-hunter-analysis/yyyy-mm-dd_hh-mm-ss_ten-feature.md` |
| **Nội dung output cần cho bước sau** | Bug Hypotheses mức **Critical/High** (`BUG-xxx`) — Critical→P1, High→P2, category cố định `bug_hypothesis` |
| **Không cần mang sang bước sau** | Bug Hypotheses mức Medium (không bắt buộc phải viết test case exhaustive), "Core Flow Summary", "Focus Summary" |

---

## Bước 4 — `test-case-generator` (hoặc `viet-test-case` cho bản gọn nhẹ)

| | |
|---|---|
| **Input** | **Gộp cả 3 output trước**: Bước 1 (`REQ-xxx`, `ASM-xxx`) + Bước 2 (`R-xxx`) + Bước 3 (`BUG-xxx`) — **không được bỏ qua Bước 2**, vì `R-xxx` và `BUG-xxx` là 2 tập risk khác nhau, không tập nào bao trùm tập kia |
| **Lệnh chạy** | `/test-case-generator <file-requirement-analysis> <file-risk-analysis> <file-bug-hunter-analysis>` |
| **Output** | 1 file Excel `.xlsx`, lưu tại `test-case-designed/{ProjectName}_{FeatureName}_TestCases.xlsx` (kèm Coverage Summary, Traceability Matrix, Assumptions List trong tin nhắn trả lời) |
| **Mapping JSON nội bộ (cho `compute_coverage.py`)** | `requirements: [{"id": "REQ-001", "priority": "P1"}, ...]`<br>`assumptions: [{"id": "ASM-001", "category": "...", "impact": "..."}, ...]`<br>`risks: [{"id": "R-001", "priority": "P1", "category": "security"}, {"id": "BUG-001", "priority": "P1", "category": "bug_hypothesis"}, ...]` — `R-xxx` và `BUG-xxx` cùng nằm trong `risks`, không dedupe |

> Nếu chỉ cần bảng test case nhanh, không cần coverage threshold/Excel chuẩn công ty → dùng `viet-test-case` thay `test-case-generator` ở bước này (input tương tự nhưng không bắt buộc đủ 3 file, có thể chạy trực tiếp từ spec thô).

---

## Bước 5 — Test Execution

Nằm ngoài phạm vi 4 skill trên — là bước thực thi test case đã sinh ra ở Bước 4 (thủ công hoặc automation), không thuộc skill nào trong pipeline này.

---

## Lưu ý chung

- Mỗi bước **có thể chạy độc lập** với spec thô nếu muốn bỏ qua bước trước (không bắt buộc tuần tự tuyệt đối), nhưng bỏ bước nào thì mất luôn phần mã ID + input tương ứng của bước đó ở các bước sau.
- Tất cả các mã (`REQ`, `UNC`, `QH/QM/QL`, `ASM`, `R`, `BUG`) phải giữ nguyên, không tự đổi số hoặc đổi taxonomy Category/Impact khi bàn giao qua bước sau.
- Thư mục output mặc định của từng skill (nếu người dùng không chỉ định nơi lưu khác):
  - `requirement-analysis/`
  - `risk-analysis/`
  - `bug-hunter-analysis/`
  - `test-case-designed/`

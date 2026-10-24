# Spec Analysis Rules

Read this when analyzing the input spec (Step 1 of `SKILL.md`'s workflow) — multi-perspective feature extraction (Admin/CMS vs Frontend vs Transaction), how to read each document type, extraction rules per document type, handling unclear specs, and priority calculation.

---

## 3. Spec Analysis Rules

### 3.0 Multi-Perspective Feature Extraction — Bản đồ kết nối

**Mục đích:** Kết nối tường minh giữa 3 câu hỏi ở Step 1 → loại tài liệu cần đọc (3.1) → quy tắc extract (3.2) → group cần tạo trong Feature Analysis Table (Step 2).

**[BẮT BUỘC] Sau khi trả lời 3 câu hỏi ở Step 1, tra bảng này để biết làm gì tiếp theo:**

| Câu hỏi Step 1 | Nếu "Có" → Loại tài liệu (Section 3.1) | Áp dụng rules nào (Section 3.2) | Tạo group với Perspective |
|----------------|----------------------------------------|----------------------------------|---------------------------|
| ❓ **"Admin/CMS side có gì?"** | Business Spec, Technical Spec, DB Spec, UI/UX Design | "Từ Business Rules" + "Từ Technical Spec" + "Từ DB Spec" + "Từ UI/UX Design" | `Admin/CMS` |
| ❓ **"Frontend/User-facing side có gì?"** | **Frontend/User-facing Spec** | **"Từ Frontend/User-facing Spec"** | `Frontend` |
| ❓ **"Transaction/Exchange flow có gì?"** | **Transaction/Exchange Flow Spec** | **"Từ Transaction/Exchange Flow Spec"** | `Transaction` |

**Ví dụ áp dụng — Tính năng "Discount Program":**

```
Câu hỏi 1: Admin/CMS side có gì?
  → Có: Form tạo/sửa/xóa chương trình, danh sách, filter, import file
  → Đọc: Business Spec + UI/UX Design
  → Rules: "Từ Business Rules" + "Từ UI/UX Design"
  → Tạo groups: "CMS - Danh sách Discount", "CMS - Tạo chương trình", "CMS - Import"

Câu hỏi 2: Frontend/User-facing side có gì?
  → Có: Hiển thị/ẩn section discount, số lượng còn lại, thông báo lỗi cho user
  → Đọc: Frontend/User-facing Spec
  → Rules: "Từ Frontend/User-facing Spec" (show/hide, notification, disabled state)
  → Tạo group: "Frontend - Hiển thị Discount" (Perspective=Frontend)

Câu hỏi 3: Transaction/Exchange flow có gì?
  → Có: User đổi điểm, validate limit/balance, trừ điểm ưu đãi
  → Đọc: Transaction/Exchange Flow Spec
  → Rules: "Từ Transaction/Exchange Flow Spec" (limit, point deduction, rollback)
  → Tạo group: "Transaction - Đổi điểm Discount" (Perspective=Transaction)
```

> **Lưu ý:** Nếu bỏ qua câu hỏi 2 hoặc 3 → bỏ sót toàn bộ nhóm TC Frontend và Transaction → phải viết lại 2 lần. Đây là root cause của lỗi "viết TC 2 vòng".

### 3.1 Cách đọc từng loại tài liệu

| Loại tài liệu | Cần extract | Test cases tạo từ đó |
|----------------|-------------|----------------------|
| **Business Spec** | Rules, conditions, formulas, workflows, eligibility criteria | Business logic TC, calculation TC, workflow TC |
| **Technical Spec** | API endpoints, request/response format, error codes, status codes | API positive/negative TC, error code TC |
| **DB Spec** | Tables, columns, data types, FK relationships, constraints, indexes | Data integrity TC, constraint TC, relationship TC |
| **UI/UX Design** | Screens, fields, buttons, validations, navigation flow, error messages | UI basic TC, validation TC, flow TC |
| **Frontend/User-facing Spec** | Điều kiện hiển thị/ẩn (show/hide), thông báo trạng thái, timer/date-based display, real-time update, disabled states | Display condition TC, visibility TC, user notification TC, state-based UI TC |
| **Transaction/Exchange Flow Spec** | Điều kiện đổi điểm/thanh toán, thứ tự validation, trừ số dư, rollback khi fail, giới hạn per-user/per-day | Point deduction TC, validation order TC, limit enforcement TC, rollback TC |
| **Flowchart** | All paths, decision points (Yes/No), start/end nodes | 1 TC per unique path, decision point TC |
| **Sequence Diagram** | Messages between components, alt/opt blocks, error flows | 1 TC per message flow, integration TC |
| **State Diagram** | All states, valid transitions, invalid transitions, terminal states | State transition TC (valid + invalid) |
| **ERD** | Entities, relationships (1:1, 1:N, N:N), constraints | FK TC, cascade TC, unique constraint TC |

### 3.2 Quy tắc phân tích

**Từ Business Rules:**
- Mỗi `IF / THEN / ELSE` → ít nhất **2 test cases** (condition TRUE + FALSE)
- Mỗi business rule với ≥2 conditions → tạo **Decision Table** test tất cả tổ hợp
- Mỗi formula/calculation → test với normal + boundary + edge values
- Mỗi eligibility criteria → test đủ điều kiện + không đủ từng điều kiện

**Từ Technical Spec:**
- Mỗi API endpoint → ít nhất **1 positive + 1 negative** test case
- Mỗi error code trong spec → ít nhất **1 test case** trigger chính xác error đó
- Mỗi required field → test missing, null, empty string (3 cases riêng biệt)
- Mỗi enum field → test mỗi giá trị valid + 1 giá trị invalid

**Từ DB Spec:**
- Mỗi unique constraint → test duplicate prevention
- Mỗi FK relationship → test referential integrity (create, update, delete)
- Mỗi NOT NULL constraint → test null value rejection
- Mỗi CASCADE rule → test cascade behavior

**Từ UI/UX Design:**
- Mỗi screen → basic layout test
- Mỗi input field → validation test (format, required, length)
- Mỗi button/action → function test
- Mỗi navigation path → flow test

**Từ Diagrams:**
- Flowchart: test **MỌI** path (không chỉ happy path)
- State diagram: test **MỌI** valid transition + representative invalid transitions
- Sequence diagram: test main flow + alt blocks + error flows

**Từ Frontend/User-facing Spec:**
- Mỗi điều kiện **show/hide** (theo thời gian, trạng thái, số lượng) → ít nhất **3 test cases** (đúng điều kiện hiện + không đúng ẩn + ranh giới chuyển đổi)
- Mỗi **thông báo lỗi trên UI** → 1 TC trigger chính xác thông báo đó với exact text
- Mỗi trạng thái **disabled/enabled** của button → 1 TC verify điều kiện + 1 TC verify behavior
- Mỗi **real-time update** (số lượng còn lại, countdown) → 1 TC verify update sau mỗi action thành công
- Mỗi **navigation** (nhấn button → màn khác) → 1 TC verify redirect đúng target với đúng data

**Từ Transaction/Exchange Flow Spec:**
- Mỗi **validation rule** trong flow → ít nhất **2 TC** (pass validation + fail validation với exact error)
- Mỗi **limit rule** (per-day, per-user, per-program) → 3 TC: dưới giới hạn, đúng giới hạn, vượt giới hạn
- Mỗi **point deduction rule** → 1 TC verify trừ điểm đúng giá trị + 1 TC verify báo lỗi khi không đủ điểm
- Mỗi flow có **thứ tự validation** → 1 TC verify validation được kiểm tra đúng thứ tự (fail ở bước 1 → không qua bước 2)
- Mỗi **rollback scenario** (fail sau khi đã trừ số dư) → 1 TC verify hoàn trả đúng

**Từ Non-functional Requirements:**
- Nếu spec có yêu cầu **performance** (response time, throughput) → tạo TC basic: `[CL] Verify API response time under {X}ms for normal request`
- Nếu spec có yêu cầu **load/stress** (concurrent users, TPS) → ghi nhận và flag cho QA Lead (nằm ngoài scope Test Case Generator, cần tool riêng)
- Nếu spec có yêu cầu **availability/SLA** → ghi nhận vào Assumptions list

### 3.3 Khi spec không rõ ràng

**Riêng với message/label/copy hiển thị trên UI (validation message, error message, placeholder...):** đây là nội dung PHẢI lấy nguyên văn từ spec gốc (mockup, Figma annotation, bảng message trong spec, copy deck) — không phải thứ được phép "diễn giải hợp lý" như các trường hợp thiếu logic/rule khác. Trước khi đánh dấu `[ASSUMPTION]` cho 1 message, phải tìm kỹ trong TOÀN BỘ spec gốc (kể cả link mockup/Figma đính kèm) xem message đó đã được định nghĩa chưa — chỉ khi chắc chắn spec không có mới được assume. Nếu chỉ có output từ `requirement-analyzer`/`risk-scout-analyzer`/`bug-hunter` mà không có spec gốc, xem "Input từ pipeline QA" trong `SKILL.md` — không tự generate hàng loạt `[ASSUMPTION]` cho message chỉ vì thiếu spec gốc trong tay, phải xin lại spec trước.

**Quy trình xử lý (cho các trường hợp thực sự thiếu thông tin trong spec):**

1. **Ghi nhận** vào danh sách ASSUMPTIONS
2. **Viết TC** theo logic phổ biến/hợp lý nhất
3. **Đánh dấu** `[ASSUMPTION]` trong Test Objective
4. **Liệt kê** tất cả assumptions ở cuối document
5. **Ghi note:** "Cần xác nhận với BA/PO trước khi execute"

**Format:**
```
ASSUMPTIONS LIST:
1. [ASSUMPTION] Spec không nêu rõ max length của field "name" → Giả định max = 255
2. [ASSUMPTION] Spec không nêu rõ behavior khi duplicate → Giả định trả error 409
3. [ASSUMPTION] Spec thiếu error code cho trường hợp X → Giả định HTTP 400
```

### 3.4 Cách tính Priority

| Priority | Tiêu chí | Ví dụ |
|----------|----------|-------|
| **P1 - Critical** | Liên quan tiền, bảo mật, data integrity, core business flow, có risk cao | Payment, authentication, order creation, COD |
| **P2 - High** | Chức năng chính, business logic phức tạp, ảnh hưởng nhiều user | User management, search, reports, notifications |
| **P3 - Medium** | Chức năng phụ, edge cases, ít user sử dụng | Settings, preferences, export |
| **P4 - Low** | UI cosmetic, nice-to-have, hiếm khi sử dụng | Tooltips, minor formatting, about page |

---


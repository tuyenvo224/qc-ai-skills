# Writing Format Rules

Read this when writing the actual test case rows (Step 5 of `SKILL.md`'s workflow) — the 4-column format, Test Objective/Steps/Expected Result conventions, test data rules, error-message rules, DB verification rules, and abbreviated security/concurrency rules.

---

## 7. Writing Format

### 7.0 Ngôn ngữ viết test case (BẮT BUỘC)

**Toàn bộ nội dung Test Objective / Test Steps / Expected Result / Assumption description PHẢI viết bằng tiếng Việt.** Đây là yêu cầu bắt buộc cho mọi file Excel xuất ra, không có ngoại lệ trừ:
- `[Technique Tag]` giữ nguyên tiếng Anh: `[EP]`, `[BVA]`, `[DT]`, `[ST]`, `[UC]`, `[PW]`, `[EG]`, `[CL]`, `[EXP]` (mã kỹ thuật cố định, dùng xuyên suốt skill).
- Danh từ riêng/thuật ngữ kỹ thuật không có bản dịch tự nhiên: tên field trong UI/API (`Email`, `Password`, `orderCode`), HTTP method/status code, tên bảng/cột DB, error code cụ thể (`statusCode: 4009`) — giữ nguyên như trong spec, không tự dịch làm sai lệch giá trị thật.
- Mã định danh: Test ID, REQ-xxx, R-xxx, BUG-xxx, ASM-xxx, giá trị cột Priority (P1-P4) và Status (Pass/Fail/Blocked/Deprecated/Not Run) — đây là code/enum, không phải câu văn, giữ nguyên tiếng Anh theo convention của skill.

**Các ví dụ "Tốt/Xấu" bằng tiếng Anh trong phần 7.2-7.9 dưới đây chỉ minh họa FORMAT/PATTERN** (cấu trúc câu, cách đặt tag, cách đo lường được) — khi viết TC thật, áp dụng đúng pattern đó nhưng **viết câu bằng tiếng Việt**, ví dụ:
- Pattern: `[Tag] Verb + specific condition being tested`
- Áp dụng đúng: `[EP] Kiểm tra đăng nhập thành công với email và password hợp lệ (valid partition)`
- KHÔNG viết: `[EP] Verify login succeeds with valid email and password (valid partition)`

### 7.1 Format chuẩn (4 cột)

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| {ID} | [Tag] Verb + specific condition | Numbered steps with data | Specific, measurable outcomes |

**Giải thích:**
- **STT**: Test ID theo naming convention (Phần 8.4)
- **Test Objective**: BẮT BUỘC bắt đầu bằng `[Technique Tag]`
- **Test Steps**: Steps đánh số, có test data cụ thể
- **Expected Result**: Kết quả đo lường được (UI + API + DB)

**File xuất**
- Xuất file testcase dạng file excel

### 7.2 Cách viết Test Objective

**Format:** `[Tag] Verb + specific condition being tested`

**Rules:**
- BẮT BUỘC bắt đầu bằng `[Technique Tag]`: [EP], [BVA], [DT], [ST], [UC], [PW], [EG], [CL], [EXP]
- Tiếp theo là **action verb**: Verify, Validate, Confirm, Check, Ensure
- Cụ thể condition đang test
- 1 mục tiêu duy nhất, max 20 từ sau tag
- Pass/fail phải unambiguous

**Tốt:**
- `[EP] Verify login succeeds with valid email and password (valid partition)`
- `[BVA] Validate error when password is 7 characters (below min 8)`
- `[DT] Confirm 20% discount when VIP=Yes AND order>$100`
- `[ST] Verify order status changes from Confirmed to Shipped`
- `[EG] Verify login rejects SQL injection in email field`

**Xấu:**
- `Test login` → không có tag, quá mơ hồ
- `Verify login works` → không có tag, không cụ thể condition
- `[EP] Check login functionality with various inputs` → quá rộng, không specific partition
- `Login should work` → không phải format test objective

### 7.3 Cách viết Test Steps

**Rules:**
- Đánh số tuần tự: 1, 2, 3...
- Mỗi step **1 hành động**, bắt đầu bằng **action verb**
- Bao gồm **test data cụ thể** (không viết "valid email", phải viết "email: test@example.com")
- Include navigation nếu không obvious
- Phân loại step bằng prefix khi cần rõ ràng:
  - `[Precondition]` — Setup, tạo data trước
  - `[Action]` — Hành động chính
  - `[Verify]` — Kiểm tra trung gian

**Action verbs:** Navigate, Open, Go to, Enter, Input, Type, Select, Click, Tap, Press, Submit, Wait, Observe, Scroll, Verify, Confirm, Check

**Tốt:**
```
1. Navigate to login page (https://app.example.com/login)
2. Enter email: "test@example.com"
3. Enter password: "ValidPass123!"
4. Click "Sign In" button
5. Wait for page to load
```

**Xấu:**
```
1. Go to login and enter credentials and submit
2. Check if it works
```

**Cho API tests, steps phải bao gồm:**
```
1. [Precondition] Setup data: tạo warehouse WH-001, carrier=GHN
2. [Precondition] Authenticate: lấy access_token cho app 1
3. [Request] POST /v1.0/orders
4. [Request] Headers: { Authorization: Bearer {token}, Content-Type: application/json }
5. [Request] Body: { requestId: "ORDER-001", ... }
6. [Verify] Check HTTP status code
7. [Verify] Check response body
8. [Verify] Query database: SELECT * FROM orders WHERE request_id = 'ORDER-001'
```

### 7.4 Cách viết Expected Result

**Rules:**
- Cụ thể và đo lường được
- Dùng `✓` cho expected results
- Bao gồm **tất cả layers** applicable: UI + API response + DB state + Side effects
- Nêu exact text, values, behaviors
- Include timing expectations nếu relevant

**Template cho UI tests:**
```
✓ UI: [Mô tả hiển thị cụ thể]
✓ Message: "[exact text]"
✓ Navigation: Redirect to [page]
```

**Template cho API tests:**
```
✓ HTTP Status: {code}
✓ statusCode: {business code}
✓ statusMessage: "{exact message}"
✓ data.{field}: {expected value}
✓ DB {table}: {mô tả record expected}
✓ DB {table}.{column} = {value}
✓ Side effect: {webhook sent / queue job created / email triggered}
```

**Template cho Negative tests:**
```
✓ HTTP Status: {error code}
✓ Error: "{exact error message}"
✓ DB: No record created / No change
✓ UI: Error message displays at [position]: "[text]"
```

**Tốt:**
- `✓ User redirected to /dashboard. Welcome message: "Hello, John". Session cookie created.`
- `✓ HTTP 400. statusCode: 4009. statusMessage: "Warehouse Name existed". DB: No new record.`
- `✓ Error displays below password field: "Password must be at least 8 characters"`

**Xấu:**
- `It works` → không đo lường được
- `Login successful` → không cụ thể xảy ra gì
- `Error shows` → error gì? ở đâu?

### 7.5 Test Data Rules

**Dùng test data thực tế, đa dạng, có edge case.**

**Rules:**
- Dùng **realistic data**: tên tiếng Việt thật (Nguyễn Thị Phương Anh), SĐT đúng format (0901234567), địa chỉ thật (123 Lê Lợi, Q1, TP.HCM)
- Mỗi TC dùng **data KHÁC NHAU** — không dùng chung "test@example.com" cho mọi TC
- Bao gồm **edge data**: tên có dấu, tên rất dài (255 chars), tên 1 ký tự, tên có emoji
- **Document test data** rõ ràng trong Test Steps (để reproduce được)
- Tách test data giữa các TC (tránh conflict khi chạy parallel)


**Ví dụ test data tốt:**
```
Warehouse names: "Kho HCM - Quận 1", "Warehouse Hanoi DC", "A" (min), "K..." (255 chars)
Phones: "0901234567" (valid), "090123" (invalid-short), "1901234567" (invalid-prefix)
Emails: "user@test.com", "a@b.co" (min valid), "user+tag@sub.domain.com" (complex valid)
Names: "Nguyễn Văn A", "O'Brien", "José García", "田中太郎"
```

**Ví dụ test data xấu:**
```
Mọi TC dùng: name="Test", phone="0900000000", email="test@test.com"
→ Không catch được edge cases, không realistic
```

### 7.6 Error Message Verification Rules

**Khi Expected Result chứa error message, PHẢI verify theo tiêu chuẩn:**

```
□ Specific — không generic ("Error occurred" là XẤU, "Warehouse Name is required" là TỐT)
□ Actionable — user biết cách fix (chỉ rõ field nào, sai gì, cần gì)
□ Consistent — cùng lỗi ở mọi nơi trả cùng message (không lúc "required" lúc "missing")
□ Chỉ rõ field — "Warehouse Phone invalid" thay vì "Invalid input"
□ Error code khớp message — statusCode 4009 luôn đi với "Warehouse Name existed"
□ Bilingual đúng (nếu có) — tiếng Việt đúng chính tả, ngữ pháp tự nhiên
□ Không lộ thông tin nhạy cảm — không stack trace, không SQL query, không internal path
```

**Format verify error trong Expected Result:**
```
✓ HTTP Status: 400
✓ statusCode: 4013
✓ statusMessage: "Warehouse Phone invalid"
✓ Error chỉ rõ field "phone"
✓ Message actionable (user biết phone sai format)
✓ Không lộ internal details
```

### 7.7 DB Verification Rules

**BẮT BUỘC verify DB cho mọi test case liên quan data changes.**

**Cho CREATE operations:**
```
□ Record tồn tại trong primary table
□ FK references hợp lệ
□ Related records được tạo (1:N relationships)
□ Auto-generated fields đúng (IDs, timestamps, codes)
□ Constraints enforced (unique, check, not null)
```

**Cho UPDATE operations:**
```
□ Chỉ fields intended bị thay đổi
□ updated_at timestamp thay đổi
□ Version column increment (nếu có optimistic locking)
□ Audit log / history entry được tạo (nếu có)
```

**Cho DELETE operations:**
```
□ Record bị deleted hoặc soft-deleted (is_deleted, deleted_at)
□ Cascade deletes xảy ra đúng
□ RESTRICT ngăn deletion (nếu có dependencies)
□ Không có orphan records
```

**DB verification ghi trong Expected Result:**
```
✓ DB orders: 1 record created
✓ DB orders.status = 'pending'
✓ DB orders.request_id = 'ORDER-001'
✓ DB order_items: 3 records (match items count)
✓ DB order_logs: 1 entry (action='CREATE')
✓ No orphan records in order_items
```

### 7.8 Security Test Rules (tóm tắt)

**Bắt buộc test cho mọi feature có auth/data sensitive:**

| Category | Phải test |
|----------|-----------|
| **Authentication** | No token→401, Invalid token→401, Expired token→401, Malformed→400/401 |
| **Authorization** | Cross-app access→403, Cross-user access→403/404, Privilege escalation→block |
| **Input Injection** | SQL injection, XSS, Command injection trong text fields |
| **Webhook Security** | Signature verify, Payload tampering, Replay attack prevention |
| **Rate Limiting** | At limit → OK, Over limit → 429 (NOT 500) |

> Chi tiết checklist: xem `TD_Reference_API.md` Section 8
> OWASP Top 10: xem `TD_Reference_Advanced.md` Section 13

### 7.9 Concurrent Test Rules (tóm tắt)

**Rules quan trọng nhất:**

| DO | DON'T |
|----|-------|
| ✅ Dùng true parallel execution (multi-thread, async) | ❌ Test sequential rồi gọi là concurrent |
| ✅ Launch requests trong <10ms window | ❌ Request 1 → wait → Request 2 |
| ✅ Verify response CẢ HAI requests | ❌ Chỉ check 1 request |
| ✅ Count exact DB records sau test | ❌ Bỏ qua DB verification |
| ✅ Specify timing: "simultaneously", "within 10ms" | ❌ Viết mơ hồ "gần như cùng lúc" |

> Chi tiết xem `TD_Reference_Advanced.md` Section 4


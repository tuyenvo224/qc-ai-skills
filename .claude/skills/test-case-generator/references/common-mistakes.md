# Common Mistakes to Avoid

Read this at Step 6 of `SKILL.md`'s workflow (Self-Check) — scan every test case written so far against this list before moving on.

---

## 10. Common Mistakes to Avoid

**Rà soát danh sách này ở Step 6 — sửa ngay nếu phát hiện.**

### TOP 10 lỗi phổ biến

| # | Lỗi | Vấn đề | Cách sửa |
|---|------|--------|----------|
| 1 | **TC không có [Technique Tag]** | Không truy vết được kỹ thuật, vi phạm rule | Thêm tag: [EP], [BVA], [DT]... vào đầu Test Objective |
| 2 | **Test Objective mơ hồ** | "Test login", "Verify feature works" | Viết cụ thể: "[EP] Verify login succeeds with valid email and password" |
| 3 | **Gộp nhiều objectives vào 1 TC** | "Verify login and logout work" | Tách thành 2 TC riêng biệt |
| 4 | **Expected result không cụ thể** | "It works", "Error shows" | Viết exact: message text, HTTP code, DB state |
| 5 | **Chỉ test happy path** | Thiếu negative, boundary, error cases | Thêm negative (EP invalid), boundary (BVA), error guessing (EG) |
| 6 | **Thiếu DB verification** | Không biết data có lưu đúng không | Thêm DB expected result: table, column, value |
| 7 | **Test concurrent nhưng sequential** | Request 1 → wait → Request 2 ≠ concurrent | Dùng true parallel: multi-thread, within <10ms |
| 8 | **TC viết lộn xộn không theo nhóm** | Khó đọc, khó maintain, dễ trùng | Nhóm theo chức năng, đúng thứ tự 9 loại (Phần 8.2) |
| 9 | **Copy-paste TC không đổi test data** | Mọi TC dùng cùng data → miss edge case | Dùng varied data: min/max/special chars/realistic values |
| 10 | **Bỏ qua góc nhìn end-user** | Chỉ test theo spec, miss real-world scenarios | Chạy End-User Checklist (Phần 6.1) cho mọi feature |

### Lỗi bổ sung cần tránh

| # | Lỗi | Cách sửa |
|---|------|----------|
| 11 | Over-test P4 features, under-test P1 | Phân bổ effort theo risk: P1 exhaustive, P4 minimal |
| 12 | Thiếu preconditions trong steps | Thêm [Precondition] setup steps rõ ràng |
| 13 | Expected result thiếu timing | Thêm "within 3 seconds", "max 30s timeout" khi relevant |
| 14 | Không test error message chính xác | Verify exact text, không chỉ "error xuất hiện" |
| 15 | Missing permission tests | Mỗi feature: test với đúng role + sai role + no auth |
| 16 | **Viết Test Objective/Steps/Expected Result bằng tiếng Anh** (vd copy nguyên pattern ví dụ trong `writing-format.md`) | Dịch lại toàn bộ câu sang tiếng Việt (xem 7.0) — chỉ giữ tiếng Anh cho `[Technique Tag]`, tên field/API/DB, mã ID (REQ/R/BUG/ASM-xxx), Priority (P1-P4), Status (Pass/Fail/Blocked/Deprecated) |

---

**End of Main Document**

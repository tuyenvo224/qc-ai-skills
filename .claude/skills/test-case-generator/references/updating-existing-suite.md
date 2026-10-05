# Updating an Existing Test Suite

Đọc file này **trước Step 1** khi nhiệm vụ là cập nhật một bộ test case đã tồn tại (đã có file Excel test case cũ), KHÔNG phải viết mới hoàn toàn từ đầu. Nếu đây là lần đầu viết test case cho feature này, bỏ qua file này và bắt đầu thẳng từ Step 1 trong `SKILL.md`.

**Phạm vi:** file này chỉ xử lý việc mở rộng/sửa test case theo đúng kỹ thuật khi spec thay đổi. Nếu nhu cầu là so sánh test case với brief của một **campaign** cụ thể (khuyến mãi, sự kiện) để đối chiếu setting, đó là phạm vi của skill `viet-test-case-campaign`, không phải skill này.

## Bước 0: Thu thập input

1. File Excel test case cũ (bắt buộc).
2. Spec mới (bắt buộc) + spec cũ (nếu có, để diff chính xác). Nếu không có spec cũ, hỏi người dùng phần nào trong spec mới là thay đổi so với trước.
3. Traceability Matrix / coverage report cũ (nếu còn giữ từ lần chạy `compute_coverage.py` trước) — dùng để biết feature nào đã đạt threshold, tránh phải tính lại từ đầu.

## Bước 1: Phân loại từng feature trong spec mới

Với mỗi feature/function, xếp vào đúng 1 trong 4 nhóm:

| Nhóm | Định nghĩa | Việc cần làm |
|------|------------|--------------|
| **Unchanged** | Spec không đổi so với lần trước | Giữ nguyên toàn bộ TC + cột Status hiện tại. KHÔNG viết lại, KHÔNG reset Status. |
| **Modified** | Business rule/field/flow thay đổi | Review lại TC liên quan đến đúng phần thay đổi (không phải toàn bộ feature). TC bị ảnh hưởng trực tiếp → reset Status về "" (Not Run). TC không liên quan trong cùng feature → giữ nguyên Status. |
| **New** | Feature/function hoàn toàn mới trong spec | Chạy đầy đủ Step 1-7 của `SKILL.md` cho riêng phần này. |
| **Removed** | Feature bị bỏ khỏi spec mới | KHÔNG xóa TC khỏi file — đánh dấu Status = "Deprecated" (thêm giá trị này ngoài Pass/Fail/Blocked/Not Run) và ghi lý do vào cột Risk/Bug, vd "Deprecated - removed in spec v2". Giữ lại để không mất lịch sử test.

**Vì sao không viết lại từ đầu:** viết lại toàn bộ sẽ làm mất lịch sử Pass/Fail đã chạy, phá vỡ liên kết Test ID cũ với bug tracker/báo cáo đã tham chiếu TC đó trước đây.

## Bước 2: Viết/sửa test case cho phần Modified + New

- Áp dụng đúng quy tắc kỹ thuật như bình thường (`techniques-and-coverage.md`, `writing-format.md`, `grouping-ordering.md`).
- Với feature Modified: chỉ thêm/sửa TC ở đúng phần thay đổi — không viết lại toàn bộ nhóm nếu 80% flow vẫn giữ nguyên.
- Test ID: TC mới thêm vào một feature đã có → nối tiếp dãy số hiện có (vd feature đã có tới `LOGIN-015` → TC mới bắt đầu từ `LOGIN-016`), KHÔNG đánh số lại từ đầu.

## Bước 3: Merge & xuất lại

1. Merge 4 nhóm (Unchanged giữ nguyên, Modified đã cập nhật, New đã viết xong, Removed đã đánh dấu Deprecated) thành 1 bộ dữ liệu JSON đầy đủ theo schema của `generate_testcase_excel.py`.
2. Chạy lại `scripts/compute_coverage.py` trên **toàn bộ suite** (không chỉ phần mới) — vì thêm/bớt requirement có thể làm thay đổi % coverage tổng.
3. Chạy lại `scripts/generate_testcase_excel.py` để xuất file Excel mới — báo rõ cho người dùng đây là bản cập nhật của file cũ (không phải file độc lập), gợi ý đặt tên có version, vd `{ProjectName}_{FeatureName}_TestCases_v2.xlsx`.

## Checklist trước khi giao output

```
□ Đã phân loại 100% feature trong spec mới vào đúng 1 trong 4 nhóm (Unchanged/Modified/New/Removed)
□ TC của feature Unchanged giữ nguyên Status, không bị viết đè
□ TC của feature Modified chỉ reset Status ở đúng phần bị ảnh hưởng
□ Test ID nối tiếp dãy cũ, không đánh số lại
□ Feature Removed được đánh Deprecated, không bị xóa khỏi file
□ compute_coverage.py đã chạy lại trên toàn bộ suite (không chỉ phần mới)
□ Tên file output thể hiện đây là bản cập nhật (có version/ngày)
```

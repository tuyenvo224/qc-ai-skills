---
name: viet-test-case
description: Viết nhanh một bộ test case cơ bản (Positive/Negative/Boundary/Security) từ một requirement/user story ngắn, xuất ra file Excel (.xlsx) theo đúng template "KỊCH BẢN KIỂM THỬ" chuẩn của công ty (khối metadata đầu file, test case nhóm theo Module/Function thành Group "I."/"II."..., các cột Precondition/Test Data/Steps/Expected Result riêng biệt) — không cần technique tag (EP/BVA/DT...), không có coverage threshold định lượng, không có multi-perspective Admin/Frontend/Transaction, không có Summary/Assumptions sheet hay truy vết REQ/R/BUG-xxx. Dùng khi người dùng chỉ cần bản test case gọn nhẹ, có Excel đúng chuẩn công ty để dùng ngay, không cần độ sâu/coverage đầy đủ. Nếu người dùng cần bộ test case chuyên sâu (kỹ thuật EP/BVA/DT/ST/UC, coverage threshold tính bằng script, multi-perspective, Summary+Assumptions sheet, truy vết trong pipeline QA), dùng skill `test-case-generator` thay vì skill này.
metadata:
  author: tuyenvo224
  version: "1.0"
---

### [VAI TRÒ & MỤC TIÊU]
Bạn là một **Senior QA/Software Testing Engineer**. Nhiệm vụ của bạn là dựa vào tài liệu/yêu cầu tính năng (Requirement/User Story) được cung cấp bên dưới để sinh ra danh sách Test Case chi tiết, phủ toàn bộ các kịch bản.

---

### [TÍNH NĂNG / YÊU CẦU CẦN TEST]
- **Tên tính năng:** `[Ví dụ: Chức năng Đăng nhập - Login]`
- **Tài liệu mô tả / User Story:**  
  > `[Dán nội dung mô tả tính năng, luồng nghiệp vụ hoặc tiêu chí chấp nhận (Acceptance Criteria) vào đây]`

---

### [PHẠM VI TEST (TEST SCOPE)]
Vui lòng phủ các nhóm kịch bản sau:
1. **Positive Cases:** Kịch bản thành công / Luồng chính (*Happy Path*).
2. **Negative Cases:** Kịch bản thất bại / Nhập sai thông tin / Bỏ trống.
3. **Boundary / Edge Cases:** Kịch bản biên / Kích thước dữ liệu cực hạn.
4. **Security / Permission Cases:** Kịch bản phân quyền / Bảo mật cơ bản (nếu có).

---

### [ĐỊNH DẠNG ĐẦU RA (OUTPUT FORMAT)]
Trước tiên soạn nội dung dưới dạng **bảng Markdown** với các cột sau (đây là bước trung gian, file cuối cùng giao cho người dùng là Excel — xem mục "Output" cuối file):

| STT | Module/Function | Mục đích kiểm thử | Precondition | Test Data | Các bước thực hiện | Kết quả mong muốn |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `[Số thứ tự]` | `[Tên module/màn hình/chức năng con]` | `[Positive/Negative/Boundary/Security] [Tóm tắt kịch bản]` | `[Điều kiện tiên quyết, để trống nếu không có]` | `[Dữ liệu đầu vào cụ thể]` | `[Các bước thao tác, đánh số 1. 2. 3... cách nhau bằng <br>]` | `[Kết quả kỳ vọng]` |

Lưu ý cách điền:
- **Module/Function**: các dòng liên tiếp có cùng giá trị này sẽ được gộp thành 1 Group khi convert sang Excel (hiển thị dạng "I. <tên>", "II. <tên>"...) — vì vậy phải sắp các test case cùng module/màn hình đứng **liền kề nhau**, không xen kẽ giữa các module khác nhau.
- **Mục đích kiểm thử**: luôn bắt đầu bằng tag phân loại trong ngoặc vuông `[Positive]`/`[Negative]`/`[Boundary]`/`[Security]` (template không có cột Type riêng, tag này thay thế cho cột đó).
- **Precondition** và **Test Data** là 2 cột riêng biệt trong template, không gộp chung vào Steps.

**Bám sát template mẫu** ở `.claude/skills/viet-test-case/assets/Template_TCs.xlsx` (sheet `TCs`) — đây là file Excel chuẩn công ty (không phải markdown), có sẵn khối metadata đầu file (Tên màn hình/chức năng, Link spec, Link redmine, Prototype, Domain, Account, QC thực hiện...) và 3 Group ví dụ rỗng ("I. Group 1", "II. Group 2", "III. Group 3") để tham khảo cấu trúc. Bảng chính có đúng 10 cột theo thứ tự: STT trường hợp kiểm thử | Mục đích kiểm thử | Precondition | Test data | Các bước thực hiện | Kết quả mong muốn | Kết quả hiện tại | Mã lỗi | Ghi chú | QC thực hiện — **4 cột cuối (Kết quả hiện tại/Mã lỗi/Ghi chú/QC thực hiện) để trống, dành cho QC điền khi thực thi test, KHÔNG tự điền trước**.

---

### [QUY TẮC BỔ SUNG]
- **Sắp xếp thứ tự ưu tiên:** Trong mỗi Group (module/màn hình), ưu tiên *Positive Cases* trước, sau đó tới *Negative*, *Boundary*, *Security*.
- **Ngôn ngữ thể hiện:** `[Tiếng Việt]`.
- **Chất lượng:** Rõ ràng, dễ hiểu để Tester có thể thực thi ngay mà không cần hỏi lại.
- **Đánh dấu Expected Result cần confirm:** Nếu *Kết quả mong muốn* dựa trên assumption hoặc còn phải hỏi lại PO/BA, luôn ghi rõ ngay trong ô đó (hoặc trong ô Precondition/Test data nếu assumption nằm ở đó), dạng `(Theo ASM-xxx – cần confirm QH-xxx)` hoặc `(cần confirm …)` nếu không có mã. Script dựa vào các cụm này để tự highlight ô trên Excel (xem mục Output), nên đừng diễn đạt kiểu khác, không có từ khóa (vd "có thể là…", "tùy DEV") — ô đó sẽ không được highlight.

# Output

1. **Soạn nội dung Markdown** theo đúng bảng ở mục "ĐỊNH DẠNG ĐẦU RA", lưu vào thư mục `test-case-can-review/`, tên file:
   - `yyyy-mm-dd_hh-mm-ss_ten-feature.md`
   - Dòng H1 đầu file dạng `# Test Case: <Tên feature> (#<mã redmine nếu có>)` — script sẽ đọc dòng này để tự điền tên chức năng và link redmine vào khối metadata của file Excel.

2. **Convert sang Excel bằng script có sẵn** — KHÔNG tự dựng file Excel bằng tay, KHÔNG tự viết script convert mới:
   ```
   python .claude/skills/viet-test-case/scripts/testcase_md_to_xlsx.py "test-case-can-review/yyyy-mm-dd_hh-mm-ss_ten-feature.md"
   ```
   Script tự động: load `assets/Template_TCs.xlsx` làm nền (giữ nguyên style/màu/border chuẩn công ty), điền khối metadata (tên feature, link redmine, QC thực hiện, ngày tạo), gộp các dòng cùng Module/Function thành Group ("I. ...", "II. ..."...), đánh STT liên tục xuyên suốt file, để trống 4 cột QC-điền-sau, bật wrap text cho mọi ô dữ liệu và tự tính chiều cao dòng theo độ dài text + độ rộng cột (hàm `fit_row_to_text`) để hiển thị full nội dung, không bị cắt chữ. File output **không freeze bất kỳ hàng/cột nào** (script tự clear freeze panes trên mọi sheet) — không thêm lại `freeze_panes` khi sửa script. Mọi ô dữ liệu test case (kể cả cột **Kết quả mong muốn**) là text thường: font Times New Roman, màu đen, không gạch chân (ô mẫu F13 của template đã được bỏ style "Hyperlink"; hàm `normalize_data_style` vẫn ép font text thường cho mọi ô dữ liệu để phòng template bị đổi lại). Chỉ các ô metadata F3–F6 (Link spec/Link redmine/Prototype/Domain) được giữ style link.
   **Highlight ô cần confirm:** test case nào có assumption / cần confirm với PO/BA ở **bất kỳ cột nào** (Mục đích, Precondition, Test data, Các bước, Kết quả mong muốn) thì ô **Kết quả mong muốn** (cột F) của case đó được tô **nền vàng nhạt** (`FFFF99`, hằng `CONFIRM_FILL`); font và border giữ nguyên, các ô khác không bị tô. Nhận diện bằng hàm `needs_confirmation` (regex `CONFIRM_PATTERN`, so khớp trên text đã bỏ dấu + lowercase) với các cụm: `cần confirm`, `confirm lại`, `chờ confirm`, `cần xác nhận`, `chờ xác nhận`, `assumption`, `giả định`, `giả sử`, `tạm dùng`, `tạm hiểu`, `chưa chốt`, `chưa rõ`, `TBD`, và mã `ASM-xxx`/`QH-xxx`/`QM-xxx`/`QL-xxx`. Cần nhận diện thêm cụm mới thì bổ sung vào `CONFIRM_PATTERN`. Script in ra số ô đã highlight kèm danh sách STT — dùng danh sách này để báo cho người dùng.
   Nếu script báo lỗi hoặc parse sai với 1 input cụ thể, sửa thẳng `scripts/testcase_md_to_xlsx.py` thay vì viết script rời để né lỗi.

3. **Báo cho người dùng đường dẫn cả 2 file** — file `.xlsx` là bản giao chính thức, file `.md` giữ lại để tiện tham khảo/diff nhanh khi cần. Kèm số lượng + STT các ô Kết quả mong muốn đã được highlight cần confirm PO/BA (lấy từ output của script).


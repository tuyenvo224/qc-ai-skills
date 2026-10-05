---
name: log-bug-redmine
description: Viết bug report để người dùng tự copy và post lên Redmine, theo đúng template 7 mục của team (Môi trường, Điều kiện tiên quyết, Các bước tái hiện, Kết quả thực tế, Kết quả mong đợi, Tần suất, Ghi chú). Tiêu đề nằm trong codeblock 1, nội dung nằm trong codeblock 2. Nhận mô tả lỗi của QC (các case, kết quả thực tế, case nào đang đúng để so sánh), có thể kèm link spec (BookStack/Redmine/GitLab/SharePoint), link artifact, ảnh chụp màn hình hoặc thông tin môi trường. Có link spec thì đọc spec để trích ID rule (BR/FR/UC/AC) làm căn cứ cho Expected Result. Chạy thẳng, KHÔNG hỏi xác nhận, KHÔNG tự tạo issue trên Redmine. Trigger trên các câu như "log bug", "viết bug", "report bug", "viết lại bug để post Redmine", "đang có bug chỗ này…", "/log-bug-redmine". Không dùng để phân tích bug tiềm ẩn (dùng `bug-hunter`) hay viết test case (dùng `viet-test-case` / `test-case-generator`).
metadata:
  author: tuyenvo224
  version: "1.0"
---

# Log bug → Redmine

**Input:** mô tả lỗi của người dùng. Có thể kèm link spec, link artifact, ảnh chụp, môi trường test.
**Output:** tiêu đề + nội dung bug theo template, để người dùng **tự copy** lên Redmine.

> **Ngoại lệ với AGENTS.md:** người dùng đã chốt rằng skill này **không** trình bày kế hoạch và **không** chờ xác nhận. Chạy thẳng tới kết quả. Chỉ dừng khi lỗi xác thực lúc đọc spec.
> Skill **không** gọi API tạo/sửa issue trên Redmine.

## Bước 1 · Gom thông tin

Từ mô tả của người dùng và ngữ cảnh hội thoại (spec, artifact đã tổng hợp trước đó, các phân tích đã có), xác định:
- **Sản phẩm / Module**: ví dụ `Biz Client` / `Login`.
- **Case lỗi**: điều kiện, thao tác, kết quả thực tế quan sát được.
- **Case đối chứng đang đúng** (nếu có): đưa vào Notes, rất có ích để DEV khoanh vùng.
- **Môi trường**: URL/build, OS, browser/device, tài khoản test.
- **Ảnh**: ghi tên file hoặc "ảnh đính kèm #n" ở Notes để người dùng nhớ attach.

Mô tả có **nhiều lỗi độc lập** → tách thành nhiều bug, mỗi bug một cặp codeblock. Các case cùng một nguyên nhân, khác nhau một điều kiện (ví dụ tick / không tick) → gộp thành 1 bug: case lỗi là chính, case đúng đưa vào Notes.

## Bước 2 · Lấy căn cứ từ spec

- **Có link spec mới** (chưa đọc trong hội thoại): đọc bằng script của skill tổng hợp spec. Script tự lấy key trong `connect-key/`, không đọc file key và không in key ra.
  ```bash
  ROOT="$(pwd -W 2>/dev/null || pwd)"
  python "$ROOT/.claude/skills/tong-hop-spec-artifact/scripts/fetch_spec.py" "<link>" "<scratchpad>/<slug>"
  ```
  Exit code 3 / `AUTH_ERROR` → báo token có thể hết hạn rồi dừng.
  Link là artifact claude.ai → đọc bằng tool `Artifact` với `action: "read"`.
- **Spec / artifact đã đọc trong hội thoại**: dùng lại, không tải lại.
- Tìm mọi rule liên quan tới hành vi mong đợi, ghi **nguyên ID** (BR-xxx, FR-xx, UC-xx, AC-xx, §mục) kèm nội dung rút gọn, không đổi nghĩa.
- Chỉ ra vì sao actual sai so với rule. Ví dụ "không rule nào yêu cầu điều kiện X".
- **Không có spec**: Expected viết theo mô tả người dùng, thêm vào Notes dòng "Expected theo mô tả của QC, chưa đối chiếu spec".
- Spec **không quy định** hành vi đó, hoặc mơ hồ: không tự kết luận là bug. Ghi vào Notes "Spec chưa quy định rõ, cần BA/PO xác nhận", và báo người dùng ở phần kiểm tra cuối.

## Bước 3 · Viết bug

Theo đúng **[references/template.md](references/template.md)**: 7 mục I–VII. Xem ví dụ đầy đủ trong file đó.

**Tiêu đề**
- Dạng: `[STG][<UI|Function>][<Sản phẩm>] [<Module>] <điều kiện> thì <hành vi sai>`.
  - `[STG]` **luôn** đứng đầu, kể cả khi người dùng nhắc môi trường khác (người dùng tự sửa tay nếu cần).
  - Ngay sau `[STG]` là **đúng một** tag loại bug: `[UI]` hoặc `[Function]`, viết liền, không cách.
- Tiếng Việt, một dòng, nói được cái gì sai mà không cần mở bug. Không viết chung chung kiểu "Lỗi remember".
- Ví dụ:
  - `[STG][UI][Biz Client] [Login] Bôi đen text trong field "Email công việc" thì màu highlight vùng chọn quá nhạt, khó nhận biết đoạn text đang được chọn`
  - `[STG][Function][Biz Client] [Login] Đăng nhập ở trình duyệt khác mà không tick "Ghi nhớ đăng nhập" thì Remember của trình duyệt cũ không bị vô hiệu hóa`

**Phân loại `[UI]` / `[Function]`**
- `[UI]`: lỗi hiển thị, logic vẫn đúng. Ví dụ màu sắc, font, kích thước, căn lề, layout, icon, chính tả / câu chữ label, responsive, trạng thái hover / focus / selection.
- `[Function]`: lỗi hành vi / logic. Ví dụ validate, xử lý dữ liệu, điều hướng, session / Remember, phân quyền, message hiện sai tình huống hoặc không hiện, API trả sai.
- Ca giáp ranh:
  - Message hiện **đúng lúc nhưng sai chữ** → `[UI]`.
  - Message hiện **sai lúc hoặc không hiện** → `[Function]`.
  - Không chắc → vẫn chọn một tag, rồi nêu lý do chọn ở phần "Kiểm tra trước khi post".

**Nội dung**
- **I. Môi trường**: thông tin nào người dùng chưa cho thì để `<...>` kèm gợi ý (ví dụ `<vd: Chrome 1xx>`). Không tự điền.
- **II. Điều kiện tiên quyết**: trạng thái tài khoản, dữ liệu, số trình duyệt/thiết bị cần có.
- **III. Các bước tái hiện**: đánh số, mỗi bước một thao tác. Ghi rõ dữ liệu nhập, chỗ **tick / KHÔNG tick**, kết quả trung gian nếu cần (`→ đăng nhập thành công`). Bước cuối là bước lộ ra lỗi.
- **IV. Kết quả thực tế**: **chỉ những gì người dùng đã quan sát**. Không thêm hệ quả suy ra.
- **V. Kết quả mong đợi**: hành vi đúng, sau đó là dòng "Căn cứ <tên spec + phiên bản>:" và các rule ID.
- **VI. Tần suất**: Always / Sometimes / Rarely theo lời người dùng. Không rõ thì để `Always` và đưa vào phần kiểm tra cuối.
- **VII. Ghi chú**:
  - Case đối chứng đang đúng (ghi rõ PASS).
  - Nghi ngờ nguyên nhân: ghi rõ là "Nghi ngờ", một câu.
  - Hệ quả chưa kiểm chứng: "Cần kiểm tra thêm: …".
  - Spec tham khảo: tên, nguồn, phiên bản, ngày.
  - Ảnh cần attach (nếu có).

**Văn phong:** tiếng Việt, câu ngắn, giữ thuật ngữ gốc của spec (Remember, Session, Active, Deactive/Blocked…). Tên nút, label, message để trong ngoặc kép, đúng nguyên văn.

## Bước 4 · Trả kết quả

Đúng thứ tự sau, không thêm phần mở đầu dài:

1. Một dòng: `Viết cho: DEV/QC đọc trên Redmine. Các ô <...> cần điền.`
2. `**Tiêu đề:**` + codeblock 1 chứa **chỉ** tiêu đề.
3. `**Nội dung:**` + codeblock 2 chứa toàn bộ 7 mục.
   - Nội dung có dòng bắt đầu bằng ``` (ví dụ log, code) thì codeblock 2 dùng `~~~` để không bị vỡ.
4. Một danh sách ngắn **"Kiểm tra trước khi post"** (tối đa 4 dòng): các ô `<...>` còn trống, chỗ nào tôi đang giả định về hành vi quan sát, mục "Cần kiểm tra thêm" nào nếu đã xác nhận thì nên chuyển lên Actual, spec chưa rõ cần hỏi BA/PO.

Nhiều bug → lặp lại mục 2–3 cho từng bug, đánh số `Bug 1`, `Bug 2`, rồi gom phần kiểm tra ở cuối.

## Không làm
- Không tạo/sửa issue trên Redmine, không gọi API ghi.
- Không bịa hành vi chưa quan sát, không bịa môi trường, không bịa rule ID.
- Không in token / API key.

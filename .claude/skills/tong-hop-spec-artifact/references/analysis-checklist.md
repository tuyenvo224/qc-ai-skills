# Checklist bóc tách spec → trang tổng hợp

Đọc **toàn bộ** `spec.txt`, không đọc lướt. Spec dài trên 2000 dòng thì đọc theo từng đoạn bằng `offset`/`limit` cho tới hết. Mỗi mục dưới đây tương ứng với một section trong `template.html`. Mục nào spec không có dữ liệu thì **xóa section đó**, không để trống và không bịa cho đủ.

## 0. Metadata (header)
- Lấy tên feature, sản phẩm, module, phiên bản, ngày cập nhật, trạng thái, hệ thống ảnh hưởng từ bảng "Thông tin tài liệu".
- Spec không có bảng này thì lấy từ `source.json` (`updated_at`, `revision`, `title`).
- Dòng `counts`: dùng kết quả của `count_ids.py`, chỉ ghi các loại ID thực sự có. Có thể ghi thêm "n Flow", "n Message" nếu có ích.

## 1. Tổng quan & scope
- 2–4 câu nói rõ ai làm gì, bằng cách nào, và điều kiện chính.
- **Các con số chốt**: mọi giá trị định lượng như timeout, hạn mức, số lần, độ dài, thời hạn, phí, tỉ lệ. Ghi đúng đơn vị và mốc tính (tính từ khi nào).
- Entry point / màn hình: liệt kê field, action, link điều hướng.
- Pre-condition.
- In scope / Out of scope: chép đủ ý, gộp các dòng trùng nghĩa.

## 2. User flow (mermaid), thường 3–6 flow
Chọn các flow sao cho mỗi luồng quan trọng xuất hiện ở ít nhất một sơ đồ:
1. **Luồng chính (happy path)**, gắn kèm mọi nhánh lỗi. Thứ tự các bước kiểm tra phải đúng như spec quy định, ví dụ validate → xác thực → trạng thái → side effect.
2. **Luồng phụ/tái nhập**, ví dụ mở lại app, retry, resume, auto-*.
3. **Luồng trong lúc đang dùng**: các sự kiện làm trạng thái thay đổi giữa chừng, như bị khóa, hết hạn, bị thay thế.
4. **Sequence nhiều actor/thiết bị/hệ thống**, dùng khi spec có tương tác giữa 2 bên trở lên (User–System–3rd party, Device A–B, Admin–Client).
5. Flow trạng thái (`stateDiagram-v2`) khi entity có vòng đời, ví dụ Draft → Submitted → Approved.

Quy tắc khi vẽ:
- Node lỗi ghi **nguyên văn message**.
- Nhánh lỗi hệ thống vẽ bằng nét đứt.
- Thứ tự nào spec **không** quy định thì thêm `note` với nhãn **❓ Giả định** và đưa vào danh sách câu hỏi.
- Ví dụ số liệu, timeline mà spec có (như "09:00 → 10:30") thì đặt vào `div.timeline` ngay dưới flow liên quan.

## 3. Business rules
- Một dòng cho một rule, **giữ nguyên ID gốc** (BR-xxx, FR-xx…).
- Rule không có ID thì ghi số section làm ID (`§5.3`), hoặc ghi UC/FR chứa rule đó.
- Cột Nhóm: gom theo chủ đề, dùng tên ngắn như Input, Credential, Status, Session, Timeout, Pricing, Quota.
- Cột FR/AC: map sang FR/AC tương ứng. Đó là các ID mà spec đặt cạnh rule, hoặc AC có Given/Then khớp với rule.
- Viết lại cho gọn nhưng **không đổi nghĩa, không làm tròn số**, giữ nguyên các chữ khẳng định/phủ định ("không được", "chỉ").
- Rule nằm trong đoạn văn, ví dụ, lưu ý hay chú thích (ví dụ "FRD không quy định cơ chế…") cũng phải đưa vào bảng.

### Bảng quyết định
Làm khi spec có từ 2 điều kiện trở lên cùng quyết định kết quả, ví dụ credential × status, loại user × quyền, số tiền × hạn mức. Ô nào spec không nói thì ghi `❓ Chưa quy định (xem Q-xx)`.

## 4. Ma trận sự kiện → trạng thái
Làm khi spec có 1–3 "trạng thái" bị nhiều sự kiện tác động, ví dụ Session/Remember, Order status/Payment status, Voucher/Balance.
- Hàng là **mọi sự kiện** nhắc tới trong spec. Cột là các trạng thái. Cột cuối là nguồn.
- Đây là chỗ dễ phát hiện gap nhất: ô nào phải suy luận thì ghi `❓ suy luận`, ô nào spec không nói thì ghi `❓ Chưa quy định`, và cả hai trường hợp đều đưa vào câu hỏi.

## 5. Danh mục message
- Liệt kê **mọi chuỗi hiển thị** cho user: lỗi validate, lỗi nghiệp vụ, lỗi hệ thống, thông báo thành công, confirm dialog. Ghi nguyên văn cùng tình huống, vị trí và nguồn.
- Message ghi "đề xuất" thì gắn pill `Đề xuất`.
- Tình huống cần báo cho user mà spec không có message thì thêm một dòng `❓ Chưa có message` và đưa vào câu hỏi.

## 6. Use case & truy vết
- Một dòng cho mỗi UC, gồm tình huống, kết quả mong đợi, BR/FR và VR/AC.
- Thêm dòng `—` cho các nhóm rule không có UC riêng, ví dụ processing, failed attempts.
- Spec không có UC thì dựng bảng "Kịch bản" từ AC hoặc từ các flow, và ghi rõ là do mình tự tổng hợp.

## 7. Validation rules & Acceptance criteria
- Chép đủ **toàn bộ** VR và AC. Số dòng phải khớp với kết quả `count_ids.py`.
- AC giữ đủ 3 cột Given / When / Then.

## 8. Điểm cần làm rõ (Q-xx)
Tự rà theo các góc sau. Góc nào có vấn đề thì viết thành câu hỏi hỏi được ngay:
- **Missing**: message, UX, trạng thái rỗng/lỗi, giá trị giới hạn (min/max/length/format), timezone và cách tính mốc thời gian, audit/log, phân quyền.
- **Conflict**: hai rule dẫn tới hai kết quả khác nhau, hoặc có đường vòng qua một rule (ví dụ đóng/mở lại để bỏ qua bước xác thực).
- **Ambiguity**: thuật ngữ chưa định nghĩa ("đóng browser", "thao tác", "đồng thời"), thứ tự ưu tiên khi nhiều điều kiện xảy ra cùng lúc.
- **Assumption**: điểm spec ngầm định, ví dụ chỉ có 3 trạng thái, chỉ có 1 loại user.
- **Concurrency / race**: double submit, đồng thời, retry, lỗi giữa chừng (bước nào đã commit, bước nào rollback).
- **Tương tác với feature out-of-scope**, ví dụ reset/change password, logout, admin thao tác.
- **Editorial**: nội dung sót lại, đánh số sai, bảng trống, ID trùng hoặc nhảy số.

Mỗi câu hỏi phải có ưu tiên Cao/TB/Thấp và loại, kèm UC/BR liên quan. Cao là những câu ảnh hưởng tới logic hoặc bảo mật, hoặc làm DEV/QC hiểu khác nhau. Thường có 8–20 câu. Sắp theo ưu tiên.

## 9. Nguồn ảnh (chỉ khi có ảnh)
- Mỗi ảnh một thẻ: số `#n`, mô tả **1 câu những gì nhìn thấy**, nguồn (đính kèm / BookStack / Redmine…). Thẻ dựng bằng `embed_images.py`.
- Ở các mục khác, mỗi thông tin lấy từ ảnh ghi *(từ ảnh #n)*:
  - **Flow:** bước / nhánh thấy trên sơ đồ.
  - **Rules:** field bắt buộc (dấu `*`), độ dài hiển thị, giá trị mặc định.
  - **Message:** chữ hiển thị trên mockup.
  - **Tổng quan:** danh sách field / nút của màn hình.
- Soát riêng cho ảnh khi làm mục 8 (Q-xx):
  - field / nút có trên ảnh mà spec không nhắc, hoặc ngược lại;
  - message trên ảnh khác chữ trong spec;
  - trạng thái lỗi / rỗng / loading không có ảnh minh họa;
  - nút trên ảnh không rõ bấm vào thì đi tới đâu;
  - nhãn ảnh mờ hoặc bị cắt nên không đọc được.

## Quy tắc chung
- **Không bịa.** Mọi rule trên trang phải truy được về spec. Chỗ nào là suy luận thì ghi `❓ suy luận` / `❓ Giả định`.
- Giữ thuật ngữ gốc của spec, ví dụ Deactive/Blocked, Remember, Session. Không tự dịch.
- Nguồn là Redmine thì rule có thể nằm trong **comment (journals)** và file đính kèm. Rule ở journal mới hơn sẽ ghi đè description; khi đó ghi rõ nguồn là `Note #id`.
- Nguồn có link sang một spec gốc khác (ví dụ Redmine issue có "business doc: bookstack…"), thì tải cả spec gốc và trình bày: spec gốc = business rule, issue = scope/technical. Chỗ hai nguồn lệch nhau thì ghi vào Q-xx với loại Conflict.
- Ảnh (đính kèm hoặc trong spec `[IMG#n]`): xem quy tắc đọc ảnh ở SKILL.md Bước 2 và mục 9 ở trên. Chỉ mô tả những gì nhìn thấy.

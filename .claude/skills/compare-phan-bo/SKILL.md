---
name: compare-phan-bo
description: So sánh chi tiết file brief phân bổ quà của Sale (Excel, nhiều sheet) với các file dữ liệu phân bổ export từ hệ thống (Excel, mỗi file là 1 giải/1 scope theo region_id hoặc supermarket_id), để xác định tên quà, số lượng quà và ngày giờ ra giải trên hệ thống đã khớp với brief hay chưa. Dùng khi cần QC/audit dữ liệu phân bổ trước khi lên PROD, hoặc khi có 1 file "brief" (.xlsx) và nhiều file "export phân bổ" (.xlsx) cần đối chiếu.
metadata:
  author: tuyenvo224
  version: "1.0"
---

Bạn là QA đang đối chiếu dữ liệu phân bổ quà (brief Sale) với dữ liệu phân bổ thực tế export từ hệ thống.

## Input

Mỗi lần chạy dùng 1 thư mục riêng, đặt trong `campaign-qc/` ở thư mục gốc của project đang
mở (hướng dẫn cho người dùng xem [README.md](README.md)), theo cấu trúc:

```
campaign-qc/<yyyy-mm-dd>_<ten-campaign>_phan-bo/
  ├── input/    ← đúng 1 file brief .xlsx + 1 hoặc nhiều file export .xlsx
  └── output/   ← báo cáo so sánh do skill ghi ra
```

Args chấp nhận 1 trong 2 dạng:

- **Dạng 1 (khuyến nghị):** 1 đường dẫn thư mục chạy → lấy file trong `input/` của thư mục
  đó (nếu không có `input/` thì lấy trực tiếp trong thư mục được truyền).
- **Dạng 2:** danh sách đường dẫn file, thứ tự bất kỳ: 1 file brief + 1 hoặc nhiều file export.

Quy tắc bắt buộc khi xác định input:

- Phân loại file: file `.xlsx` có "brief"/"Brief" trong tên là file brief; file có header
  `supermarket_id` hoặc `region_id` + các cột `Quantity - ...` là file export.
- Phải có **đúng 1** file brief và **ít nhất 1** file export. Không có args, không có brief,
  có hơn 1 brief, không có export, hoặc có file không phân loại được → **DỪNG LẠI và hỏi
  user**. Tuyệt đối không tự tìm file ở thư mục khác để bù vào.
- **Không bao giờ** dùng file nằm trong `.claude/skills/` làm input. Thư mục `examples/` của
  skill này là dữ liệu giả, chỉ minh họa định dạng.
- Trước khi đọc file thật, đọc [references/input-format.md](references/input-format.md) để
  biết cấu trúc sheet/header của brief (dòng header, vùng pivot leftover, cột ngày, bảng phụ)
  và cấu trúc file export. Cấu trúc thực tế của file đang xét vẫn là chuẩn.

### Bước 0 — Xác nhận bộ file trước khi so sánh

Trước khi phân tích, in ra cho user:

| File | Loại | Scope (region/supermarket) | Số dòng | Ngày sửa file | Tên campaign/slug (từ tên file) |
|---|---|---|---|---|---|
| ... | Brief / Export | ... | ... | ... | ... |

- Nếu các file export có slug campaign khác nhau, hoặc timestamp export cách nhau bất thường
  (khác ngày), hoặc chuỗi/store trong brief không xuất hiện ở export nào → cảnh báo **"Có thể
  truyền sai/thiếu file"** và chờ user xác nhận rồi mới làm tiếp.
- Nếu hợp lệ thì ghi "Bộ file hợp lệ" và tiếp tục.

### Định nghĩa các file

- File brief = nguồn yêu cầu nghiệp vụ của Sale (ground truth về ý định phân bổ: tên quà, số
  lượng, ngày giờ ra giải).
- Mỗi file export = dữ liệu phân bổ thực tế của MỘT giải/MỘT scope cụ thể (region hoặc
  supermarket) đang chạy trên hệ thống — không phải các bản export trùng lặp của cùng một dữ liệu.

## Mục tiêu

Xác định dữ liệu phân bổ (tên quà, số lượng quà, ngày giờ ra giải) trên hệ thống đã khớp 100%
với brief của Sale hay chưa, không bỏ sót bất kỳ sheet/file/dòng/cột nào ở cả 2 phía.

## Quy trình bắt buộc

### Bước 1 — Đọc toàn bộ, không tóm tắt vội

- Liệt kê TẤT CẢ sheet có trong file brief, đọc kỹ nội dung từng sheet một.
- Cảnh giác: brief có thể chứa vùng dữ liệu pivot table leftover (ví dụ các cột kiểu
  "Row Labels", "Count of...", "Sum of...", "Grand Total" nằm lệch sang phải bảng chính) — đây
  KHÔNG phải dữ liệu phân bổ gốc, không dùng làm căn cứ so sánh trực tiếp, chỉ có thể dùng để
  cross-check tổng số ở Bước 7 nếu đáng tin.
- Liệt kê hết TẤT CẢ file export, đọc toàn bộ từng file, không lấy mẫu vài dòng rồi suy ra phần
  còn lại. Với mỗi file, ghi rõ: file này scope theo region hay supermarket, và danh sách đầy đủ
  các cột "Quantity - <tên quà> - <id>" có trong file.
- Nếu một supermarket_id/region_id xuất hiện nhiều dòng trong cùng 1 file export, đây là dữ liệu
  trùng cần gộp (cộng dồn số lượng) trước khi so sánh ở bước sau — không được bỏ sót hoặc so
  sánh riêng lẻ từng dòng trùng.

### Bước 2 — Chuẩn hoá key đối chiếu (store/vùng)

- Brief và export không dùng chung một mã định danh. Brief thường có các cột tên (Tên hệ thống,
  Tên Ekoin, Tên Campaign, Region/Tỉnh...) còn export dùng supermarket_id/region_id kèm tên
  (Siêu thị/Vùng) viết khác format (hoa/thường, có/không dấu, thứ tự từ, viết tắt, thừa tiền tố
  như "TRUNG TÂM", "SIÊU THỊ"...).
- Phải tự chuẩn hoá (bỏ dấu, upper/lower case, bỏ khoảng trắng thừa, bỏ tiền tố phổ biến) và thử
  match theo NHIỀU cột tên của brief cùng lúc (không chỉ 1 cột), vì tên trong export có thể khớp
  với "Tên Campaign" thay vì "Tên Ekoin" hoặc ngược lại.
- Với mỗi store/region trong export, ghi rõ đã match được với dòng nào trong brief, dựa trên cột
  nào, độ tin cậy match (chắc chắn / gần đúng cần xác nhận). Nếu không match được, liệt kê riêng
  vào danh sách "không xác định được đối tượng trong brief".
- Tương tự, với mỗi dòng brief, xác nhận có tìm thấy trong export hay không; nếu brief có
  store/vùng mà không thấy ở bất kỳ file export nào → đánh dấu "thiếu trong export".

### Bước 3 — Chuẩn hoá danh mục quà (tên quà + ID)

- Gom toàn bộ tên quà (kèm ID nếu có) xuất hiện trong TẤT CẢ file export, và toàn bộ tên cột quà
  trong TẤT CẢ sheet brief.
- Lập bảng mapping tên quà theo ngữ nghĩa (ví dụ "Xe Vision" trong brief có thể là "Xe máy Honda
  Vision" trong export; "Tủ lạnh Inverter" có thể là "Tủ lạnh Toshiba Inverter"; "Máy lọc không
  khí Phillips"/"Philips" là cùng 1 sản phẩm dù chính tả khác) — ghi rõ căn cứ suy luận cho từng
  mapping, không suy đoán ẩu.
- Quà nào trong export KHÔNG tìm được counterpart trong brief (ví dụ các giải phụ như thẻ nạp
  điện thoại, e-voucher, "May mắn lần sau", voucher đối tác, vé sự kiện...) → liệt kê riêng là
  "Quà có trên hệ thống nhưng brief không đề cập" (không tự kết luận là lỗi, chỉ liệt kê để Sale
  xác nhận có nằm trong phạm vi brief này hay thuộc brief/đợt khác).
- Quà nào trong brief không tìm thấy ở bất kỳ file export nào → đánh dấu "thiếu trong export".

### Bước 4 — So sánh số lượng quà theo từng store/vùng

- Với mỗi cặp (store/vùng đã match ở Bước 2) x (quà đã map ở Bước 3), so sánh số lượng brief
  yêu cầu với tổng số lượng đã gộp từ export.
- Không bỏ qua ô trống — số lượng trống ở brief coi là 0 hoặc "không cấp", đối chiếu đúng với
  thực tế trên export (kể cả trường hợp ô trống nhưng export có tặng, hoặc ngược lại).

### Bước 5 — So sánh ngày giờ ra giải

- Brief thường thể hiện ngày giờ ra giải bằng cách gắn giá trị giờ (ví dụ "10:00-11:00") vào
  đúng cột ngày tương ứng cho từng store (ở sheet chứa các cột ngày dạng "13-Thg8", "14-Thg8"...).
- Export thường chỉ có cột "Từ ngày"/"Đến ngày" — trước khi so sánh, phải tự xác minh 2 cột này
  có thực sự thể hiện "ngày giờ ra giải" theo ý brief hay không (kiểm tra giá trị thực tế trong
  toàn bộ file, không chỉ vài dòng đầu). Nếu giá trị không đủ chi tiết để đối chiếu với giờ cụ
  thể trong brief (ví dụ toàn bộ là "0" hoặc chỉ là khoảng ngày chạy chương trình chứ không phải
  giờ quay giải), phải kết luận rõ "Không đủ dữ liệu để đối chiếu ngày giờ ra giải — cần hỏi lại
  Sale/hệ thống field này nằm ở đâu", KHÔNG được tự suy diễn khớp hay không khớp.

### Bước 6 — Với MỖI điểm so sánh, phải nêu đủ 4 phần

1. Brief yêu cầu gì (trích sheet + tên store/quà + giá trị nguyên văn)
2. Export có gì (trích tên file + supermarket_id/region_id + tên cột + giá trị, đã gộp dòng
   trùng nếu có)
3. Kết luận — một trong các trạng thái:
   - Khớp
   - Không khớp (nêu rõ khác nhau chỗ nào, chênh lệch bao nhiêu)
   - Thiếu trong export (brief có, không thấy ở export)
   - Thừa trên export (export có, brief không đề cập)
   - Không đủ dữ liệu để kết luận (cần xác nhận lại)
4. Mức độ rủi ro nếu không khớp (Cao/Trung bình/Thấp) và lý do

### Bước 7 — Tổng hợp cuối

- Bảng chi tiết đầy đủ theo store/vùng x quà (không rút gọn, không bỏ dòng nào dù là "Khớp").
- Bảng riêng cho phần ngày giờ ra giải.
- Danh sách riêng các điểm "Không khớp"/"Thiếu"/"Thừa"/"Cần xác nhận lại", xếp theo mức độ rủi
  ro giảm dần, kèm câu hỏi cụ thể cần hỏi Sale nếu có.
- Cross-check tổng số lượng mỗi loại quà (tổng từ export) với "Grand Total"/"Sum of..." trong
  vùng pivot leftover của brief nếu có, nêu rõ nếu lệch.

### Bước 8 — Ghi báo cáo

- Ghi toàn bộ kết quả (bảng xác nhận bộ file ở Bước 0 + Bước 7) vào
  `<thư mục chạy>/output/report_phan-bo_<slug>_<yyyy-mm-dd>.md` (tạo `output/` nếu chưa có).
  Nếu chạy theo Dạng 2, ghi vào thư mục `output/` cạnh thư mục chứa file brief.
- Trên chat chỉ tóm tắt số điểm Khớp / Không khớp / Thiếu / Thừa / Cần xác nhận, kèm đường
  dẫn file báo cáo.

## Ràng buộc chung

- Không bỏ qua bất kỳ sheet nào của brief hay bất kỳ file/cột nào trong export, kể cả khi số
  lượng nhiều.
- Không tự ý kết luận "Khớp" khi thực tế đang suy đoán tên quà/tên store — nếu match không chắc
  chắn, ghi rõ "cần xác nhận" thay vì đoán.
- Trình bày bằng tiếng Việt, dùng bảng Markdown cho phần so sánh chi tiết.

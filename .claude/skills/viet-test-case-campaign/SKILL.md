---
name: viet-test-case-campaign
description: Cập nhật file test case campaign (Excel) theo đúng yêu cầu của file brief BA (Excel), áp dụng đầy đủ kỹ thuật thiết kế test case (equivalence partitioning, boundary value, decision table, state transition, error guessing...) để đảm bảo độ phủ, giữ nguyên format/màu sắc file test case, xoá kết quả P/F cũ, và xuất theo đúng cấu trúc file template. Dùng khi có 1 file "brief" (.xlsx) và 1 file "test case" (.xlsx) cần đối chiếu rồi cập nhật lại test case.
metadata:
  author: tuyenvo224
  version: "1.0"
---

Bạn là QA đang cập nhật lại bộ test case của một campaign cho khớp với brief BA mới nhất.

## Input

Mỗi lần chạy dùng 1 thư mục riêng, đặt trong `campaign-qc/` ở thư mục gốc của project đang
mở (hướng dẫn cho người dùng xem [README.md](README.md)), theo cấu trúc:

```
campaign-qc/<yyyy-mm-dd>_<ten-campaign>_test-case/
  ├── input/    ← đúng 1 file brief .xlsx + đúng 1 file test case .xlsx
  │               (+ tuỳ chọn 1 file template, tên có chữ "template")
  └── output/   ← file test case đã cập nhật + báo cáo do skill ghi ra
```

Args chấp nhận 1 trong 2 dạng:

- **Dạng 1 (khuyến nghị):** 1 đường dẫn thư mục chạy → lấy file trong `input/` của thư mục
  đó (nếu không có `input/` thì lấy trực tiếp trong thư mục được truyền).
- **Dạng 2:** đường dẫn file, thứ tự bất kỳ: 1 file brief + 1 file test case (+ tuỳ chọn 1
  file template).

Quy tắc bắt buộc khi xác định input:

- Phân loại file: tên có "BRIEF"/"Brief" → brief; tên có "template"/"Template" → template;
  file còn lại (thường dạng `[C] <Tên campaign> (#<id>).xlsx`) → test case.
- Phải có **đúng 1** brief và **đúng 1** test case. Thiếu, thừa, hoặc có file không phân loại
  được → **DỪNG LẠI và hỏi user**. Tuyệt đối không tự tìm file ở thư mục khác để bù vào.
- Template: nếu input không có file template thì dùng template mặc định
  [assets/Template_TCs.xlsx](assets/Template_TCs.xlsx) — đây là file duy nhất trong skill được
  phép dùng, và chỉ dùng làm khung output, không phải dữ liệu.
- **Không bao giờ** dùng file trong `examples/` của skill làm input — đó là dữ liệu giả, chỉ
  minh họa định dạng.
- Trước khi đọc file thật, đọc [references/input-format.md](references/input-format.md) để
  biết cấu trúc brief, file test case (header 2 dòng, cột kết quả P/F) và template. Cấu trúc
  thực tế của file đang xét vẫn là chuẩn.

### Bước 0 — Xác nhận cặp file trước khi cập nhật

Trước khi làm, in ra cho user:

| | File brief | File test case | Template |
|---|---|---|---|
| Đường dẫn | ... | ... | ... (hoặc "mặc định trong skill") |
| Ngày sửa file | ... | ... | ... |
| Tên campaign | (lấy từ sheet `BRIEF`) | (lấy từ ô `Tên màn hình/Tên chức năng`) | — |
| Cột kết quả P/F sẽ xoá | — | (sheet + cột, vd `Test cases!E:P`, `Test on Prd!E`) | — |

- Nếu tên campaign ở brief và test case khác nhau rõ rệt → cảnh báo **"Có thể truyền sai cặp
  file"** và chờ user xác nhận rồi mới làm tiếp.
- Nếu khớp thì ghi "Cặp file hợp lệ" và tiếp tục.

### Định nghĩa các file

- File brief = nguồn yêu cầu nghiệp vụ (ground truth về ý định của Sale/BA cho campaign).
- File test case = bộ test case đang có, có thể đã cũ/lệch so với brief mới nhất, cần cập nhật
  lại nội dung nhưng giữ nguyên toàn bộ format.
- File template = quy định cấu trúc/cột của file output cuối cùng.

## Mục tiêu

Test case sau khi cập nhật phải bám sát 100% nội dung brief, đủ độ phủ theo các kỹ thuật thiết
kế test case chuẩn, không bỏ sót yêu cầu nào của brief và không có test case "mồ côi" (không
bám vào yêu cầu nào trong brief) — đồng thời không làm hỏng format/màu sắc file gốc và không xoá
nhầm dữ liệu.

## Quy trình bắt buộc

### Bước 1 — Đọc & đối chiếu toàn bộ, không tóm tắt vội

- Liệt kê TẤT CẢ sheet trong file brief, đọc kỹ nội dung từng sheet một: cơ cấu giải/quà, điều
  kiện tham gia, thời gian hiệu lực, hotline, quy tắc ưu tiên/override, giới hạn số lượng, luồng
  OTP/OCR nếu có, role/quyền, và mọi ghi chú đặc biệt của BA.
- Liệt kê TẤT CẢ sheet trong file test case hiện có, đọc kỹ từng sheet, xác định rõ cấu trúc cột
  hiện tại (đặc biệt cột nào đang chứa kết quả Pass/Fail).
- Đối chiếu từng yêu cầu trong brief với các test case đang có:
  - Yêu cầu đã có TC tương ứng nhưng mô tả/bước/kết quả mong đợi SAI hoặc CŨ so với brief mới →
    cần sửa lại nội dung.
  - Yêu cầu CHƯA có TC nào → cần bổ sung TC mới.
  - TC đang có nhưng không còn liên quan tới brief mới → liệt kê ra để user xác nhận, KHÔNG tự
    ý xoá.
- Nếu brief có nội dung mập mờ, thiếu, hoặc mâu thuẫn giữa các sheet → liệt kê riêng thành mục
  "Cần hỏi lại BA", không tự suy diễn để viết test case.

### Bước 2 — Áp dụng kỹ thuật thiết kế test case

Khi viết mới hoặc sửa lại mô tả/bước thực hiện/kết quả mong đợi của từng TC, áp dụng các kỹ
thuật sau (chỉ áp dụng kỹ thuật nào phù hợp với nghiệp vụ thực tế của brief, không máy móc áp
hết cho mọi TC):

1. **Equivalence Partitioning** (phân vùng tương đương): với mỗi input (mã supermarket, mã sản
   phẩm, số điện thoại, mã quà...), chia thành nhóm hợp lệ / không hợp lệ, chỉ cần TC đại diện
   cho mỗi nhóm.
2. **Boundary Value Analysis** (phân tích giá trị biên): test tại các mốc biên thời gian (đúng
   giờ bắt đầu/kết thúc campaign, trước/sau mốc đó), số lượng quà (còn 1 suất cuối, hết quà,
   vượt quota), độ dài dữ liệu nhập (min/max ký tự).
3. **Decision Table** (bảng quyết định): dùng khi nhiều điều kiện kết hợp cùng lúc quyết định
   kết quả (ví dụ override vs master code, ưu tiên OCR, điều kiện combo nhiều loại giải) — liệt
   kê đủ tổ hợp điều kiện quan trọng, không chỉ test rời rạc từng điều kiện riêng lẻ.
4. **State Transition** (chuyển trạng thái): với entity có vòng đời trạng thái (đơn hàng, lượt
   quay, mã quà: chưa dùng → đã dùng → hết hạn), test cả chuyển trạng thái hợp lệ lẫn chuyển
   trạng thái KHÔNG được phép.
5. **Positive & Negative Testing**: mỗi luồng chính phải có ít nhất 1 TC hợp lệ (positive) và
   các TC cho input sai/thiếu/định dạng lạ/ký tự đặc biệt nếu có form nhập liệu (negative).
6. **Error Guessing** (đoán lỗi theo kinh nghiệm QA): double-submit, spam-click, thao tác đồng
   thời (concurrency) khi quà sắp hết, sai lệch múi giờ/server time, refresh giữa chừng, mất
   mạng giữa luồng, đổi thiết bị/đổi tài khoản giữa chừng.
7. **Role-based / Permission testing**: nếu có nhiều vai trò (customer, sale, admin, BA...),
   test đúng quyền hạn từng role, và TC cho role KHÔNG được phép truy cập.
8. **Requirement Traceability**: đảm bảo mỗi yêu cầu/mục trong brief map được với ít nhất 1 TC,
   và không có TC không bám vào yêu cầu nào trong brief.
9. **Risk-based prioritization**: TC mới thêm gắn mức ưu tiên theo mức ảnh hưởng nghiệp vụ (TC
   liên quan phát quà/tiền → priority cao).

### Bước 3 — Quy tắc cập nhật file (ràng buộc bắt buộc)

- CHỈ cập nhật nội dung (mô tả, bước test, kết quả mong đợi, dữ liệu test) cho đúng với brief.
  KHÔNG thay đổi format, màu sắc, border, font, độ rộng cột, thứ tự sheet của file test case gốc.
- Xoá kết quả P/F đang có ở cột chứa Pass/Fail — CHỈ xoá sau khi đã xác nhận chắc chắn đó đúng
  là cột kết quả (kiểm tra lại header và nội dung cột trước khi xoá, tránh xoá nhầm cột khác).
- Không tự ý xoá test case, hàng, hoặc sheet nếu không chắc chắn — TC nghi ngờ không còn phù hợp
  phải được đánh dấu và hỏi lại user trước khi xoá.
- Output file phải theo đúng cấu trúc của file template được truyền vào (hoặc mặc định
  `Template_TCs.xlsx` trong skill này).

### Bước 4 — Báo cáo kết quả

Sau khi cập nhật xong, tóm tắt:

- Số TC đã thêm mới / đã sửa nội dung / đã đánh dấu nghi ngờ không còn phù hợp (kèm lý do).
- Danh sách các điểm chưa rõ trong brief cần BA xác nhận (nếu có).
- Đường dẫn file output.

Vị trí ghi file:

- File test case đã cập nhật: `<thư mục chạy>/output/<tên file test case gốc>_updated_<yyyy-mm-dd>.xlsx`
  (tạo `output/` nếu chưa có). **Không ghi đè** file trong `input/`.
- Báo cáo tóm tắt ở trên: `<thư mục chạy>/output/report_test-case_<yyyy-mm-dd>.md`.
- Nếu chạy theo Dạng 2, ghi vào thư mục `output/` cạnh thư mục chứa file brief.

## Ràng buộc chung

- Không bỏ qua bất kỳ sheet nào của brief hay file test case, kể cả sheet trông như phụ trợ.
- Không suy diễn nghiệp vụ khi brief không rõ ràng — luôn liệt kê vào mục cần hỏi lại BA thay vì
  đoán.
- Trình bày báo cáo bằng tiếng Việt.

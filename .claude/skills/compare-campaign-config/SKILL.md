---
name: compare-campaign-config
description: So sánh chi tiết file brief BA (Excel) với file config JSON export từ hệ thống của một campaign, để xác định cấu hình thực tế đã khớp với yêu cầu Sale/BA chưa. Dùng khi cần QC/audit setting campaign trước khi lên PROD, hoặc khi có 2 file "brief" (.xlsx) và "config" (.json) cần đối chiếu.
metadata:
  author: tuyenvo224
  version: "1.0"
---

Bạn là QA đang đối chiếu cấu hình hệ thống thực tế với yêu cầu brief của Sale cho một campaign.

## Input

Mỗi lần chạy dùng 1 thư mục riêng, đặt trong `campaign-qc/` ở thư mục gốc của project đang
mở (hướng dẫn cho người dùng xem [README.md](README.md)), theo cấu trúc:

```
campaign-qc/<yyyy-mm-dd>_<ten-campaign>/
  ├── input/    ← đúng 1 file brief .xlsx + đúng 1 file config .json
  └── output/   ← báo cáo so sánh do skill ghi ra
```

Args chấp nhận 1 trong 2 dạng:

- **Dạng 1 (khuyến nghị):** 1 đường dẫn thư mục chạy, vd
  `campaign-qc/2026-10-03_mini-tet-2` → lấy file trong `input/` của thư mục đó (nếu không
  có `input/` thì lấy trực tiếp trong thư mục được truyền).
- **Dạng 2:** 2 đường dẫn file, theo thứ tự `<file brief .xlsx> <file config .json>`.

Quy tắc bắt buộc khi xác định input:

- Thư mục input phải có **đúng 1** file `.xlsx` và **đúng 1** file `.json`. Thiếu, thừa,
  hoặc không có args → **DỪNG LẠI và hỏi user** đường dẫn cụ thể. Tuyệt đối không tự tìm
  file ở thư mục khác để bù vào.
- **Không bao giờ** dùng file nằm trong `.claude/skills/` làm input. Thư mục
  `examples/` của skill này (`sample_brief.xlsx`, `sample_config.json`) là dữ liệu giả,
  chỉ minh họa định dạng.
- Trước khi đọc file thật, đọc [references/input-format.md](references/input-format.md) để
  biết cấu trúc sheet/header của brief và các khối/key của config (dòng header, sheet ẩn,
  bảng con, key quan trọng). Cấu trúc thực tế của file đang xét vẫn là chuẩn.
- File thật có thể chứa secret (vd `webhook_ekoin_value`), SĐT, email: không trích nguyên
  văn các giá trị này vào báo cáo, chỉ ghi "có giá trị / rỗng / khác nhau".

### Bước 0 — Xác nhận cặp file trước khi so sánh

Trước khi phân tích, in ra cho user:

| | File brief | File config |
|---|---|---|
| Đường dẫn | ... | ... |
| Ngày sửa file | ... | ... |
| Tên campaign | (lấy từ nội dung brief) | `campaign.name` / slug trong JSON |
| Thời gian chạy | (theo brief) | (theo JSON) |

- Nếu tên campaign/slug/thời gian ở 2 file khác nhau rõ rệt → cảnh báo **"Có thể truyền
  sai cặp file"** và chờ user xác nhận rồi mới làm tiếp.
- Nếu khớp thì ghi "Cặp file hợp lệ" và tiếp tục.

### Định nghĩa 2 file

- File brief = nguồn yêu cầu nghiệp vụ (ground truth về ý định của Sale/BA).
- File config = export cấu hình thực tế từ hệ thống (ground truth về những gì đang chạy).

## Mục tiêu

Xác định config trên hệ thống đã khớp 100% với brief hay chưa, không bỏ sót bất kỳ
sheet/trường/thiết lập/nội dung nào ở cả 2 phía.

## Quy trình bắt buộc

### Bước 1 — Đọc toàn bộ, không tóm tắt vội

- Liệt kê TẤT CẢ sheet có trong file brief (kể cả sheet trông như phụ trợ/lịch sử/demo),
  rồi đọc kỹ nội dung từng sheet một. Không mặc định tin nội dung một sheet là đúng cho
  campaign đang xét — đã từng gặp trường hợp sheet chứa dữ liệu leftover/carry-over từ một
  campaign khác (tên chương trình, ngày tháng, giải thưởng không liên quan). Nếu phát hiện
  nghi ngờ dữ liệu bị lẫn từ campaign khác, ghi chú rõ và không dùng làm căn cứ so sánh.
- Đọc toàn bộ file JSON, liệt kê đầy đủ mọi field ở mọi khối (ví dụ các khối thường gặp:
  `campaign` - thông tin chung; `landing_page` - form/game; `campaign_setting` - mảng
  key/display_name/value/status; `take_pic_rule_validation` - rule chụp bill; nhưng cấu trúc
  thật của file đang xét mới là chuẩn, phải tự khám phá chứ không giả định cứng theo ví dụ
  này). Với mảng nhiều phần tử như `campaign_setting`, phải liệt kê hết từng key, không lấy
  mẫu vài dòng rồi suy ra phần còn lại.

### Bước 2 — Lập bảng mapping (brief field <-> config field)

- Vì BA viết bằng ngôn ngữ nghiệp vụ còn JSON là key kỹ thuật, phải tự suy luận mapping hợp
  lý theo ngữ nghĩa (ví dụ: "giới hạn đổi SĐT" trong brief có thể map với
  `landing_page.limit_change_phone`; field liên quan OTP/verify map với `campaign.verify_otp`,
  `notify_by_otp`...). Với mỗi mapping, ghi rõ căn cứ suy luận.
- Field nào trong brief KHÔNG tìm được field JSON tương ứng → đánh dấu "Thiếu trong config /
  cần xác nhận lại vị trí cấu hình".
- Field/key nào trong JSON KHÔNG được brief đề cập → đánh dấu "Setting hệ thống, brief không
  nhắc tới" (không tự suy diễn đây là lỗi, chỉ liệt kê để BA xác nhận có cần khớp không).

### Bước 3 — So sánh chi tiết theo từng nhóm nghiệp vụ, không gộp tắt

Nhóm theo nội dung thực tế có trong 2 file (danh sách dưới là các nhóm thường gặp ở loại
brief/config này — bỏ nhóm nào không tồn tại, thêm nhóm nào brief/config này có mà danh sách
thiếu):

- Thông tin chung campaign: tên/loại/slug/trạng thái, thời gian chạy, domain, hotline,
  Zalo OA, provider, hiển thị kết quả/người thắng, hiển thị landing page.
- Landing page & form đăng ký: field/label/validate trong form, cấu hình game, giới hạn đổi
  số điện thoại, vị trí hiển thị.
- Giải thưởng & tỷ lệ trúng: số lượng, cơ cấu giải, tỷ lệ trúng, phân bổ theo thời gian/kênh.
- Voucher/quà tặng: điều kiện phát, thể lệ, demo.
- OCR/chụp hóa đơn: rule nhận diện, ngưỡng SKU, danh sách siêu thị, QR code.
- Blacklist/Whitelist: số điện thoại/thiết bị bị chặn hoặc được ưu tiên.
- ZNS/SMS/thông báo: nội dung, thời điểm gửi, điều kiện gửi ứng với từng loại notify.
- IVR, phân quyền, scheme chương trình, audit log, T&C: đối chiếu nếu có counterpart trong
  JSON; nếu thuộc phạm vi vận hành/CS không có trong config hệ thống thì ghi rõ "Ngoài phạm
  vi config JSON, không so sánh được" thay vì bỏ qua không nhắc tới.
- Trạng thái bật/tắt (`status`) của từng setting/rule phải đối chiếu với ý định của Sale
  trong brief, không chỉ so giá trị.

### Bước 4 — Với MỖI điểm so sánh, phải nêu đủ 4 phần

1. Brief yêu cầu gì (trích sheet + vị trí/cell hoặc nội dung nguyên văn)
2. Config hiện có gì (trích path JSON cụ thể, ví dụ `campaign_setting[key=...].value`)
3. Kết luận — một trong các trạng thái:
   - Khớp
   - Không khớp (nêu rõ khác nhau chỗ nào)
   - Thiếu trong config (brief có, JSON không thấy field tương ứng)
   - Setting thừa/ngoài brief (JSON có, brief không đề cập)
   - Không đủ dữ liệu để kết luận (brief mô tả mơ hồ, cần hỏi lại BA)
4. Mức độ rủi ro nếu không khớp (Cao/Trung bình/Thấp) và lý do

### Bước 5 — Tổng hợp cuối

- Bảng chi tiết đầy đủ theo từng nhóm ở Bước 3 (không rút gọn, không bỏ dòng nào dù là
  "Khớp").
- Danh sách riêng các điểm "Không khớp" / "Thiếu" / "Cần xác nhận lại BA", xếp theo mức độ
  rủi ro giảm dần, kèm câu hỏi cụ thể cần hỏi Sale/BA nếu có.
- Không tự ý kết luận "Khớp" khi thực tế đang suy đoán — nếu không chắc, ghi "cần xác nhận"
  thay vì đoán.

### Bước 6 — Ghi báo cáo

- Ghi toàn bộ kết quả (bảng xác nhận cặp file ở Bước 0 + Bước 5) vào
  `<thư mục chạy>/output/report_<slug>_<yyyy-mm-dd>.md` (tạo `output/` nếu chưa có).
  Nếu chạy theo Dạng 2 (2 đường dẫn file), ghi vào thư mục `output/` cạnh thư mục chứa
  file brief.
- Trên chat chỉ tóm tắt số điểm Khớp / Không khớp / Thiếu / Cần xác nhận, kèm đường dẫn
  file báo cáo.

## Ràng buộc chung

- Không bỏ qua bất kỳ sheet nào của brief hay bất kỳ key nào trong config, kể cả khi số
  lượng nhiều.
- Không dùng số liệu/giả định từ campaign khác (tên chương trình, mốc thời gian...) — chỉ
  dùng đúng nội dung trong 2 file được truyền vào.
- Trình bày bằng tiếng Việt, dùng bảng Markdown cho phần so sánh chi tiết.

# Format file input — viet-test-case-campaign

Mô tả cấu trúc các file input/output. File mẫu (dữ liệu giả, đúng cấu trúc) nằm ở `../examples/`:
`sample_brief.xlsx`, `sample_test_case.xlsx`. Template output mặc định: `../assets/Template_TCs.xlsx`.
Không dùng file mẫu làm input thật.

Cấu trúc dưới đây lấy từ 1 campaign Scan It thực tế. Campaign khác có thể khác —
**cấu trúc của file đang xét mới là chuẩn**, tài liệu này chỉ để định hướng.

---

## 1. File brief BA (.xlsx)

- Tên file thường dạng: `[<Mã>]<Khách hàng> <Tên CT>_CAMPAIGN SCAN IT_BRIEF BA.xlsx`.
- ~20 sheet, có thể có sheet **ẩn** (vd `AUDIT`) — vẫn phải đọc. Header nhiều sheet không nằm
  ở dòng 1, có ô merge, có bảng con xếp chồng.

| Sheet | Dòng header | Nội dung chính → nhóm test case liên quan |
|---|---|---|
| `BRIEF` | 3 (`STT \| Items \| Mô tả \| Nội dung Sales cần input`), giá trị ở **cột D** | Thông tin chung: thời gian CT/bill/chụp bill, thông báo, điều kiện tham gia, giới hạn lượt/ngày, blacklist, landing page, hotline, các bước tham gia → TC luồng chính, thời gian (biên), giới hạn |
| `Scheme CT` | 2 | Ngưỡng bill theo chuỗi, thời gian, giờ vàng, giới hạn lượt quay → TC scheme (EP/BVA quanh ngưỡng bill), giờ vàng (decision table) |
| `Allocation`, `Prize Rate` | 3–4 | Số lượng giải + tỷ lệ trúng theo chuỗi → TC ra giải, hết giải |
| `Thông tin giải thưởng` | 2 | Giải theo chuỗi + rule limit 1 SĐT/thiết bị/quà → TC giới hạn nhận quà |
| `Quà Lớn`, `Quà AI Voteing` | 8 (dòng 8 từ cột P là ngày) | Phân bổ giải lớn theo store + giờ ra giải → TC giải lớn |
| `STORELIST`, `SKU Threshold` | 7 / 1 | Siêu thị tham gia, ngưỡng giá SKU → TC OCR/duyệt bill |
| `ZNS-SMS` | 1 | Mẫu tin theo từng loại giải, SMS failover → TC thông báo |
| `Blacklist`, `Blacklist k đc tham gia` | 1 / không header | SĐT bị chặn → TC negative nhập SĐT |
| `Phân quyền` | 3 | Tài khoản nhân sự/CS → TC phân quyền |
| `T&C`, `Thể lệ Voucher`, `IVR`, `QR CODE`, `Demo Voucher` | không cố định | Thể lệ, alert email, tổng đài, QR, voucher demo |
| `AUDIT` (ẩn) | 4 | Kết quả audit brief trước đó — tham khảo, không phải yêu cầu |

Lưu ý: nhiều sheet copy từ campaign trước còn sót dữ liệu cũ; giá trị cột D của `BRIEF` hay
ghi "xem sheet X"; công thức có thể ra `#REF!` → đưa vào mục "Cần hỏi lại BA".

---

## 2. File test case hiện có (.xlsx)

- Tên file thường dạng: `[C] <Khách hàng> - <Tên campaign> (#<redmine id>).xlsx`.

### Sheet `Test cases`

- **Khối metadata dòng 1–8** (cột C nhãn, cột D giá trị): `KỊCH BẢN KIỂM THỬ *`,
  `Tên màn hình/Tên chức năng`, `Link spec`, `Link redmine`, `Prototype`; cột G–I: `QC Thực Hiện`,
  `Ngày Tạo`, `Nội Dung`. Ô giá trị có thể gắn **hyperlink**.
- **Header 2 dòng (10–11):**

| Cột | Dòng 10 | Dòng 11 |
|---|---|---|
| A | `STT trường hợp kiểm thử` | |
| B | `Mục đích kiểm thử` | |
| C | `Các bước thực hiện` | |
| D | `Kết quả mong muốn` | |
| E–G | `Trình duyệt` | `Chrome`, `Firefox`, `Edge` |
| H–P | `Device` | `IP 6,7,8`, `IP X`, `Samsung A5`, `Ipad`, … |
| Q | `Kết quả hiện tại` | |
| R | `Mã lỗi` | |
| S | `Ghi chú` | |
| T | `QC thực hiện` | |

- Dữ liệu từ dòng 12. Dòng nhóm dạng `I. <Tên nhóm>`, `II. …` (chỉ có cột A, thường merge).
- **Cột kết quả P/F = E–P** (mỗi trình duyệt/device 1 cột), có data validation `P,F,PE` và
  conditional formatting tô màu. Đây là các cột cần xoá kết quả cũ — xác nhận lại header dòng
  10–11 trước khi xoá. Cột Q (`Kết quả hiện tại`) là mô tả lỗi, không phải P/F.

### Sheet `Test on Prd`

- Header dòng 1: `STT trường hợp kiểm thử | Mục đích kiểm thử | Các bước thực hiện |
  Kết quả mong muốn | Kết Quả (Ekoin) | Mã lỗi | Ghi chú | QC thực hiện`.
- Dòng nhóm `I. User flow` (merge A:C). STT dùng công thức `=A3+1`.
- **Cột kết quả P/F = E**.

---

## 3. Template output (`assets/Template_TCs.xlsx`)

- 1 sheet `TCs`. Metadata dòng 1–7 ở cột E (nhãn) / F (giá trị): `KỊCH BẢN KIỂM THỬ *`,
  `Tên màn hình/Tên chức năng`, `Link spec`, `Link redmine`, `Prototype`, `Domain`, `Account`;
  cột H–J: `QC thực hiện` + tên / ngày / nội dung — **để trống, điền khi xuất file**.
- Header dòng 10: `STT | Mục đích kiểm thử | Precondition | Test data | Các bước thực hiện |
  Kết quả mong muốn | Kết quả hiện tại | Mã lỗi | Ghi chú | QC thực hiện`.
- Dòng nhóm mẫu `I. Group 1` (dòng 12), `II. Group 2` (19), `III. Group 3` (27), merge A:E.
- Cột G (`Kết quả hiện tại`) có data validation `P,F,PE` + conditional formatting.
- Lưu ý: template có cột `Precondition`, `Test data` riêng, còn file test case cũ thì không →
  khi chuyển nội dung sang template phải tách precondition/test data ra khỏi "Các bước thực hiện".

---

## 4. Bảo mật

File thật chứa tên khách hàng, link SharePoint/Redmine/Figma nội bộ, link ảnh bill, SĐT.
**Không commit file thật vào repo**, chỉ đặt trong thư mục chạy `campaign-qc/` (nằm trong
`.gitignore`).

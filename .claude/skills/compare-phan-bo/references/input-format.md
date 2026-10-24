# Format file input — compare-phan-bo

Mô tả cấu trúc file input. File mẫu (dữ liệu giả, đúng cấu trúc) nằm ở `../examples/`:
`sample_brief_phan_bo.xlsx`, `sample_export_supermarket_id.xlsx`, `sample_export_region_id.xlsx`.
Không dùng file mẫu làm input thật.

Cấu trúc dưới đây lấy từ 1 campaign thực tế. Campaign khác có thể khác tên sheet/cột —
**cấu trúc của file đang xét mới là chuẩn**, tài liệu này chỉ để định hướng.

---

## 1. File brief phân bổ (.xlsx) — 1 file

- Tên file thường có chữ `brief` / `Brief` (vd `Brief_phan_bo_sale.xlsx`).
- Thường gồm 2 sheet:

### Sheet `list1` — phân bổ quà theo store/vùng (quà nhỏ/trung)

- **Header ở dòng 1**, dữ liệu từ dòng 2.
- Cột thông tin store: `Group` (INTER / LOCAL / Mini), `Tên hệ thống` (chuỗi), `Code store`,
  `Tên Ekoin`, `Tên Campaign`, `Region`, `Tỉnh cũ`, `Province (New)`.
- Tiếp theo là **mỗi cột 1 loại quà** (vd `Đồng Vàng 0.5 chỉ`, `Bộ Nồi …`, `Voucher … 100k`) —
  giá trị là số lượng; ô trống = không cấp.
- Cột cuối: `Agency`.
- Dòng nhóm `Mini` thường **không có tên store**, chỉ có `Region` → phân bổ theo vùng, đối chiếu
  với file export `region_id`.
- **Vùng pivot leftover** lệch sang phải (từ cột ~Q): `Row Labels`, `Count of …`, `Sum of …`,
  `Grand Total`, xếp thành nhiều bảng con. Không phải dữ liệu gốc — chỉ dùng cross-check tổng.

### Sheet `list2` — giải lớn + ngày giờ ra giải

- **Dòng 1 trống, header ở dòng 2**, dữ liệu từ dòng 3.
- Cột thông tin store giống `list1` (không có `Tỉnh cũ`), tiếp theo là cột giải lớn
  (vd `Xe Vision`, `Tủ lạnh Inverter`, `TV`), `Agency`.
- Sau `Agency` là **các cột ngày** dạng text `13-Thg8`, `14-Thg8`, … — ô của store tại cột ngày
  nào có giá trị giờ (vd `10:00-11:00`) nghĩa là giải ra vào ngày + khung giờ đó.
- **Bảng phụ phía dưới** (cách bảng chính vài dòng trống, bắt đầu ở cột D):
  `HỆ THỐNG | Feedback | Feedback` + thời gian chạy theo từng chuỗi (vd `27/08 - 09/09`).
  Không phải dữ liệu phân bổ store, nhưng dùng để kiểm tra ngày ra giải có nằm trong thời gian
  chạy của chuỗi không.

---

## 2. File export phân bổ (.xlsx) — nhiều file

- Tên file dạng: `danh_sach_phan_bo_<slug-campaign>_<region_id|supermarket_id>_<yyyy_mm_dd_hh_mm_ss>.xlsx`.
- Mỗi file = phân bổ của **1 giải/1 game** (thường tương ứng 1 chuỗi) trên hệ thống. Có thể có
  hơn chục file cho 1 campaign.
- 1 sheet tên `Worksheet`, **header ở dòng 1**.

| Cột | Ý nghĩa |
|---|---|
| `supermarket_id` + `Siêu thị` **hoặc** `region_id` + `Vùng` | Scope phân bổ. Tên siêu thị viết HOA, có thể thêm tiền tố (`TRUNG TÂM MUA SẮM`, `SIÊU THỊ`…), không dấu hoặc khác thứ tự từ so với brief |
| `Từ ngày`, `Đến ngày` | Thực tế thường toàn `0` → không đủ để đối chiếu giờ ra giải |
| `Quantity - <tên quà> - <prize_id>` | Mỗi cột 1 quà; giá trị = số lượng; ô trống = 0. Tên quà thường dài hơn brief (vd `01 Xe máy Honda Vision` vs `Xe Vision`) |

**Lưu ý dễ nhầm:**
- Cùng 1 `supermarket_id` có thể xuất hiện **nhiều dòng** (mỗi dòng 1 quà) → phải cộng dồn.
- Export có thêm quà mà brief không có (thẻ nạp, e-voucher, `May mắn lần sau`, vé sự kiện…).
- Cùng 1 tên quà có `prize_id` khác nhau ở các file khác nhau (mỗi game 1 bộ prize).
- Chính tả khác nhau giữa brief và export (vd `Phillips` vs `Philips`, `E-voucher` vs `E-Voucher`).

---

## 3. Bảo mật

File thật chứa tên khách hàng, danh sách siêu thị, số lượng quà thật. **Không commit file thật
vào repo**, chỉ đặt trong thư mục chạy `campaign-qc/` (đã nằm trong `.gitignore`).

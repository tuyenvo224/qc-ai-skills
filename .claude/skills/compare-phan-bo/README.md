# compare-phan-bo

Skill so sánh file brief phân bổ quà của Sale (.xlsx) với các file phân bổ export từ hệ thống
(.xlsx, mỗi file 1 giải, scope theo `region_id` hoặc `supermarket_id`).
File này hướng dẫn người dùng. Claude làm theo `SKILL.md`.

## Cấu trúc skill

```
.claude/skills/compare-phan-bo/
  ├── SKILL.md      ← hướng dẫn cho Claude
  ├── README.md     ← hướng dẫn cho người dùng (file này)
  ├── references/
  │     └── input-format.md   ← mô tả cấu trúc file brief / export (sheet, header, cột)
  └── examples/     ← file mẫu dữ liệu GIẢ, đúng cấu trúc, KHÔNG dùng làm input
        ├── sample_brief_phan_bo.xlsx
        ├── sample_export_supermarket_id.xlsx
        └── sample_export_region_id.xlsx
```

Muốn biết file cần có dạng gì: đọc `references/input-format.md` hoặc mở các file trong
`examples/`. Toàn bộ dữ liệu trong `examples/` là giả ("CHUỖI A/B/C", quà "DEMO").

## Chuẩn bị dữ liệu

Mỗi lần so sánh dùng 1 thư mục riêng, đặt trong `campaign-qc/` ở thư mục gốc của project:

```
<project>/campaign-qc/
  └── 2026-10-03_mini-tet-2_phan-bo/
        ├── input/    ← 1 file brief + tất cả file export danh_sach_phan_bo_*.xlsx
        └── output/   ← skill tự ghi báo cáo vào đây
```

1. Tạo thư mục `campaign-qc/<yyyy-mm-dd>_<ten-campaign>_phan-bo/input/`.
2. Copy 1 file brief (tên có chữ `brief`) và **tất cả** file export của campaign vào `input/`.
3. Chạy:

   ```
   /compare-phan-bo campaign-qc/2026-10-03_mini-tet-2_phan-bo
   ```

   Hoặc truyền thẳng các file:

   ```
   /compare-phan-bo <file brief .xlsx> <file export 1 .xlsx> <file export 2 .xlsx> ...
   ```

## Skill sẽ làm gì

- Không có brief, có hơn 1 brief, không có file export, hoặc có file không nhận diện được →
  skill dừng lại hỏi, không tự lấy file khác (kể cả file trong `examples/`).
- Trước khi so sánh, skill liệt kê toàn bộ file (loại, scope, số dòng, slug campaign). Nếu slug
  khác nhau hoặc brief có chuỗi không thấy ở export nào, skill cảnh báo "Có thể truyền sai/thiếu
  file" và chờ bạn xác nhận.
- Báo cáo được ghi vào `output/report_phan-bo_<slug>_<yyyy-mm-dd>.md`. Trên chat chỉ hiện tóm tắt.

## Lưu ý khi dùng git

Brief và file export là dữ liệu thật của campaign, không được commit. Thêm dòng sau vào
`.gitignore` của project:

```
campaign-qc/
```

Không đặt file thật vào thư mục skill. Nếu format brief/export thay đổi, tạo lại bản mẫu dữ
liệu giả rồi thay vào `examples/`, sau đó mở kiểm tra không còn dữ liệu thật.

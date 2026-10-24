# viet-test-case-campaign

Skill cập nhật file test case campaign (.xlsx) theo file brief BA (.xlsx) mới nhất, xuất theo
cấu trúc template.
File này hướng dẫn người dùng. Claude làm theo `SKILL.md`.

## Cấu trúc skill

```
.claude/skills/viet-test-case-campaign/
  ├── SKILL.md      ← hướng dẫn cho Claude
  ├── README.md     ← hướng dẫn cho người dùng (file này)
  ├── assets/
  │     └── Template_TCs.xlsx     ← template output mặc định (khung trống, dùng thật)
  ├── references/
  │     └── input-format.md       ← mô tả cấu trúc brief / test case / template
  └── examples/     ← file mẫu dữ liệu GIẢ, đúng cấu trúc, KHÔNG dùng làm input
        ├── sample_brief.xlsx
        └── sample_test_case.xlsx
```

Muốn biết file cần có dạng gì: đọc `references/input-format.md` hoặc mở các file trong
`examples/`. Toàn bộ dữ liệu trong `examples/` là giả (campaign "DEMO 2030", "CHUỖI A/B").

## Chuẩn bị dữ liệu

Mỗi lần chạy dùng 1 thư mục riêng, đặt trong `campaign-qc/` ở thư mục gốc của project:

```
<project>/campaign-qc/
  └── 2026-10-03_mini-tet-2_test-case/
        ├── input/    ← 1 file brief + 1 file test case (+ tuỳ chọn 1 file template)
        └── output/   ← skill ghi file test case đã cập nhật + báo cáo vào đây
```

1. Tạo thư mục `campaign-qc/<yyyy-mm-dd>_<ten-campaign>_test-case/input/`.
2. Copy file brief (tên có chữ `BRIEF`) và file test case `[C] ... (#<id>).xlsx` vào `input/`.
   Muốn dùng template khác mặc định thì copy thêm file template (tên có chữ `template`).
3. Chạy:

   ```
   /viet-test-case-campaign campaign-qc/2026-10-03_mini-tet-2_test-case
   ```

   Hoặc truyền thẳng các file:

   ```
   /viet-test-case-campaign <file brief .xlsx> <file test case .xlsx> [<file template .xlsx>]
   ```

## Skill sẽ làm gì

- Thiếu/thừa file brief hoặc test case → skill dừng lại hỏi, không tự lấy file khác (kể cả
  file trong `examples/`).
- Trước khi cập nhật, skill liệt kê cặp file, tên campaign ở 2 file và các cột P/F sẽ bị xoá.
  Nếu tên campaign khác nhau, skill cảnh báo "Có thể truyền sai cặp file" và chờ bạn xác nhận.
- File test case gốc trong `input/` không bị ghi đè; bản cập nhật và báo cáo nằm trong `output/`.

## Lưu ý khi dùng git

Brief và test case là dữ liệu thật (tên khách hàng, link SharePoint/Redmine/Figma, ảnh bill...),
không được commit. Thêm dòng sau vào `.gitignore` của project:

```
campaign-qc/
```

Không đặt file thật vào thư mục skill. `assets/Template_TCs.xlsx` phải luôn là khung trống —
không để lại tên campaign, người tạo, ngày tạo của lần chạy trước. Nếu format thay đổi, tạo lại
bản mẫu dữ liệu giả rồi thay vào `examples/`, sau đó mở kiểm tra (kể cả hyperlink) không còn
dữ liệu thật.

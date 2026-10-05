# compare-campaign-config

Skill so sánh file brief BA (.xlsx) với file config JSON export từ hệ thống của một campaign.
File này hướng dẫn người dùng. Claude làm theo `SKILL.md`.

## Cấu trúc skill

```
.claude/skills/compare-campaign-config/
  ├── SKILL.md      ← hướng dẫn cho Claude
  ├── README.md     ← hướng dẫn cho người dùng (file này)
  ├── references/
  │     └── input-format.md   ← mô tả cấu trúc file brief / config (sheet, header, key)
  └── examples/     ← file mẫu dữ liệu GIẢ, đúng cấu trúc, KHÔNG dùng làm input
        ├── sample_brief.xlsx
        └── sample_config.json
```

Muốn biết file brief/config cần có dạng gì: đọc `references/input-format.md` hoặc mở 2 file
trong `examples/`. Toàn bộ dữ liệu trong `examples/` là giả (campaign "DEMO 2030", "CHUỖI A/B",
SĐT `09000000xx`).

## Chuẩn bị dữ liệu

Mỗi lần so sánh dùng 1 thư mục riêng, đặt trong `campaign-qc/` ở thư mục gốc của project:

```
<project>/campaign-qc/
  └── 2026-10-03_mini-tet-2/
        ├── input/    ← đúng 1 file brief .xlsx + đúng 1 file config .json
        └── output/   ← skill tự ghi báo cáo vào đây
```

1. Tạo thư mục `campaign-qc/<yyyy-mm-dd>_<ten-campaign>/input/`.
2. Copy file brief (.xlsx) và file config (.json) vào `input/`.
3. Chạy:

   ```
   /compare-campaign-config campaign-qc/2026-10-03_mini-tet-2
   ```

   Hoặc truyền thẳng 2 file:

   ```
   /compare-campaign-config <file brief .xlsx> <file config .json>
   ```

## Skill sẽ làm gì

- `input/` thiếu hoặc thừa file thì skill dừng lại hỏi, không tự lấy file khác (kể cả file trong `examples/`).
- Trước khi so sánh, skill kiểm tra tên campaign và thời gian chạy ở 2 file. Nếu khác nhau,
  skill cảnh báo "Có thể truyền sai cặp file" và chờ bạn xác nhận.
- Báo cáo được ghi vào `output/report_<slug>_<yyyy-mm-dd>.md`. Trên chat chỉ hiện tóm tắt.

## Lưu ý khi dùng git

Brief và config là dữ liệu thật của campaign (SĐT, họ tên, email, secret webhook...), không
được commit. Thêm dòng sau vào `.gitignore` của project:

```
campaign-qc/
```

Không đặt file thật vào thư mục skill. Nếu cần cập nhật file mẫu khi format brief/config thay
đổi, tạo lại bản ẩn danh rồi thay vào `examples/`, sau đó mở kiểm tra không còn dữ liệu thật.

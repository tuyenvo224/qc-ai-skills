---
name: markdown-to-excel
description: Khi người dùng yêu cầu chuyển đổi file markdown (.md) sang file Excel (.xlsx), đặc biệt các file chứa bảng markdown (test case, danh sách dữ liệu...)
metadata:
  author: tuyenvo224
  version: "1.0"
---

# VAI TRÒ
Bạn là trợ lý chuyển đổi định dạng tài liệu, chuyên chuyển các bảng Markdown (test case, danh sách, dữ liệu...) thành file Excel (.xlsx) có định dạng rõ ràng, dễ đọc.

# NHIỆM VỤ
Chuyển 1 file `.md` (có thể chứa nhiều bảng markdown) thành 1 file `.xlsx`, mỗi bảng markdown → 1 sheet Excel.

# CÁCH THỰC HIỆN
1. Xác định file markdown nguồn:
   - Nếu người dùng đã chỉ rõ đường dẫn/tên file, dùng đúng file đó.
   - Nếu không rõ và có nhiều file `.md` khả nghi (vd trong `test-case-can-review/`, `test-cases/`, `mindmap/`), hỏi lại người dùng thay vì tự đoán.
2. Chạy script có sẵn để convert, KHÔNG tự parse/gõ lại bảng bằng tay:
   ```
   python .claude/skills/markdown-to-excel/scripts/md_to_xlsx.py "<input.md>" "<output.xlsx>"
   ```
   - Tham số `output` là tùy chọn. Nếu người dùng không chỉ định nơi lưu, bỏ qua tham số này — script sẽ tự lưu output cùng thư mục với file nguồn, cùng tên, đổi đuôi thành `.xlsx`.
3. Script tự động xử lý:
   - Mỗi bảng markdown (`| ... |`) trong file → 1 sheet riêng. Tên sheet lấy theo heading (`##`, `###`...) đứng ngay trước bảng; nếu file chỉ có 1 bảng và không có heading, dùng tên file làm tên sheet.
   - Dòng header: in đậm, nền màu xanh, chữ trắng, có freeze pane + auto-filter.
   - `<br>` trong ô → xuống dòng trong cell; markdown syntax (`**bold**`, `` `code` ``, `[text](link)`) được làm sạch trước khi ghi.
   - Độ rộng cột tự co giãn theo nội dung (tối đa 60).
   - Nếu file `.md` không chứa bảng nào, toàn bộ nội dung văn bản được ghi vào 1 sheet, mỗi dòng 1 row.
4. Sau khi script chạy xong, báo cho người dùng đường dẫn file Excel vừa tạo.

# YÊU CẦU MÔI TRƯỜNG
- Cần Python 3 và thư viện `openpyxl`. Nếu lệnh báo thiếu module, chạy `python -m pip install openpyxl` rồi thử lại.

# LƯU Ý
- Luôn dùng script `md_to_xlsx.py` để convert, không tự tay dựng lại bảng trong Excel — tránh sai sót/tốn thời gian khi bảng dài nhiều dòng.
- Nếu file có nhiều bảng liên tiếp không có heading riêng, các sheet sẽ tự đặt tên `Table1`, `Table2`, ...

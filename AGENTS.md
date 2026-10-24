# AGENTS.md

## Quy tắc quan trọng

- Luôn trình bày những việc sẽ làm cho yêu cầu của tôi, sau đó chờ tôi xác nhận rồi mới bắt đầu thực hiện.
  - Ngoại lệ: skill `tong-hop-spec-artifact` và `tong-hop-ta-db-artifact` chạy thẳng từ link tới link artifact, không cần hỏi xác nhận.
  - Ngoại lệ: skill `log-bug-redmine` chạy thẳng từ mô tả lỗi tới bug report (tiêu đề + nội dung để tự copy lên Redmine), không cần hỏi xác nhận.
- Không ghi token, API key, mật khẩu thật vào skill, script hay file output; key đọc từ thư mục `connect-key/` (không commit).
- Spec, test case, brief và báo cáo có thể chứa URL/thông tin nội bộ — không gửi ra dịch vụ bên ngoài.

## Quy tắc riêng trên máy cá nhân

Nếu có file `CLAUDE.local.md` ở thư mục gốc (không commit), áp dụng thêm các quy tắc trong đó, vd: cách kết nối hệ thống nội bộ (Redmine / BookStack / GitLab / SharePoint) để đọc spec từ link.

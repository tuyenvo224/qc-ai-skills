# tong-hop-ta-db-artifact

Đọc tài liệu TA / technical design trên GitLab (`/-/tree/…` hoặc `/-/blob/…`) và xuất **một trang artifact cho QA**: flow nghiệp vụ đi qua bước nào, mỗi bước lưu hoặc đổi dữ liệu ở table nào (cột, giá trị), SQL gợi ý để kiểm tra, ý nghĩa trạng thái, con số cần test. Chỉ đọc các file TA trong link.

Gọi: `/tong-hop-ta-db-artifact <link thư mục TA>`

**Bắt buộc cài kèm** skill `tong-hop-spec-artifact`, vì skill này dùng script `fetch_spec.py` và `append_link.py` của skill đó. Hướng dẫn cài đặt, cách chuẩn bị `connect-key/`, yêu cầu môi trường và vị trí output: xem [`../tong-hop-spec-artifact/README.md`](../tong-hop-spec-artifact/README.md).

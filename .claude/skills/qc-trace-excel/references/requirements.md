# Yêu cầu của file Excel (chốt với user 27–28/09/2026)

Mọi mục dưới đây được `scripts/verify_excel.py` kiểm lại sau mỗi lần xuất. Mục có ký hiệu (M) là kiểm bằng mắt, không tự động được.

## Chung
- E1: Dựng trên file mẫu của team, đi kèm skill tại `assets/Template_TCs.xlsx`, nên copy skill sang máy khác vẫn dùng được. Không sửa file mẫu gốc.
- E2: Thứ tự sheet là **Ghi chú → TCs → Ma trận FRD → Test flow → Tóm tắt**, và mở file thì vào sheet Ghi chú.
- E3: Mọi con số được tính từ dữ liệu của report (`data.json`, `qc-cases.csv`), không ghi cứng.
- E4: Mọi ô có nhiều chữ đều hiển thị đủ. Chiều cao dòng được tính theo nội dung, và không dòng nào vượt 409pt. Case quá dài thì tách sang dòng `… (tiếp n)`.
- E5: Trước khi ghi đè file cũ, lưu bản `*_backup.xlsx`. Nếu file đang mở trong Excel thì dừng và báo đóng file.
- E6: Chỉ đọc repo dev, BookStack và Redmine. Không ghi gì lên đó.
- E7: Dùng thống nhất cách gọi "yêu cầu FRD (R-xxx)", không gọi là "dòng FRD".

## Sheet TCs
- T1: Header lấy theo mẫu: tên chức năng kèm mã Redmine, link FRD, link Redmine, phiên bản FRD, ngày xuất.
- T2: Mỗi dòng là một case: **TC, SEC, E2E**. Case đã rút (withdrawn) không đưa vào. TF nằm ở sheet riêng.
- T3: Cột A–J đúng như mẫu: STT, Mục đích, Precondition, Test data, Các bước, Kết quả mong muốn, Kết quả hiện tại (dropdown P/F/PE), Mã lỗi, Ghi chú, QC thực hiện.
- T4: Thêm cột **K Có test được?** (có màu), **L Yêu cầu FRD liên quan**, **M Nguồn (file:dòng)**.
- T5: Gom case theo **Nhóm chức năng** (tên tiếng Việt), xếp theo thứ tự FRD. Tiêu đề dạng `I. <tên> (N case)`, **không ghi làn**. Nhóm cuối là "Tính năng ngoài FRD (BA tự thêm)".
- T6: Cột K đánh giá **theo từng case**, dựa trên trạng thái code của đúng các yêu cầu FRD mà case kiểm. Giá trị là ✅ / ⚠ (kèm giả định A-*) / ⏸ / ⛔.
- T7: Mã phần tử `EL-xx` được chèn tên phần tử lấy từ ui-contract. Bỏ ký hiệu markdown. Bảng Expected chuyển thành các dòng `• … → …`.
- T8: Không lặp bảng giữa Test data và Kết quả mong muốn.
- T9: **Không freeze** sheet TCs.
- T10: Không case nào để trống ô Các bước hoặc Kết quả mong muốn.

## Sheet Ma trận FRD
- X1: Đủ **mọi** yêu cầu FRD của report, bằng số dòng trong `data.json`.
- X2: Có các cột R · **Nhóm chức năng** · **Mã yêu cầu** · Mục FRD · Loại · Trích nguyên văn · BA · BA IDs · Chênh lệch BA · TA · TA IDs · Chênh lệch TA · Case QC · Case test được ngay · Tình trạng test.
- X3: Ô Case QC có link nhảy tới case đầu tiên ở sheet TCs. Mọi link đều trỏ đúng dòng của case đó.
- X4: Có bộ lọc, freeze dòng tiêu đề, và tô màu theo trạng thái BA/TA.

## Sheet Test flow · Tóm tắt
- F1: Đủ mọi TF, mỗi TF liệt kê các bước kèm case cần chạy.
- S1: Sheet Tóm tắt có số liệu theo cột K, danh sách case đã rút, và các câu hỏi cần PO chốt.

## Sheet Ghi chú
- G1: Giới thiệu file và nguồn dữ liệu (kèm phiên bản FRD), ngày xuất, skill đã sinh ra file.
- G2: Vai trò từng sheet và thứ tự nên dùng.
- G3: Định nghĩa **yêu cầu FRD (R-xxx)**, các quy tắc tách, các mục không sinh yêu cầu, và ví dụ thật lấy từ FRD.
- G4: Ý nghĩa mọi cột của sheet TCs và sheet Ma trận.
- G5: Ý nghĩa các giá trị trạng thái (cột K; Đủ / Một phần / Lệch / Thiếu / N/A) và việc cần làm với mỗi giá trị.
- G6: Cách đọc đúng. Tối thiểu phải có: yêu cầu nào chưa có case (kèm số lượng); case kiểm những yêu cầu nào; yêu cầu có những case nào; vì sao số yêu cầu nhiều hơn số case (quan hệ nhiều–nhiều); vì sao không gộp yêu cầu trùng; case ngoài FRD; dòng "(tiếp)"; case đã rút; cần kiểm gì trước khi log bug.
- G7: Bảng tra mã tiền tố, và bảng mã ENT → tên bảng DB nếu có tài liệu TA.
- G8: Lưu ý khi dùng: xuất lại sẽ ghi đè file, dữ liệu DB, việc cần làm khi PO chốt nguồn chuẩn, lưu ý riêng của dự án (`narrative.json` → `excel_notes`), và giới hạn của việc đánh giá bằng AI.

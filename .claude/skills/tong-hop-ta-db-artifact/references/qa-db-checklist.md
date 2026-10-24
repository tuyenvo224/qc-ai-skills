# Checklist: tài liệu TA → report DB cho QA

Người đọc là **QA**, không phải DEV. Mỗi câu phải trả lời được một trong ba câu hỏi: *người dùng làm gì*, *màn hình hiện gì*, *DB đổi gì*. Câu nào không phục vụ ba câu hỏi này thì bỏ.

## Quy tắc viết

- Tiếng Việt, câu ngắn. Giữ nguyên **tên table, tên cột, giá trị status, tên API, mã message** như TA; đặt trong `<code>`.
- Giải thích thuật ngữ **ngay lần đầu** xuất hiện: `suppressed` = *tạm khóa quyền tự đăng nhập*; `active_account_id = NULL` = *phiên đã kết thúc*.
- Hạn chế mã ID của TA (TD-, BR-, SEQ-, NFR-, CF-…). Chỉ giữ tên API (`API-001 POST /auth/verify`) và tên event nếu nó là một dòng trong table audit.
- Không bịa. TA không ghi rõ mà phải suy ra thì gắn `❓` và đưa vào mục 6 nếu ảnh hưởng tới việc test.
- TA nhắc tới feature khác: ghi *(theo TA)*, không đọc thêm file nào.
- **Độ dài:** phần sau `</style>` khoảng ≤ 380 dòng. Mỗi flow tối đa khoảng **8 bước chính**. Nhánh lỗi gom vào một bảng nhỏ. Vượt giới hạn thì rút gọn theo thứ tự ở SKILL.md Bước 3.
- **Mã ID:** trong nội dung chỉ giữ tên API. Cột "Ở đâu trong TA" ở mục 6 **được** ghi vị trí đầy đủ (`design.md §4.2`, `AC-114`) để QA tra ngược.
- **TA tự mâu thuẫn** (hai chỗ, hoặc ngay trong một câu, nói khác nhau): không tự chọn. Trình bày theo chỗ chính (bảng API / sequence), gắn `❓`, rồi đưa vào mục 6 kèm cả hai vị trí.

## Nhãn table (dùng thống nhất ở mục 1 và mục 4)

| Nhãn | Pill | Khi nào |
|---|---|---|
| `mới` | `p-new` | Bảng mới do feature này tạo |
| `sửa schema` | `p-change` | Feature này thêm hoặc đổi cột / enum của bảng đang có |
| `ghi thêm` | `p-info` | Không đổi schema, nhưng feature này ghi hoặc đổi giá trị |
| `chỉ đọc` | `p-read` | Feature này chỉ đọc. Kể cả khi TA ghi `change` mà việc đổi thuộc feature khác: ghi `chỉ đọc` + *(sửa schema do FEAT-xxx, theo TA)* |

Không tin tuyệt đối vào nhãn `new` / `change` / `reuse` của TA hay của `extract_ta.py`. Đọc mô tả table rồi chọn nhãn theo bảng trên.

## 1 · Tóm tắt

- **2–3 câu:** tính năng làm gì, bắt đầu ở đâu, kết thúc ở đâu.
- **Stat:** số flow, số table liên quan, cộng 2 con số quan trọng nhất (ví dụ "60 phút idle", "14 ngày ghi nhớ").
- **Danh sách table:** mỗi table một dòng, gồm tên, nhãn `mới` / `sửa` / `chỉ đọc`, và vai trò bằng lời thường ("mỗi lần đăng nhập thành công = 1 dòng").

## 2 · Bản đồ flow tổng

- **Một** sơ đồ `flowchart LR` hoặc `TD` nối các flow theo hành trình của người dùng (ví dụ: Đăng nhập → Đang dùng → Hết phiên → Mở lại app).
- Mỗi node ghi tên bước và các table bị ghi. Không quá khoảng 14 node.
- Dưới sơ đồ là danh sách link nhảy tới từng flow ở mục 3.

## 3 · Từng flow

Mỗi flow là một `<section class="flow">`:
1. **Tiêu đề + 1 câu:** khi nào xảy ra, API nào.
2. **Bảng các bước chính** (happy path), 5 cột: `# · Người dùng làm gì · Hệ thống kiểm tra / xử lý · Thấy gì trên màn hình · DB thay đổi`.
   - Cột **DB thay đổi** dùng op-chip: `<span class="op op-i">+</span>` thêm dòng, `<span class="op op-u">~</span>` sửa, `<span class="op op-r">đọc</span>` chỉ đọc. Kèm `table.cột = giá trị`.
   - Bước không đổi DB thì ghi `—`.
   - Nhiều thao tác trong cùng một transaction thì ghi "*(cùng 1 transaction: lỗi là không lưu gì)*".
3. **Bảng nhánh lỗi / nhánh rẽ**, 4 cột: `Tình huống · Thấy gì (message / mã) · DB thay đổi · Ghi chú`. Gom các nhánh giống nhau. Flow chỉ có ≤ 1 nhánh thì bỏ bảng, ghi 1 câu.
4. **SQL gợi ý** (`<pre class="sql">`): 1–3 câu `SELECT` để QA kiểm DB sau khi chạy flow. Flow chỉ đến từ event của feature khác thì SQL là tùy chọn.
   - Chỉ dùng tên table/cột **có khai báo trong TA**. Không giả định cột `id` / `created_at` nếu bảng cột của TA không ghi. Để sắp xếp, dùng cột thời gian có thật (`issued_at`, `occurred_at`…).
   - Tham số để dạng `:account_id`, `:device_ref`.
   - Luôn có dòng comment đầu `-- Gợi ý, dựng từ tên cột trong TA; kiểm lại schema thật`.
   - **Chỉ SELECT**, không bao giờ UPDATE/DELETE.
   - Giá trị thật của một cột (ví dụ `event_code`) không được TA liệt kê: ghi mã TA (`EVT-008`) kèm `❓` và đưa vào mục 6.
5. Ví dụ mốc thời gian (chỉ khi flow có thời hạn): `.timeline` ngắn. Nếu tự dựng từ công thức TA thì ghi "(dựng từ công thức TA)".

Các flow thường có (chọn theo TA, đặt theo thứ tự hành trình người dùng):
- luồng chính;
- luồng vào lại (auto login, resume);
- luồng mỗi request khi đang dùng;
- hết hạn / timeout;
- sự kiện từ feature khác (ví dụ đổi mật khẩu);
- hai thao tác cùng lúc.

## 4 · Tra cứu table

Mỗi table (đủ mọi ENT ở `== 4` của script) là một thẻ `.card`. Table phụ (chỉ đọc, hoặc chỉ ghi 1–2 cột) được dùng **thẻ rút gọn**: tên + nhãn + 1 đoạn văn. Script báo `⚠ không có bảng cột` (TA mô tả bằng bảng giá trị / mapping) thì lấy các cột từ bảng đó của TA; không có thì dùng thẻ rút gọn. Thẻ đầy đủ gồm:
- Tên, nhãn (`mới` / `sửa` / `chỉ đọc`), vai trò 1 câu.
- **Cột QA cần nhìn**, chỉ khoảng 3–8 cột: khóa để tìm dòng, `status`, các mốc thời gian, cờ, lý do. Bỏ digest, hash, correlation_id… trừ khi QA cần để tìm dòng.
- **Chuỗi trạng thái** (nếu có cột status) dạng `.chain`: `valid → (idle 60 phút) → suppressed → (đăng nhập lại) → invalidated`, kèm một dòng giải thích từng giá trị.
- Table chỉ đọc: một dòng "được đọc ở bước nào, để làm gì".
- Dữ liệu **không nằm trong DB** mà QA cần biết khi test (cookie, localStorage, sessionStorage, IndexedDB, header): gom vào một note cuối mục.
- Dữ liệu được ghi mà TA **không cấp ENT** (role mặc định, budget, bảng nối, bản ghi qua port của feature khác): ghi 1 dòng *(theo TA)* trong note cuối mục và ở bước tương ứng của mục 3, không làm thẻ.

## 5 · Ràng buộc và con số để test

- **Ràng buộc DB ép** (unique index…) viết thành câu kiểm được: "Mỗi Account tối đa 1 dòng `login_sessions` có `active_account_id` khác NULL".
- **Con số:** thời hạn, giới hạn, TTL, kèm giá trị và nơi lưu (`remember_logins.expires_at = lúc đăng nhập + 14 ngày`).
- **Message thấy trên UI ↔ mã ↔ tình huống:** bảng gọn 3 cột `Tình huống · Hiển thị (data-msg-code / chữ) · HTTP · mã số` (HTTP và mã gộp một ô, ví dụ `401 · 100100011`).
- **Môi trường test** (chỉ khi TA có ghi): cấu hình rút ngắn cho môi trường test (ví dụ TTL 5s), tài khoản hạt giống, mock của hệ thống ngoài, và AC chỉ test được ở tầng INT / không test được trên môi trường deploy. Ghi thành danh sách ngắn dưới tiêu đề `<h4>Môi trường test</h4>`.

## 6 · Điểm chưa rõ (tối đa 8)

- Chỉ ghi những chỗ **làm QA không biết kết quả mong đợi**: TA im lặng, hai chỗ trong TA nói khác nhau, hoặc tên cột dùng mà không khai báo.
- Mỗi dòng gồm câu hỏi bằng lời thường, lý do ảnh hưởng tới test, và vị trí trong TA (`design.md §4.2`).
- Xếp theo mức ảnh hưởng. Không liệt kê lỗi biên tập thuần túy (đánh số sai, câu lặp).

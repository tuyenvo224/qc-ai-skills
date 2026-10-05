---
name: tong-hop-ta-db-artifact
description: Dành cho QA. Nhận link tài liệu TA / technical design (thường là thư mục GitLab `technical-design/...` gồm analysis.md, design.md, ui-contract.md; hoặc 1 file TA), CHỈ đọc các file TA trong link đó, rồi tổng hợp NGẮN GỌN, DỄ HIỂU cho QA: nghiệp vụ đi từ bước nào tới bước nào và mỗi bước LƯU / ĐỔI DỮ LIỆU Ở TABLE NÀO của DB (cột nào, giá trị gì), kèm câu SQL gợi ý để kiểm tra, ý nghĩa các trạng thái, con số cần test và vài điểm chưa rõ — xuất thành MỘT TRANG ARTIFACT HTML và trả về LINK. Chạy thẳng từ link tới link artifact, KHÔNG hỏi xác nhận. Trigger trên các câu như "tổng hợp TA này cho QA", "logic nghiệp vụ lưu vào table nào của DB", "flow này ghi vào bảng nào", "/tong-hop-ta-db-artifact <link>". KHÔNG dùng cho spec nghiệp vụ của PO/BA (FRD/PRD/user story) — việc đó thuộc skill `tong-hop-spec-artifact`.
metadata:
  author: tuyenvo224
  version: "1.0"
---

# Tổng hợp TA → report DB cho QA

**Người đọc là QA.** Họ cần hiểu: người dùng làm gì → hệ thống kiểm tra gì → màn hình hiện gì → **DB thay đổi ở table nào, cột nào, thành giá trị gì**, và kiểm tra DB bằng cách nào. Report phải **ngắn, dễ đọc**. Không phải bản review kỹ thuật cho DEV/TA.

**Input:** link TA (GitLab thư mục `/-/tree/…` hoặc file `/-/blob/…`). **Output:** link artifact claude.ai kèm tóm tắt ngắn.

> **Ngoại lệ với AGENTS.md:** người dùng đã chốt rằng skill này **không** trình bày kế hoạch và **không** chờ xác nhận. Chạy thẳng hết 5 bước. Chỉ dừng lại khi gặp lỗi xác thực hoặc không lấy được nội dung.

Mọi đường dẫn tính từ **thư mục gốc project** `$ROOT`: thư mục chứa `.claude/` và `connect-key/`, thường là working directory của Claude Code. Skill này **cần cài cùng** skill `tong-hop-spec-artifact` (dùng chung script lấy tài liệu và script ghi link). Đầu mỗi lần chạy, đặt biến bằng bash:

```bash
ROOT="$(pwd -W 2>/dev/null || pwd)"; [ -d "$ROOT/.claude" ] || echo "⚠ không thấy .claude/ trong $(pwd), cd về gốc project"
SKILL="$ROOT/.claude/skills/tong-hop-ta-db-artifact"
SHARED="$ROOT/.claude/skills/tong-hop-spec-artifact/scripts"   # fetch_spec.py, append_link.py
FETCH="$SHARED/fetch_spec.py"
OUT="$ROOT/spec-summary/ta-db"
mkdir -p "$OUT"
[ -f "$FETCH" ] || echo "⚠ thiếu skill tong-hop-spec-artifact (cần cài kèm)"
```

## Phạm vi (bắt buộc)

- **Chỉ đọc các file TA nằm trong link được đưa vào.** Không tải BA nguồn, FRD, TA của feature khác, file `ui-contract-common.md` hay bất kỳ file nào được TA dẫn link tới, kể cả khi người dùng gửi kèm link khác. Người dùng muốn đối chiếu nghiệp vụ thì đó là việc khác, ngoài skill này.
- TA nhắc tới feature khác (ví dụ "do FEAT-003 ghi"): chỉ ghi lại đúng lời TA, gắn nhãn *(theo TA)*.
- **Không đưa vào report:** xung đột với sourcebase (CF), migration và thứ tự deploy, rủi ro kỹ thuật (RSK), danh sách index đầy đủ, ERD, hợp đồng API chi tiết, service worker / cách hiện thực FE, lịch sử các bản sửa của TA, bảng truy vết mã ID. Chỉ lấy từ những phần đó các **sự thật QA test được** (ví dụ "mỗi Account chỉ có 1 dòng `active`", "hạn 14 ngày không đổi khi auto login").
- Người dùng đưa link spec PO/BA: báo đây là việc của `tong-hop-spec-artifact`.

## Bước 1 · Lấy tài liệu TA

```bash
python "$FETCH" "<link TA>" "<scratchpad>/<slug>"
```
- Script tự đọc token trong `$ROOT/connect-key/` (hoặc `--config-dir`, hoặc biến `CONNECT_KEY_DIR`), không in token ra. Định dạng file key xem `README.md` của skill. Link thư mục thì tải **mọi file** trong thư mục vào `files/`, ghép vào `spec.txt` với marker `# FILE: <path>`. `source.json` có `last_commit` (sha, ngày).
- **Exit code 3 / `AUTH_ERROR`**: báo token có thể đã hết hạn, rồi dừng. Không thử lại liên tục.
- Ảnh **trong** thư mục (`image: true`): mở bằng Read nếu là sơ đồ luồng / schema. Ảnh nằm ngoài thư mục: không tải.

## Bước 2 · Đọc kỹ và quét

1. Đọc **toàn bộ** `spec.txt` bằng Read, theo từng đoạn cho tới dòng cuối. File lớn (hơn 25k token) thì đọc lần lượt theo marker `# FILE:`. Có thể đọc thẳng từng file trong `files/`. Đọc kỹ nhất các phần: entity / data model (cột, giá trị status), sequence (`SEQ-*`), bảng "việc BE làm" của từng API, state machine, handler event, message code, cấu hình (các con số).
2. Chạy script để có danh sách đủ, không đếm tay và không sót table:
   ```bash
   python "$SKILL/scripts/extract_ta.py" "<scratchpad>/<slug>/spec.txt" --json "<scratchpad>/<slug>/ta.json"
   ```
   Dùng các mục: `== 1 STAT` (số table, API còn hiệu lực), `== 4` (ENT → table → cột), `== 7` (khóa cấu hình, mã message). Các cảnh báo `⚠` chỉ là gợi ý cho mục "Điểm chưa rõ", và chỉ đưa vào khi ảnh hưởng tới việc test. Số dòng trong cảnh báo `[design.md:267]` là số dòng **trong file đó** (`files/design.md`), không phải trong `spec.txt`.
3. Bóc tách theo **[references/qa-db-checklist.md](references/qa-db-checklist.md)**, gồm 6 mục.

## Bước 3 · Dựng HTML

- Tạo thư mục output nếu chưa có, rồi copy template:
  ```bash
  mkdir -p "$OUT" && cp "$SKILL/assets/template.html" "$OUT/<slug>.html"
  ```
  `<slug>` = `feat-xxx-<tên-thư-mục>`, ví dụ `feat-001-login`.
- Mẫu hoàn chỉnh: `$SKILL/assets/example-login-qa.html` (FEAT-001, khoảng 450 dòng). Học **độ dài và giọng văn**, không copy nội dung.
- Giữ nguyên `<style>` và token màu light/dark, không thêm màu literal. Trang artifact tự render `<pre class="mermaid">`, không load thư viện. Label mermaid: **được dùng `<br/>`** để xuống dòng, ngoài ra không dùng `<` `>` hay dấu `"` bên trong label, và không dùng node `{{…}}`.
- `<title>`: `FEAT-xxx <Tên ngắn> QA DB Map`.
- **Giới hạn độ dài:** phần **sau `</style>` khoảng ≤ 380 dòng**; phần style cố định khoảng 95 dòng không tính. Vượt thì làm lần lượt:
  1. gộp các nhánh lỗi giống nhau;
  2. flow chỉ có ≤ 1 nhánh thì bỏ bảng nhánh, ghi thành 1 câu;
  3. table phụ dùng **thẻ rút gọn** (1 đoạn văn, không có bảng cột);
  4. gộp flow nhỏ vào flow gần nhất (ví dụ "hai thao tác cùng lúc" gộp vào flow chính).
- Tự kiểm tra (bắt buộc chạy):
  ```bash
  f="$OUT/<slug>.html"
  grep -c "{{" "$f"                     # phải = 0
  for t in div table tr pre; do echo "$t $(grep -o "<$t[ >]" "$f" | wc -l)/$(grep -o "</$t>" "$f" | wc -l)"; done
  sed -n '/<\/style>/,$p' "$f" | grep -nE '#[0-9a-fA-F]{6}\b|rgb\(' | head   # phải rỗng
  python "$SKILL/scripts/extract_ta.py" "<scratchpad>/<slug>/spec.txt" --check-html "$f" | sed -n '/CHECK HTML/,$p'
  # → số dòng sau </style>, mọi ENT có ở mục 3 và mục 4, SQL chỉ SELECT
  ```

## Bước 4 · Publish

- Đọc `$OUT/registry.json` (map `link TA → {artifact, file, …}`), nếu chưa có file thì coi là `{}`.
  - **Đã có link:** gọi `Artifact` `action: "read"` với `url` đó, sau đó publish `file_path = $OUT/<slug>.html` với cùng `url` để giữ nguyên link. `label` = sha commit TA.
  - **Mới:** publish với `icon: "database"` và `description` một câu: "Flow nghiệp vụ FEAT-xxx … đi qua những bước nào và lưu vào table DB nào — bản cho QA, tổng hợp từ tài liệu TA."
- Ghi registry: `{ "<link TA>": {"artifact": "<url>", "file": "<slug>.html", "spec_updated_at": "<ngày> (<sha>)", "published_at": "<today>", "audience": "qa"} }`. Skill dùng file này để tìm link cũ.
- **Ghi link vào file tracking** (bắt buộc, cả khi tạo link mới lẫn khi cập nhật đè link cũ):
  ```bash
  python "$SHARED/append_link.py" \
    --skill tong-hop-ta-db-artifact --feature "FEAT-xxx <Tên> (TA <thư mục>)" --url "<link artifact>"
  ```
  Script ghi vào `$ROOT/artifact-links/tong-hop-ta-db-artifact.md` (tự tạo thư mục) (Ngày giờ xuất · Tính năng · Link artifact, giờ VN). **Mỗi link chỉ 1 dòng**: link đã có thì dòng cũ được cập nhật giờ xuất + tính năng và chuyển xuống cuối bảng. Dùng tên tính năng **ổn định** giữa các lần chạy, không gắn sha hay số bản. Lỗi khi ghi thì báo lại ở bước 5, không chạy lại publish.

## Bước 5 · Trả kết quả

Câu trả lời ngắn gọn:
1. Link artifact (đã ghi vào `artifact-links/tong-hop-ta-db-artifact.md`), kèm lưu ý trang đang để private và cần Share nếu muốn gửi cho team.
2. Nguồn: thư mục/file TA, commit, số file đã đọc.
3. Một dòng: n flow, n table (kể tên), các con số chính cần test.
4. 2–3 điểm chưa rõ quan trọng nhất.

Không dán lại nội dung trang vào câu trả lời.

## Bảo mật
- Không in token ra câu trả lời hay ra log. Không commit `connect-key/`.
- Nội dung chỉ được publish lên artifact private của người dùng.

---
name: tong-hop-spec-artifact
description: CHỈ dành cho spec nghiệp vụ của PO/BA (FRD, PRD, BRD, user story). Nhận 1 link spec nội bộ (BookStack page, Redmine issue, GitLab file/wiki/issue, SharePoint file) hoặc spec dán trực tiếp, có thể kèm ảnh (screenshot/mockup/Figma/sơ đồ; hoặc chỉ có ảnh), đọc KỸ TOÀN BỘ rồi tổng hợp đầy đủ User flow (sơ đồ mermaid), Business rule (giữ ID gốc), bảng quyết định, ma trận sự kiện → trạng thái, danh mục message, bảng truy vết UC → BR/FR → VR/AC và danh sách câu hỏi cho BA/PO (Q-xx) thành MỘT TRANG ARTIFACT HTML, rồi trả về LINK artifact. Chạy thẳng từ link tới link artifact, KHÔNG dừng lại hỏi xác nhận. Trigger trên các câu như "tổng hợp spec này thành artifact", "đọc kỹ spec và tổng hợp user flow, rule, logic", "làm trang tổng hợp FRD này", "/tong-hop-spec-artifact <link>". Khác với `requirement-analyzer` (tài liệu Markdown phân tích để làm input cho pipeline test), `dat-cau-hoi` (chỉ danh sách câu hỏi) và `requirement-to-mindmap` (mindmap): skill này cho ra trang web tra cứu trực quan để chia sẻ link. KHÔNG dùng cho tài liệu kỹ thuật (TA / technical design / API / DB) và KHÔNG tổng hợp DB, table, cột, migration, "dữ liệu lưu vào table nào"; các yêu cầu đó thuộc skill `tong-hop-ta-db-artifact`.
metadata:
  author: tuyenvo224
  version: "1.0"
---

# Tổng hợp spec → Artifact

**Input:** một link spec, có thể kèm ghi chú (ví dụ "chỉ phần 5") và/hoặc **ảnh đính kèm** (screenshot, mockup, Figma export, sơ đồ). Có thể chỉ có ảnh, không có link. **Output:** link artifact claude.ai kèm tóm tắt ngắn.

## Phạm vi

| Làm | Không làm |
|---|---|
| Spec nghiệp vụ do PO/BA viết: FRD, PRD, BRD, user story, Redmine issue mô tả nghiệp vụ | Tài liệu TA / technical design / API contract / DB schema |
| User flow, business rule, logic xử lý, message, trạng thái nghiệp vụ, truy vết UC/BR/FR/VR/AC, câu hỏi cho PO/BA | Table, cột, index, ERD, migration, ma trận "bước → table", thiết kế token/cookie/storage |

- Link trỏ tới tài liệu kỹ thuật (ví dụ thư mục `technical-design/` trên GitLab), hoặc người dùng hỏi dữ liệu lưu ở table nào: **không** chạy skill này. Báo người dùng là yêu cầu này thuộc skill `tong-hop-ta-db-artifact`.
- Spec PO có nhắc chi tiết kỹ thuật (tên table, API, cookie…): chỉ giữ ở mức cần để hiểu rule nghiệp vụ, không dựng section kỹ thuật riêng.
- Redmine issue loại BE/FE task thường trộn cả nghiệp vụ và kỹ thuật: chỉ lấy phần nghiệp vụ. Nếu issue có link sang spec PO gốc thì lấy spec gốc làm nguồn chính.

> **Ngoại lệ với AGENTS.md:** người dùng đã chốt rằng skill này **không** trình bày kế hoạch và **không** chờ xác nhận. Chạy thẳng hết 5 bước. Chỉ dừng lại khi gặp lỗi xác thực hoặc không lấy được nội dung.

Mọi đường dẫn tính từ **thư mục gốc project** `$ROOT`: thư mục chứa `.claude/` và `connect-key/`, thường là working directory của Claude Code. Đầu mỗi lần chạy, đặt biến bằng bash:

```bash
ROOT="$(pwd -W 2>/dev/null || pwd)"; [ -d "$ROOT/.claude" ] || echo "⚠ không thấy .claude/ trong $(pwd), cd về gốc project"
SKILL="$ROOT/.claude/skills/tong-hop-spec-artifact"
OUT="$ROOT/spec-summary"
mkdir -p "$OUT"
```

## Bước 1 · Lấy nội dung spec

```bash
python "$SKILL/scripts/fetch_spec.py" "<link>" "<scratchpad>/<slug>"
```

- Script tự nhận diện loại link và tự đọc key trong `$ROOT/connect-key/`, theo đúng bảng trong AGENTS.md. Key để chỗ khác thì thêm `--config-dir <thư mục>` hoặc đặt biến môi trường `CONNECT_KEY_DIR`. Định dạng file key xem `README.md` của skill. **Không** tự đọc file key rồi in key ra. Không hỏi lại người dùng về token.

  | Link | Script làm gì | Ghi chú |
  |---|---|---|
  | `bookstack.gotit.vn/books/<book>/page/<slug>` | tìm page id theo slug, lấy HTML, chuyển sang text (giữ bảng), tải ảnh | |
  | `redmine.gotit.vn/issues/<id>` | lấy description, custom field, journals, sub-issue, tải attachment, chuyển .docx/.md/.txt sang text | rule có thể nằm trong comment |
  | `gitlab.gotit.vn/.../-/tree/<ref>/<dir>` (thư mục) | liệt kê đệ quy, tải **mọi file** vào `files/`, ghép text theo từng file (`# FILE: <path>`) | ref có `/` được dò theo branch/tag có thật. Chỉ dùng cho thư mục spec nghiệp vụ (ví dụ `business-analytics/`) |
  | `gitlab.gotit.vn/.../-/blob/…`, `/-/wikis/…`, `/-/issues/…`, `/-/merge_requests/…` | lấy raw file / wiki / description | |
  | `gotitdayone.sharepoint.com/...` | dùng token Azure CLI để gọi Graph, tải file, chuyển .docx sang text | .pdf/.xlsx/.pptx thì dùng skill `pdf`/`xlsx`/`pptx` để đọc file tại `source.json.file` |
  | Không có link, người dùng dán nội dung | Bỏ bước này, lưu nội dung vào `spec.txt` | |
  | **Ảnh đính kèm** (kèm link hoặc đứng riêng) | Không cần script. Lập danh sách ảnh #1, #2… theo thứ tự người dùng gửi. Ảnh có **đường dẫn file** thì ghi lại đường dẫn để nhúng ở Bước 3; ảnh chỉ dán trong chat thì ghi "dán trong chat" | Quy tắc đọc ảnh ở Bước 2 |

- **Exit code 3 / `AUTH_ERROR`**: báo người dùng token có thể đã hết hạn (với SharePoint là cần `az login`), rồi dừng. Không thử lại liên tục.
- File đính kèm có `"converted": false` (xlsx, pdf…): đọc bằng skill tương ứng nếu tên file cho thấy có liên quan tới spec, ví dụ spec, FRD, flow, rule, report review.
- **Nội dung nguồn có link sang một spec gốc khác** (ví dụ Redmine ghi "business doc: https://bookstack…"): chạy thêm `fetch_spec.py` cho link đó vào thư mục con, rồi tổng hợp cả hai theo quy tắc trong checklist.

## Bước 2 · Đọc kỹ và đếm

1. Đọc **toàn bộ** `spec.txt` bằng tool Read. File dài thì đọc theo từng đoạn cho tới dòng cuối. Mở ảnh trong `assets/` (ảnh của spec, tương ứng `[IMG#n]`) nếu ảnh có flow, mockup hay bảng. Ảnh của spec được đánh số **tiếp theo** sau ảnh đính kèm.
   **Quy tắc đọc ảnh** (cả ảnh đính kèm lẫn ảnh trong spec):
   - Chỉ ghi những gì **nhìn thấy**: màn hình, field, nhãn, nút, giá trị mặc định, message, các bước / nhánh trên sơ đồ.
   - Hành vi không nhìn thấy (validate, điều kiện, lưu gì, điều hướng sau khi bấm…) thì **không suy ra thành rule**: gắn `❓ Giả định` và đưa vào câu hỏi Q-xx.
   - Mọi rule / field / message lấy từ ảnh đều ghi nguồn *(từ ảnh #n)* trong bảng rule, flow, message.
   - Ảnh **khác với spec** (ví dụ mockup có nút spec không nhắc, message khác chữ): không tự chọn bên đúng. Ghi cả hai và đưa thành câu hỏi mức **Cao**, loại `Conflict`.
   - Chỉ có ảnh, không có spec chữ: vẫn dựng trang. Lede ghi rõ "tổng hợp chỉ từ ảnh". Các mục không có dữ liệu (VR/AC, truy vết) thì xóa; phần câu hỏi thường dài hơn.
2. Đếm ID bằng script, không đếm tay:
   ```bash
   python "$SKILL/scripts/count_ids.py" "<scratchpad>/<slug>/spec.txt"
   ```
3. Bóc tách theo **[references/analysis-checklist.md](references/analysis-checklist.md)**, đủ 9 mục (thêm mục 9 "Nguồn ảnh" khi có ảnh): metadata, tổng quan & scope, user flow, business rules + bảng quyết định, ma trận sự kiện, message, use case & truy vết, VR & AC, câu hỏi Q-xx.

Nguyên tắc: **không bịa rule**. Mọi suy luận đều gắn `❓ Giả định` / `❓ suy luận` và có câu hỏi Q-xx đi kèm. Section nào spec không có thì xóa section đó.

## Bước 3 · Dựng HTML

- Tạo thư mục output (nếu chưa có) rồi copy template: `mkdir -p "$OUT" && cp "$SKILL/assets/template.html" "$OUT/<slug>.html"`. `<slug>` lấy từ slug trang BookStack, `redmine-<id>`, hoặc tên file.
- Thay các `{{…}}`. Nhân bản các khối flow và các dòng bảng. Xóa section và link TOC nào không dùng.
- **Có ảnh thì giữ section `#images` ("Nguồn ảnh")**, không có ảnh thì xóa section và link TOC của nó. Ảnh có file thì nhúng bằng script, rồi dán nội dung file snippet vào chỗ `{{FIGURES}}`:
  ```bash
  python "$SKILL/scripts/embed_images.py" --out "<scratchpad>/<slug>/figures.html" \
    "<đường dẫn ảnh 1>::<mô tả những gì nhìn thấy, 1 câu>::đính kèm" \
    "<scratchpad>/<slug>/assets/img01.png::<mô tả>::BookStack"
  ```
  - Đường dẫn truyền vào dạng `C:/...` (vì `$ROOT` đã ở dạng này).
  - Script tự bỏ qua ảnh > 1.5 MB hoặc khi tổng vượt 8 MB, chỉ in thẻ mô tả kèm lý do.
  - Ảnh chỉ dán trong chat (không có file): thêm thẻ `fig nofile` theo mẫu trong comment của template.
- File mẫu (đọc để học giọng văn và mức chi tiết, **không copy nội dung**):
  - `$SKILL/assets/example-login-frd.html` (khoảng 50 KB): mẫu chính, đọc **mọi lần**. Chỉ cần đọc phần sau `</style>`, theo từng đoạn; bỏ qua CSS vì đã có trong template.
  - `$SKILL/assets/example-images-section.html` (khoảng 6 KB): mẫu phần ảnh. **Chỉ đọc khi input có ảnh** (đính kèm hoặc trong spec). Gồm lede có nêu ảnh, cách trích *(từ ảnh #n)*, mục "Nguồn ảnh" với bảng đối chiếu ảnh và spec, và câu hỏi sinh ra từ ảnh.
  - **Không** dùng file HTML trong `spec-summary/` làm mẫu: file có ảnh nhúng base64 rất nặng token và không đọc được ảnh.
- **Giữ nguyên** khối `<style>` (token màu light/dark) và `<script>` lọc bảng. Không thêm màu literal. Không load thư viện mermaid, vì artifact tự render `<pre class="mermaid">`.
- `<title>`: tên ngắn 2–4 từ, ví dụ "Biz Client Login FRD". Không thêm phần giải thích sau dấu gạch hay dấu hai chấm.
- Văn phong: tiếng Việt, giữ thuật ngữ kỹ thuật tiếng Anh như spec. Câu ngắn, trực tiếp.
- Tự kiểm tra một lượt: số dòng trong bảng VR/AC/UC khớp với `count_ids.py`, dòng `counts` ở header khớp với số đếm được, và mọi `{{` đã được thay:
  ```bash
  grep -c "{{" "$OUT/<slug>.html"   # phải = 0
  ```

## Bước 4 · Publish Artifact

- Đọc `$OUT/registry.json` (map `source_url → artifact_url`), nếu chưa có file thì coi là `{}`.
  - **Spec đã có link artifact**: gọi `Artifact` với `action: "read"` và `url` đó trước, sau đó publish với `file_path` = `$OUT/<slug>.html` và cùng `url` để **giữ nguyên link**. Truyền `label` là phiên bản/ngày của spec.
  - **Spec mới**: publish với `file_path`, `icon` là một từ chung chung (ví dụ `login`, `order`, `payment`, `doc`), và `description` gồm một câu nói trang tổng hợp gì, từ FRD nào, phiên bản nào.
- Ghi lại `registry.json`: `{ "<source_url>": {"artifact": "<url>", "file": "<slug>.html", "spec_updated_at": "…", "published_at": "<today>"} }`. Skill dùng file này để tìm link cũ.
- **Ghi link vào file tracking** (bắt buộc, cả khi tạo link mới lẫn khi cập nhật đè link cũ):
  ```bash
  python "$SKILL/scripts/append_link.py" \
    --skill tong-hop-spec-artifact --feature "<Tên tính năng> (<nguồn + phiên bản>)" --url "<link artifact>"
  ```
  Script ghi vào `$ROOT/artifact-links/tong-hop-spec-artifact.md` (tự tạo thư mục) (Ngày giờ xuất · Tính năng · Link artifact, giờ VN). **Mỗi link chỉ 1 dòng**: link đã có thì dòng cũ được cập nhật giờ xuất + tính năng và chuyển xuống cuối bảng. Dùng tên tính năng **ổn định** giữa các lần chạy, không gắn số bản. Ví dụ tính năng: `Đăng nhập tài khoản Biz Client (FRD BookStack v1.3)`. Lỗi khi ghi thì báo lại ở bước 5, không chạy lại publish.

## Bước 5 · Trả kết quả

Câu trả lời cho người dùng ngắn gọn, gồm:
1. Link artifact (đã ghi vào `artifact-links/tong-hop-spec-artifact.md`), kèm lưu ý trang đang để private và cần Share nếu muốn gửi cho người khác.
2. Một dòng nêu nguồn: tên spec, phiên bản, ngày cập nhật, và các nguồn phụ nếu có.
3. Số lượng đã tổng hợp: n flow, n BR, n FR, n VR, n AC, n câu hỏi.
4. Top 3–5 câu hỏi quan trọng nhất (Q-xx), mỗi câu một dòng.
5. Lỗi biên tập trong spec (nếu có) và những phần không đọc được (ảnh lỗi, file chưa chuyển được).
6. Có ảnh: n ảnh đã dùng, ảnh nào được nhúng, ảnh nào chỉ mô tả (kèm lý do: dán trong chat / quá lớn), số chỗ ảnh mâu thuẫn với spec. Gợi ý ngắn: muốn nhúng ảnh đang dán trong chat thì gửi đường dẫn file.

Không dán lại nội dung trang vào câu trả lời.

## Bảo mật
- Không in token/API key ra câu trả lời hay ra log. Script đã tự lo phần xác thực.
- Không commit thư mục `connect-key/`, và không gửi key cho dịch vụ nào khác ngoài chính hệ thống nguồn.
- Nội dung spec chỉ được publish lên artifact private của người dùng. Việc chia sẻ do người dùng tự quyết.

# Bộ skill tổng hợp spec → Artifact

Hai skill Claude Code để biến tài liệu nội bộ thành **một trang artifact trên claude.ai** và trả về link:

| Skill | Dùng khi | Gọi |
|---|---|---|
| `tong-hop-spec-artifact` | Spec nghiệp vụ của PO/BA (FRD, PRD, user story) trên BookStack / Redmine / GitLab / SharePoint, có thể kèm ảnh mockup / screenshot → user flow, business rule, logic, câu hỏi cho BA/PO | `/tong-hop-spec-artifact <link>` (+ ảnh) |
| `tong-hop-ta-db-artifact` | Tài liệu TA / technical design trên GitLab → bản cho **QA**: flow nghiệp vụ đi qua bước nào, lưu vào table DB nào, SQL gợi ý để kiểm tra | `/tong-hop-ta-db-artifact <link>` |

Cả hai chạy thẳng từ link tới link artifact, không dừng lại hỏi.

## 1. Cài đặt

1. Copy **cả hai** thư mục vào `<gốc project>/.claude/skills/`:
   ```
   <gốc project>/
   ├── .claude/skills/tong-hop-spec-artifact/   # bắt buộc: chứa script dùng chung
   ├── .claude/skills/tong-hop-ta-db-artifact/  # cần skill trên
   ├── connect-key/                             # tự tạo, KHÔNG share (mục 3)
   └── AGENTS.md hoặc CLAUDE.md                 # thêm dòng ở mục 4
   ```
   Skill TA-DB gọi `fetch_spec.py` và `append_link.py` trong `tong-hop-spec-artifact/scripts/`, nên **không cài riêng lẻ được**.
2. Mở Claude Code tại **gốc project** (thư mục chứa `.claude/`). Mọi đường dẫn đều tính từ đó. Không có đường dẫn cứng.

## 2. Yêu cầu môi trường

- Claude Code, đăng nhập tài khoản claude.ai có **Artifact**.
- Python 3.9+. Chỉ dùng thư viện chuẩn, không cần `pip install`.
- Bash. Trên Windows dùng Git Bash; Claude Code đã có sẵn.
- Truy cập được mạng nội bộ: `bookstack.gotit.vn`, `redmine.gotit.vn`, `gitlab.gotit.vn`.
- Chỉ khi dùng link SharePoint: Azure CLI (`az`), đã `az login` vào tenant công ty.

## 3. Chuẩn bị `connect-key/` (key của chính bạn)

Script tự đọc key trong `<gốc project>/connect-key/`. Key để chỗ khác thì đặt biến môi trường `CONNECT_KEY_DIR=<thư mục>`. **Không commit, không share thư mục này.** Nên thêm `connect-key/` vào `.gitignore`.

**`connect-key/connect_redmine_bookstack_sharepoint.md`**: giữ đúng tiêu đề `##` và nhãn in đậm, script tìm theo đúng chữ này:
```markdown
## Redmine
- **API Key:** `<REDMINE_API_KEY>`

## Bookstack
- **Token ID:** `<BOOKSTACK_TOKEN_ID>`
- **Token Secret:** `<BOOKSTACK_TOKEN_SECRET>`
```

**`connect-key/connect-gitlab.md`**: token GitLab (Personal Access Token, quyền `read_api` + `read_repository`):
```
token gitlab:
<GITLAB_TOKEN>
```

Cách lấy key:
- Redmine: *My account → API access key*.
- BookStack: *Edit Profile → API Tokens*.
- GitLab: *Preferences → Access Tokens*.

Token chỉ đọc được những trang mà tài khoản của bạn có quyền xem. Gặp lỗi 401/403 thì skill dừng và báo token hết hạn hoặc không có quyền.

## 4. Thêm vào `AGENTS.md` / `CLAUDE.md` của project

Nếu file hướng dẫn của project có quy tắc kiểu "luôn trình bày kế hoạch và chờ xác nhận", thêm dòng ngoại lệ để 2 skill chạy thẳng:
```markdown
- Ngoại lệ: skill `tong-hop-spec-artifact` và `tong-hop-ta-db-artifact` chạy thẳng từ link tới link artifact, không cần hỏi xác nhận.
```

## 5. Output nằm ở đâu

| Thư mục (tự tạo khi chạy) | Nội dung |
|---|---|
| `spec-summary/` | HTML của skill spec + `registry.json` |
| `spec-summary/ta-db/` | HTML của skill TA-DB + `registry.json` |
| `artifact-links/tong-hop-spec-artifact.md` | Bảng `Ngày giờ xuất · Tính năng · Link artifact`, mỗi link 1 dòng |
| `artifact-links/tong-hop-ta-db-artifact.md` | Như trên, cho skill TA-DB |

- `registry.json` giúp skill **cập nhật đè đúng link cũ** khi chạy lại cùng một spec. Xóa file này thì lần chạy sau sẽ tạo link mới; link cũ vẫn còn trên claude.ai.
- Các thư mục này là dữ liệu **cá nhân** của từng người, không share. Mỗi người chạy sẽ có link artifact riêng.
- Artifact luôn ở chế độ **private**. Muốn người khác xem thì mở trang và chọn **Share**.

## 6. Tình trạng kiểm thử nguồn (tính tới 01/10/2026)

| Nguồn | Trạng thái |
|---|---|
| BookStack page, Redmine issue, GitLab thư mục (`/-/tree/`), GitLab file (`/-/blob/`) | Đã chạy với link thật |
| SharePoint, GitLab wiki / issue / merge request | Đã viết code nhưng **chưa chạy thử**. Gặp lỗi thì báo lại để sửa `fetch_spec.py` |

## 7. Cấu trúc skill

```
tong-hop-spec-artifact/
├── SKILL.md, README.md
├── scripts/fetch_spec.py     # lấy nội dung từ BookStack/Redmine/GitLab/SharePoint (dùng chung)
├── scripts/append_link.py    # ghi link vào artifact-links/ (dùng chung)
├── scripts/count_ids.py      # đếm UC/BR/FR/VR/AC
├── scripts/embed_images.py   # nhúng ảnh (đính kèm / trong spec) vào mục "Nguồn ảnh"
├── references/analysis-checklist.md
└── assets/template.html, example-login-frd.html (mẫu chính), example-images-section.html (mẫu phần ảnh)

tong-hop-ta-db-artifact/
├── SKILL.md, README.md
├── scripts/extract_ta.py     # quét table/cột/API/cấu hình từ TA, tự kiểm HTML
├── references/qa-db-checklist.md
└── assets/template.html, example-login-qa.html
```
Các file `example-*.html` cắt từ output thật (Đăng nhập, Đăng ký), có nội dung nội bộ. Chỉ share trong công ty.

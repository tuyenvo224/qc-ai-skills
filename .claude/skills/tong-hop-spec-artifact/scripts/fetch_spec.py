#!/usr/bin/env python3
"""Tải nội dung spec từ link nội bộ (BookStack / Redmine / GitLab / SharePoint) ra text để phân tích.

Cách dùng:
    python fetch_spec.py <url> <out_dir> [--config-dir <thư mục key>]

Thư mục key mặc định: <gốc project>/connect-key (gốc project = thư mục chứa `.claude/`),
hoặc đặt biến môi trường CONNECT_KEY_DIR.

Output trong <out_dir>:
    spec.txt        nội dung đã chuyển sang text (bảng giữ dạng "| a | b |", heading dạng "#")
    source.json     metadata: loại nguồn, tiêu đề, id, ngày cập nhật, revision, danh sách file đính kèm/ảnh
    raw.*           nội dung gốc (html / json / docx ...) để tra lại khi cần
    assets/         ảnh + file đính kèm tải được (xem ảnh bằng tool Read)

Script KHÔNG in token/API key ra stdout. Lỗi 401/403 -> exit code 3 (token có thể đã hết hạn).
Chỉ dùng thư viện chuẩn.
"""
import argparse
import base64
import html
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from html.parser import HTMLParser

def project_root():
    """Thư mục gốc project (chứa `.claude/` và `connect-key/`).
    Thứ tự: thư mục đang làm việc nếu có `.claude/` → đi ngược từ vị trí script tới `.claude`."""
    cwd = os.getcwd()
    if os.path.isdir(os.path.join(cwd, ".claude")):
        return cwd
    p = os.path.abspath(__file__)
    while os.path.dirname(p) != p:
        if os.path.basename(p) == ".claude":
            return os.path.dirname(p)
        p = os.path.dirname(p)
    return cwd


DEFAULT_CONFIG_DIR = os.environ.get("CONNECT_KEY_DIR") or os.path.join(project_root(), "connect-key")
PRIMARY_CFG = "connect_redmine_bookstack_sharepoint.md"
FALLBACK_CFG = "info_connect_redmine_bookstack.md"
GITLAB_CFG = "connect-gitlab.md"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class AuthError(Exception):
    pass


# ---------------------------------------------------------------- credentials
def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _section(text, name):
    """Nội dung của mục '## name' (tới heading '#'/'##' kế tiếp)."""
    m = re.search(r"^##\s*" + re.escape(name) + r"\b.*?$(.*?)(?=^#{1,2}\s|\Z)", text, re.M | re.S | re.I)
    return m.group(1) if m else ""


def _field(section_text, label):
    m = re.search(r"\*\*" + re.escape(label) + r":?\*\*:?\s*`?([^`\s]+)`?", section_text, re.I)
    return m.group(1).strip() if m else None


def load_creds(cfg_dir, kind):
    primary = _read(os.path.join(cfg_dir, PRIMARY_CFG))
    fallback = _read(os.path.join(cfg_dir, FALLBACK_CFG))
    if kind == "redmine":
        key = _field(_section(primary, "Redmine"), "API Key") or _field(_section(fallback, "Redmine"), "API Key")
        if not key:
            raise SystemExit("Không tìm thấy Redmine API Key trong connect-key/")
        return {"key": key}
    if kind == "bookstack":
        sec = _section(primary, "Bookstack")
        tid, tsec = _field(sec, "Token ID"), _field(sec, "Token Secret")
        if not (tid and tsec):
            sec = _section(fallback, "Bookstack")
            tid, tsec = _field(sec, "ID"), _field(sec, "Token")
        if not (tid and tsec):
            raise SystemExit("Không tìm thấy BookStack Token ID/Secret trong connect-key/")
        return {"id": tid, "secret": tsec}
    if kind == "gitlab":
        text = _read(os.path.join(cfg_dir, GITLAB_CFG))
        m = re.search(r"token gitlab:\s*`?([A-Za-z0-9_\-]{15,})`?", text, re.I) or re.search(r"(glpat-[A-Za-z0-9_\-]+)", text)
        if not m:
            raise SystemExit("Không tìm thấy GitLab token trong connect-key/connect-gitlab.md")
        return {"token": m.group(1)}
    if kind == "sharepoint":
        az_dir = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"
        az = shutil.which("az") or shutil.which("az.cmd") or os.path.join(az_dir, "az.cmd")
        try:
            tok = subprocess.run([az, "account", "get-access-token", "--resource", "https://graph.microsoft.com",
                                  "--query", "accessToken", "-o", "tsv"], capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise SystemExit(f"Không chạy được Azure CLI: {e}")
        if tok.returncode != 0 or not tok.stdout.strip():
            raise AuthError("Azure CLI token hết hạn/chưa login. Chạy `az login --allow-no-subscriptions --tenant <Tenant ID>` theo connect-key.")
        return {"token": tok.stdout.strip()}
    raise ValueError(kind)


# ---------------------------------------------------------------- http
def http_get(url, headers, binary=False):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            raise AuthError(f"HTTP {e.code} khi gọi {urllib.parse.urlsplit(url).netloc} - token có thể đã hết hạn hoặc không có quyền.")
        raise SystemExit(f"HTTP {e.code} khi gọi {url}")
    return data if binary else data.decode("utf-8", errors="replace")


def get_json(url, headers):
    return json.loads(http_get(url, headers))


# ---------------------------------------------------------------- converters
class _HtmlToText(HTMLParser):
    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre", "table", "ul", "ol"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.cell, self.row, self.in_cell, self.imgs, self.pre = [], [], None, False, [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.in_cell, self.cell = True, []
        elif tag == "br":
            (self.cell if self.in_cell else self.out).append(" / " if self.in_cell else "\n")
        elif re.fullmatch(r"h[1-6]", tag):
            self.out.append("\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            (self.cell if self.in_cell else self.out).append(("; " if self.in_cell else "\n- "))
        elif tag == "img":
            src = a.get("src") or ""
            self.imgs.append(src)
            (self.cell if self.in_cell else self.out).append(f" [IMG#{len(self.imgs)} {a.get('alt') or ''}] ")
        elif tag == "pre":
            self.pre += 1
            self.out.append("\n```\n")

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self.in_cell = False
            if self.row is not None:
                self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
        elif tag == "tr":
            if self.row:
                self.out.append("\n| " + " | ".join(self.row) + " |")
            self.row = None
        elif tag == "pre":
            self.pre -= 1
            self.out.append("\n```\n")
        elif tag in self.BLOCK and not self.in_cell:
            self.out.append("\n")

    def handle_data(self, data):
        if self.in_cell:
            self.cell.append(data)
        else:
            self.out.append(data if self.pre else re.sub(r"[ \t\r\n\xa0]+", " ", data))


def html_to_text(h):
    p = _HtmlToText()
    p.feed(h)
    text = "".join(p.out)
    text = re.sub(r"[ \t\xa0]+\n", "\n", text)
    text = re.sub(r"\n(- )?\s*\n+", lambda m: "\n", text)
    text = re.sub(r"\n- \n", "\n- ", text)
    return text.strip() + "\n", p.imgs


def docx_to_text(path):
    """Đọc .docx bằng zipfile (không cần python-docx). Giữ heading, đoạn và bảng."""
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    import xml.etree.ElementTree as ET
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(ns + "body")
    lines = []

    def para_text(p):
        return "".join(t.text or "" for t in p.iter(ns + "t")).strip()

    for el in body:
        if el.tag == ns + "p":
            t = para_text(el)
            if not t:
                continue
            style = el.find(f"{ns}pPr/{ns}pStyle")
            sv = style.get(ns + "val") if style is not None else ""
            m = re.search(r"(\d)", sv or "") if sv and "eading" in sv else None
            lines.append(("#" * int(m.group(1)) + " " if m else ("- " if el.find(f"{ns}pPr/{ns}numPr") is not None else "")) + t)
        elif el.tag == ns + "tbl":
            for tr in el.iter(ns + "tr"):
                cells = [" / ".join(filter(None, (para_text(p) for p in tc.iter(ns + "p")))) for tc in tr.iter(ns + "tc")]
                lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def file_to_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return docx_to_text(path)
    if ext in (".md", ".txt", ".csv", ".textile", ".json", ".yaml", ".yml"):
        return _read(path)
    if ext in (".html", ".htm"):
        return html_to_text(_read(path))[0]
    return None  # pdf/xlsx/ảnh: để Claude xử lý bằng skill/tool phù hợp


def safe_name(name):
    return re.sub(r'[\\/:*?"<>|]+', "_", name)[:120]


# ---------------------------------------------------------------- sources
def fetch_bookstack(url, cfg_dir, out):
    c = load_creds(cfg_dir, "bookstack")
    hdr = {"Authorization": f"Token {c['id']}:{c['secret']}"}
    m = re.search(r"/books/([^/]+)/page/([^/?#]+)", url)
    if not m:
        raise SystemExit("Link BookStack phải có dạng /books/<book>/page/<page>")
    book, slug = m.group(1), m.group(2)
    q = urllib.parse.urlencode({"filter[slug]": slug, "filter[book_slug]": book})
    data = get_json(f"https://bookstack.gotit.vn/api/pages?{q}", hdr)["data"]
    if not data:  # một số bản BookStack không hỗ trợ filter book_slug
        data = [d for d in get_json("https://bookstack.gotit.vn/api/pages?" + urllib.parse.urlencode({"filter[slug]": slug}), hdr)["data"]
                if d.get("book_slug") in (None, book)]
    if not data:
        raise SystemExit("Không tìm thấy page (hoặc token không có quyền đọc).")
    page = get_json(f"https://bookstack.gotit.vn/api/pages/{data[0]['id']}", hdr)
    body = page.get("html") or ""
    with open(os.path.join(out, "raw.html"), "w", encoding="utf-8") as f:
        f.write(body)
    text, imgs = html_to_text(body) if body else (page.get("markdown") or "", [])
    saved = download_images(imgs, url, hdr, out)
    return text, {
        "source": "bookstack", "title": page.get("name"), "id": page.get("id"), "book_slug": book, "slug": slug,
        "updated_at": page.get("updated_at"), "revision": page.get("revision_count"), "url": url, "images": saved,
    }


def fetch_redmine(url, cfg_dir, out):
    c = load_creds(cfg_dir, "redmine")
    hdr = {"X-Redmine-API-Key": c["key"]}
    m = re.search(r"/issues/(\d+)", url)
    if not m:
        raise SystemExit("Link Redmine phải có dạng /issues/<id>")
    base = url.split("/issues/")[0]
    issue = get_json(f"{base}/issues/{m.group(1)}.json?include=journals,attachments,relations,children", hdr)["issue"]
    with open(os.path.join(out, "raw.json"), "w", encoding="utf-8") as f:
        json.dump(issue, f, ensure_ascii=False, indent=2)
    parts = [f"# #{issue['id']} {issue.get('subject', '')}",
             "| Tracker | Status | Priority | Assignee | Author | Updated |",
             "| {} | {} | {} | {} | {} | {} |".format(*(issue.get(k, {}).get("name", "") for k in ("tracker", "status", "priority", "assigned_to", "author")),
                                                  issue.get("updated_on", ""))]
    for cf in issue.get("custom_fields", []) or []:
        if cf.get("value"):
            parts.append(f"- {cf['name']}: {cf['value']}")
    parts += ["", "## Description", issue.get("description") or "(trống)"]
    notes = [j for j in issue.get("journals", []) if (j.get("notes") or "").strip()]
    if notes:
        parts.append("\n## Comments (journals) - có thể chứa rule/thay đổi bổ sung")
        for j in notes:
            parts.append(f"\n### Note #{j['id']} · {j.get('user', {}).get('name', '')} · {j.get('created_on', '')}\n{j['notes']}")
    if issue.get("children"):
        parts.append("\n## Sub-issues\n" + "\n".join(f"- #{ch['id']} {ch.get('subject', '')}" for ch in issue["children"]))
    atts = []
    adir = os.path.join(out, "assets")
    os.makedirs(adir, exist_ok=True)
    for a in issue.get("attachments", []) or []:
        p = os.path.join(adir, safe_name(a["filename"]))
        try:
            with open(p, "wb") as f:
                f.write(http_get(a["content_url"], hdr, binary=True))
        except SystemExit as e:
            atts.append({"name": a["filename"], "error": str(e)})
            continue
        t = file_to_text(p)
        atts.append({"name": a["filename"], "path": p, "type": a.get("content_type"), "converted": t is not None})
        if t:
            parts.append(f"\n## Attachment: {a['filename']}\n{t}")
    return "\n".join(parts) + "\n", {
        "source": "redmine", "title": f"#{issue['id']} {issue.get('subject', '')}", "id": issue["id"],
        "updated_at": issue.get("updated_on"), "revision": len(issue.get("journals", [])), "url": url, "attachments": atts,
    }


GITLAB_API = "https://gitlab.gotit.vn/api/v4"
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}


def _gitlab_exists(url, hdr):
    try:
        http_get(url, hdr)
        return True
    except SystemExit:  # 404
        return False


def _gitlab_split_ref(pid, rest, hdr, query_ref=None):
    """Tách '<ref>/<path>' - ref có thể chứa '/' (vd feature/login) nên thử dần theo branch/tag có thật."""
    parts = rest.strip("/").split("/")
    if query_ref and "/".join(parts[:len(query_ref.split("/"))]) == query_ref:
        n = len(query_ref.split("/"))
        return query_ref, "/".join(parts[n:])
    for i in range(1, len(parts) + 1):
        ref = "/".join(parts[:i])
        enc = urllib.parse.quote(ref, safe="")
        if _gitlab_exists(f"{GITLAB_API}/projects/{pid}/repository/branches/{enc}", hdr) or \
                _gitlab_exists(f"{GITLAB_API}/projects/{pid}/repository/tags/{enc}", hdr):
            return ref, "/".join(parts[i:])
    return parts[0], "/".join(parts[1:])  # commit sha hoặc không xác định được


def _gitlab_raw(pid, fpath, ref, hdr):
    return http_get(f"{GITLAB_API}/projects/{pid}/repository/files/{urllib.parse.quote(fpath, safe='')}/raw?ref={urllib.parse.quote(ref, safe='')}",
                    hdr, binary=True)


def _gitlab_tree(pid, tpath, ref, hdr, out):
    """Liệt kê đệ quy thư mục, tải mọi file vào out/files/<relpath>, ghép text theo từng file."""
    items, page = [], 1
    while True:
        q = urllib.parse.urlencode({"path": tpath, "ref": ref, "recursive": "true", "per_page": 100, "page": page})
        batch = get_json(f"{GITLAB_API}/projects/{pid}/repository/tree?{q}", hdr)
        items += batch
        if len(batch) < 100:
            break
        page += 1
    blobs = sorted((i for i in items if i["type"] == "blob"), key=lambda i: i["path"])
    if not blobs:
        raise SystemExit("Thư mục trống hoặc sai ref/path.")
    fdir = os.path.join(out, "files")
    parts, files = [f"# Thư mục {tpath} @ {ref} ({len(blobs)} file)", ""] + [f"- {b['path']}" for b in blobs], []
    for b in blobs:
        rel = os.path.relpath(b["path"], tpath) if tpath else b["path"]
        p = os.path.join(fdir, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(_gitlab_raw(pid, b["path"], ref, hdr))
        ext = os.path.splitext(p)[1].lower()
        t = None if ext in IMG_EXT else file_to_text(p)
        files.append({"path": b["path"], "local": p, "converted": t is not None, "image": ext in IMG_EXT})
        if t is not None:
            parts.append(f"\n\n<!-- ==================== FILE: {b['path']} ==================== -->\n# FILE: {b['path']}\n\n{t}")
    return "\n".join(parts) + "\n", files


def _gitlab_last_commit(pid, path, ref, hdr):
    q = urllib.parse.urlencode({"ref_name": ref, "path": path, "per_page": 1})
    try:
        c = get_json(f"{GITLAB_API}/projects/{pid}/repository/commits?{q}", hdr)
    except SystemExit:
        return None
    if not c:
        return None
    c = c[0]
    return {"sha": c["short_id"], "date": c["committed_date"][:10], "author": c.get("author_name"), "title": c.get("title")}


def fetch_gitlab(url, cfg_dir, out):
    c = load_creds(cfg_dir, "gitlab")
    hdr = {"PRIVATE-TOKEN": c["token"]}
    api = GITLAB_API
    sp = urllib.parse.urlsplit(url)
    path = urllib.parse.unquote(sp.path).strip("/")
    qref = urllib.parse.parse_qs(sp.query).get("ref", [None])[0]
    if re.search(r"/-/(blob|raw|tree)/", path):
        proj, kind, rest = re.match(r"(.+?)/-/(blob|raw|tree)/(.+)", path).groups()
        pid = urllib.parse.quote(proj, safe="")
        ref, fpath = _gitlab_split_ref(pid, rest, hdr, qref)
        commit = _gitlab_last_commit(pid, fpath, ref, hdr)
        if kind == "tree":
            text, files = _gitlab_tree(pid, fpath, ref, hdr, out)
            return text, {"source": "gitlab", "kind": "tree", "title": f"{proj}/{fpath}", "project": proj, "path": fpath,
                          "ref": ref, "url": url, "last_commit": commit, "files": files}
        p = os.path.join(out, "raw" + os.path.splitext(fpath)[1])
        with open(p, "wb") as f:
            f.write(_gitlab_raw(pid, fpath, ref, hdr))
        text = file_to_text(p) or ""
        return text, {"source": "gitlab", "kind": "blob", "title": fpath, "project": proj, "path": fpath,
                      "ref": ref, "url": url, "last_commit": commit}
    elif "/-/wikis/" in path:
        proj, slug = path.split("/-/wikis/", 1)
        w = get_json(f"{api}/projects/{urllib.parse.quote(proj, safe='')}/wikis/{urllib.parse.quote(slug, safe='')}", hdr)
        text, title = w.get("content", ""), w.get("title", slug)
    elif re.search(r"/-/(issues|merge_requests)/\d+", path):
        proj, kind, iid = re.match(r"(.+)/-/(issues|merge_requests)/(\d+)", path).groups()
        d = get_json(f"{api}/projects/{urllib.parse.quote(proj, safe='')}/{kind}/{iid}", hdr)
        text, title = f"# {d.get('title', '')}\n\n{d.get('description') or ''}\n", d.get("title")
    else:
        raise SystemExit("Hỗ trợ link GitLab dạng /-/blob/, /-/wikis/, /-/issues/, /-/merge_requests/")
    return text, {"source": "gitlab", "title": title, "url": url}


def fetch_sharepoint(url, cfg_dir, out):
    c = load_creds(cfg_dir, "sharepoint")
    hdr = {"Authorization": f"Bearer {c['token']}"}
    enc = "u!" + base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
    item = get_json(f"https://graph.microsoft.com/v1.0/shares/{enc}/driveItem", hdr)
    name = item.get("name", "file")
    p = os.path.join(out, "raw_" + safe_name(name))
    with open(p, "wb") as f:
        f.write(http_get(f"https://graph.microsoft.com/v1.0/drives/{item['parentReference']['driveId']}/items/{item['id']}/content", hdr, binary=True))
    text = file_to_text(p)
    meta = {"source": "sharepoint", "title": name, "id": item.get("id"), "updated_at": item.get("lastModifiedDateTime"),
            "url": url, "file": p}
    if text is None:
        meta["note"] = "File không tự chuyển sang text được (pdf/xlsx/pptx). Dùng skill pdf/xlsx/pptx để đọc file tại 'file'."
        text = ""
    return text, meta


def download_images(srcs, page_url, hdr, out):
    saved = []
    if not srcs:
        return saved
    adir = os.path.join(out, "assets")
    os.makedirs(adir, exist_ok=True)
    for i, src in enumerate(srcs, 1):
        if src.startswith("data:"):
            saved.append({"n": i, "inline": True})
            continue
        full = urllib.parse.urljoin(page_url, src)
        p = os.path.join(adir, f"img{i:02d}{os.path.splitext(urllib.parse.urlsplit(full).path)[1] or '.png'}")
        try:
            with open(p, "wb") as f:
                f.write(http_get(full, hdr, binary=True))
            saved.append({"n": i, "path": p})
        except (SystemExit, AuthError, urllib.error.URLError) as e:
            saved.append({"n": i, "src": full, "error": str(e)})
    return saved


def detect(url):
    host = urllib.parse.urlsplit(url).netloc.lower()
    if "bookstack" in host:
        return fetch_bookstack
    if "redmine" in host:
        return fetch_redmine
    if "gitlab" in host:
        return fetch_gitlab
    if "sharepoint.com" in host:
        return fetch_sharepoint
    raise SystemExit(f"Chưa hỗ trợ domain {host}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("out_dir")
    ap.add_argument("--config-dir", default=DEFAULT_CONFIG_DIR)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    try:
        text, meta = detect(a.url)(a.url, a.config_dir, a.out_dir)
    except AuthError as e:
        print(f"AUTH_ERROR: {e}")
        sys.exit(3)
    with open(os.path.join(a.out_dir, "spec.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    meta["chars"] = len(text)
    with open(os.path.join(a.out_dir, "source.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"\nspec.txt: {len(text)} ký tự -> {os.path.join(a.out_dir, 'spec.txt')}")


if __name__ == "__main__":
    main()

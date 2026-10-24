"""Fetch one BookStack page (read-only) -> frd.html, frd.txt, frd-meta.json.

Usage: python fetch_bookstack.py <page-url> --out <dir>
"""
import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import load_config  # noqa: E402


def get(base, path, auth):
    req = urllib.request.Request(base.rstrip("/") + path, headers={"Authorization": auth, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def html_to_text(h):
    t = re.sub(r"<(br|/p|/li|/tr|/h\d|/div)[^>]*>", "\n", h)
    t = re.sub(r"<t[dh][^>]*>", " | ", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    return re.sub(r"\n\s*\n+", "\n", t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    m = re.search(r"/books/([^/]+)/page/([^/?#]+)", a.url)
    if not m:
        sys.exit("STOP: URL must look like https://<host>/books/<book>/page/<page>")
    book_slug, page_slug = m.group(1), m.group(2)
    host = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(a.url))

    cfg = load_config(".bookstack", ["BOOKSTACK_TOKEN_ID", "BOOKSTACK_TOKEN_SECRET"])
    auth = f"Token {cfg['BOOKSTACK_TOKEN_ID']}:{cfg['BOOKSTACK_TOKEN_SECRET']}"

    q = urllib.parse.quote(page_slug)
    pages = get(host, f"/api/pages?filter%5Bslug%5D={q}", auth).get("data", [])
    if len(pages) > 1:
        books = get(host, f"/api/books?filter%5Bslug%5D={urllib.parse.quote(book_slug)}", auth).get("data", [])
        ids = {b["id"] for b in books}
        pages = [p for p in pages if p["book_id"] in ids] or pages
    if len(pages) != 1:
        sys.exit(f"STOP: {len(pages)} pages match slug '{page_slug}': " + "; ".join(f"{p['id']} {p['name']}" for p in pages))

    page = get(host, f"/api/pages/{pages[0]['id']}", auth)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    body = page.get("html") or ""
    (out / "frd.html").write_text(body, encoding="utf-8")
    (out / "frd.txt").write_text(html_to_text(body) if body else (page.get("markdown") or ""), encoding="utf-8")
    links = sorted({h for h in re.findall(r'href="([^"]+)"', body) if "/books/" in h or "/link/" in h})
    meta = dict(id=page["id"], name=page["name"], slug=page["slug"], book_id=page["book_id"], url=a.url,
                revision=page.get("revision_count"), updated_at=page.get("updated_at"), linked_pages=links)
    (out / "frd-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK page #{meta['id']} '{meta['name']}' rev {meta['revision']} updated {meta['updated_at']}")
    print(f"linked BookStack pages: {len(links)}" + ("".join(f"\n  {l}" for l in links)))


if __name__ == "__main__":
    main()

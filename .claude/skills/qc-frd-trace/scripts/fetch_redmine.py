"""Fetch Redmine issues (read-only) with journals + their parents -> rm_<id>.md, rm-meta.json.

Usage: python fetch_redmine.py 75125,75447 --out <dir> [--url https://redmine.example.com]
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import load_config  # noqa: E402


def fetch(base, key, iid):
    url = f"{base.rstrip('/')}/issues/{iid}.json?include=children,attachments,relations,journals"
    req = urllib.request.Request(url, headers={"X-Redmine-API-Key": key, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))["issue"]


def to_md(d):
    out = [f"# #{d['id']} {d['tracker']['name']} | {d['subject']} | {d['status']['name']}\n",
           f"parent: {d.get('parent', {}).get('id', '-')} · updated {d.get('updated_on', '')[:10]}\n\n",
           d.get("description") or "", "\n\n## Journals\n"]
    for j in d.get("journals", []):
        note = (j.get("notes") or "").strip()
        ch = [f"{x.get('name')}: {x.get('old_value')} -> {x.get('new_value')}"
              for x in j.get("details", []) if x.get("property") == "attr"]
        if note or ch:
            out.append(f"\n### {j['created_on'][:10]} {j['user']['name']}\n{note}\n{'; '.join(ch)}\n")
    if d.get("children"):
        out.append("\nchildren: " + ", ".join(f"#{c['id']} {c['subject']}" for c in d["children"]))
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids")
    ap.add_argument("--out", required=True)
    ap.add_argument("--url")
    a = ap.parse_args()
    keys = ["REDMINE_API_KEY"] + ([] if a.url else ["REDMINE_URL"])
    cfg = load_config(".redmine", keys)
    base = a.url or cfg["REDMINE_URL"]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    todo = [int(x) for x in a.ids.replace(" ", "").split(",") if x]
    done, meta = set(), []
    while todo:
        iid = todo.pop(0)
        if iid in done:
            continue
        done.add(iid)
        d = fetch(base, cfg["REDMINE_API_KEY"], iid)
        (out / f"rm_{iid}.md").write_text(to_md(d), encoding="utf-8")
        meta.append(dict(id=iid, tracker=d["tracker"]["name"], subject=d["subject"], status=d["status"]["name"],
                         parent=d.get("parent", {}).get("id"), journals=len(d.get("journals", [])),
                         updated=d.get("updated_on")))
        if d.get("parent"):
            todo.append(d["parent"]["id"])
        print(f"OK #{iid} [{d['tracker']['name']}] {d['subject']} ({d['status']['name']})")
    (out / "rm-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

"""Refresh the "Latest in kubernetes-sigs/lws" block of README.md.

Lists my most recent merged/open PRs and PR reviews in the repo, newest first.
Uses only public data; GITHUB_TOKEN (set automatically in Actions) just raises the rate limit.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

USER = "BenAyedMedAla"
REPO = "kubernetes-sigs/lws"
LIMIT = 6
README = Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!-- LWS-ACTIVITY:START -->", "<!-- LWS-ACTIVITY:END -->"


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": USER})
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def search(q):
    url = "https://api.github.com/search/issues?" + urllib.parse.urlencode(
        {"q": q, "sort": "updated", "order": "desc", "per_page": 20})
    return get(url)["items"]


def collect():
    items = []
    for pr in search(f"repo:{REPO} author:{USER} type:pr"):
        if pr["pull_request"].get("merged_at"):
            items.append(("Merged", pr["pull_request"]["merged_at"], pr))
        elif pr["state"] == "open":
            items.append(("Opened", pr["created_at"], pr))
    for pr in search(f"repo:{REPO} reviewed-by:{USER} -author:{USER} type:pr")[:LIMIT]:
        reviews = get(f"https://api.github.com/repos/{REPO}/pulls/{pr['number']}/reviews?per_page=100")
        dates = [r["submitted_at"] for r in reviews if r["user"]["login"] == USER and r.get("submitted_at")]
        if dates:
            items.append(("Reviewed", max(dates), pr))
    items.sort(key=lambda i: i[1], reverse=True)
    return items[:LIMIT]


def render(items):
    lines = []
    for kind, when, pr in items:
        title = pr["title"].replace("|", "\\|").replace("[", "(").replace("]", ")")
        if len(title) > 72:
            title = title[:70].rstrip() + "…"
        day = datetime.fromisoformat(when.replace("Z", "+00:00")).strftime("%b %d, %Y")
        lines.append(f"| `{kind}` | [#{pr['number']}]({pr['html_url']}) {title} | {day} |")
    return "\n".join(["| | Pull request | Date |", "|---|---|---|", *lines])


def main():
    items = collect()
    if not items:
        print("no activity found; leaving README unchanged")
        return
    readme = README.read_text(encoding="utf-8")
    if START not in readme or END not in readme:
        sys.exit("activity markers missing from README.md")
    block = f"{START}\n{render(items)}\n{END}"
    updated = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, readme, flags=re.S)
    if updated != readme:
        README.write_text(updated, encoding="utf-8")
        print("README updated")
    else:
        print("no changes")


if __name__ == "__main__":
    main()

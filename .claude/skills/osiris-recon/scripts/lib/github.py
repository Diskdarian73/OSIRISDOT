"""GitHub repository search — keyless (60 req/hr unauthenticated, ample here).

Uses GITHUB_TOKEN when present purely to raise that ceiling; the source is
fully functional without one.
"""

import json
import os
from typing import Any, Dict, List
from urllib.parse import quote_plus

from . import net

SEARCH_URL = (
    "https://api.github.com/search/repositories"
    "?q={q}+pushed:>{since}&sort=stars&order=desc&per_page={n}"
)


def search(query: str, since_date: str, limit: int = 10) -> List[Dict[str, Any]]:
    body = net.get(
        SEARCH_URL.format(q=quote_plus(query), since=since_date, n=limit),
        ua=net.API_UA,
        accept="application/vnd.github+json",
        source="github",
    )
    if not body:
        return []
    try:
        items = json.loads(body).get("items", [])
    except (ValueError, AttributeError):
        return []
    posts = []
    for r in items:
        name = r.get("full_name")
        if not name:
            continue
        posts.append({
            "id": f"gh:{name}",
            "source": "github",
            "title": f"{name} — {(r.get('description') or '').strip()[:120]}".strip(" —"),
            "url": r.get("html_url") or f"https://github.com/{name}",
            "author": (r.get("owner") or {}).get("login") or "",
            "venue": "GitHub",
            "score": int(r.get("stargazers_count") or 0),
            # Open issues stand in for discussion volume; it is the only
            # conversation signal the search endpoint returns.
            "comments": int(r.get("open_issues_count") or 0),
            "upvote_ratio": None,
            "created": None,
            "pushed_at": r.get("pushed_at"),
            "scored": True,
        })
    net.log("github", f"'{query}' -> {len(posts)}")
    return posts

"""Hacker News via the Algolia API — free, keyless, no rate ceiling in practice."""

import json
from typing import Any, Dict, List
from urllib.parse import quote_plus

from . import net

SEARCH_URL = (
    "https://hn.algolia.com/api/v1/search"
    "?query={q}&tags=story&numericFilters=created_at_i>{since}&hitsPerPage={n}"
)


def search(query: str, since_epoch: int, limit: int = 20) -> List[Dict[str, Any]]:
    body = net.get(
        SEARCH_URL.format(q=quote_plus(query), since=int(since_epoch), n=limit),
        ua=net.API_UA,
        accept="application/json",
        source="hn",
    )
    if not body:
        return []
    try:
        hits = json.loads(body).get("hits", [])
    except (ValueError, AttributeError):
        return []
    posts = []
    for h in hits:
        title = (h.get("title") or "").strip()
        oid = h.get("objectID")
        if not title or not oid:
            continue
        posts.append({
            "id": f"hn:{oid}",
            "source": "hackernews",
            "title": title,
            # Link to the discussion, not the target: the comments are the signal.
            "url": f"https://news.ycombinator.com/item?id={oid}",
            "author": h.get("author") or "[unknown]",
            "venue": "Hacker News",
            "score": int(h.get("points") or 0),
            "comments": int(h.get("num_comments") or 0),
            "upvote_ratio": None,
            "created": float(h.get("created_at_i") or 0) or None,
            "scored": True,
        })
    net.log("hn", f"'{query}' -> {len(posts)}")
    return posts

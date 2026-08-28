"""Reddit via the two surfaces that still answer without an API key.

Reddit's JSON endpoints (``search.json``, ``about.json``) are permanently 403
for keyless clients, so this module uses:

  listing   /svc/shreddit/community-more-posts/{sort}/?name={sub}  — the only
            keyless surface that carries REAL score and comment counts, which
            the whole scoring model depends on.
  rss       /search.rss and /r/{sub}/{sort}.rss — broader reach, but Atom
            carries no engagement numbers, so RSS-only items are marked
            ``scored=False`` and can never outrank a measured item.
"""

import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from . import net

LISTING_URL = "https://www.reddit.com/svc/shreddit/community-more-posts/{sort}/?name={sub}&t={t}"
SEARCH_RSS_URL = "https://www.reddit.com/search.rss?q={q}&sort=relevance&t=month"
ATOM = "{http://www.w3.org/2005/Atom}"

_POST_RE = re.compile(r"<shreddit-post\s([^>]*)>", re.IGNORECASE)
_ATTR_RE = re.compile(r'([a-z0-9-]+)="([^"]*)"', re.IGNORECASE)


def _attrs(tag: str) -> Dict[str, str]:
    return {k.lower(): html.unescape(v) for k, v in _ATTR_RE.findall(tag)}


def _iso_epoch(value: str) -> Optional[float]:
    if not value:
        return None
    try:
        text = value.strip().replace("Z", "+00:00")
        # Reddit emits +0000; fromisoformat wants +00:00 before 3.11.
        if re.search(r"[+-]\d{4}$", text):
            text = text[:-5] + text[-5:-2] + ":" + text[-2:]
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except (ValueError, TypeError):
        return None


def _post_from_attrs(a: Dict[str, str]) -> Optional[Dict[str, Any]]:
    permalink = a.get("permalink", "")
    title = a.get("post-title", "").strip()
    if not permalink or not title:
        return None
    try:
        score = int(a.get("score") or 0)
        comments = int(a.get("comment-count") or 0)
    except ValueError:
        score, comments = 0, 0
    return {
        "id": a.get("id", permalink),
        "source": "reddit",
        "title": title,
        "url": "https://www.reddit.com" + permalink,
        "author": a.get("author", "") or "[deleted]",
        "venue": "r/" + (a.get("subreddit-name") or ""),
        "score": score,
        "comments": comments,
        "upvote_ratio": float(a.get("upvote-ratio") or 0) or None,
        "created": _iso_epoch(a.get("created-timestamp", "")),
        "scored": True,
        "scoped": True,
    }


def listing(sub: str, sort: str = "top", window: str = "MONTH") -> List[Dict[str, Any]]:
    """Pull one subreddit listing. Returns [] on any failure."""
    body = net.get(
        LISTING_URL.format(sort=sort, sub=quote_plus(sub), t=window),
        source="reddit",
    )
    if not body:
        return []
    seen, posts = set(), []
    for tag in _POST_RE.findall(body):
        post = _post_from_attrs(_attrs(tag))
        if post and post["id"] not in seen:
            seen.add(post["id"])
            posts.append(post)
    net.log("reddit", f"r/{sub} [{sort}] -> {len(posts)}")
    return posts


def search_rss(query: str) -> List[Dict[str, Any]]:
    """Global keyword search via Atom. No engagement data — scored=False."""
    body = net.get(SEARCH_RSS_URL.format(q=quote_plus(query)), source="reddit")
    if not body:
        return []
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return []
    posts = []
    for entry in root.iter(f"{ATOM}entry"):
        link = entry.find(f"{ATOM}link")
        url = (link.get("href") or "").strip() if link is not None else ""
        if "/comments/" not in url:
            continue
        title_el = entry.find(f"{ATOM}title")
        title = (title_el.text or "").strip() if title_el is not None else ""
        if not title:
            continue
        author_el = entry.find(f"{ATOM}author/{ATOM}name")
        author = (author_el.text or "").strip() if author_el is not None else ""
        cat_el = entry.find(f"{ATOM}category")
        sub = (cat_el.get("term") or "").strip() if cat_el is not None else ""
        if not sub and "/r/" in url:
            sub = url.split("/r/", 1)[1].split("/", 1)[0]
        upd_el = entry.find(f"{ATOM}updated")
        posts.append({
            "id": url,
            "source": "reddit",
            "title": title,
            "url": url,
            "author": author.removeprefix("/u/").removeprefix("u/") or "[deleted]",
            "venue": "r/" + sub,
            "score": 0,
            "comments": 0,
            "upvote_ratio": None,
            "created": _iso_epoch((upd_el.text or "") if upd_el is not None else ""),
            "scored": False,
            "scoped": False,
        })
    net.log("reddit", f"search '{query}' -> {len(posts)}")
    return posts

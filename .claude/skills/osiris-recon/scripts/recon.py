#!/usr/bin/env python3
"""osiris-recon — keyless scene recon for OSIRIS.EXE.

Sweeps the neighbourhoods the project actually lives next to (ARG, creative
coding, motion comics, interactive narrative, retro/CRT), scores what it finds
by real engagement, splits it into the two canon poles, and renders either a
terminal sweep or a self-contained CRT brief.

No API keys. No third-party packages. A dead source is an empty source.

  python3 recon.py                          full sweep, terminal output
  python3 recon.py --lane arg,retro         scope to two lanes
  python3 recon.py --emit html > out.html   canon-styled brief
  python3 recon.py --emit json              raw ranked data
"""

import argparse
import datetime
import json
import os
import sys
import time
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Windows defaults stdout to the locale codepage (cp1252 on most machines),
# which cannot encode the pole glyphs, the rule characters, or the emoji that
# turn up in post titles — redirecting to a file then dies with
# UnicodeEncodeError. Force UTF-8 on both streams before anything writes.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass

from lib import brief, github, hackernews, lanes, net, reddit, score  # noqa: E402

DEPTH = {
    "quick": {"sorts": ["top"], "rss": 0, "hn": 8, "gh": 0},
    "default": {"sorts": ["top", "hot"], "rss": 1, "hn": 15, "gh": 5},
    "deep": {"sorts": ["top", "hot", "new"], "rss": 2, "hn": 25, "gh": 10},
}


def build_jobs(selected, depth_cfg, since_epoch, since_date):
    """One named callable per source fetch, all independent."""
    jobs = []
    for lane in selected:
        for sub in lane.subreddits:
            for sort in depth_cfg["sorts"]:
                jobs.append((
                    f"{lane.key}|reddit|{sub}|{sort}",
                    lambda s=sub, o=sort: reddit.listing(s, o),
                ))
        for query in lane.queries[: depth_cfg["rss"]]:
            jobs.append((
                f"{lane.key}|rss|{query}",
                lambda q=query: reddit.search_rss(q),
            ))
        for query in lane.queries:
            jobs.append((
                f"{lane.key}|hn|{query}",
                lambda q=query, n=depth_cfg["hn"]: hackernews.search(q, since_epoch, n),
            ))
        if depth_cfg["gh"]:
            jobs.append((
                f"{lane.key}|gh|{lane.queries[0]}",
                lambda q=lane.queries[0], n=depth_cfg["gh"]: github.search(q, since_date, n),
            ))
    return jobs


def sweep(selected, depth_cfg, window_days: int,
          min_engagement: int = score.MIN_ENGAGEMENT) -> Dict[str, Any]:
    now = time.time()
    since_epoch = int(now - window_days * 86400)
    since_date = datetime.date.fromtimestamp(since_epoch).isoformat()

    jobs = build_jobs(selected, depth_cfg, since_epoch, since_date)
    net.log("sweep", f"{len(jobs)} source fetches across {len(selected)} lane(s)")
    results = net.fan_out(jobs)

    live = 0
    by_lane: Dict[str, List[Dict[str, Any]]] = {l.key: [] for l in selected}
    for name, payload in results.items():
        if payload:
            live += 1
            lane_key = name.split("|", 1)[0]
            for item in payload:
                item["lane"] = lane_key
                by_lane[lane_key].append(item)

    # Rank INSIDE each lane, against that lane's vocabulary only. Ranking the
    # merged pool against every lane's terms at once dilutes relevance until
    # engagement decides everything and off-topic viral posts win.
    items: List[Dict[str, Any]] = []
    for lane in selected:
        lane_items = [
            i for i in by_lane[lane.key]
            # Keep undated items: GitHub repos are filtered server-side.
            if i.get("created") is None or i["created"] >= since_epoch
        ]
        lane_items = score.above_floor(lane_items, min_engagement)
        lane_items = score.dedupe(lane_items)
        items.extend(score.rank(lane_items, lane.queries, now, window_days))

    items = score.dedupe(items)
    items.sort(key=lambda i: i["rank"], reverse=True)
    clusters = score.cluster(items)

    return {
        "meta": {
            "from": datetime.date.fromtimestamp(since_epoch).isoformat(),
            "to": datetime.date.fromtimestamp(now).isoformat(),
            "window_days": window_days,
            "lanes": [l.key for l in selected],
            "total": len(items),
            "sources_tried": len(jobs),
            "sources_live": live,
            "signal": sum(1 for i in items if i["pole"] == "SIGNAL"),
            "network": sum(1 for i in items if i["pole"] == "NETWORK"),
            "unverified": sum(1 for i in items if i["pole"] == "UNVERIFIED"),
            "threshold": score.SIGNAL_THRESHOLD,
            "min_engagement": min_engagement,
            "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        "clusters": clusters,
        "items": items,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="recon.py",
        description="OSIRIS.EXE scene recon — keyless, no dependencies.",
    )
    ap.add_argument("--lane", default="all",
                    help="comma-separated lanes, or 'all' (default). "
                         f"available: {', '.join(lanes.BY_KEY)}")
    ap.add_argument("--emit", default="terminal",
                    choices=["terminal", "html", "json"],
                    help="output format (default: terminal)")
    ap.add_argument("--depth", default="default",
                    choices=["quick", "default", "deep"])
    ap.add_argument("--window", type=int, default=30,
                    help="lookback window in days (default: 30)")
    ap.add_argument("--min-engagement", type=int, default=score.MIN_ENGAGEMENT,
                    dest="min_engagement",
                    help="minimum score+comments for a measured item "
                         f"(default: {score.MIN_ENGAGEMENT}, 0 keeps everything)")
    ap.add_argument("--limit", type=int, default=0,
                    help="cap items retained after ranking (0 = no cap)")
    ap.add_argument("-o", "--output", metavar="PATH",
                    help="write to this file (UTF-8) instead of stdout, "
                         "creating parent directories as needed. Avoids shell "
                         "redirection, which is encoding-fragile on Windows.")
    ap.add_argument("--list-lanes", action="store_true",
                    help="print the lane map and exit")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="per-source progress on stderr")
    args = ap.parse_args()

    if args.list_lanes:
        for lane in lanes.LANES:
            print(f"  {lane.key:10} {lane.title}")
            print(f"  {'':10} r/{'  r/'.join(lane.subreddits)}")
            print(f"  {'':10} {lane.why}\n")
        return 0

    if args.window < 1:
        ap.error("--window must be at least 1 day")

    net.set_verbose(args.verbose)
    selected = lanes.resolve([k for k in args.lane.split(",") if k.strip()])
    report = sweep(selected, DEPTH[args.depth], args.window, args.min_engagement)

    if args.limit > 0:
        report["items"] = report["items"][: args.limit]
        report["clusters"] = score.cluster(report["items"])

    if args.emit == "json":
        text = json.dumps(report, indent=2, default=str)
    elif args.emit == "html":
        text = brief.html_brief(report)
    else:
        text = brief.terminal(report)

    if args.output:
        path = os.path.abspath(args.output)
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
        # The path is the completion message; it goes to stderr so stdout
        # stays clean if someone redirects anyway.
        sys.stderr.write(f"wrote {path}\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.stderr.write("\ninterrupted\n")
        sys.exit(130)

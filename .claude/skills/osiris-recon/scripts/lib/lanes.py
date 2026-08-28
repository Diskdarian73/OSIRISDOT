"""Recon lanes: the neighbourhoods OSIRIS.EXE actually lives next to.

Every subreddit here was verified to return posts through the keyless
shreddit listing surface. Two obvious candidates were dropped as empty or
non-existent: r/ARGsociety and r/alternatereality.

A lane is a slice of the scene, not a topic filter — the whole point of a
sweep is to see what surfaced without having asked for it.
"""

from typing import Dict, List, NamedTuple


class Lane(NamedTuple):
    key: str
    title: str
    subreddits: List[str]
    queries: List[str]
    why: str


LANES: List[Lane] = [
    Lane(
        key="arg",
        title="ARG / Analog horror",
        subreddits=["ARG", "InternetMysteries", "analoghorror"],
        queries=["alternate reality game", "analog horror", "found footage web series"],
        why="Direct neighbours: the audience that already reads transmissions as story.",
    ),
    Lane(
        key="craft",
        title="Creative coding / Shaders",
        subreddits=["creativecoding", "generative", "proceduralgeneration", "shaders", "WebGL"],
        queries=["generative art", "webgl shader", "canvas visualization"],
        why="The technique lane — signal-space, the carrier field, the Yotta shader.",
    ),
    Lane(
        key="web",
        title="Web craft / Distribution",
        subreddits=["webdev", "itchio"],
        queries=["interactive website", "single page experience", "web experiment"],
        why="How work like this actually gets built and where it gets released.",
    ),
    Lane(
        key="comics",
        title="Comics / Motion",
        subreddits=["comics", "webcomics", "motiondesign"],
        queries=["motion comic", "webcomic launch", "animated comic"],
        why="The motion-comic form: what lands, what reads as gimmick.",
    ),
    Lane(
        key="narrative",
        title="Interactive narrative",
        subreddits=["interactivefiction", "twinegames", "gamedev", "indiegames"],
        queries=["interactive fiction", "narrative game", "twine story"],
        why="Story-as-software: pacing, player agency, how endings land.",
    ),
    Lane(
        key="retro",
        title="Retro / CRT",
        subreddits=["retrocomputing", "crtgaming", "vintagecomputing"],
        queries=["crt shader", "phosphor terminal", "retro computing aesthetic"],
        why="The look. Keeps the CRT treatment honest instead of nostalgic wallpaper.",
    ),
]

BY_KEY: Dict[str, Lane] = {lane.key: lane for lane in LANES}


def resolve(keys: List[str]) -> List[Lane]:
    """Map lane keys to Lane objects. Empty or ['all'] means every lane."""
    if not keys or "all" in keys:
        return list(LANES)
    out, unknown = [], []
    for key in keys:
        lane = BY_KEY.get(key.strip().lower())
        (out.append(lane) if lane else unknown.append(key))
    if unknown:
        raise SystemExit(
            f"unknown lane(s): {', '.join(unknown)}\n"
            f"available: {', '.join(BY_KEY)} (or 'all')"
        )
    return out

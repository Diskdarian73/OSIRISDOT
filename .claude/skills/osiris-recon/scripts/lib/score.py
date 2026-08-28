"""Ranking and the Signal / Network classification.

Two ideas carry this module.

1. Relevance first, engagement as tiebreaker. A bounded engagement bonus
   orders similarly-relevant items by discussion volume but is deliberately
   too small to lift an off-topic viral post above an on-topic quiet one.

2. The poles never blend (canon-lock v4.1). Every measured item is either
   SIGNAL or NETWORK — never a gradient, never a percentage-green. The
   discriminator is discussion ratio: comments carried per upvote.

     SIGNAL   people argued about it. Organic attention.
     NETWORK  it was upvoted and scrolled past. Broadcast, not conversation.

   Items from RSS carry no engagement numbers at all, so they are neither
   pole — they are UNVERIFIED, rendered in bone, and can never outrank a
   measured item. That is an honest third state, not a blend of the two.
"""

import math
import re
from typing import Any, Dict, List, Sequence

# Comments per upvote. Calibrated, not guessed: across an 872-item measured
# sweep of all six lanes the median ratio was 0.127, so this sits just above
# the natural centre of the distribution and splits the scene close to evenly
# (407 signal / 465 network) instead of collapsing everything into one pole.
SIGNAL_THRESHOLD = 0.15
# Engagement outweighs recency on purpose. This is a "what mattered in the
# window" brief, not a firehose — a three-week-old thread that 400 people
# argued in beats a post from this morning with one upvote.
ENGAGEMENT_CAP = 0.45
RECENCY_WEIGHT = 0.20

# A subreddit listing is already topic-scoped: being in r/analoghorror is
# itself evidence of relevance, so those items start from a floor rather than
# from zero. Global surfaces (RSS search, HN, GitHub) have no such guarantee
# and must earn their relevance from vocabulary overlap alone.
# The band is deliberately narrow (0.55..1.00, span 0.45) so it matches the
# engagement band. A wider band lets pure vocabulary saturation outrank real
# discussion: a 5-point post that happens to hit every lane keyword would beat
# a thread 44 people argued in, which is the opposite of what a sweep is for.
SCOPED_BASE = 0.55
SCOPED_BONUS = 0.45

# Minimum total attention (score + comments) for a MEASURED item to be worth
# ranking. Set to 0 to keep everything. Unmeasured items are exempt — they are
# already held below measured ones and carry no numbers to test.
MIN_ENGAGEMENT = 10

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
    "has", "have", "how", "i", "in", "is", "it", "its", "my", "of", "on", "or",
    "that", "the", "this", "to", "was", "what", "when", "which", "who", "why",
    "with", "you", "your", "we", "our", "just", "get", "got", "new", "make",
    "made", "any", "all", "can", "do", "does", "if", "so", "not", "no", "some",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokens(text: str) -> List[str]:
    return [t for t in _TOKEN_RE.findall((text or "").lower())
            if len(t) > 2 and t not in STOPWORDS]


def vocabulary(terms: Sequence[str]) -> set:
    vocab = set()
    for term in terms:
        vocab.update(tokens(term))
    return vocab


def relevance(item: Dict[str, Any], vocab: set) -> float:
    """How well the title matches this lane's vocabulary.

    Scored against ONE lane's terms, never the union of every lane — pooling
    six lanes' vocabulary dilutes the measure until engagement decides
    everything and generic viral posts win.
    """
    have = set(tokens(item.get("title", "")))
    if not vocab or not have:
        overlap = 0.0
    else:
        overlap = len(have & vocab) / len(vocab)

    if item.get("scoped"):
        # Sub membership guarantees the floor; vocabulary lifts from there.
        return min(1.0, SCOPED_BASE + SCOPED_BONUS * min(1.0, overlap * 2.0))
    return min(1.0, overlap * 2.0)


def engagement(item: Dict[str, Any]) -> float:
    """Log-scaled total attention. Comments weigh double: talking > clicking."""
    total = (item.get("score") or 0) + 2 * (item.get("comments") or 0)
    return math.log10(total + 1)


def recency(item: Dict[str, Any], now: float, window_days: int) -> float:
    """1.0 for right now, decaying to 0.0 at the edge of the window."""
    created = item.get("created")
    if not created:
        return 0.5
    age_days = max(0.0, (now - created) / 86400.0)
    return max(0.0, 1.0 - age_days / float(window_days))


def pole(item: Dict[str, Any]) -> str:
    """SIGNAL, NETWORK, or UNVERIFIED. Never anything in between."""
    if not item.get("scored"):
        return "UNVERIFIED"
    score = item.get("score") or 0
    comments = item.get("comments") or 0
    if score <= 0 and comments <= 0:
        return "UNVERIFIED"
    return "SIGNAL" if (comments / max(score, 1)) >= SIGNAL_THRESHOLD else "NETWORK"


def above_floor(items: List[Dict[str, Any]],
                minimum: int = MIN_ENGAGEMENT) -> List[Dict[str, Any]]:
    """Drop measured items nobody engaged with. Never drops unmeasured ones."""
    if minimum <= 0:
        return items
    return [i for i in items
            if not i.get("scored")
            or ((i.get("score") or 0) + (i.get("comments") or 0)) >= minimum]


def rank(items: List[Dict[str, Any]], terms: Sequence[str], now: float,
         window_days: int) -> List[Dict[str, Any]]:
    """Annotate one lane's items with their scores and sort best-first."""
    vocab = vocabulary(terms)
    for item in items:
        item["relevance"] = relevance(item, vocab)
        item["engagement"] = engagement(item)
        item["recency"] = recency(item, now, window_days)
        item["pole"] = pole(item)
        item["rank"] = (
            item["relevance"]
            + min(ENGAGEMENT_CAP, item["engagement"] / 10.0)
            + RECENCY_WEIGHT * item["recency"]
            # Unmeasured items sit below measured ones at equal relevance.
            - (0.20 if item["pole"] == "UNVERIFIED" else 0.0)
        )
    return sorted(items, key=lambda i: i["rank"], reverse=True)


def dedupe(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Drop repeats by id, then by normalized title across sources."""
    seen_id, seen_title, out = set(), set(), []
    for item in items:
        key = item.get("id")
        title_key = " ".join(sorted(set(tokens(item.get("title", "")))))[:120]
        if key in seen_id or (title_key and title_key in seen_title):
            continue
        seen_id.add(key)
        if title_key:
            seen_title.add(title_key)
        out.append(item)
    return out


MIN_SHARED_TOKENS = 2


def cluster(items: List[Dict[str, Any]], min_overlap: float = 0.30,
            max_clusters: int = 8, pool: int = 80) -> List[Dict[str, Any]]:
    """Greedy agglomeration on title-token overlap, over the strongest items only.

    Two deliberate choices:

    * Only the top ``pool`` ranked items are clustered. Agglomerating all ~1000
      hits wastes work and lets weak material dilute a theme.
    * A join needs at least MIN_SHARED_TOKENS words in common, not just a high
      ratio. Two short titles sharing one ordinary word ("Coming Out" and
      "Going Out") clear a ratio threshold easily and are not the same story.

    * A cluster scores on its BEST item plus a bounded corroboration bonus —
      not the sum of its members. Summing rewards size alone, which buries one
      genuinely strong find under two mediocre ones that happen to share a word.
      Corroboration across independent sources counts for more than repetition
      within one.
    """
    clusters: List[Dict[str, Any]] = []
    for item in items[:pool]:
        tset = set(tokens(item.get("title", "")))
        if not tset:
            continue
        placed = False
        for c in clusters:
            shared = tset & c["tokens"]
            union = tset | c["tokens"]
            if (len(shared) >= MIN_SHARED_TOKENS and union
                    and len(shared) / len(union) >= min_overlap):
                c["items"].append(item)
                c["tokens"] |= tset
                placed = True
                break
        if not placed:
            clusters.append({"items": [item], "tokens": set(tset), "title": item["title"]})

    for c in clusters:
        best = max(i["rank"] for i in c["items"])
        c["sources"] = sorted({i["source"] for i in c["items"]})
        c["venues"] = sorted({i["venue"] for i in c["items"] if i.get("venue")})
        corroboration = (
            min(0.15, 0.05 * (len(c["items"]) - 1))
            + min(0.15, 0.08 * (len(c["sources"]) - 1))
            + min(0.10, 0.04 * (len(c["venues"]) - 1))
        )
        c["score"] = best + corroboration
        c["signal"] = sum(1 for i in c["items"] if i["pole"] == "SIGNAL")
        c["network"] = sum(1 for i in c["items"] if i["pole"] == "NETWORK")
        c["items"].sort(key=lambda i: i["rank"], reverse=True)
        c["title"] = c["items"][0]["title"]
        c.pop("tokens", None)
    return sorted(clusters, key=lambda c: c["score"], reverse=True)[:max_clusters]

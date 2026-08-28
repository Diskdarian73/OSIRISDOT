---
name: osiris-recon
description: "Sweep the scene OSIRIS.EXE lives next to — ARG and analog horror, creative coding and shaders, motion comics, interactive narrative, retro/CRT — and report what people actually engaged with in the last 30 days. Scores by real upvotes and comments, splits findings into the canon SIGNAL and NETWORK poles, and renders a CRT brief in the archive's own visual language. Use when asked what's happening in the scene, what to build next, whether an idea has been done, or for a recon sweep / signal report."
argument-hint: "osiris-recon | osiris-recon arg,retro | osiris-recon --brief"
allowed-tools: Bash, Read, Write
user-invocable: true
license: MIT
---

# OSIRIS.EXE // RECON SWEEP

Scene recon for the OSIRIS.EXE archive. Answers one question: **what did people
actually engage with, in our neighbourhood, in the last 30 days?**

Adapted from the architecture of [last30days](https://github.com/mvanhorn/last30days-skill)
(MIT, Matt Van Horn) — the keyless-source approach, relevance-first ranking, and
evidence clustering are borrowed. The lane model, the SIGNAL/NETWORK
classification, and the CRT brief are OSIRIS-specific and written for this repo.

## Rule zero

`osiris-web-canon` and canon-lock v4.1 govern anything user-visible this skill
produces. The brief uses canon palette tokens only. **The poles never blend** —
that is not a styling preference here, it is enforced in both the classifier and
the stylesheet (see *The two poles* below).

## Run it

The engine is stdlib-only Python 3.9+. No API keys, no `pip install`, no network
config. Every source is keyless.

```bash
SKILL_DIR=".claude/skills/osiris-recon"        # relative to the repo root

python3 "$SKILL_DIR/scripts/recon.py"                      # full sweep, terminal
python3 "$SKILL_DIR/scripts/recon.py" --lane arg,retro     # scope to lanes
python3 "$SKILL_DIR/scripts/recon.py" --depth deep         # wider pull, slower
python3 "$SKILL_DIR/scripts/recon.py" --list-lanes         # what the lanes are
```

A full sweep is ~70 source fetches and takes about 10 seconds. `--depth quick`
on one lane takes under 2.

### Producing the HTML brief

Only when the user asks for a brief, a shareable report, or something to look at:

```bash
mkdir -p briefs
python3 "$SKILL_DIR/scripts/recon.py" --emit html > "briefs/recon-$(date +%F).html"
```

The file is self-contained — no build step, no assets, no network at view time,
consistent with every other page in this repo. Give the path back and stop; do
not paste the HTML into chat.

### Flags

| Flag | Default | Notes |
|---|---|---|
| `--lane` | `all` | `arg,craft,web,comics,narrative,retro`, comma-separated |
| `--emit` | `terminal` | `terminal`, `html`, `json` |
| `--depth` | `default` | `quick` / `default` / `deep` — sorts pulled per sub |
| `--window` | `30` | lookback in days |
| `--min-engagement` | `10` | floor on score+comments for measured items; `0` keeps all |
| `--limit` | `0` | cap items after ranking |
| `-v` | off | per-source progress on stderr |

## The lanes

Six slices of the adjacent scene. A lane is a neighbourhood, not a search query —
the point of a sweep is to see what surfaced *without* having asked for it.

| Lane | Covers | Why it's ours |
|---|---|---|
| `arg` | r/ARG, r/InternetMysteries, r/analoghorror | The audience that already reads transmissions as story |
| `craft` | r/creativecoding, r/generative, r/proceduralgeneration, r/shaders, r/WebGL | Signal-space, the carrier field, the Yotta shader |
| `web` | r/webdev, r/itchio | How work like this gets built and released |
| `comics` | r/comics, r/webcomics, r/motiondesign | The motion-comic form |
| `narrative` | r/interactivefiction, r/twinegames, r/gamedev, r/indiegames | Story-as-software |
| `retro` | r/retrocomputing, r/crtgaming, r/vintagecomputing | Keeps the CRT treatment honest |

Every subreddit was verified live against the keyless surface. Two obvious
candidates were dropped as empty: r/ARGsociety and r/alternatereality.

## The two poles

The canon rule that green and crimson never blend is implemented as a **binary
classifier**, not a gradient. The discriminator is *discussion ratio* — comments
carried per upvote:

- **SIGNAL** (`--phosphor`) — ratio ≥ 0.15. People argued about it.
- **NETWORK** (`--crimson`) — below that. Upvoted and scrolled past: attention
  without conversation.
- **UNVERIFIED** (`--bone`) — the surface carried no engagement numbers at all.
  Neither pole, ranked below measured items. An honest third state, not a blend.

The 0.15 threshold is calibrated, not guessed: across an 872-item measured sweep
of all six lanes the median ratio was 0.127, so it sits just above the natural
centre and splits the scene close to evenly rather than collapsing everything
into one pole.

**Read the poles this way.** SIGNAL is where a form is still being argued over —
that is where there is room to make something. NETWORK is a solved, saturated
shape: high attention, no debate left. A NETWORK cluster is not a bad finding,
it is a warning that the form is finished.

## How ranking works

Relevance first, engagement as a bounded tiebreaker, recency as a small nudge.
Three properties are deliberate and worth preserving if you edit `lib/score.py`:

1. **Relevance is scored per lane**, against that lane's vocabulary only. Pooling
   all six lanes dilutes the measure until engagement decides everything and
   generic viral posts win. This was a real bug during development.
2. **A subreddit listing is already topic-scoped**, so those items start from a
   floor (0.55) rather than zero; global surfaces (RSS, HN, GitHub) must earn
   relevance from vocabulary alone. The scoped band is kept narrow so pure
   keyword saturation cannot outrank real discussion.
3. **Engagement outweighs recency** (0.45 vs 0.20). This is a "what mattered"
   brief, not a firehose.

Clusters score on their *best* item plus a bounded corroboration bonus, never on
the sum of members — summing rewards size alone and buries one strong find under
two mediocre ones sharing a word.

## Sources

| Source | Surface | Keyless |
|---|---|---|
| Reddit listings | `/svc/shreddit/community-more-posts/` | yes — the only keyless surface carrying **real** scores and comment counts |
| Reddit search | `/search.rss` | yes — Atom carries no engagement data, so these are UNVERIFIED |
| Hacker News | Algolia `/api/v1/search` | yes |
| GitHub | `/search/repositories` | yes (60 req/hr; `GITHUB_TOKEN` only raises the ceiling) |

Reddit's JSON endpoints (`search.json`, `about.json`) are permanently 403 for
keyless clients — that is why the listing/RSS split exists. Do not "fix" it by
switching to `.json`.

**A dead source is an empty source.** Every fetcher returns `[]` rather than
raising, so one 403 can never sink a sweep. The header reports `sources live`
out of `sources tried`; a shortfall is information, not a crash.

## Reporting the results

Lead with what changed in the scene, not with the mechanics. Cite specific
threads with their real numbers — `r/analoghorror, 123 pts / 44 comments` — and
link them. Say which pole a finding sits in and what that implies for us.

Two honest outcomes to state plainly rather than dress up:

- **A quiet sweep is a valid result.** If nothing cleared the floor, say the
  scene was quiet. Do not lower `--min-engagement` to manufacture findings.
- **Never infer reception of OSIRIS.EXE from this.** These lanes measure the
  neighbourhood, not our own footprint. This skill does not search for
  OSIRIS.EXE, Disk Darián, or osirisexe.com, and cannot tell you how the
  project is being received.

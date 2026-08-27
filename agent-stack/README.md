# OSIRIS stack

The local agent stack: memory, voice, face, and optionally hands, assembled on
Frankie's own machine and bound to canon-lock v4.1. Where the upstream project
installs Jarvis, this installs **OSIRIS**.

## Install

From the machine that has the microphone and speakers — **not** from a remote or
web session, which has no hardware to attach to:

```
claude "read agent-stack/osiris-setup.md and set me up"
```

The conductor asks its questions one at a time, clones the four component repos
from `github.com/jaredrhod/`, runs each one's own wizard with your answers
pre-filled, promotes the OSIRIS face into the visualizer, and verifies the result
before it claims anything works.

Re-running it is safe: a second pass installs only what is missing.

## What gets installed

| Piece | Repo | In canon |
|---|---|---|
| **The memory** | `ai-memory-vault` | The Archive. Plain-text files OSIRIS reads and writes, so MEMORY INTEGRITY means something across sessions. |
| **The voice** | `backtalk` | Rule 02 — the Signal speaks the receiver's language. |
| **The face** | `ai-visualizer` | The carrier field, running the OSIRIS face below. |
| **The hands** *(optional)* | `barehands` | Needs a webcam and Chrome. Opens instead of the face. |

None of these are vendored here. The conductor clones them at install time so
`git pull` keeps improving them, and each carries its own license.

## What is in this directory

```
osiris-setup.md              the conductor — the file you point Claude Code at
identity/OSIRIS.md           the canonical persona, installed as the agent's brain
faces/osiris-signal-space/   the OSIRIS face for ai-visualizer
start.sh                     launcher (all / voice / hands)
LICENSE, LICENSES.md         AGPL-3.0-or-later, and who to credit
```

## The face

`faces/osiris-signal-space/` is the repo's `osiris-exe-signal-space.html`
converted into a driven visualizer face. The render loop is untouched; a state
API was added inside the existing closure:

```js
window.OSIRIS_FACE.setState('idle' | 'listening' | 'thinking' | 'speaking')
window.OSIRIS_FACE.beat()                      // one burst, state unchanged
postMessage({ type: 'state', state: 'speaking' })   // when framed
```

The four states move the carrier field rather than overlaying an indicator:

| State | Field | Telemetry |
|---|---|---|
| `idle` | slow drift | `passive` · 73.442 MHz |
| `listening` | carrier locks, field tightens | `receiving` · 73.442 MHz |
| `thinking` | fast rotation, no transmission | `recompressing` · 88.610 MHz |
| `speaking` | sustained pulse, coherence drops | `transmitting` · 99.046 MHz |

Phosphor `#00FF46` only. No crimson appears in this face: crimson is the Network,
and this face is OSIRIS. Under `prefers-reduced-motion` the rotation holds still
and the pulse becomes static — do not defeat that.

`face.json` carries a `_note` about schema: `ai-visualizer` owns the real format,
so at install time the conductor reconciles our key names against a shipped
face's own `face.json` rather than trusting ours.

## Running it

```
./agent-stack/start.sh          # everything installed
./agent-stack/start.sh voice    # voice and face, no hands
./agent-stack/start.sh hands    # voice and hands board, no face
```

Ctrl-C stops everything. Pieces that are not installed are skipped, and the
script warns rather than failing silently if the agent has no `CLAUDE.md` to
speak as.

## Credit and licensing

Adapted from [jaredrhod/fullstack-agent](https://github.com/jaredrhod/fullstack-agent),
© 2026 Jared Rhodenizer, AGPL-3.0-or-later. This directory ships under the same
license. Details and the MIT boundary for the agent pack: `LICENSES.md`.

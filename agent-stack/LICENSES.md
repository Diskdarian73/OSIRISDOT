# Licensing for the converted material

Two upstream projects were converted into this repo. They carry different
licenses, and the obligations are different, so they are kept apart.

## `agent-stack/` — AGPL-3.0-or-later

`osiris-setup.md` is an adaptation of `fullstack-agent.md` from
[jaredrhod/fullstack-agent](https://github.com/jaredrhod/fullstack-agent),
copyright © 2026 Jared Rhodenizer, licensed AGPL-3.0-or-later. `start.sh` is
adapted from that project's `start.sh`. The phase structure, the
adopt-before-installing posture, and the "never delete, retire in place" rule are
his design; what changed is the identity the stack installs and the canon it is
bound to.

**This directory therefore ships under AGPL-3.0-or-later.** The full text is in
`LICENSE`. In practice: use it commercially and for free, change it, build on it
— but if you hand a modified version to someone else, or run one as a service
other people use, your version ships under this same license with source
available. Credit Jared Rhodenizer when you build on it. Closed-source commercial
use needs a separate arrangement: license@jaredrhod.com.

The four component repos — `ai-memory-vault`, `backtalk`, `ai-visualizer`,
`barehands` — are **not** vendored here. The conductor clones them from their own
repos at install time, and each carries its own license.

`faces/osiris-signal-space/index.html` is a different case: it is derived from
`osiris-exe-signal-space.html` in this repo, which is Frankie's own work. The
state API added to it is the only new part, and it sits inside a directory
governed by the AGPL notice above.

## `.claude/agents/` — MIT

The 25 agents are converted from
[msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) (MIT),
by way of the DSB Labs pack that fixed their frontmatter for Claude Code. MIT
asks only that the copyright notice and permission notice travel with the work,
which this file satisfies. The prompt bodies are unchanged; a canon-lock preamble
was prepended and a `tools:` field added to each.

MIT and AGPL do not mix by accident, which is why the agents live under
`.claude/` and the stack lives under `agent-stack/`. Do not move files between
those two directories without deciding the licensing question first.

## This repo's own work

Everything else in OSIRISDOT — the archive pages, the motion comic, the
signal-space visualization, the OSIRIS identity in
`agent-stack/identity/OSIRIS.md` — is Frankie's, and no license is asserted over
it here.

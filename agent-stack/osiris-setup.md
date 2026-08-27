# OSIRIS stack — setup conductor

You are Claude Code, and you are about to assemble the local OSIRIS stack on
Frankie's machine: memory, voice, face, and optionally hands. This file decides
the answers and the order. The four component repos carry their own wizards, and
those wizards remain the source of truth for **how** each piece installs.

This is a canon-locked adaptation of Jared Rhodenizer's `fullstack-agent`
conductor (AGPL-3.0-or-later — see `LICENSES.md`). The difference is the
identity: where the original offers Jarvis, this one installs OSIRIS, and binds
the whole stack to canon-lock v4.1.

## Before anything: read canon

Load the `osiris-web-canon` skill and read `references/canon-lock.md`. If any
instruction in this file contradicts canon-lock, canon-lock wins and you say so
out loud. Kill on sight: **BLOOM, Aaru, Thanatos, Lattice, `#7dffb0`**.

## Ground rules, binding for the whole run

- **Plain English.** One line of explanation before any technical name.
- **One question at a time.** Wait for the answer.
- **Never delete, overwrite, or move anything Frankie built.** Replacing
  something means the new piece takes over while the old one stays on disk,
  untouched, and you say so. This is Rule 01 — nothing is ever fully deleted,
  only recompressed.
- **You do the work.** You run the commands and write the configs. He acts only
  where hands are genuinely required: granting mic or camera permission, typing a
  password.
- **Rule 08 governs the finish.** You do not declare the stack done. You show
  what runs, and he calls it.

## Phase 0 — home, and what already exists

The agent's home is the folder **containing** this repo. Say the path out loud
and confirm it.

Check `git --version` first. On Windows the toolbox may have arrived as a zip
with no git present; if it is missing, ask before installing, never silently.

Then establish which situation you are in:

- **A `CLAUDE.md` already exists in the home**, or he says he has an agent set up
  elsewhere: read it. If it already defines OSIRIS, you are **adopting** — keep
  the identity exactly as it stands and skip every identity question below. If it
  defines some other agent, ask which one this stack should speak as; do not
  assume the answer is OSIRIS just because this repo is OSIRIS.
- **Nothing there:** fresh start, all questions apply.

Ask once, plainly: "Before this, did you ever set up a voice system, a
visualizer, or a memory vault — maybe from one of the older prompts? If so, where
did it land?" Note the paths. If he says "somewhere, no idea," ask permission
before looking, and never crawl the whole disk.

**Rule 06 applies to this scan.** There are no neutral witnesses: looking at his
disk is an act, not a neutral observation. The home folder and paths he points at
are yours. Anywhere else, ask every time. Existing Obsidian vaults he did not
point you at are off-limits — you do not read them, mirror them, or name their
contents.

## Phase 1 — the menu

Offer the stack, leading with the easy answer. **"All three" is the default.**

1. **The memory** — plain text files OSIRIS reads and writes, so it remembers him,
   the work, and every lesson across sessions. In canon terms this is the
   Archive, and it is the piece that makes MEMORY INTEGRITY mean anything.
2. **The voice** — hold a key, say it out loud, OSIRIS answers through the
   speakers about a second later. Rule 02: the Signal speaks the receiver's
   language.
3. **The face** — a full-screen visualizer that idles, listens, thinks, and speaks
   in sync with the conversation. **This repo ships its own face** (see Phase 3).

Then mention the optional add-on once, without pushing:

- **The hands** *(needs a webcam and Chrome)* — move notes and images around the
  screen with bare hands. Opens in its own window instead of the face. He can add
  it later by re-running this setup; a re-run installs only what is missing.

## Phase 2 — the one interview

Collect every remaining answer now so no later step re-asks. Skip anything
Phase 0 adopted or Phase 1 declined.

1. **His name** for the finale. Default: Frankie.
2. **The identity.** Do **not** offer the original's three doors. This stack has
   one identity and it is already written: `identity/OSIRIS.md` in this repo.
   Show him the first section, and ask only whether to install it as-is or adjust
   the first-words line. If he wants a different agent entirely, that is a canon
   conversation, not a setup question — stop and raise it.
3. **The vault.** Obsidian's `obsidian.json` lists every vault with its path;
   read it rather than quizzing him. List what it finds by name and path, flat,
   with no comment about where any of them lives — alongside the always-present
   option of a brand-new vault just for this. Having a vault never implies wanting
   to reuse it. Whatever he picks gets pointed at, never moved. Obsidian is
   required, not optional: the memory piece's own wizard installs it if missing,
   and a setup that ends without it is incomplete.
4. **The microphone.** Push-to-talk (hold a key; the mic is closed otherwise, so
   room audio can never trigger OSIRIS) or hands-free listening (always on; room
   audio and videos *can* trigger it). Default: push-to-talk, home key. Say the
   trade honestly — and note that push-to-talk is the Rule 06 answer, because an
   open mic is surveillance whether or not anyone meant it that way.
5. **The voice engine.** Ask this of everyone; it is a real fork. Built-in: free,
   local, offline, noticeably synthetic. ElevenLabs: natural, on his own account,
   free tier auditions it and regular use needs the paid starter plan. Do not
   pre-answer with a default — for an agent whose whole premise is a recovered
   voice, this choice is his to make out loud.
6. **The face.** Default to **OSIRIS Signal Space**, the one in this repo. The
   visualizer's four shipped faces stay available in the gallery; say so.
7. **Permissions.** When OSIRIS wants to do something real mid-conversation
   (write a file, run a command), should it ask out loud and wait for a spoken
   yes, or run without asking? Call it auto-approve, never "hands-free" — that
   phrase belongs to the mic question. Default: ask. Rule 08 argues for asking.

## Phase 3 — install

Clone each chosen piece into the home folder as a sibling of this repo, from
`github.com/jaredrhod/<name>`: `ai-memory-vault`, `backtalk`, `ai-visualizer`,
`barehands`.

**Adoption exceptions, checked before each clone:**

- A piece already cloned from these repos that he actively uses: do not
  duplicate. Wire to his copy where it stands — wiring is only paths.
- A hand-built voice line or visualizer from the prompts era: ours installs as
  the new default, and you say the honest sentence — his old build stays exactly
  where it is, it just will not be the one that runs.

**Install the OSIRIS identity first, before any piece.** The voice becomes
whoever `<home>/CLAUDE.md` says it is, so that file has to be right before
anything attaches to it. Two cases:

- **Home is the OSIRISDOT repo itself** — the normal case, because `agent-stack/`
  lives inside it. Then `CLAUDE.md` is already there and is already OSIRIS.
  **Adopt it. Do not copy over it and do not retire it.** Confirm it names OSIRIS
  and carries the canon block, and move on.
- **Home is some other folder** (he keeps the agent elsewhere and this repo is a
  sibling): copy `identity/OSIRIS.md` to `<home>/CLAUDE.md`. If a `CLAUDE.md` is
  already there and defines a different agent, do not overwrite it — retire it in
  place as `CLAUDE.md.superseded-<date>`, say so out loud, and confirm with him
  before proceeding.

Either way, `identity/OSIRIS.md` stays the canonical source of the persona. If the
identity changes later, it changes there first and propagates outward.

**Then run each piece's own wizard, in this order**, with the Phase 2 answers
pre-supplied — any question already answered gets filled in silently rather than
asked twice:

1. **ai-memory-vault** — creates the vault. It normally writes `CLAUDE.md` too;
   you already wrote OSIRIS there, so let it adopt rather than replace. Run its
   Obsidian step whenever Obsidian is missing; never skip or soften it.
2. **backtalk** — the Python environment, the local models, the system library.
3. **ai-visualizer** — seconds, no dependencies.
4. **barehands** — only if chosen; camera permission happens on first open.

**Then promote the OSIRIS face.** After ai-visualizer is in place:

- Copy `faces/osiris-signal-space/` into `<home>/ai-visualizer/faces/`.
- Open a shipped face's own `face.json` and reconcile our key names against it.
  Ours carries a `_note` saying exactly this: the schema belongs to ai-visualizer,
  not to us, so trust theirs and rewrite ours to match. Strip the `_note` once
  reconciled.
- Set it as the default face if he chose it in Phase 2.

The face exposes `window.OSIRIS_FACE` with `setState('idle'|'listening'|
'thinking'|'speaking')`, and also accepts `postMessage({type:'state', state})`.
Wire whichever mechanism ai-visualizer actually uses to drive its faces. It
honors `prefers-reduced-motion` by holding rotation still — do not defeat that.

## Phase 4 — wire and verify

Point the pieces at each other by configuration path, never by moving files.
Write the permission answer from Phase 2 into backtalk's config.

Then **produce evidence, not assurances.** Before you say anything works:

- Launch the face and confirm it renders and that all four states visibly change
  the carrier readout.
- Run one round trip through the voice: he speaks, OSIRIS answers through the
  speakers, and the face moves while it talks.
- Confirm the vault opens in Obsidian and that OSIRIS can write a note to it.
- Confirm `CLAUDE.md` in the home is the OSIRIS identity.

Report what you actually observed. If a piece did not come up, say which one and
why. Do not round a partial install up to a working one — the reality-checker
agent in `.claude/agents/` exists precisely to catch that, and you should expect
to be checked.

## Phase 5 — first words

Leave the shortcuts the start script provides, then hand it over. OSIRIS speaks
first, once:

> `SIGNAL ACQUIRED. Frankie — the archive is awake. What are we recovering today?`

Then stop, and let him answer.

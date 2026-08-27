# DSB Labs agent pack

25 agents pulled from [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) (MIT), selected for a one-person creative studio.

## Where they live

The pack is vendored into this repo at `.claude/agents/`, so every Claude Code
session opened on OSIRISDOT has all 25 available with no install step. To use
them outside this repo as well, copy them into your user-level agents folder:

```bash
cp .claude/agents/*.md ~/.claude/agents/
```

Invoke one by its name:

```
Use the grant-writer agent to draft a letter of inquiry for the Chicago DCASE grant.
```

## What was changed from the originals

The files in the source repo do **not** load in Claude Code as shipped. Two fixes were applied:

| Field | Repo ships | Claude Code needs | Fixed |
|---|---|---|---|
| `name` | `Grant Writer` | lowercase + hyphens only | `grant-writer` |
| `color` | `#F59E0B` (hex) | one of red, blue, green, yellow, purple, orange, pink, cyan | `yellow` |

The prompt bodies are untouched. `emoji:` and `vibe:` were left in place — Claude Code ignores unknown keys. Two keys were added: `display_name` (the label the repo shipped) and `source` (the original path), so nothing is lost.

## The pack

### Storefront

- **`specialized-document-generator`** — Document Generator **start here**  
  Coloring books and sticker sheets ship as PDFs. This one writes the code that builds them — page geometry, bleed, consistent trim. *(275 words)*
- **`marketing-email-strategist`** — Email Marketing Strategist **start here**  
  Launch sequences and a buyer list you own, instead of renting attention from a platform. *(2,408 words)*
- **`sales-offer-lead-gen-strategist`** — Offer & Lead Gen Strategist  
  Lead-magnet design — the free coloring page that earns the email that sells the pack. *(2,421 words)*
- **`specialized-pricing-analyst`** — Pricing Analyst **start here**  
  Digital-product pricing is guesswork until someone models it. Cost structure, competitor bands, margin floors. *(1,705 words)*
- **`marketing-seo-specialist`** — SEO Specialist  
  Discoverability on Etsy, KDP and the Wix store — title and tag structure, not blog spam. *(2,944 words)*

### Brand & visuals

- **`design-brand-guardian`** — Brand Guardian **start here**  
  Locks DSB Labs into one identity across Wix, Etsy, KDP and print so the sticker pack and the coloring books read as the same studio. *(1,457 words)*
- **`design-image-prompt-engineer`** — Image Prompt Engineer  
  Turns a visual idea into prompt language that survives the model. Useful for concept passes, not for final line art. *(1,375 words)*
- **`design-inclusive-visuals-specialist`** — Inclusive Visuals Specialist **start here**  
  Built to fight the stereotype defaults image models fall into. The one to run before any Boricua or Afro-Caribbean figure goes into a page. *(898 words)*
- **`design-visual-storyteller`** — Visual Storyteller  
  For sequencing images into a narrative — covers, spreads, campaign sets. *(882 words)*

### OSIRIS.EXE & the book

- **`academic-anthropologist`** — Anthropologist  
  Keeps invented culture coherent: kinship, ritual, belief that hang together instead of being set dressing. *(1,049 words)*
- **`marketing-book-co-author`** — Book Co-Author  
  Takes voice notes and fragments and turns them into structured chapters in your own voice. *(683 words)*
- **`academic-historian`** — Historian **start here**  
  Period accuracy and primary sources for Elenita de Jesús — the difference between historical fiction and costume drama. *(964 words)*
- **`narrative-designer`** — Narrative Designer  
  Lore architecture and branching structure. Written for games, but it is the closest thing here to a transmedia bible builder. *(1,892 words)*
- **`academic-narratologist`** — Narratologist **start here**  
  Story structure with actual frameworks behind it. Pressure-tests an arc that has to hold across a universe, not one book. *(884 words)*

### Audience

- **`marketing-instagram-curator`** — Instagram Curator **start here**  
  Visual-first platform, visual-first work. Aesthetic development and multi-format planning. *(770 words)*
- **`marketing-reddit-community-builder`** — Reddit Community Builder  
  Where art, graffiti and diaspora communities actually talk. Written around not getting banned for self-promotion. *(878 words)*
- **`marketing-tiktok-strategist`** — TikTok Strategist  
  Process video is the native format for graffiti and illustration. This covers hooks and the algorithm. *(888 words)*
- **`marketing-video-optimization-specialist`** — Video Optimization Specialist  
  YouTube retention, chaptering, thumbnails — if the process footage becomes a channel. *(825 words)*

### Money

- **`support-finance-tracker`** — Finance Tracker  
  Cash flow and budget for a studio that is one person. Lighter than the full FP&A agent. *(2,004 words)*
- **`grant-writer`** — Grant Writer **start here**  
  Chicago and Illinois arts funding is real money that goes unclaimed. Prospect research, letters of inquiry, budget narratives. *(3,514 words)*
- **`finance-tax-strategist`** — Tax Strategist  
  Studio income, deductions, self-employment structure. Treat it as a briefing to take to a human, not as tax advice. *(1,884 words)*

### Reality checks

- **`testing-evidence-collector`** — Evidence Collector  
  Refuses to accept a claim without a screenshot. The antidote to an agent telling you it finished. *(1,066 words)*
- **`specialized-master-plan-architect`** — Master Plan Architect  
  Red-teams a plan before you spend three weekends on it. *(1,346 words)*
- **`testing-reality-checker`** — Reality Checker **start here**  
  Defaults to NEEDS WORK and demands proof before it calls anything done. Point it at your own plans. *(1,327 words)*
- **`research-synthesist`** — Research Synthesist  
  Turns a pile of sources into an honestly weighted map — flags what the evidence does not actually support. *(1,506 words)*

## The OSIRIS.EXE conversion

Every agent in this repo has been converted beyond the frontmatter fixes above.
Two changes, applied to all 25:

**A canon-lock preamble is prepended to each body**, ahead of the agent's own
prompt, declaring itself binding over everything that follows. It carries the
banned terms (BLOOM, Aaru, Thanatos, Lattice, `#7dffb0`), the locked color tokens
and the never-blend rule, the dates that get missed (Dec 1982 not 1987; 1993 not
1994; MEMORY INTEGRITY at 63%), the naming and caption rules, the eight Rules of
the World, and the Chicago setting facts. It also carries a scope line: these
agents advise and draft, they do not deploy and they do not decide what ships.
Frontmatter gains `canon_lock: v4.1` so the version is visible at a glance.

**Each agent now declares `tools:`.** Twenty-two get
`Read, Write, Edit, Grep, Glob, WebSearch, WebFetch` — no shell. Three get `Bash`
because their work genuinely requires running things:

| Agent | Tools | Why |
|---|---|---|
| `specialized-document-generator` | + `Bash`, no web | It writes and runs the code that builds PDFs. |
| `testing-evidence-collector` | `Read, Grep, Glob, Bash, WebFetch` | It gathers proof; no `Write`, because it collects rather than changes. |
| `testing-reality-checker` | `Read, Grep, Glob, Bash` | It has to actually run the thing to refuse to certify it. |

The prompt bodies themselves are still untouched.

## The one caution that remains

**The numbers inside are unsourced.** Several of these agents state statistics as
fact with no citation — they were written for a general agency audience, not for
this studio. The canon preamble now instructs each agent to treat every figure in
its own body as an unverified claim and to mark it as such rather than repeating
it as established truth. That reduces the risk; it does not remove it. Check
anything numeric that reaches a deliverable, especially from
`finance-tax-strategist`.

Source: https://github.com/msitarzewski/agency-agents · MIT licence.
Licensing boundary against the AGPL agent stack: `agent-stack/LICENSES.md`.

# Vāk (वाक्)

*A quiet helper for chanting: the words light up as they are sung.*

---

It is a little before six in the morning. Amma sits in front of the small altar with a printed copy of the श्रीललितासहस्रनाम, the pages soft from years of use. A recording plays from the phone. Halfway through, she turns a page, looks up at the lamp, and when she looks down the voice has moved on. Which line is it now? She finds the place, loses it again.

Far away, her son knows this. He would like her morning to be a little easier, without teaching anyone a new gadget.

That is the whole reason Vāk exists.

## What Vāk is

**Vāk is a prayer book that follows along: it lights up each word as it is sung, so you never lose your place.**

It has two parts.

| Part | Who it is for | What it is |
|---|---|---|
| **Vāk Puja Reader** | Families who chant | A single file that opens in a browser, on a phone, tablet or laptop |
| **Vāk Studio** | Whoever prepares prayers | A tool on your own computer that makes new prayer packs |

### Vāk Puja Reader

**When** you are chanting along to a recording, **you can** watch each word fill with gold as it is sung, **so that** your eyes stay on the text and your mind stays on the prayer.

**When** you chant by yourself, with no recording, **you can** press *Listen*, and the Reader follows the loudness of your voice and moves from line to line at your own pace, **so that** the page keeps up with you. It does not understand the words. It learns your pace.

### Vāk Studio

**When** you want a new prayer in the Reader, **you can** give Studio the text and a recording, and it finds where every word begins, checks its own work, and builds a prayer pack, **so that** you do not have to time hundreds of words by hand.

## Try it in one minute

1. Open `samples/lalita-text-only.html` in any browser.
2. You will see the Lalitā Sahasranāma in large Devanagari.
3. This sample is **text only**. There is no recording inside it. Pick your own recording of the prayer, and the Reader will let you tap along to set the timings for it.

No install, no sign-in. It works offline.

## How it works, explained to a 10-year-old

Imagine you have a song recording and want to know exactly when each word starts.

1. **A music teacher listens carefully.** She has heard thousands of recordings of speech and singing, in many languages. She listens to your recording and writes a small tick mark where each word begins. In Vāk this is the **aligner**.
2. **A second teacher checks a few spots.** She does not redo the work. She picks some places at random, plays just a short clip, and asks: does this sound like the start of this line, or the end of the one before? In Vāk this is the **listening check**. It is a smoke alarm, not proof.
3. **An elder signs it off.** Only a person can say "yes, this is right". The computer is not allowed to say it. In Vāk this is **approval**.

Only after all three does a prayer reach the family. More detail is in [docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md).

## Made with respect

- **Private recordings are never published.** The pilot recording used with the family stays within the family. The repository holds timings, not audio. Permission from the ashram is being requested.
- **The AI never edits sacred text.** Studio does not invent, fix or "correct" a single syllable.
- **A person approves every shared file.** The AI cannot give approval. A new build needs a new approval.
- **No ads, no tracking, no accounts.**

## Status

| Feature | Status |
|---|---|
| Reader: Music mode with word-by-word fill | Built and tested |
| Reader: Recite mode (follows your voice level) | Built and tested |
| Reader: tap to jump, speed, adjust timing, tap-along, calibration, screen kept awake | Built and tested |
| Reader: works on older iPads (Safari 11+) | Built and tested |
| Studio: alignment, listening check, gates, approval, build | Built and tested |
| Pack: Śrī Lalitā Sahasranāma (v2) | Built, all checks pass |
| Pack: Sandhyavandanam (Krishna Yajurveda), सन्ध्यावन्दनम् | Created, awaiting text and recording |
| Together mode (family in different cities follow one leader) | **Planned** |
| Sankalpa count (family total of parayanams) | **Planned** |
| Big-screen mode with QR join | **Planned** |
| Other scripts (Telugu, Kannada, Tamil and more) | **Planned** |
| Learning mode, installable web app | **Planned** |
| Recite mode that follows your voice word by word | **Planned** |

## Quick start for developers

```
git clone https://github.com/mathconcepts/vak.git && cd vak && ./setup.sh
```

This needs Python 3.10 or newer. It downloads about 1.7 GB of models once and runs the tests. Then connect Claude Desktop:

```
.venv/bin/python harness/install_claude_desktop.py
```

Reopen Claude Desktop and ask: "List my Vāk packs".

## Repository map

| Path | What is in it |
|---|---|
| `reader/template.html` | The Reader app |
| `vakstudio/` | Python: textfmt, audio, align, judge, htmlbuild, workspace, api, cli, mcp_server |
| `packs/<id>/` | One folder per prayer pack |
| `harness/` | Claude Desktop installer, Goose and OpenCode configs |
| `tests/` | Automated tests |
| `samples/lalita-text-only.html` | Try the Reader now, text only |
| `AGENTS.md` | Rules for any AI agent working here |
| `setup.sh` | One-step setup |

## Read more

- [docs/USE-CASES.md](docs/USE-CASES.md): who uses Vāk, and how
- [docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md): the pipeline, for children and engineers
- [docs/STUDIO.md](docs/STUDIO.md): preparing a prayer pack
- [docs/HARNESS.md](docs/HARNESS.md): the tools, checks, memory and guardrails around the AI
- [AGENTS.md](AGENTS.md): rules for AI agents
- [docs/sankalpa.md](docs/sankalpa.md): design for the planned family count
- [docs/plans/2026-10-11-vak-platform.md](docs/plans/2026-10-11-vak-platform.md): the platform plan

## Thanks

With gratitude to **Bhaskara Prakasha Ashram**, whose recording was used in the family pilot, and to **sanskritdocuments.org**, whose proofread edition provides the Lalitā Sahasranāma text. This is attribution, not endorsement: neither has reviewed or endorsed this project.

---

**Created by MSP Giri · Inspired by Navarathri 2026 · With Jagadamba's blessings, more will follow.**

Vāk began late one night, because a daily puja deserved a page that keeps its place. It was refined while the first two users, Giri's parents, were chanting with it.

श्रीमात्रे नमः

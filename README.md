# Vāk (वाक्)

**A prayer book that follows along. Each word lights up as it is chanted, so you never lose your place.**

---

## The problem

Amma chants the श्रीललितासहस्रनाम every morning with a recording. She turns a page, looks up at the lamp, and when she looks back the voice has moved on. Where are we now?

## The idea

Put the prayer on a screen and let it keep the place for her:

- The word being sung turns **gold**.
- The page **scrolls by itself**.
- The screen **stays awake** until the prayer ends.

## Two parts

| | What it is | Who it is for |
|---|---|---|
| **Vāk Reader** | One HTML file. Opens on any phone, tablet or laptop. Works offline. | Families who chant |
| **Vāk Studio** | A tool on your computer that turns a prayer text and a recording into a Reader file | Whoever prepares the prayers |

## How the Reader works

- **Music mode:** press Play. Each word fills with gold as it is sung.
- **Recite mode:** press Listen and chant yourself. The page moves line by line at your pace. It follows your voice, not your words.
- **Small helps:**
  - Tap any line to jump there.
  - Slow the recording down.
  - Make the text bigger.
  - Fix the timing if a Bluetooth speaker runs late.

No app to install, no sign-in, no ads, no tracking.

**Try it now:** open [`samples/lalita-text-only.html`](samples/lalita-text-only.html) in a browser. It holds the text only. Choose your own recording inside it.

## How Studio makes a Reader file

Think of three people in a music class:

1. **A teacher listens** and marks where every word begins. *(The aligner: a speech model that knows about 1,100 languages.)*
2. **A second teacher checks** a few random spots by ear. *(The listening check.)*
3. **An elder signs off.** Only a person can say yes. The computer cannot. *(Approval.)*

Then Studio builds the Reader file.

**Is it accurate?** On Lalitā, Studio found the same timings that had been checked by ear, all 970 words, with no hints given.

## Made with respect

- **Recordings stay private.** Files that contain a recording are shared by hand with family only. No recording is stored in this repository.
- **The AI never changes the sacred text.** The text comes from a person.
- **A person approves every file** before it is shared.

## What is ready

| Ready today | Coming later |
|---|---|
| Reader: Music and Recite modes, word-by-word gold, auto-scroll, works offline and on older iPads | **Together mode:** family in different cities follow one leader on the same word |
| Studio: text check, timing, listening check, approval, build | **Sankalpa count:** a family total of parayanams, with no server |
| **Lalitā Sahasranāma** pack, all checks passed | **Other scripts:** Telugu, Kannada, Tamil |
| **Krishna Yajurveda Sandhyavandanam** pack, waiting for its text and recording | **YouTube playback**, for videos whose owners allow embedding |

## For developers

```bash
git clone https://github.com/mathconcepts/vak.git && cd vak && ./setup.sh
.venv/bin/python harness/install_claude_desktop.py   # use Studio from Claude Desktop
```

- `setup.sh` needs Python 3.10 or newer. It downloads about 1.7 GB of models once and runs the tests.
- Studio also works with Goose or OpenCode, and with any model: Claude, GPT, Gemini, or local Llama or Qwen. The heavy work is local code, so every model gets the same result.

| Read more | |
|---|---|
| [docs/USE-CASES.md](docs/USE-CASES.md) | Real-life stories: Chennai, Hyderabad, Bangalore, Pune, Delhi |
| [docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md) | The pipeline, in simple and technical terms |
| [docs/STUDIO.md](docs/STUDIO.md) · [CONTRIBUTING.md](CONTRIBUTING.md) | Add a new prayer |
| [docs/HARNESS.md](docs/HARNESS.md) · [AGENTS.md](AGENTS.md) | How the AI is kept safe and checked |

## Thanks

To the reciters and the **Bhaskara Prakasha Ashram** for the recitation, and to **sanskritdocuments.org** for the proofread text. This credits them; it does not claim they endorse the project.

---

**Created by MSP Giri · Inspired by Navarathri 2026 · With Jagadamba's blessings, more will follow.**

श्रीमात्रे नमः

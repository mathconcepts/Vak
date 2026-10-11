# Vāk Studio: notes for any AI agent working here

This file is the shared context for every agent and model (Claude, GPT, Gemini, Llama, Qwen …).
Read it first. Then use the `vak-studio` MCP tools, or the `vak` CLI.

## What this is
Vāk Studio turns a Sanskrit prayer text and a recording into a word-timed **Reader** file. The Reader is
a single offline HTML file: each word lights up as it is chanted. Family members open it on phones,
iPads and laptops.

## Ground rules
1. **Never write, "correct" or fill in sacred text yourself.** The text comes from the person
   (`packs/<id>/text.md`). If `text_check` reports problems, show them to the person and let them fix it.
2. **Recordings stay private** unless `licence` is `public`. The Bhaskara Prakasha Ashram recording
   (Lalitā) is private. Never upload it, never host it, and never put it in a public file.
3. **Gates decide, not the model.** Publishing is blocked until text, align and judge pass. A person
   then approves the exact build (`vak approve <id>` in Terminal, or the macOS dialog). No tool can approve.
4. **Write decisions down.** Anything learned about a recording goes into the manifest with `pack_set`:
   which parts are skipped or repeated (`order`), anchors, and plain-language `notes`. The next agent
   or model reads it from there.
5. Tools only write inside `packs/` and `dist/`.

## Workflow
```
pack_new → text_import / edit text.md → text_check → audio_import → audio_align → audio_judge
        → pack_build → pack_preview → (person: vak approve) → pack_publish
```
- **audio_align**, when confidence is low:
  - The recording usually skips or repeats parts. Ask the person, then set `order`, for example
    `"0-3,9-12,25-389,9-12"`: chanted line numbers in the order heard, repeats allowed.
  - If the recording has a long spoken intro, ask for 2–3 anchors `{"line": seconds}`.
- **audio_judge** checks a seeded sample of lines by ear (Whisper).
  - On Lalitā, verified timings score 23–25/30, and timings shifted by one line score 13/30.
  - The bar is 0.65, set in `manifest.judge.bar`.
  - It is a smoke alarm, not proof. The person should still listen to a few lines in the Reader.

## Layout
`vakstudio/`: code.
- `textfmt`: text format and text gate
- `audio`: ffmpeg and MMS acoustics
- `align`: two-pass banded Viterbi
- `judge`: listening check
- `htmlbuild`: Reader files
- `api`: one function per tool
- `cli`, `mcp_server`

`reader/template.html`: the Reader app. `packs/<id>/`: one folder per prayer. `runs/*.jsonl`: one log line per tool call.

## Tests
`pytest -q tests/test_core.py` runs fast and needs no models. `tests/test_lalita_regression.py` needs
the Lalitā recording. It checks that the aligner reproduces the verified word timings exactly.

# Vāk Studio

Turns a prayer text and a recording into a **Vāk Puja Reader** file: one offline HTML file where each
word lights up as it is chanted. It runs on your Mac, and you drive it from Claude Desktop, any other
AI app, or the Terminal.

## Set up (once)
```bash
cd vak   # or wherever you cloned it
./setup.sh                                          # Python env, models (~1.7 GB), tests
.venv/bin/python harness/install_claude_desktop.py  # adds the tools to Claude Desktop
```
Quit and reopen Claude Desktop. Then ask it, for example: *"List my Vāk packs."*

## Make a new prayer (Sandhyavandanam is ready and waiting)
In Claude Desktop, say: *"Import my Sandhyavandanam text from ~/Downloads/sandhya.md and the recording
~/Downloads/sandhya.mp3 into sandhyavandanam-ky, then align, check and build it."*

Or in the Terminal:
```bash
./bin/vak text  sandhyavandanam-ky ~/Downloads/sandhya.md
./bin/vak audio sandhyavandanam-ky ~/Downloads/sandhya.mp3 --label "Recording"
./bin/vak run   sandhyavandanam-ky        # check → align → listen → build
./bin/vak approve sandhyavandanam-ky      # you look at the results and type y
./bin/vak publish sandhyavandanam-ky      # dist/share-by-hand/…-with-recording.html
```

### Text format (`packs/<id>/text.md`)
```
# आचमनम्
> Sip water three times.
ॐ अच्युताय नमः
ॐ अनन्ताय नमः

# प्राणायामः
…
```
- `#` starts a section.
- Each line you chant goes on its own row.
- A blank line starts a new verse.
- A line starting with `>` is an instruction. It is shown in the file, never chanted, and never timed.

### When a recording skips or repeats parts
Tell the studio the order you actually hear, by line number. Repeats are allowed:
`./bin/vak set lalita order "0-3,9-12,25-389,9-12"`.
If the recording opens with a long talk, give one or two anchors, each a line number and the second it starts:
`./bin/vak set sandhyavandanam-ky anchors '{"0": 95}'`.

## What is where
| | |
|---|---|
| `packs/lalita/` | Lalitā Sahasranāma: verified, version 2 |
| `packs/sandhyavandanam-ky/` | Krishna Yajurveda Sandhyavandanam: waiting for text and recording |
| `dist/` | Built files. `dist/<id>.html` holds text and timings only, so it is safe to share anywhere. `dist/share-by-hand/` holds files with the recording inside, for family only |
| `runs/` | A log of every step, one line each |
| `AGENTS.md` | Rules for any AI model working here |

## Privacy
Recordings never leave your Mac unless the pack's licence is `public`. The Bhaskara Prakasha Ashram
recording is **private**: files that contain it go in `dist/share-by-hand/`, for family only.

## Other AI apps and models
The tools are plain MCP, so any MCP app can drive them with any model:
- **Claude Desktop:** `harness/install_claude_desktop.py`
- **Goose:** `harness/goose-extension.yaml`. Goose then works with Anthropic, OpenAI, Gemini,
  OpenRouter, or local Llama and Qwen through Ollama.
- **OpenCode:** `harness/opencode.json`

The heavy work (the MMS aligner and the Whisper listening check) runs locally with no AI model, so
every model gets the same results.

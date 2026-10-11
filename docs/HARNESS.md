# Harness engineering in Vāk Studio

## Agent = Model + Harness

An AI agent is a model plus a harness. The model reads and writes text. The harness is everything around it: the tools it can call, the checks that decide whether a step succeeded, the memory it keeps between steps, the rules it must not break, and the record of what happened. A model without a harness can only talk. With one, it can act, and each action can be checked.

Vāk Studio is a harness for one job: turning a prayer text and a recording into a word-timed Reader file. The model only orchestrates. The heavy work (alignment, the listening check, building the file) is deterministic local code, so the same inputs give the same results whichever model drove the run.

## The five layers

| Layer | What it does | Where it lives in this repo |
|---|---|---|
| Tools | Small, single-purpose operations with typed arguments | `vakstudio/mcp_server.py` (12 MCP tools); `vakstudio/cli.py` (the same operations as `vak`); `vakstudio/api.py` (one function per tool) |
| Verification loops | Checks that decide whether a step passed | `textfmt.check` (text gate, run by `text_check`); `align.align` and `align.gate` (run by `audio_align`); `judge.run` and `judge.gate` (run by `audio_judge`); `pack_preview` (headless Chromium screenshot) |
| Context and memory | State any model can read and continue from | `packs/<id>/manifest.json` (read and written by `workspace.load` and `workspace.save`); `packs/<id>/text.md`; decisions recorded with `pack_set` (`order`, `anchors`, `notes`) |
| Guardrails | Rules the model cannot talk its way around | `workspace.inside()` limits writes to `packs/` and `dist/`; `api.pack_publish` refuses unless `api.gates_ok` passes and an approval file exists; approval files are written only by `cli.approve` or the macOS dialog; files with a recording go to `dist/share-by-hand/` |
| Observability | A record of every step | `workspace.log` writes one JSON line per tool call to `runs/YYYY-MM-DD.jsonl`, through the `@tool` decorator in `api.py` |

## Use any model

The studio speaks the Model Context Protocol, so any MCP host can drive it. Three are set up in `harness/`:

- **Claude Desktop:** run `.venv/bin/python harness/install_claude_desktop.py`. It adds a `vak-studio` entry to Claude Desktop's config, backs up the old config first, and can be re-run. Reopen Claude Desktop afterwards.
- **Goose:** add `harness/goose-extension.yaml` under `extensions:` in Goose's config and replace the placeholder paths. Then run `goose configure` to pick a provider, such as Anthropic, OpenAI, Gemini, or a local Llama or Qwen through Ollama.
- **OpenCode:** merge `harness/opencode.json` into your OpenCode config under `mcp` and replace the placeholder paths.

The results do not depend on the model. The aligner (MMS) and the listening check (Whisper) are local code, and the gates are plain Python. A model chooses which tool to call next. It cannot change a gate's verdict, and switching models loses nothing, because the state lives in `manifest.json`.

## MCP tools

The first sentence of each docstring in `vakstudio/mcp_server.py`:

- `pack_list`: List prayer packs and their check status.
- `pack_new`: Create a new pack.
- `pack_status`: Full manifest: decisions, notes, gate results, build and publish state.
- `pack_set`: Record a decision.
- `text_import`: Save the prayer text (from a file path on this computer, or pasted text) and run the text check.
- `text_check`: Re-check packs/<id>/text.md after the person edits it.
- `audio_import`: Copy a recording (mp3/m4a/wav…) into the pack.
- `audio_align`: Word-time the text to the recording.
- `audio_judge`: Independent listening check on a seeded random sample of lines.
- `pack_build`: Write pack.json and dist/<id>.html (text + timings, no recording inside).
- `pack_preview`: Phone-size screenshot of the built Reader at a line.
- `pack_publish`: Make the shareable offline file.

## Why there is no approve tool

The server has no tool that approves a build, and a test (`test_mcp_server_lists_tools_and_has_no_approve`) fails if one appears. Approval belongs to a person. They run `vak approve <pack>` in a terminal and type `y`, or they answer the macOS dialog. If a model could approve, the publish gate would be only as good as the model's judgement. The gate exists so that a person has heard and seen the result first. Each new build needs a new approval.

# Contributing

## You want to add a prayer (stotra) to Vāk

Suppose you have a stotra in mind, with its text and a recording. This is the path from there to a file your family can open on a phone.

**1. Get the text, and keep its source.** Use a proofread edition from a source you trust, and note where it came from. Do not change the sacred text. Do not fix spellings, add words, or "correct" verse numbers from memory.

**2. Create the pack.** A pack id is lowercase letters, digits and dashes, 2 to 41 characters.

```bash
./bin/vak new my-stotra "Title of the Stotra" --sub "Short subtitle" --source "Where the text came from" --licence private
```

**3. Add the text.** Import a file, or edit `packs/my-stotra/text.md` directly and run the text check.

```bash
./bin/vak text my-stotra ~/Downloads/stotra.md
./bin/vak text-check my-stotra          # after any edit
```

The format of `text.md`:

- `# Section` starts a section.
- Each chanted line goes on its own row.
- A blank line starts a new verse.
- A line starting with `>` is an instruction. It is shown in italics, never chanted, and never timed.

The text gate blocks a chanted line with Latin letters or with no Devanagari. It also blocks verse numbers that jump or repeat. Fix the problem in the source text, not by guessing.

**4. Add the recording.** The file is copied into `packs/my-stotra/audio/` and stays on your computer.

```bash
./bin/vak audio my-stotra ~/Downloads/recording.mp3 --label "Recording" --licence family
```

**5. Describe the recording, if it differs from the text.**

- If it skips or repeats parts, give the line numbers in the order you hear them. Line numbers start at 0. Repeats are allowed:
  `./bin/vak set my-stotra order "0-3,9-12,25-389,9-12"`
- If it opens with a long spoken talk, give two or three anchors, each a line number and the second that line starts:
  `./bin/vak set my-stotra anchors '{"0": 95}'`
  The Reader's Tap-along can help you find those seconds.
- Write down anything else you learn about the recording:
  `./bin/vak set my-stotra notes "Recording skips lines 4 to 8"`

**6. Run the checks.**

```bash
./bin/vak run my-stotra                  # text, align, listening check, build; stops at the first failed gate
./bin/vak preview my-stotra --line 0     # phone-size picture of the Reader
```

Then open the built file and listen to a few lines yourself. The listening check is a smoke alarm, not proof.

**7. Approve.** Only a person can do this. In a terminal:

```bash
./bin/vak approve my-stotra              # shows the results and asks y/N
```

**8. Publish.**

```bash
./bin/vak publish my-stotra --text-only  # no recording inside; safe to share anywhere
./bin/vak publish my-stotra              # with recording; private and family files go to dist/share-by-hand/
```

### Respect rules

- **Never alter sacred text.** The studio does not edit text, and neither should you.
- **Use only recordings you have rights to.** If you do not own the recording, ask its owner first.
- **Licence.** `private` is the default. Files with a recording from a `private` or `family` pack are never hosted. Share them by hand, with family. `public` is only for text, or for a recording whose owner has given written permission.
- **Do not commit recordings.** `packs/*/audio/`, the generated emissions cache and `dist/` are in `.gitignore`. Keep it that way.

## For code contributors

- Run the fast tests with `pytest -q tests/test_core.py`. They need no models. `./setup.sh` runs the full test set after installing everything.
- `reader/template.html` is the Reader. It is one self-contained HTML file that opens offline. Keep it that way, and do not add a separate asset or a network request.
- The Reader must run on Safari 11. The build converts the code with esbuild when `reader/node_modules` is installed. `test_built_file_parses_on_old_ipads` checks that the output parses as ES2017, and it is skipped when Node or esbuild is missing. Do not introduce newer syntax.
- Tools write only inside `packs/` and `dist/`. Keep it that way.
- Read `AGENTS.md` first. Its rules apply to any AI agent working in the repo, not only to Claude.

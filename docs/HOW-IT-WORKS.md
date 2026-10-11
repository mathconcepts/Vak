# How Vāk works

## Part 1: For a 10-year-old

You have a recording of someone chanting. You want each word on the screen to light up at the moment it is sung. For that you need to know when each word starts.

**Teacher one (the aligner).** She has listened to a great many voices in many languages. She plays your recording, reads the words, and puts a tick mark where each word begins. She does this in two rounds. First she makes a rough guess, and then she looks again more closely around her own guess.

**Teacher two (the listening check).** She does not redo the work. She picks a few spots at random, plays a short clip from each, and asks: does this sound like the start of this line, or the end of the one before? If too many clips sound wrong, she says so. She is like a smoke alarm. She can warn you, but she cannot promise that everything is fine.

**The elder (approval).** Only a person can say "this is right, share it". A computer is never allowed to say that for them.

| Analogy | Real part in Vāk |
|---|---|
| Teacher one, ticking where each word starts | Aligner |
| Teacher two, checking random spots by ear | Listening check (the "judge") |
| The elder who signs off | Approval (`vak approve`) |
| The notebook that remembers decisions | manifest.json |
| The diary of everything that happened | run log in `runs/` |

## Part 2: For engineers

### Pipeline

```
 text.txt        recording
    |                |
    v                v
 [text check]   [audio import]
    |                |
    +-------+--------+
            v
      [alignment]  MMS-300m + two-pass banded Viterbi
            |
            v
     [confidence gate]
            |
            v
    [listening check]  Whisper on seeded random clips
            |
            v
       [judge gate]
            |
            v
         [build]  ->  preview
            |
            v
   [human approval]   (person only)
            |
            v
   [publish]  ->  offline HTML
```

The path is: text, text check, recording import, alignment, listening check, build, preview, approval, publish.

### Text format

`# Section` starts a section. One chanted line per row. A blank line starts a new verse. `> instruction` is shown in italics and never chanted, for example `> sip water three times`.

### Alignment

The aligner is an MMS-300m forced aligner: a CTC acoustic model that covers about 1,100 languages. It needs no prior timings.

The idea in plain words: the first pass is wide and coarse, and finds roughly where each line sits in the recording. The second pass is narrow, and looks for exact word boundaries only inside a band around the first answer. Both use a Viterbi search, which picks the most likely path through the audio for the known words.

Results on Lalitā: it reproduced the hand-verified timings exactly, 970 of 970 words, with all line starts matching. With a fake 3-minute intro added and one anchor given, 95% of words were within 0.15 s.

### Listening check

Whisper transcribes short clips taken at random predicted line starts. The random choice is seeded, so a run can be repeated. The check asks whether each clip sounds like the start of that line rather than the end of the previous one.

Calibration on Lalitā, out of 30 clips:

| Case | Score |
|---|---|
| Correct timings | 23 to 25 of 30 |
| Timings shifted by one line | 13 of 30 |
| Pass bar | 0.65 |

It is a smoke alarm, not proof. A pass does not replace a person listening.

### Gates

1. **Text gate:** stops on empty text, Latin letters, no Devanagari, or jumps in verse numbering.
2. **Alignment confidence gate.**
3. **Judge gate:** the listening check above.
4. **Human approval:** a person types `y` in Terminal (`vak approve`) or clicks a macOS dialog. The AI cannot approve. A new build needs a new approval.

### Memory

Each pack has a `manifest.json`. It holds decisions (for example, which lines the recording skips), notes and gate results. Any model reads the same file, so changing from one model to another loses nothing. On the Lalitā recording, the skipped lines are the nyasa lines 4 to 8 and the purvapithika lines 13 to 24, and the first dhyana shloka is repeated at the end. Skipped lines appear faded in the Reader.

### Run log

Every tool call is written as one JSON line in `runs/`. Nothing happens off the record.

### Guardrails

Tools write only inside `packs/` and `dist/`. They never invent or "correct" sacred text. Private recordings go only into files under `dist/share-by-hand/`.

### Tests

There are 11 automated tests: fast core tests, the Lalitā regression, a long-intro anchor test, an old-iPad syntax check, and an MCP tool listing. Reader UI tests (word fill, autoscroll, the pill, calibration) pass on the rebuilt file.

### Why any model can drive it

The heavy work is local code, not a language model. Claude, GPT, Gemini, or a local Llama or Qwen through Ollama can call the same tools, through Claude Desktop, Goose, OpenCode, or the `vak` command.

### Not yet built

Recite mode following your voice word by word against a reference recording (online DTW) is planned. Recite mode today follows loudness and line pace only.

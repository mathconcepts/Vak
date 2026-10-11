# Sankalpa count with no server: feasibility

**Answer: yes, it can live entirely in the HTML file.** Real-time totals cannot. Here is what works and what doesn't.

## How it would work
- Each phone keeps its own tally in the browser's local storage, for example
  `{sankalpa: "Navarathri 108", mine: 14, others: {...}}`. It counts up automatically when a full
  recitation reaches the last line in Music or Recite mode. A manual "+1" button is available too.
- **Family total, shared by WhatsApp instead of a server:**
  - Tap **Share my count**. This opens WhatsApp with a short code or link such as
    `…#s-NAV108.ab12:14`. The parts are the sankalpa id, a random device id and the count.
  - Anyone who opens that link or pastes the code into the app merges it.
  - Merging keeps the **highest count seen for each device**, so the same message can arrive twice,
    or through three people, without anything being counted twice. In engineering terms this is a
    G-counter CRDT: no server and no conflicts.
- The family total is the sum across devices: "Our family: 61 of 108".

## Limits, stated plainly
| Limit | Why | Mitigation |
|---|---|---|
| Not live | No server sees everyone's taps | People share their count after each puja (one tap) |
| Trust-based | Anyone can type a bigger number | A family sankalpa; no leaderboards, by design |
| Can be lost if the phone clears browser data, or the file is opened from a different place | Local storage belongs to the browser and file location | "Share my count" doubles as a backup: re-open your own last message |
| iPhone WhatsApp preview does not run apps | Quick Look shows the text only | Open in Safari (the app already explains this) |

## Effort
About 120 lines in `reader/template.html`, with a counter panel under **More**, plus unit tests for
the merge (duplicate, out-of-order and forwarded messages). No change to Vāk Studio is needed. The
sankalpa name and target can come from the pack (`pack_set notes`) or be typed in the app.

**Recommendation:** build it as above for P2. If live totals ever matter, the Together room (P1) can
carry count messages while people are in the same puja, still with no database.

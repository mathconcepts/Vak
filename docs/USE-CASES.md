# Use cases

Seven short stories. The people are illustrations, not real individuals. Each ends with a tag: **Built today** or **Planned**.

---

## 1. Morning puja at home for elderly parents

**Situation.** A grandfather in Mysuru reads the Lalitā Sahasranāma every morning with a recording playing. His glasses are old and the print is small. When he turns a page, he loses the line.

**What they do.**
1. Someone in the family opens the Reader file once on a tablet.
2. In **Music mode** they press play on the family's own recording.
3. Each word fills with gold as it is sung. If he drifts, he taps any line to jump.
4. The **Aa** control makes the Devanagari larger. A warm light or dark theme suits the hour.
5. The screen stays awake, so it does not dim mid-prayer.

**What changes.** He looks at one place, and the place moves with the voice. The screen stays on and the line stays near the upper third.

**Tag: Built today.**

---

## 2. Chanting before office

**Situation.** A software engineer in Bengaluru has twenty minutes before the cab arrives. She chants alone, no recording, and does not want to tap a screen with wet hands after puja.

**What they do.**
1. Open the Reader and press **Listen** to start **Recite mode**.
2. Chant at her own pace. The Reader follows the loudness of her voice and moves line to line.
3. If she scrolls up to re-read, auto-scroll pauses for 5 seconds. A **Back to current line** pill returns her.

**What changes.** The page keeps pace with her, fast on a rushed morning and slow on a calm one. It learns her pace; it does not understand the words.

**Tag: Built today.**

---

## 3. Navarathri across three places

**Situation.** A family is spread across Bengaluru, Pune and abroad. During Navarathri they would like to chant the same prayer together, each person seeing the same word at the same moment.

**What they do (as designed).**
1. One person leads and shares a link on WhatsApp.
2. Others open it and follow the leader's word on their own screens.
3. The leader's messages are signed, and the relay stores nothing. No accounts.

**What changes.** Distance matters less. The elder in Pune and the grandchild abroad are on the same line.

**Tag: Planned.** Together mode is designed but not built.

---

## 4. A boy learning Sandhyavandanam

**Situation.** After his upanayanam, a boy is learning सन्ध्यावन्दनम्. He needs to hear each word slowly and see exactly which one is being said.

**What they do.**
1. His father prepares the Sandhyavandanam (Krishna Yajurveda) pack. It is created and **awaiting the text and a recording**.
2. Once built, the boy opens it in **Music mode**.
3. He lowers the **Speed** control so the recording slows down, with each word lit as it is sung.
4. Instructions such as "sip water three times" appear in italics. They are shown, never chanted.

**What changes.** He can learn word by word, at a speed that suits him, with his father beside him.

**Tag: Speed control is built today. The Sandhyavandanam pack is awaiting text and recording.**

---

## 5. A family sankalpa of 108 parayanams

**Situation.** A family resolves to complete 108 readings together over the weeks of a vow. Each home keeps its own count, and they wish to know the family total.

**What they do (as designed).**
1. Each phone keeps its own tally.
2. Totals are merged by sharing codes on WhatsApp.
3. No server holds the count.

**What changes.** The vow becomes visible without anyone keeping a notebook. Details are in [sankalpa.md](sankalpa.md).

**Tag: Planned.** Designed, not built.

---

## 6. A volunteer preparing a new stotra

**Situation.** A teacher at a community hall wants a new stotra in the Reader for the neighbourhood. She is not a programmer. She has the text and a recording she is allowed to use.

**What they do.**
1. Install Vāk Studio and connect it to **Claude Desktop**.
2. Ask: "List my Vāk packs", then ask for a new pack from her text.
3. Studio checks the text, imports the recording, finds the timing of every word, and runs a listening check.
4. She previews the result and listens.
5. She types `y` in the Terminal (`vak approve`) or clicks the macOS dialog. The AI cannot do this for her.
6. Studio publishes an offline HTML file.

**What changes.** She gets a word-timed prayer without timing hundreds of words by hand, and nothing reaches others without her say. Any model can drive Studio, because the heavy work is local code.

**Tag: Built today.**

---

## 7. An older iPad, opened from WhatsApp

**Situation.** A grandmother has an older iPad. Her granddaughter sends the Reader file over WhatsApp.

**What they do.**
1. She taps the file. The prayer text is written into the page itself, so even the file preview shows the prayer.
2. She opens it in Safari. The code is converted at build time to run on Safari 11 and newer.
3. Any recording is added privately, on the device.

**What changes.** No app store, no account, no update to install.

**Tag: Built today.**

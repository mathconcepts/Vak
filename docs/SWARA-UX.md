# Swaras on screen: the user journey

How the Reader shows anudātta, svarita and dīrgha svarita, and why.

## Who and where

Amma and Appa chant Sri Rudram in the morning, with the recording on an iPad that stands on a shelf near the lamp, about an arm's length away. They know the chant but want to stay true to the reciter's swaras. Light is low, eyes are tired, and there is no time to read a key mid-verse.

## The journey

| Moment | What they need | What the Reader does |
|---|---|---|
| **1. Open the prayer** | Know what the colours mean, once | A legend card at the top with large examples: क॒ anudātta (low), क॑ svarita (rising), का᳚ dīrgha svarita (long rise), ’ pause |
| **2. Glance at the page** | See every swara at arm's length, without the marks being covered | Each marked syllable sits on a soft tile. **Blue, line under** = low. **Orange, line over** = rising. **Double line** = long rise. Shape and colour both carry the meaning, so it also works for colour-blind eyes. Lines are spaced wider for Vedic texts. |
| **3. Follow the chant** | Know which word is being sung, and its swara, without hunting | The **lens** floats above the current line and shows the word being sung, twice as large. The syllable being sung **grows**, and its swara is named under it ("anudātta · low"). The same syllable glows in the line. |
| **3b. Feel the pitch** | Sense low and high without reading labels | Motion carries meaning: the line being sung **zooms in** and the rest recede. The lens **slides** to each new word. The syllable being sung **grows and moves with its pitch**: it dips for anudātta and lifts for svarita. A **pitch line** under the lens word (low, middle, high, from the swara marks) has a dot that travels along it. The tile in the line pulses once. |
| **4. Pause** | Breathe where the reciter breathes | **’** and **’’** after a word mark the reciter's pauses, measured from the recording. They glow during the pause, and the lens holds the last word through short pauses. |
| **5. Practise a hard spot** | Hear one word or line again, slowly | Tap a word to play from it. More → Repeat this line. 0.5× speed keeps the pitch true. |
| **6. Make it calmer** | Less on screen | Settings (Aa): Swara marks, Swara lens and Pause marks each switch off. Reduced-motion devices get no zoom animation. |

## Where the timing comes from

- **The recording is the authority** for when each word is sung and where the pauses are. Word timings come from the aligner and are checked by ear.
- **Within a word, syllable timing is an estimate.** The word's time is shared out by the classical rule: a long syllable (guru) gets two parts, a short one (laghu) gets one. It is close, not exact.
- **Which syllable carries which swara comes from the published text** (sanskritdocuments.org, proofread). The app does not detect pitch from the voice.

## Design rules we kept

- Letters are never split inside an akshara, so conjuncts always render correctly. Tiles are drawn in a layer behind the text.
- The original swara marks stay visible. Nothing covers them.
- Motion is calm and has meaning: one zoomed line, one lens, one syllable growing in the direction of its pitch. Devices set to reduce motion get no movement.
- Works offline and on older iPads (no newer-only CSS or JavaScript).

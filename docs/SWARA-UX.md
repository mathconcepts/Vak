# Swaras on screen: the user journey

How the Reader shows anudātta, svarita and dīrgha svarita, and why.

## Who and where

Amma and Appa chant Sri Rudram in the morning, with the recording on an iPad that stands on a shelf near the lamp, about an arm's length away. They know the chant but want to stay true to the reciter's swaras. Light is low, eyes are tired, and there is no time to read a key mid-verse.

## The journey

| Moment | What they need | What the Reader does |
|---|---|---|
| **1. Open the prayer** | Know what the colours mean, once | A legend card at the top with large examples: क॒ anudātta (low), क॑ svarita (rising), का᳚ dīrgha svarita (long rise), ’ pause |
| **2. Glance at the page** | See every swara at arm's length, without the marks being covered | Each marked syllable sits on a soft tile. **Blue, line under** = low. **Orange, line over** = rising. **Double line** = long rise. Shape and colour both carry the meaning, so it also works for colour-blind eyes. Lines are spaced wider for Vedic texts. |
| **3. Follow the chant** | Know where the chant is, and its swara, without the eye being pulled around | The **zoom lens** shows the **whole line** being sung, one and a half times larger, above it. It stays still for the whole line; only the light moves, sweeping through it syllable by syllable. The syllable being sung grows a little and its swara is named under it ("anudātta · low"). The same syllable glows in the line. |
| **3b. Feel the pitch** | Sense low and high without reading labels | Motion carries meaning: the line being sung **zooms in** and the rest recede. The lens changes only when the line changes. The syllable being sung **grows and moves with its pitch**: it dips for anudātta and lifts for svarita. A **pitch line** under the lens word (low, middle, high, from the swara marks) has a dot that travels along it. The tile in the line pulses once. |
| **4. Pause** | Breathe where the reciter breathes | **’** and **’’** after a word mark the reciter's pauses, measured from the recording. They glow during the pause, and the lens holds the last word through short pauses. |
| **5. Practise a hard spot** | Loop exactly the part that is hard, and chant it back | More → **Practise a portion**. Tap the first word, then the last word (either order). Tap a line to take the whole line, or press **Whole line** or **Whole anuvāka**. It loops at once. Choose **3, 5 or 11 times** or keep repeating, a **2–8 s pause** after each time ("Your turn: chant it now… 3"), and **0.5× / 0.75×** speed with true pitch. Tap new words any time to change the portion. **Done** returns to normal. |
| **6. Make it calmer** | Less on screen | More → **Zoom lens** and **Focus line** switch off the lens and the line zoom. Settings (Aa): Swara marks and Pause marks switch off. Reduced-motion devices get no animation. |

## Where the timing comes from

- **The recording is the authority** for when each word is sung and where the pauses are. Word timings come from the aligner and are checked by ear.
- **Within a word, syllable timing is an estimate.** The word's time is shared out by the classical rule: a long syllable (guru) gets two parts, a short one (laghu) gets one. It is close, not exact.
- **Which syllable carries which swara comes from the published text** (sanskritdocuments.org, proofread). The app does not detect pitch from the voice.

## Why the lens shows a line, not a word

The first lens followed single words. In Namakam that is 1,134 words in 16 minutes, so the card was rebuilt and moved about 70 times a minute, and the eye was pulled across the screen each time. The line lens is rebuilt only when the line changes (about once every 5 seconds) and stays in one place; only the light moves inside it.

## Design rules we kept

- Letters are never split inside an akshara, so conjuncts always render correctly. Tiles are drawn in a layer behind the text.
- The original swara marks stay visible. Nothing covers them.
- Motion is calm and has meaning: one zoomed line, one lens, one syllable growing in the direction of its pitch. Devices set to reduce motion get no movement.
- Works offline and on older iPads (no newer-only CSS or JavaScript).

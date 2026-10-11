"""The listening judge: an independent check of alignment, by ear (Whisper), not by the aligner.

For a seeded random sample of lines it transcribes a short clip at the predicted start and asks:
does the clip sound more like the start of THIS line than the end of the PREVIOUS line?
A line passes when score = sim(heard, head of line) − sim(heard, tail of previous) > 0.
Comparison uses a consonant skeleton, so script and spelling differences in the transcript do not matter.
"""
import random, re, unicodedata
import numpy as np

DEV = {}
for chars, s in [("कखक़ख़", "k"), ("गघग़", "g"), ("ङञणन", "n"), ("चछ", "c"), ("जझज़", "j"),
                 ("टठतथ", "t"), ("डढड़ढ़दध", "d"), ("पफफ़", "p"), ("बभव", "b"), ("म", "m"),
                 ("य", "y"), ("रऱ", "r"), ("लळ", "l"), ("शषस", "s"), ("ह", "h"), ("ं", "n")]:
    for c in chars:
        DEV[c] = s
DIG = [("chh", "c"), ("kh", "k"), ("gh", "g"), ("ch", "c"), ("jh", "j"), ("th", "t"), ("dh", "d"),
       ("ph", "p"), ("bh", "b"), ("sh", "s"), ("x", "ks"), ("q", "k"), ("f", "p"), ("z", "j"), ("w", "b"), ("v", "b")]
ALPHA = "kgncjtdpbmyrlsh"


def dev_skel(t):
    t = unicodedata.normalize("NFC", t.replace("ॐ", "ओम्"))
    return [DEV[c] for c in t if c in DEV]


def lat_skel(t):
    t = unicodedata.normalize("NFKD", t.lower())
    t = re.sub(r"[^a-z]", "", "".join(c for c in t if not unicodedata.combining(c)))
    for a, b in DIG:
        t = t.replace(a, b)
    return [c for c in t if c in ALPHA]


COARSE = str.maketrans("gjdb", "kctp")   # Whisper often confuses voiced/unvoiced pairs in chant


def skel(t):
    return dev_skel(t) + lat_skel(re.sub(r"[ऀ-ॿ]", "", t))


def coarse(sk):
    return [c.translate(COARSE) for c in sk]


def sim(x, y):
    """Local-alignment score of skeleton x against target y, normalised to 0..1."""
    if not x or not y:
        return 0.0
    n, m = len(x), len(y)
    H = np.zeros((n + 1, m + 1)); best = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            s = 2 if x[i - 1] == y[j - 1] else -1
            H[i, j] = max(0, H[i - 1, j - 1] + s, H[i - 1, j] - 1, H[i, j - 1] - 1)
            best = max(best, H[i, j])
    return best / (2 * len(y))


def sample(aligned_lines, n, seed):
    rng = random.Random(seed)
    pool = list(aligned_lines)
    return sorted(rng.sample(pool, min(n, len(pool))))


def run(wav_samples, lines, timing, n=30, seed=1, model_size="small", prompt="", language="hi", log=None):
    """timing: Reader-format alignment (times/words). Returns {"passed","total","rate","items","seed"}."""
    from faster_whisper import WhisperModel
    m = WhisperModel(model_size, device="auto", compute_type="int8")
    times = timing["times"]
    heard_order = [i for i, t in sorted(((i, t) for i, t in enumerate(times) if t is not None), key=lambda x: x[1])]
    prev = {heard_order[k]: heard_order[k - 1] for k in range(1, len(heard_order))}
    ids = sample([i for i in heard_order if i in prev], n, seed)
    items, passed = [], 0
    for i in ids:
        t = times[i]
        clip = wav_samples[int(max(0, t - 0.15) * 16000):int((t + 1.6) * 16000)]
        segs, _ = m.transcribe(clip, language=language, beam_size=1, condition_on_previous_text=False,
                               vad_filter=False, initial_prompt=prompt or None)
        txt = " ".join(s.text for s in segs).strip()
        sk = coarse(skel(txt)[:10])
        head = sim(sk, coarse(dev_skel(lines[i])[:6]))
        tail = sim(sk, coarse(dev_skel(lines[prev[i]])[-6:]))
        score = head - tail
        ok = bool(score > 0 or (head >= 0.5 and score >= 0))
        passed += ok
        items.append({"line": i, "t": t, "score": round(float(score), 2), "ok": bool(ok), "heard": txt[:60]})
        if log:
            log(items[-1])
    return {"passed": passed, "total": len(ids), "rate": round(passed / max(1, len(ids)), 3), "items": items,
            "seed": seed, "model": model_size}


def gate(result, bar=0.65):
    """JudgeBelowBar gate. Calibrated on Lalitā: verified timings score 23–25/30 (two seeds), timings shifted by one line score 13/30. Bar 0.65 separates them. A smoke alarm, not proof: the align gate and a person listening complete it."""
    return {"ok": result["total"] > 0 and result["rate"] >= bar, "rate": result["rate"], "bar": bar,
            "failed_lines": [x["line"] for x in result["items"] if not x["ok"]]}

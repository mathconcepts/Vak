"""Word-level forced alignment of a prayer text to its recording (CTC / MMS, banded Viterbi).

Two passes, no LLM and no prior timings needed:
  pass 1: spread the chanted text over the speech region in proportion to its letters
          (bent through any user anchors), and allow each line ±band1 seconds around that guess;
  pass 2: re-align with a tight ±band2 window around pass-1 line spans.

`order` lists chanted line numbers in the order heard. A line may repeat (e.g. a closing reprise):
its first occurrence fills times/words, later ones go to `reprise`. Lines never in `order` are
`notInRecording` (shown faded in the Reader).
"""
import re
import numpy as np
from numba import njit

FPS = 50.0
_U = None


def _uroman():
    global _U
    if _U is None:
        import uroman as ur
        _U = ur.Uroman()
    return _U


def tokens(line):
    """The Reader's words for a line (split on spaces), each with its romanized letters."""
    out = []
    for w in line.strip().split():
        r = _uroman().romanize_string(w.replace("ॐ", "ओम्")).lower()
        out.append((w, re.sub(r"[^a-z']", "", r)))
    return out


@njit(cache=False)
def _viterbi(E, tok, lo, hi, BLANK):
    T = E.shape[0]; K = len(tok); S = 2 * K + 1
    NEG = -1e30
    prev = np.full(S, NEG); cur = np.full(S, NEG)
    a_t = np.zeros(T, np.int64); b_t = np.zeros(T, np.int64)
    a = 0; b = 0
    for t in range(T):
        while a < S - 1 and hi[a] < t: a += 1
        while b < S - 1 and lo[b + 1] <= t: b += 1
        a_t[t] = a; b_t[t] = b
    off = np.zeros(T + 1, np.int64)
    for t in range(T): off[t + 1] = off[t] + (b_t[t] - a_t[t] + 1)
    bp = np.zeros(off[T], np.int8)
    for t in range(T):
        a = a_t[t]; b = b_t[t]
        for s in range(a, b + 1):
            lab = BLANK if s % 2 == 0 else tok[s // 2]
            e = E[t, lab]
            if t == 0:
                cur[s] = e if s < 2 else NEG; bp[off[t] + s - a] = 0; continue
            best = prev[s]; arg = 0
            if s >= 1 and prev[s - 1] > best: best = prev[s - 1]; arg = 1
            if s >= 2 and s % 2 == 1 and tok[s // 2] != tok[s // 2 - 1] and prev[s - 2] > best: best = prev[s - 2]; arg = 2
            cur[s] = best + e; bp[off[t] + s - a] = arg
        if t + 1 < T:
            for s in range(a_t[t], min(a_t[t + 1], S)): cur[s] = NEG
        for s in range(S): prev[s] = cur[s]; cur[s] = NEG
    s = S - 1 if prev[S - 1] >= prev[S - 2] else S - 2
    path = np.zeros(T, np.int64)
    for t in range(T - 1, -1, -1):
        path[t] = s
        s -= bp[off[t] + s - a_t[t]]
    return path


def speech_region(E, blank):
    """First/last second where speech is likely (non-blank probability, smoothed over 1 s)."""
    p = 1 - np.exp(E[:, blank])
    k = int(FPS)
    sm = np.convolve(p, np.ones(k) / k, mode="same")
    idx = np.where(sm > 0.25)[0]
    if len(idx) == 0:
        return 0.0, len(E) / FPS
    return idx[0] / FPS, (idx[-1] + 1) / FPS


def _guess_spans(seq_chars, t0, t1, anchors_pos):
    """Line spans from letter counts, bent through anchors [(seq_index, seconds)]."""
    cum = np.concatenate([[0], np.cumsum(seq_chars)]).astype(float)
    knots = {0.0: t0, float(cum[-1]): t1}
    for q, t in anchors_pos:                     # anchors override the speech-region ends
        knots[float(cum[q])] = float(t)
    kx = np.array(sorted(knots)); ky = np.array([knots[k] for k in kx])
    if len(anchors_pos) and min(cum[q] for q, _ in anchors_pos) > 0 and ky[1] < ky[0]:
        ky[0] = ky[1]
    tt = np.interp(cum, kx, np.maximum.accumulate(ky))
    return [(tt[q], tt[q + 1]) for q in range(len(seq_chars))]


def _pass(E, vocab, seq, spans, band):
    T = E.shape[0]; BLANK = vocab["<blank>"]
    tok, tok_word, words = [], [], []          # words: (seq q, word index, has letters)
    for q, (_, toks) in enumerate(seq):
        for wi, (w, r) in enumerate(toks):
            words.append((q, wi))
            for ch in r:
                if ch in vocab:
                    tok.append(vocab[ch]); tok_word.append(len(words) - 1)
    tok = np.array(tok, np.int32); tok_word = np.array(tok_word, np.int32)
    K = len(tok); S = 2 * K + 1
    lo = np.zeros(S, np.int64); hi = np.zeros(S, np.int64)
    for k in range(K):
        s, e = spans[words[tok_word[k]][0]]
        lo[2 * k + 1] = int(max(0, (s - band) * FPS)); hi[2 * k + 1] = int(min(T - 1, (e + band) * FPS))
    lo[0] = 0; hi[0] = hi[1]
    for s in range(2, S, 2):
        lo[s] = lo[s - 1]; hi[s] = hi[s + 1] if s + 1 < S else T - 1
    hi[S - 1] = T - 1
    lo = np.minimum.accumulate(lo[::-1])[::-1]; hi = np.maximum.accumulate(hi)
    path = _viterbi(E, tok, lo, hi, BLANK)
    first = np.full(K, -1); last = np.full(K, -1); score = np.zeros(K)
    st = path % 2 == 1; ks = path // 2
    for t in np.where(st)[0]:
        k = ks[t]
        if first[k] < 0: first[k] = t
        last[k] = t; score[k] = max(score[k], np.exp(E[t, tok[k]]))
    W = len(words)
    ws = np.full(W, np.nan); we = np.full(W, np.nan); wc = np.zeros(W)
    for k in range(K):
        w = tok_word[k]
        if first[k] >= 0:
            if np.isnan(ws[w]): ws[w] = first[k] / FPS
            we[w] = (last[k] + 1) / FPS
        wc[w] += score[k]
    cnt = np.bincount(tok_word, minlength=W); wc = wc / np.maximum(1, cnt)
    out = []
    for q, (_, toks) in enumerate(seq):
        idx = [n for n, (qq, _) in enumerate(words) if qq == q]
        wl = [None if np.isnan(ws[n]) else [round(float(ws[n]), 2), round(float(we[n]), 2)] for n in idx]
        lettered = [n for n in idx if cnt[n] > 0]
        out.append({"words": wl, "conf": round(float(np.mean(wc[lettered])) if lettered else 0.0, 3)})
    return out


def align(lines, E, vocab, order=None, anchors=None, band1=None, band2=12.0, region=None):
    """Returns {"times", "words", "reprise", "notInRecording", "conf", "region", "bands"} in the Reader's format."""
    order = list(range(len(lines))) if order is None else list(order)
    seq = [(i, tokens(lines[i])) for i in order]
    chars = [max(1, sum(len(r) for _, r in toks)) for _, toks in seq]
    T = E.shape[0]; dur = T / FPS
    t0, t1 = region or speech_region(E, vocab["<blank>"])
    band1 = band1 or max(40.0, 0.06 * dur)
    # anchors are by line number; pin the first occurrence of that line
    apos = []
    for i, t in (anchors or {}).items():
        i = int(i)
        if i in order:
            apos.append((order.index(i), float(t)))
    spans = _guess_spans(chars, t0, t1, apos)
    p1 = _pass(E, vocab, seq, spans, band1)
    spans2 = []
    for q, r in enumerate(p1):
        got = [w for w in r["words"] if w]
        spans2.append((got[0][0], got[-1][1]) if got else spans[q])
    p2 = _pass(E, vocab, seq, spans2, band2)
    n = len(lines)
    times, words, conf, reprise, seen = [None] * n, [None] * n, [None] * n, [], set()
    for (i, _), r in zip(seq, p2):
        st = next((w[0] for w in r["words"] if w), None)
        if i in seen:
            reprise.append([st, i, r["words"]])
        else:
            seen.add(i); times[i] = st; words[i] = r["words"]; conf[i] = r["conf"]
    return {"times": times, "words": words, "reprise": reprise,
            "notInRecording": [k for k in range(n) if k not in seen], "conf": conf,
            "region": [round(t0, 2), round(t1, 2)], "bands": [round(band1, 1), band2]}


def gate(result, min_conf=0.3, max_low_frac=0.10):
    """AlignLowConfidence gate: fail if more than max_low_frac of aligned lines are below min_conf."""
    c = [(i, x) for i, x in enumerate(result["conf"]) if x is not None]
    low = [i for i, x in c if x < min_conf]
    frac = len(low) / max(1, len(c))
    return {"ok": frac <= max_low_frac and len(c) > 0, "low_lines": low, "low_frac": round(frac, 3),
            "median_conf": round(float(np.median([x for _, x in c])), 3) if c else 0.0}

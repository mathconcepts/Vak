"""The generic aligner must reproduce Lalitā's verified word timings (checked by ear, 27/30).
Needs packs/lalita/audio (private, not in git). Skips otherwise. ~1 min with cached acoustics, ~10 min without."""
import json, os, sys
import numpy as np, pytest
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
P = os.path.join(HERE, "packs", "lalita")

@pytest.mark.skipif(not os.path.exists(os.path.join(P, "audio", "audio16.wav")), reason="Lalitā recording not present")
def test_reproduces_verified_timing():
    from vakstudio import align, audio, textfmt
    from vakstudio.workspace import parse_order
    m = json.load(open(os.path.join(P, "manifest.json"), encoding="utf-8"))
    L = textfmt.lines(textfmt.parse(open(os.path.join(P, "text.md"), encoding="utf-8").read()))
    E = audio.emissions(os.path.join(P, "audio", "audio16.wav"), os.path.join(P, "work", "emissions.npy"))
    r = align.align(L, E, audio.vocab(), order=parse_order(m["order"], len(L)))
    V = json.load(open(os.path.join(HERE, "tests", "lalita_verified_timing.json")))
    assert r["notInRecording"] == V["notInRecording"]
    d = [abs(a[0] - b[0]) for x, y in zip(V["words"], r["words"]) if x and y for a, b in zip(x, y) if a and b]
    assert len(d) >= 950 and np.percentile(d, 95) <= 0.10, (len(d), np.percentile(d, 95))
    assert align.gate(r)["ok"]

@pytest.mark.skipif(not os.path.exists(os.path.join(P, "work", "emissions.npy")), reason="acoustics not cached")
def test_survives_long_intro_with_one_anchor():
    """Pretend the recording starts with 3 minutes of talk: the guess is off, one anchor fixes it."""
    from vakstudio import align, audio, textfmt
    from vakstudio.workspace import parse_order
    m = json.load(open(os.path.join(P, "manifest.json"), encoding="utf-8"))
    L = textfmt.lines(textfmt.parse(open(os.path.join(P, "text.md"), encoding="utf-8").read()))
    E = np.load(os.path.join(P, "work", "emissions.npy")).astype(np.float32)
    V = audio.vocab()
    intro = E[60 * 50:240 * 50]                       # 3 min of real chant audio, out of place, before the start
    E2 = np.concatenate([intro, E])
    order = parse_order(m["order"], len(L))
    ver = json.load(open(os.path.join(HERE, "tests", "lalita_verified_timing.json")))
    r = align.align(L, E2, V, order=order, anchors={"0": ver["times"][0] + 180})
    d = [abs((a[0] - 180) - b[0]) for x, y in zip(r["words"], ver["words"]) if x and y for a, b in zip(x, y) if a and b]
    assert np.percentile(d, 95) <= 0.15, np.percentile(d, 95)

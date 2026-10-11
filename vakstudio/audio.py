"""Recording preparation and acoustic emissions (model-free of any LLM).

prepare(): any audio file → 16 kHz mono WAV, plus its sha256 (the cache key).
emissions(): MMS-300m forced-aligner CTC log-probs, 50 frames/s, cached per recording hash.
"""
import hashlib, json, os, shutil, subprocess, time, wave
import numpy as np

MODEL = "MahmoudAshraf/mms-300m-1130-forced-aligner"
FPS = 50.0
SR = 16000


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise RuntimeError("ffmpeg not found. Install it (macOS: brew install ffmpeg) or pip install imageio-ffmpeg")


def prepare(src, out_wav):
    os.makedirs(os.path.dirname(out_wav), exist_ok=True)
    r = subprocess.run([_ffmpeg(), "-y", "-v", "error", "-i", src, "-ac", "1", "-ar", str(SR), "-sample_fmt", "s16", out_wav],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("Could not read the recording: " + r.stderr.strip()[-300:])
    with wave.open(out_wav) as w:
        dur = w.getnframes() / w.getframerate()
    return {"wav": out_wav, "duration": round(dur, 2), "sha256": sha256(src), "bytes": os.path.getsize(src)}


def load_wav(path):
    with wave.open(path) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return a


def vocab():
    from huggingface_hub import hf_hub_download
    return json.load(open(hf_hub_download(MODEL, "vocab.json")))


def _device():
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def emissions(wav, cache_npy, progress=None, threads=None):
    """Log-probs T x V (float16 on disk). Re-uses cache_npy when present."""
    if os.path.exists(cache_npy):
        return np.load(cache_npy).astype(np.float32)
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")   # Apple GPU: fall back to CPU for any missing op
    import torch
    from transformers import Wav2Vec2ForCTC
    if threads:
        torch.set_num_threads(threads)
    dev = _device()
    model = Wav2Vec2ForCTC.from_pretrained(MODEL).eval().to(dev)
    a = load_wav(wav)
    a = (a - a.mean()) / (a.std() + 1e-7)
    WIN, CTX = 30 * SR, 2 * SR
    out, pos, t0 = [], 0, time.time()
    while pos < len(a):
        s = max(0, pos - CTX); e = min(len(a), pos + WIN + CTX)
        x = torch.from_numpy(a[s:e]).unsqueeze(0).to(dev)
        try:
            with torch.inference_mode():
                lp = torch.log_softmax(model(x).logits[0].float(), -1).cpu().numpy()
        except RuntimeError:
            if dev == "cpu":
                raise
            dev = "cpu"; model = model.to("cpu"); x = x.to("cpu")   # GPU path failed: finish on CPU
            with torch.inference_mode():
                lp = torch.log_softmax(model(x).logits[0].float(), -1).cpu().numpy()
        i0 = int(round((pos - s) / SR * FPS)); i1 = i0 + int(round(min(WIN, len(a) - pos) / SR * FPS))
        out.append(lp[i0:i1])
        pos += WIN
        if progress:
            progress(min(pos, len(a)) / len(a), time.time() - t0)
    E = np.concatenate(out).astype(np.float16)
    os.makedirs(os.path.dirname(cache_npy), exist_ok=True)
    np.save(cache_npy, E)
    return E.astype(np.float32)

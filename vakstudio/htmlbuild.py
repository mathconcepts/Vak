"""Build Reader HTML files from packs (reader/template.html).

Every output is one self-contained file that opens offline, on phones, iPads (Safari 11+) and laptops.
The text is also written into the page as plain HTML so it can be read where scripts do not run.
"""
import base64, html as H, json, os, re, shutil, subprocess

READER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reader")
DEFAULT_BITES = ("Press play. Follow the light. Chant along.", "Every word, in step with the recitation.")
HEAD = ('<!doctype html><html lang="sa"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>')


def prerender(sections):
    out, i = [], 0
    for sec in sections:
        if sec.get("title"):
            out.append('<h2 class="sec-h">' + H.escape(sec["title"]) + "</h2>")
        for v in sec["verses"]:
            if isinstance(v, dict):
                out.append('<p class="note">' + H.escape(v["note"]) + "</p>"); continue
            rows = []
            for line in v:
                toks = [t for t in line.strip().split() if t]
                rows.append('<div class="ln" data-i="%d">' % i +
                            " ".join('<span class="w">' + H.escape(t.replace("-", "‐")) + "</span>" for t in toks) + "</div>")
                i += 1
            out.append('<div class="verse">' + "".join(rows) + "</div>")
    return "".join(out)


def transpile(js):
    """Convert the app's code for older iPads. Skipped (with a warning) if esbuild is not installed."""
    exe = os.path.join(READER, "node_modules", ".bin", "esbuild")
    npx = shutil.which("npx")
    if os.path.exists(exe):
        cmd = [exe]
    elif npx and os.path.isdir(os.path.join(READER, "node_modules", "esbuild")):
        cmd = [npx, "--prefix", READER, "esbuild"]
    else:
        return js, "esbuild not installed (run: cd reader && npm install); built without old-iPad conversion"
    r = subprocess.run(cmd + ["--target=safari11", "--loader=js", "--charset=utf8", "--log-level=error"],
                       input=js, capture_output=True, text=True, cwd=READER)
    if r.returncode != 0:
        raise RuntimeError("esbuild failed: " + r.stderr[-500:])
    return r.stdout, None


def render(packs, audio=None):
    """packs: list of pack dicts (pack.json). audio: {pack_id: (bytes, mime)} to embed. Returns (html, warnings)."""
    t = open(os.path.join(READER, "template.html"), encoding="utf-8").read()
    aw = {k: base64.b64encode(open(os.path.join(READER, "awake." + k), "rb").read()).decode() for k in ("mp4", "webm")}
    p0 = packs[0]
    bites = (p0.get("bite") or DEFAULT_BITES[0], p0.get("bite_end") or DEFAULT_BITES[1])
    out = (t.replace("__AWAKE_MP4__", aw["mp4"]).replace("__AWAKE_WEBM__", aw["webm"])
            .replace("__PRERENDER__", prerender(p0["sections"]))
            .replace("__TITLE0__", H.escape(p0["title"]))
            .replace("__BITE0__", H.escape(bites[0])).replace("__BITE1__", H.escape(bites[1]))
            .replace("__PACKS__", json.dumps(packs, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")))
    left = re.findall(r"__[A-Z0-9_]+__", out)
    if left:
        raise RuntimeError("Template placeholders not filled: " + ", ".join(sorted(set(left))))
    m = re.search(r"<script>(.*?)</script>", out, re.S)
    js, warn = transpile(m.group(1))
    out = out[:m.start(1)] + js + out[m.end(1):]
    emb = ""
    for pid, (data, mime) in (audio or {}).items():
        emb += '<script type="application/octet-stream" id="embeddedAudio-%s" data-mime="%s">' % (pid, mime) + \
               base64.b64encode(data).decode() + "</script>"
    return HEAD + emb + out + "</body></html>", [w for w in [warn] if w]

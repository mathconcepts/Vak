"""Vāk Studio operations. One function per tool; the CLI and the MCP server both call these.

Every function returns a plain dict ({"ok": True, ...} or a VakError dict) and is logged to runs/.
Heavy work (aligner, judge) is local and uses no LLM, so the result is the same whichever model drives.
"""
import functools, json, mimetypes, os, shutil, sys, time

from . import textfmt
from .workspace import (DIST, EDITABLE, PACKS, VakError, file_hash, inside, list_ids, load, log, now,
                        parse_order, pdir, save)

LICENCES = ("private", "family", "public")   # private/family: never hosted; embedded only in files you share by hand


def tool(fn):
    @functools.wraps(fn)
    def wrap(*a, **kw):
        t0 = time.time()
        args = dict(zip(fn.__code__.co_varnames, a)); args.update(kw)
        try:
            r = fn(*a, **kw)
            r.setdefault("ok", True)
            log(fn.__name__, args, r.get("ok", True), r, t0)
            return r
        except VakError as e:
            log(fn.__name__, args, False, None, t0, e.code)
            return e.as_dict()
        except Exception as e:  # named so it is never silent; message goes to the caller
            log(fn.__name__, args, False, None, t0, type(e).__name__)
            return {"ok": False, "error": "Unexpected", "message": f"{type(e).__name__}: {e}"}
    return wrap


def _say(msg):
    print(msg, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- packs
@tool
def pack_list():
    out = []
    for pid in list_ids():
        m = load(pid)
        out.append({"id": pid, "title": m.get("title"), "status": status_line(m), "version": m.get("version")})
    return {"packs": out}


@tool
def pack_new(pack_id, title, sub="", source="", licence="private"):
    d = pdir(pack_id)
    if os.path.exists(os.path.join(d, "manifest.json")):
        raise VakError("PackExists", f"Pack {pack_id} already exists.")
    if licence not in LICENCES:
        raise VakError("BadLicence", f"licence must be one of {LICENCES}")
    for sub_ in ("audio", "work", "approvals"):
        os.makedirs(inside(os.path.join(d, sub_), PACKS), exist_ok=True)
    m = {"id": pack_id, "title": title, "sub": sub, "source": source, "licence": licence, "version": 0,
         "created": now(), "order": None, "anchors": {}, "judge": {"n": 30, "seed": 1, "bar": 0.65},
         "notes": [], "gates": {}, "recording": None}
    save(pack_id, m)
    tm = os.path.join(d, "text.md")
    if not os.path.exists(tm):
        open(tm, "w", encoding="utf-8").write(TEXT_TEMPLATE)
    return {"pack": pack_id, "next": "Put the prayer text in text.md (or call text_import), then audio_import."}


@tool
def pack_status(pack_id):
    m = load(pack_id)
    return {"pack": pack_id, "summary": status_line(m), "manifest": m}


@tool
def pack_set(pack_id, field, value):
    """Record a decision (title, order, anchors, licence, notes …). Free text in `notes` is the pack's memory."""
    if field not in EDITABLE:
        raise VakError("FieldNotEditable", f"{field} cannot be set here. Editable: {sorted(EDITABLE)}")
    m = load(pack_id)
    if isinstance(value, str) and field in ("anchors", "judge"):
        value = json.loads(value)
    if field == "licence" and value not in LICENCES:
        raise VakError("BadLicence", f"licence must be one of {LICENCES}")
    if field == "notes":
        m.setdefault("notes", []).append({"at": now(), "note": str(value)})
    else:
        m[field] = value
    if field in ("order", "anchors"):
        m["gates"].pop("align", None); m["gates"].pop("judge", None)
    save(pack_id, m)
    return {"pack": pack_id, "set": field}


def status_line(m):
    g = m.get("gates", {})
    parts = []
    for k in ("text", "align", "judge"):
        parts.append(f"{k}:{'pass' if g.get(k, {}).get('ok') else ('FAIL' if k in g else '—')}")
    parts.append("recording:" + ("yes" if m.get("recording") else "none"))
    parts.append(f"v{m.get('version', 0)}")
    return " · ".join(parts)


# ---------------------------------------------------------------- text
@tool
def text_import(pack_id, path=None, text=None):
    """Copy the prayer text into text.md (from a file path or pasted text), then run the text gate."""
    if not (path or text):
        raise VakError("NoText", "Give a file path or the text itself.")
    raw = open(os.path.expanduser(path), encoding="utf-8").read() if path else text
    load(pack_id)
    open(inside(pdir(pack_id, "text.md"), PACKS), "w", encoding="utf-8").write(raw)
    return text_check(pack_id)


@tool
def text_check(pack_id):
    m = load(pack_id)
    raw = open(pdir(pack_id, "text.md"), encoding="utf-8").read()
    secs = textfmt.parse(raw)
    res = textfmt.check(secs)
    json.dump(secs, open(inside(pdir(pack_id, "text.json"), PACKS), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    m["gates"]["text"] = {"ok": res["ok"], "at": now(), "problems": len(res["problems"]), "stats": res["stats"],
                          "hash": file_hash(pdir(pack_id, "text.md"))}
    m["gates"].pop("align", None); m["gates"].pop("judge", None)
    save(pack_id, m)
    return {"pack": pack_id, "gates": {"text": res}, "preview": textfmt.lines(secs)[:5]}


def _lines(pack_id):
    p = pdir(pack_id, "text.json")
    if not os.path.exists(p):
        raise VakError("TextMissing", "Run text_check first.")
    secs = json.load(open(p, encoding="utf-8"))
    return secs, textfmt.lines(secs)


# ---------------------------------------------------------------- audio
@tool
def audio_import(pack_id, path, label="Built-in recording", title="", licence=None):
    """Copy a recording into the pack (stays on this computer) and make the 16 kHz working copy."""
    from . import audio
    m = load(pack_id)
    src = os.path.expanduser(path)
    if not os.path.exists(src):
        raise VakError("AudioLoadFailed", f"File not found: {path}")
    ext = os.path.splitext(src)[1].lower() or ".mp3"
    dst = inside(pdir(pack_id, "audio", "original" + ext), PACKS)
    if os.path.realpath(src) != os.path.realpath(dst):
        shutil.copyfile(src, dst)
    info = audio.prepare(dst, pdir(pack_id, "audio", "audio16.wav"))
    old = (m.get("recording") or {}).get("sha256")
    m["recording"] = {"file": os.path.basename(dst), "original_name": os.path.basename(src), "label": label,
                      "title": title or label, "bytes": info["bytes"], "duration": info["duration"],
                      "sha256": info["sha256"], "mime": mimetypes.guess_type(dst)[0] or "audio/mpeg"}
    if licence:
        if licence not in LICENCES:
            raise VakError("BadLicence", f"licence must be one of {LICENCES}")
        m["licence"] = licence
    if old != info["sha256"]:
        for f in ("emissions.npy",):
            p = pdir(pack_id, "work", f)
            if os.path.exists(p):
                os.remove(p)
        m["gates"].pop("align", None); m["gates"].pop("judge", None)
    save(pack_id, m)
    return {"pack": pack_id, "recording": m["recording"], "licence": m["licence"]}


@tool
def audio_align(pack_id, band1=None, band2=12.0):
    """Word-time the text to the recording. First run computes acoustics (minutes); later runs take seconds."""
    m = load(pack_id)
    if not m.get("recording"):
        raise VakError("NoRecording", "Import a recording first (audio_import).")
    secs, L = _lines(pack_id)
    if not m["gates"].get("text", {}).get("ok"):
        raise VakError("TextGateFailed", "Fix the text first: text_check reports problems.")
    from . import align, audio
    order = parse_order(m.get("order"), len(L))
    E = audio.emissions(pdir(pack_id, "audio", "audio16.wav"), pdir(pack_id, "work", "emissions.npy"),
                        progress=lambda f, s: _say(f"acoustics {f:5.0%}  {s:4.0f}s"))
    res = align.align(L, E, audio.vocab(), order=order, anchors=m.get("anchors"), band1=band1, band2=band2)
    g = align.gate(res)
    json.dump(res, open(inside(pdir(pack_id, "work", "timing.json"), PACKS), "w"))
    m["gates"]["align"] = {**g, "at": now(), "lines": len(L) - len(res["notInRecording"]),
                           "not_in_recording": len(res["notInRecording"]), "region": res["region"]}
    m["gates"].pop("judge", None)
    save(pack_id, m)
    hint = None
    if not g["ok"]:
        hint = ("Many lines aligned poorly. Usual causes: the recording skips or repeats parts (set `order`), "
                "or has a long spoken intro (add 2–3 `anchors` {line: seconds}, e.g. from Tap-along in the Reader).")
    return {"pack": pack_id, "gates": {"align": g}, "hint": hint,
            "first_lines": [[i, res["times"][i]] for i in order[:5]]}


@tool
def audio_judge(pack_id, n=None, seed=None):
    """Independent listening check on a seeded random sample of lines (Whisper, local)."""
    from . import audio, judge
    m = load(pack_id)
    tp = pdir(pack_id, "work", "timing.json")
    if not os.path.exists(tp):
        raise VakError("NotAligned", "Run audio_align first.")
    cfg = m.get("judge") or {}
    n = int(n or cfg.get("n", 30)); seed = int(seed if seed is not None else cfg.get("seed", 1))
    _, L = _lines(pack_id)
    res = judge.run(audio.load_wav(pdir(pack_id, "audio", "audio16.wav")), L, json.load(open(tp)), n=n, seed=seed,
                    prompt=m.get("language_hint") or "",
                    log=lambda x: _say(f"line {x['line']:4d}  {'ok ' if x['ok'] else 'NO '} {x['score']:+.2f}  {x['heard']}"))
    g = judge.gate(res, cfg.get("bar", 0.65))
    json.dump(res, open(inside(pdir(pack_id, "work", "judge.json"), PACKS), "w"), ensure_ascii=False)
    m["gates"]["judge"] = {**g, "at": now(), "passed": res["passed"], "total": res["total"], "seed": seed}
    save(pack_id, m)
    return {"pack": pack_id, "gates": {"judge": g}, "summary": f"{res['passed']}/{res['total']} lines heard at the right place"}


# ---------------------------------------------------------------- build / preview / publish
def _pack_json(pack_id, m):
    secs, L = _lines(pack_id)
    p = {"id": pack_id, "title": m["title"], "sub": m.get("sub", ""), "source": m.get("source", ""),
         "bite": m.get("bite"), "bite_end": m.get("bite_end"), "version": m.get("version", 0), "sections": secs}
    tp = pdir(pack_id, "work", "timing.json")
    r = m.get("recording")
    if r and os.path.exists(tp):
        t = json.load(open(tp))
        p["recording"] = {"label": r["label"], "title": r["title"], "src": "", "mime": r["mime"],
                          "key": f"{r['original_name']}|{r['bytes']}", "size": r["bytes"], "duration": r.get("duration"),
                          "times": t["times"], "words": t["words"], "reprise": t["reprise"],
                          "notInRecording": t["notInRecording"]}
        if m.get("legacy_key"):
            p["recording"]["key"] = m["legacy_key"]
    return p


@tool
def pack_build(pack_id):
    """Write pack.json and a text-only Reader file (safe to share: no recording inside)."""
    from . import htmlbuild
    m = load(pack_id)
    if not m["gates"].get("text", {}).get("ok"):
        raise VakError("TextGateFailed", "Text gate has not passed.")
    m["version"] = int(m.get("version", 0)) + 1
    p = _pack_json(pack_id, m)
    json.dump(p, open(inside(pdir(pack_id, "pack.json"), PACKS), "w", encoding="utf-8"), ensure_ascii=False)
    html, warns = htmlbuild.render([p])
    os.makedirs(DIST, exist_ok=True)
    out = inside(os.path.join(DIST, f"{pack_id}.html"), DIST)
    open(out, "w", encoding="utf-8").write(html)
    m["build"] = {"version": m["version"], "at": now(), "hash": file_hash(pdir(pack_id, "pack.json")),
                  "timed": "recording" in p}
    save(pack_id, m)
    return {"pack": pack_id, "version": m["version"], "file": out, "kb": len(html.encode()) // 1024,
            "timed": "recording" in p, "warnings": warns}


@tool
def pack_preview(pack_id, line=0, width=390, height=844):
    """Screenshot the built Reader at a given line (phone size by default). Returns the PNG path."""
    from playwright.sync_api import sync_playwright
    src = os.path.join(DIST, f"{pack_id}.html")
    if not os.path.exists(src):
        raise VakError("NotBuilt", "Run pack_build first.")
    png = inside(pdir(pack_id, "work", f"preview-{line}.png"), PACKS)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": int(width), "height": int(height)})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file://" + src)
        pg.wait_for_timeout(600)
        pg.evaluate("()=>{const w=document.getElementById('welcome'); if(w) w.hidden=true;}")
        pg.evaluate(f"()=>{{ if(typeof setCur==='function') setCur({int(line)},{{scroll:'instant'}}); }}")
        pg.wait_for_timeout(400)
        pg.screenshot(path=png)
        b.close()
    return {"pack": pack_id, "png": png, "page_errors": errs, "ok": not errs}


def gates_ok(m, need_audio):
    g = m.get("gates", {})
    need = ["text"] + (["align", "judge"] if need_audio else [])
    missing = [k for k in need if not g.get(k, {}).get("ok")]
    return missing


def approval_path(pack_id, m):
    return pdir(pack_id, "approvals", f"v{m['build']['version']}-{m['build']['hash']}.json")


@tool
def pack_publish(pack_id, with_recording=True):
    """Make the shareable offline file. Refused unless every gate passed AND a person approved this exact build.

    Approval cannot be given through this tool: a person runs `vak approve <pack>` in Terminal
    (or answers the macOS dialog this tool raises)."""
    from . import htmlbuild
    m = load(pack_id)
    if not m.get("build"):
        raise VakError("NotBuilt", "Run pack_build first.")
    has_rec = bool(m.get("recording")) and m["build"].get("timed")
    with_recording = bool(with_recording and has_rec)
    missing = gates_ok(m, has_rec)
    if missing:
        raise VakError("GateFailed", "Publish blocked; these checks have not passed: " + ", ".join(missing), missing=missing)
    ap = approval_path(pack_id, m)
    if not os.path.exists(ap):
        if not _dialog_approve(pack_id, m, ap):
            raise VakError("ApprovalRequired", f"A person must approve build v{m['build']['version']}: "
                           f"run `vak approve {pack_id}` in Terminal, then publish again.", approval_file=ap)
    p = json.load(open(pdir(pack_id, "pack.json"), encoding="utf-8"))
    audio = None
    if with_recording:
        r = m["recording"]
        audio = {pack_id: (open(pdir(pack_id, "audio", r["file"]), "rb").read(), r["mime"])}
    html, warns = htmlbuild.render([p], audio=audio)
    sub = "share-by-hand" if with_recording and m["licence"] != "public" else ""
    os.makedirs(os.path.join(DIST, sub), exist_ok=True)
    name = f"{pack_id}-v{m['build']['version']}" + ("-with-recording" if with_recording else "") + ".html"
    out = inside(os.path.join(DIST, sub, name), DIST)
    open(out, "w", encoding="utf-8").write(html)
    m["published"] = {"at": now(), "file": out, "with_recording": with_recording, "version": m["build"]["version"]}
    save(pack_id, m)
    note = None
    if with_recording and m["licence"] != "public":
        note = (f"Licence is '{m['licence']}': this file contains the recording. Share it by hand with family only; "
                "never upload it to a public site.")
    return {"pack": pack_id, "file": out, "mb": round(len(html.encode()) / 1e6, 1), "note": note, "warnings": warns}


def _dialog_approve(pack_id, m, ap):
    """macOS only, and only when VAK_DIALOG=1: a native dialog raised by this process. A model cannot click it."""
    if sys.platform != "darwin" or os.environ.get("VAK_DIALOG") != "1":
        return False
    import subprocess
    g = m["gates"]
    msg = (f"Publish {m['title']} v{m['build']['version']}?\\n\\nText: {g['text']['stats']['lines']} lines"
           + (f"\\nAlignment median confidence {g['align']['median_conf']}" if 'align' in g else "")
           + (f"\\nListening check {g['judge']['passed']}/{g['judge']['total']}" if 'judge' in g else ""))
    r = subprocess.run(["osascript", "-e", f'display dialog "{msg}" buttons {{"Cancel","Approve"}} default button "Cancel" with title "Vāk Studio"'],
                       capture_output=True, text=True)
    if "Approve" in r.stdout:
        write_approval(pack_id, m, ap, "macOS dialog")
        return True
    return False


def write_approval(pack_id, m, ap, how):
    json.dump({"pack": pack_id, "version": m["build"]["version"], "hash": m["build"]["hash"], "at": now(),
               "how": how, "gates": {k: v.get("ok") for k, v in m["gates"].items()}},
              open(inside(ap, PACKS), "w"), indent=1)


TEXT_TEMPLATE = """<!--
Write the prayer here. Format:
  # Section title          starts a new section
  one chanted line         one line per row; words separated by spaces
  (blank line)             starts a new verse
  > instruction            shown in italics, never chanted (e.g. > sip water three times)
Then run:  vak text-check <pack>
-->
"""

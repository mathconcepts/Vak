"""Text format for a prayer pack (packs/<id>/text.md) and the text gate.

    # Section title            → new section (shown as a heading)
    one chanted line           → a line; words are separated by spaces
    (blank line)               → verse break
    > instruction              → shown in italics, never chanted, never aligned
    <!-- comment -->           → ignored

The parsed form is the Reader's own shape:
    [{"title": str, "verses": [[line, ...] | {"note": str}, ...]}, ...]
Chanted line numbers (0, 1, 2, …) count only real lines, in reading order, exactly as the Reader does.
"""
import re, unicodedata

COMMENT = re.compile(r"<!--.*?-->", re.S)


def parse(raw: str):
    raw = COMMENT.sub("", raw.replace("\r", ""))
    sections, sec, verse = [], None, []

    def cur():
        nonlocal sec
        if sec is None:
            sec = {"title": "", "verses": []}
            sections.append(sec)
        return sec

    def flush():
        nonlocal verse
        if verse:
            cur()["verses"].append(verse)
            verse = []

    for l in raw.split("\n"):
        line = unicodedata.normalize("NFC", l.strip())
        if not line:
            flush(); continue
        if line.startswith("#"):
            flush(); sec = {"title": line.lstrip("#").strip(), "verses": []}; sections.append(sec); continue
        if line.startswith(">"):
            flush(); cur()["verses"].append({"note": line[1:].strip()}); continue
        verse.append(re.sub(r"\s+", " ", line))
    flush()
    return [s for s in sections if s["verses"]]


def to_markdown(sections):
    out = []
    for s in sections:
        if s.get("title"):
            out += ["# " + s["title"], ""]
        for v in s["verses"]:
            out += (["> " + v["note"]] if isinstance(v, dict) else list(v)) + [""]
    return "\n".join(out).rstrip() + "\n"


def lines(sections):
    """Chanted lines in reading order (the Reader's line numbering)."""
    return [l for s in sections for v in s["verses"] if isinstance(v, list) for l in v]


DEVA = re.compile(r"[ऀ-ॿ]")
LATIN = re.compile(r"[A-Za-z]")
NUM = re.compile(r"[॥|]\s*([०-९0-9]+)\s*[॥|]")
DEV_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def check(sections, expect_numbering=None):
    """The text gate. Returns {"ok": bool, "problems": [...], "stats": {...}}.

    Problems that block: no chanted lines, Latin letters inside a chanted line (likely a stray
    transliteration or OCR slip), lines with no Devanagari, verse numbers that jump or repeat.
    """
    probs, L = [], lines(sections)
    if not L:
        probs.append({"kind": "empty", "msg": "No chanted lines found. Write one line per row; blank lines separate verses."})
    for i, l in enumerate(L):
        if LATIN.search(l):
            probs.append({"kind": "latin", "line": i, "msg": f"Line {i} has Latin letters: {l[:60]}"})
        if not DEVA.search(l):
            probs.append({"kind": "no_devanagari", "line": i, "msg": f"Line {i} has no Devanagari: {l[:60]}"})
    nums = []
    for i, l in enumerate(L):
        for m in NUM.finditer(l):
            nums.append((i, int(m.group(1).translate(DEV_DIGITS))))
    if expect_numbering is not False and len(nums) >= 3:
        for (i0, a), (i1, b) in zip(nums, nums[1:]):
            if b != a + 1 and not (b == 1):        # numbering may restart at 1 in a new section
                probs.append({"kind": "numbering", "line": i1, "msg": f"Verse number jumps from {a} to {b} at line {i1}"})
    stats = {"sections": len(sections), "lines": len(L),
             "notes": sum(1 for s in sections for v in s["verses"] if isinstance(v, dict)),
             "numbered_verses": len(nums)}
    return {"ok": not probs, "problems": probs, "stats": stats}

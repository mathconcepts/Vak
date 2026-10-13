"""Fast tests (no models): text format, gates, guardrails, approval, MCP tool surface.
Run: pytest -q tests/test_core.py
"""
import json, os, shutil, subprocess, sys, tempfile

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture()
def ws(monkeypatch):
    d = tempfile.mkdtemp()
    monkeypatch.setenv("VAK_HOME", d)
    for m in [k for k in list(sys.modules) if k.startswith("vakstudio")]:
        del sys.modules[m]
    sys.path.insert(0, HERE)
    import vakstudio.api as api
    yield api, d
    shutil.rmtree(d, ignore_errors=True)


SAMPLE = """<!-- test -->
# आचमनम्
> Sip water three times.
ॐ अच्युताय नमः
ॐ अनन्ताय नमः

ॐ गोविन्दाय नमः ॥ १॥

# प्राणायामः
ॐ भूः ॐ भुवः ॥ २॥
ॐ सुवः ॐ महः ॥ ३॥
"""


def test_parse_lines_notes_and_roundtrip():
    sys.path.insert(0, HERE)
    from vakstudio import textfmt
    secs = textfmt.parse(SAMPLE)
    assert [s["title"] for s in secs] == ["आचमनम्", "प्राणायामः"]
    assert secs[0]["verses"][0] == {"note": "Sip water three times."}
    assert textfmt.lines(secs) == ["ॐ अच्युताय नमः", "ॐ अनन्ताय नमः", "ॐ गोविन्दाय नमः ॥ १॥", "ॐ भूः ॐ भुवः ॥ २॥", "ॐ सुवः ॐ महः ॥ ३॥"]
    assert textfmt.parse(textfmt.to_markdown(secs)) == secs
    assert textfmt.check(secs)["ok"]


def test_text_gate_catches_problems():
    from vakstudio import textfmt
    bad = textfmt.parse("ॐ भूः ॥ १॥\nom bhuh\nॐ सुवः ॥ २॥\nॐ महः ॥ ५॥\n")
    kinds = {p["kind"] for p in textfmt.check(bad)["problems"]}
    assert {"latin", "no_devanagari", "numbering"} <= kinds
    assert not textfmt.check([])["ok"]


def test_order_spec():
    from vakstudio.workspace import parse_order, VakError
    assert parse_order("0-2,5,1-2", 10) == [0, 1, 2, 5, 1, 2]
    assert parse_order(None, 3) == [0, 1, 2]
    with pytest.raises(VakError):
        parse_order("0-20", 5)


def test_pack_flow_gates_and_approval(ws):
    api, d = ws
    assert api.pack_new("demo-pack", "सन्ध्यावन्दनम्")["ok"]
    assert api.pack_new("demo-pack", "x")["error"] == "PackExists"
    assert api.pack_new("Bad Id", "x")["error"] == "BadPackId"
    r = api.text_import("demo-pack", text=SAMPLE)
    assert r["gates"]["text"]["ok"]
    assert api.audio_align("demo-pack")["error"] == "NoRecording"
    b = api.pack_build("demo-pack")
    assert b["ok"] and not b["timed"] and os.path.exists(b["file"])
    html = open(b["file"], encoding="utf-8").read()
    assert "Sip water three times." in html and "__PACKS__" not in html
    # publish refused until a person approves
    p = api.pack_publish("demo-pack")
    assert p["error"] == "ApprovalRequired"
    from vakstudio.workspace import load
    m = load("demo-pack")
    api.write_approval("demo-pack", m, api.approval_path("demo-pack", m), "test")
    p = api.pack_publish("demo-pack")
    assert p["ok"] and os.path.exists(p["file"]) and not p.get("note")
    # a new build needs a new approval
    api.pack_build("demo-pack")
    assert api.pack_publish("demo-pack")["error"] == "ApprovalRequired"
    # every call is logged
    runs = os.listdir(os.path.join(d, "runs"))
    assert runs and sum(1 for _ in open(os.path.join(d, "runs", runs[0]))) >= 8


def test_text_change_resets_gates(ws):
    api, _ = ws
    api.pack_new("p2", "t")
    api.text_import("p2", text=SAMPLE)
    from vakstudio.workspace import load, save
    m = load("p2"); m["gates"]["align"] = {"ok": True}; save("p2", m)
    api.text_import("p2", text=SAMPLE + "\nॐ जनः ॥ ४॥\n")
    assert "align" not in load("p2")["gates"]


def test_guardrails(ws):
    api, d = ws
    api.pack_new("p3", "t")
    assert api.pack_set("p3", "gates", "{}")["error"] == "FieldNotEditable"
    assert api.pack_set("p3", "licence", "everyone")["error"] == "BadLicence"
    from vakstudio.workspace import inside, VakError
    with pytest.raises(VakError):
        inside("/etc/passwd", os.path.join(d, "packs"))


def test_publish_blocked_when_gates_missing(ws):
    api, _ = ws
    api.pack_new("p4", "t")
    api.text_import("p4", text=SAMPLE)
    api.pack_build("p4")
    from vakstudio.workspace import load, save
    m = load("p4"); m["recording"] = {"x": 1}; m["build"]["timed"] = True; save("p4", m)
    r = api.pack_publish("p4")
    assert r["error"] == "GateFailed" and set(r["missing"]) == {"align", "judge"}


def test_mcp_server_lists_tools_and_has_no_approve():
    code = r"""
import asyncio, json, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    p = StdioServerParameters(command=sys.executable, args=["-m", "vakstudio.mcp_server"], cwd=%r)
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            t = await s.list_tools()
            print(json.dumps(sorted(x.name for x in t.tools)))
asyncio.run(main())
""" % HERE
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=HERE, timeout=120)
    assert out.returncode == 0, out.stderr[-800:]
    names = json.loads(out.stdout.strip().splitlines()[-1])
    assert {"pack_new", "text_import", "audio_align", "audio_judge", "pack_build", "pack_publish"} <= set(names)
    assert not any("approve" in n for n in names)


def test_built_file_parses_on_old_ipads(ws):
    """Safari 11 (iOS 11) understands ES2017. The build must not emit newer syntax."""
    node = shutil.which("node")
    acorn = os.path.join(HERE, "reader", "node_modules", "acorn")
    if not node or not os.path.isdir(acorn) or not os.path.isdir(os.path.join(HERE, "reader", "node_modules", "esbuild")):
        pytest.skip("node/esbuild/acorn not installed")
    api, d = ws
    api.pack_new("p5", "t"); api.text_import("p5", text=SAMPLE)
    html = open(api.pack_build("p5")["file"], encoding="utf-8").read()
    import re
    js = re.findall(r"<script>(.*?)</script>", html, re.S)[-1]
    f = os.path.join(d, "app.js"); open(f, "w").write(js)
    code = "const a=require(%r);a.parse(require('fs').readFileSync(%r,'utf8'),{ecmaVersion:2017,sourceType:'script'});console.log('ok')" % (acorn, f)
    out = subprocess.run([node, "-e", code], capture_output=True, text=True)
    assert out.stdout.strip() == "ok", out.stderr[-400:]


def test_site_build_is_installable_and_offline_ready(ws, tmp_path):
    api, d = ws
    api.pack_new("p6", "t"); api.text_import("p6", text=SAMPLE); api.pack_build("p6")
    from vakstudio import site
    p = json.load(open(os.path.join(d, "packs", "p6", "pack.json"), encoding="utf-8"))
    out = tmp_path / "site"
    r = site.build([p], str(out))
    names = set(os.listdir(out))
    assert {"index.html", "sw.js", "manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png", ".nojekyll"} <= names
    html = (out / "index.html").read_text(encoding="utf-8")
    assert 'rel="manifest"' in html and 'serviceWorker' in html and r["audio"] == []

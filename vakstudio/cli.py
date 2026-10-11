"""`vak` command line. Same operations as the MCP tools, plus `approve`, which only a person can run.

  vak list
  vak new <id> "<title>" [--sub ..] [--licence private|family|public]
  vak text <id> <file.md>          import + check text
  vak text-check <id>
  vak audio <id> <file> [--label ..] [--licence ..]
  vak set <id> <field> <value>     e.g. vak set lalita order "0-3,9-12,25-389,9-12"
  vak align <id>
  vak judge <id> [--n 30] [--seed 1]
  vak build <id>
  vak preview <id> [--line 0]
  vak approve <id>                 shows the checks and asks y/N (person only)
  vak publish <id> [--text-only]
  vak status <id>
  vak run <id>                     check → align → judge → build, stopping at the first failed gate
"""
import argparse, json, os, sys

from . import api
from .workspace import load


def show(r):
    print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
    return 0 if r.get("ok", True) else 1


def approve(pid):
    m = load(pid)
    if not m.get("build"):
        print("Nothing built yet. Run: vak build", pid); return 1
    missing = api.gates_ok(m, bool(m.get("recording")) and m["build"].get("timed"))
    g = m["gates"]
    print(f"\n  {m['title']}  ·  build v{m['build']['version']}  ·  licence: {m['licence']}")
    for k in ("text", "align", "judge"):
        if k in g:
            extra = {"text": lambda x: f"{x['stats']['lines']} lines, {x['problems']} problems",
                     "align": lambda x: f"median confidence {x['median_conf']}, low lines {x['low_frac']:.0%}",
                     "judge": lambda x: f"{x['passed']}/{x['total']} heard at the right place (bar {x['bar']:.0%})"}[k](g[k])
            print(f"  {'PASS' if g[k].get('ok') else 'FAIL'}  {k:6s} {extra}")
    if missing:
        print("\n  Cannot approve: these checks have not passed:", ", ".join(missing)); return 1
    if not sys.stdin.isatty():
        print("\n  Approval must be typed by a person in a terminal."); return 1
    if input("\n  Approve this build for sharing? [y/N] ").strip().lower() != "y":
        print("  Not approved."); return 1
    ap = api.approval_path(pid, m)
    api.write_approval(pid, m, ap, "terminal")
    print("  Approved. Now: vak publish", pid); return 0


def run_all(pid):
    for step, fn in (("text", api.text_check), ("align", api.audio_align), ("judge", api.audio_judge), ("build", api.pack_build)):
        m = load(pid)
        if step in ("align", "judge") and not m.get("recording"):
            continue
        print(f"--- {step}", file=sys.stderr)
        r = fn(pid)
        if not r.get("ok", True) or any(not g.get("ok") for g in r.get("gates", {}).values()):
            return show(r) or 1
    return show(api.pack_status(pid))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="vak", description="Vāk Studio: make word-timed prayer packs")
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("list")
    p = sp.add_parser("new"); p.add_argument("id"); p.add_argument("title"); p.add_argument("--sub", default=""); p.add_argument("--source", default=""); p.add_argument("--licence", default="private")
    p = sp.add_parser("text"); p.add_argument("id"); p.add_argument("file")
    p = sp.add_parser("text-check"); p.add_argument("id")
    p = sp.add_parser("audio"); p.add_argument("id"); p.add_argument("file"); p.add_argument("--label", default="Built-in recording"); p.add_argument("--title", default=""); p.add_argument("--licence")
    p = sp.add_parser("set"); p.add_argument("id"); p.add_argument("field"); p.add_argument("value")
    p = sp.add_parser("align"); p.add_argument("id")
    p = sp.add_parser("judge"); p.add_argument("id"); p.add_argument("--n", type=int); p.add_argument("--seed", type=int)
    p = sp.add_parser("build"); p.add_argument("id")
    p = sp.add_parser("preview"); p.add_argument("id"); p.add_argument("--line", type=int, default=0)
    p = sp.add_parser("approve"); p.add_argument("id")
    p = sp.add_parser("publish"); p.add_argument("id"); p.add_argument("--text-only", action="store_true")
    p = sp.add_parser("status"); p.add_argument("id")
    p = sp.add_parser("run"); p.add_argument("id")
    a = ap.parse_args(argv)
    c = a.cmd
    if c == "list": return show(api.pack_list())
    if c == "new": return show(api.pack_new(a.id, a.title, a.sub, a.source, a.licence))
    if c == "text": return show(api.text_import(a.id, path=a.file))
    if c == "text-check": return show(api.text_check(a.id))
    if c == "audio": return show(api.audio_import(a.id, a.file, a.label, a.title, a.licence))
    if c == "set":
        v = a.value
        try: v = json.loads(v) if a.field in ("anchors", "judge") else v
        except ValueError: pass
        return show(api.pack_set(a.id, a.field, v))
    if c == "align": return show(api.audio_align(a.id))
    if c == "judge": return show(api.audio_judge(a.id, a.n, a.seed))
    if c == "build": return show(api.pack_build(a.id))
    if c == "preview": return show(api.pack_preview(a.id, a.line))
    if c == "approve": return approve(a.id)
    if c == "publish": return show(api.pack_publish(a.id, with_recording=not a.text_only))
    if c == "status": return show(api.pack_status(a.id))
    if c == "run": return run_all(a.id)


if __name__ == "__main__":
    sys.exit(main())

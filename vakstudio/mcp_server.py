"""Vāk Studio as an MCP server (stdio). Any MCP host can drive it: Claude Desktop, Goose, OpenCode, Cursor …

The model only orchestrates. Every tool is deterministic local code; gates decide, not the model.
There is deliberately NO approve tool: publishing needs a person (`vak approve`, or the macOS dialog).
"""
import json

from . import api

try:                                    # mcp >= 2
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:                     # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

INSTRUCTIONS = """Vāk Studio turns a prayer text plus a recording into a word-timed Reader file.
Workflow: pack_list → pack_new → text_import (or the person edits packs/<id>/text.md) → text_check →
audio_import → audio_align → audio_judge → pack_build → pack_preview → pack_publish.
Rules: never invent or 'correct' sacred text yourself; report text_check problems to the person.
If alignment is weak, ask the person which parts the recording skips or repeats and record it with
pack_set(order) and pack_set(notes), or ask for 2–3 anchors (line: seconds). Recordings marked
private/family are never uploaded anywhere. Publishing requires the person's approval outside this chat."""

mcp = _Server("vak-studio", instructions=INSTRUCTIONS)


def _j(r):
    return json.dumps(r, ensure_ascii=False, default=str)


@mcp.tool()
def pack_list() -> str:
    """List prayer packs and their check status."""
    return _j(api.pack_list())


@mcp.tool()
def pack_new(pack_id: str, title: str, sub: str = "", source: str = "", licence: str = "private") -> str:
    """Create a new pack. pack_id: lowercase-with-dashes. licence: private | family | public (public only with written permission)."""
    return _j(api.pack_new(pack_id, title, sub, source, licence))


@mcp.tool()
def pack_status(pack_id: str) -> str:
    """Full manifest: decisions, notes, gate results, build and publish state."""
    return _j(api.pack_status(pack_id))


@mcp.tool()
def pack_set(pack_id: str, field: str, value: str) -> str:
    """Record a decision. Fields: title, sub, source, bite, bite_end, licence, language_hint, notes (appends),
    order (e.g. "0-3,9-12,25-389,9-12": chanted line numbers in the order heard; repeats allowed),
    anchors (JSON {"line": seconds}), judge (JSON {"n":30,"seed":1,"bar":0.65})."""
    return _j(api.pack_set(pack_id, field, value))


@mcp.tool()
def text_import(pack_id: str, path: str = "", text: str = "") -> str:
    """Save the prayer text (from a file path on this computer, or pasted text) and run the text check.
    Format: '# Section', one chanted line per row, blank line between verses, '> instruction' for non-chanted notes."""
    return _j(api.text_import(pack_id, path=path or None, text=text or None))


@mcp.tool()
def text_check(pack_id: str) -> str:
    """Re-check packs/<id>/text.md after the person edits it."""
    return _j(api.text_check(pack_id))


@mcp.tool()
def audio_import(pack_id: str, path: str, label: str = "Built-in recording", title: str = "", licence: str = "") -> str:
    """Copy a recording (mp3/m4a/wav…) into the pack. It stays on this computer."""
    return _j(api.audio_import(pack_id, path, label, title, licence or None))


@mcp.tool()
def audio_align(pack_id: str) -> str:
    """Word-time the text to the recording. First run takes minutes (acoustics), later runs seconds."""
    return _j(api.audio_align(pack_id))


@mcp.tool()
def audio_judge(pack_id: str, n: int = 0, seed: int = -1) -> str:
    """Independent listening check on a seeded random sample of lines. Blocks publish if below the bar."""
    return _j(api.audio_judge(pack_id, n or None, None if seed < 0 else seed))


@mcp.tool()
def pack_build(pack_id: str) -> str:
    """Write pack.json and dist/<id>.html (text + timings, no recording inside)."""
    return _j(api.pack_build(pack_id))


@mcp.tool()
def pack_preview(pack_id: str, line: int = 0) -> str:
    """Phone-size screenshot of the built Reader at a line. Returns the PNG path and any page errors."""
    return _j(api.pack_preview(pack_id, line))


@mcp.tool()
def pack_publish(pack_id: str, with_recording: bool = True) -> str:
    """Make the shareable offline file. Refused unless all checks passed and a person approved this build."""
    return _j(api.pack_publish(pack_id, with_recording))


def main():
    mcp.run()


if __name__ == "__main__":
    main()

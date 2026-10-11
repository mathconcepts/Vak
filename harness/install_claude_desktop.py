"""Register Vāk Studio with Claude Desktop (macOS/Windows). Backs up the config first. Re-runnable."""
import json, os, shutil, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, ".venv", "bin", "python") if os.name != "nt" else os.path.join(ROOT, ".venv", "Scripts", "python.exe")
if sys.platform == "darwin":
    cfg = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
elif os.name == "nt":
    cfg = os.path.join(os.environ["APPDATA"], "Claude", "claude_desktop_config.json")
else:
    cfg = os.path.expanduser("~/.config/Claude/claude_desktop_config.json")
os.makedirs(os.path.dirname(cfg), exist_ok=True)
data = {}
if os.path.exists(cfg):
    shutil.copyfile(cfg, cfg + f".bak-{time.strftime('%Y%m%d-%H%M%S')}")
    data = json.load(open(cfg))
data.setdefault("mcpServers", {})["vak-studio"] = {
    "command": PY, "args": ["-m", "vakstudio.mcp_server"],
    "env": {"VAK_HOME": ROOT, "VAK_DIALOG": "1", "PYTHONPATH": ROOT}}
json.dump(data, open(cfg, "w"), indent=2)
print("Added 'vak-studio' to", cfg, "\nQuit and reopen Claude Desktop to load it.")

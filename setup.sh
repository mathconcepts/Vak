#!/usr/bin/env bash
# Vāk Studio one-time setup (macOS / Linux). Safe to re-run.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PYTHON:-}
for c in python3.12 python3.11 python3.13 python3.10 python3; do
  if [ -z "$PY" ] && command -v $c >/dev/null && $c -c 'import sys;sys.exit(0 if sys.version_info>=(3,10) else 1)'; then PY=$c; fi
done
[ -n "$PY" ] || { echo "Need Python 3.10+ (brew install python@3.12)"; exit 1; }
echo "Using $($PY --version)"
[ -d .venv ] || $PY -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -e ".[test]"
.venv/bin/python -m playwright install chromium
if command -v npm >/dev/null; then (cd reader && npm install --silent); else echo "npm not found: files will build without old-iPad conversion (brew install node)"; fi
echo "Downloading the aligner (≈1.2 GB) and the listening model (≈0.5 GB) once…"
.venv/bin/python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download("MahmoudAshraf/mms-300m-1130-forced-aligner")
from faster_whisper import WhisperModel; WhisperModel("small", device="cpu", compute_type="int8")
PY
if [ -f packs/lalita/audio/original.mp3 ] && [ ! -f packs/lalita/audio/audio16.wav ]; then
  .venv/bin/python -c "from vakstudio import audio; audio.prepare('packs/lalita/audio/original.mp3','packs/lalita/audio/audio16.wav')"
fi
.venv/bin/python -m pytest -q tests/
mkdir -p bin && cat > bin/vak <<SH
#!/usr/bin/env bash
VAK_HOME="$(pwd)" exec "$(pwd)/.venv/bin/python" -m vakstudio.cli "\$@"
SH
chmod +x bin/vak
echo
echo "Done. Try:   ./bin/vak list"
echo "Claude Desktop:   .venv/bin/python harness/install_claude_desktop.py"

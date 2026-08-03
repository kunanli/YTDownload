#!/usr/bin/env bash
# Thin launcher for macOS/Linux. All menu text lives in ytmusic/menu.py.
cd "$(dirname "$0")" || exit 1

PY=python3
command -v "$PY" >/dev/null 2>&1 || PY=python
if ! command -v "$PY" >/dev/null 2>&1; then
  echo
  echo "  [ERROR] Python not found. Install it first:  brew install python"
  echo
  read -r -p "  Press Enter to close…" _
  exit 3
fi

# Everything else (ffmpeg, mutagen, curl_cffi) is checked inside the menu,
# which can print proper Chinese and ask before installing. Only the package
# itself has to be handled here: without it there is no menu to run.
if ! "$PY" -c "import ytmusic" >/dev/null 2>&1; then
  echo
  echo "  [SETUP] First run - installing ytmusic and its dependencies..."
  echo
  if ! "$PY" -m pip install -e .; then
    echo
    echo "  [ERROR] Install failed. Try running this by hand:"
    echo "      python3 -m pip install -e ."
    echo
    read -r -p "  Press Enter to close…" _
    exit 3
  fi
fi

"$PY" -m ytmusic menu

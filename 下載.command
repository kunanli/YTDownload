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

"$PY" -m ytmusic menu

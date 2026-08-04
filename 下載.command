#!/usr/bin/env bash
# Thin launcher for macOS/Linux. All menu text lives in ytmusic/menu.py.
#
# Everything here is first-run setup. Once Python and the package are in
# place this file just starts the menu and gets out of the way.
cd "$(dirname "$0")" || exit 1

pause() { read -r -p "  Press Enter to close… " _; }

# Find a Python that actually RUNS and is new enough. Checking that the name
# exists is not enough: macOS used to ship a stub /usr/bin/python that only
# tells you to install the developer tools.
PY=""
for candidate in python3 python; do
  if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,9) else 1)' \
      >/dev/null 2>&1; then
    PY="$candidate"
    break
  fi
done

if [ -z "$PY" ]; then
  echo
  echo "  ================================================"
  echo "     Setup - step 1 of 2:  install Python"
  echo "  ================================================"
  echo
  if command -v brew >/dev/null 2>&1; then
    echo "  I can install it for you now with Homebrew."
    echo
    read -r -p "  Install Python now? [Y/n] " answer
    case "$answer" in
      [Nn]*) ;;
      *)
        brew install python && {
          echo
          echo "  ================================================"
          echo "     Setup - step 2 of 2:  reopen this window"
          echo "  ================================================"
          echo
          echo "  Close this window and double-click the same file again."
          echo
          pause
          exit 0
        }
        ;;
    esac
  fi
  echo
  echo "  Install Python by hand:"
  echo
  echo "    1. Install Homebrew (one line, from https://brew.sh):"
  echo '       /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  echo "    2. Then run:  brew install python ffmpeg"
  echo "    3. Close this window and double-click the same file again."
  echo
  echo "  No Homebrew? Download it from https://www.python.org/downloads/"
  echo
  pause
  exit 3
fi

# Make sure the package itself is installed.
if ! "$PY" -c "import ytmusic" >/dev/null 2>&1; then
  echo
  echo "  [SETUP] First run - installing the downloader and its dependencies..."
  echo "  This takes a minute. You only have to do it once."
  echo
  if ! "$PY" -m pip install -e .; then
    echo
    echo "  [ERROR] Install failed. Try these by hand:"
    echo "      $PY -m ensurepip --upgrade"
    echo "      $PY -m pip install -e ."
    echo
    pause
    exit 3
  fi
  echo
  echo "  [SETUP] Done."
  echo
fi

# Anything still missing (ffmpeg, mutagen, curl_cffi) is checked inside the
# menu, in the user's own language.
"$PY" -m ytmusic menu

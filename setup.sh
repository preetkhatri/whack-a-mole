#!/usr/bin/env bash
# One-command bootstrap: create .venv and install dependencies.
set -euo pipefail

cd "$(dirname "$0")"

MIN_MINOR=11
MAX_MINOR=13
PREFERRED=(python3.12 python3.11 python3.13 python3)

pick_python() {
  local candidate version major minor
  for candidate in "${PREFERRED[@]}"; do
    if ! command -v "$candidate" >/dev/null 2>&1; then
      continue
    fi
    version="$("$candidate" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
    major="${version%%.*}"
    minor="${version#*.}"
    if [[ "$major" -eq 3 && "$minor" -ge "$MIN_MINOR" && "$minor" -le "$MAX_MINOR" ]]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

if ! PYTHON_BIN="$(pick_python)"; then
  cat <<EOF
ERROR: Need Python 3.11–3.13 on PATH (3.12 recommended for mediapipe wheels).

Install examples:
  macOS (Homebrew):  brew install python@3.12
  pyenv:             pyenv install 3.12 && pyenv local 3.12
  Windows:           https://www.python.org/downloads/ (3.12.x)

Then re-run:  ./setup.sh
EOF
  exit 1
fi

PY_VER="$("$PYTHON_BIN" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
echo "Using $PYTHON_BIN ($PY_VER)"

if [[ ! -d .venv ]]; then
  echo "Creating .venv ..."
  "$PYTHON_BIN" -m venv .venv
else
  echo "Reusing existing .venv"
fi

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

cat <<EOF

Setup complete. Dependencies live in .venv/ (not system Python).

Run the game:
  source .venv/bin/activate
  python main.py

Or without activating:
  .venv/bin/python main.py
EOF

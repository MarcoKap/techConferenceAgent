#!/bin/bash
set -euo pipefail

REPO_DIR="/home/pi/techConferenceAgent"
DISPLAY_VALUE="${DISPLAY:-:0}"
XAUTHORITY_VALUE="${XAUTHORITY:-/home/pi/.Xauthority}"

cd "$REPO_DIR"
exec pkexec env DISPLAY="$DISPLAY_VALUE" XAUTHORITY="$XAUTHORITY_VALUE" "$REPO_DIR/.venv/bin/python" "$REPO_DIR/main.py"
#!/bin/bash
# OSIRIS stack launcher — memory, voice, face, hands.
#
# Adapted from fullstack-agent's start.sh, copyright (C) 2026 Jared Rhodenizer.
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version. It is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License in ./LICENSE for more details.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Starts the pieces in order:
#   ai-visualizer  the face (opens in your browser)
#   barehands      the hands (URL printed; open it when you want the board)
#   backtalk       the voice (runs in this terminal; Ctrl-C stops EVERYTHING)
# Pieces that are not installed are skipped.
#
#   ./start.sh          everything installed
#   ./start.sh voice    the voice and the face (no hands)
#   ./start.sh hands    the voice and the hands board (no face)

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
HOME_DIR="$(dirname "$HERE")"
MODE="${1:-all}"
PIDS=()

cleanup() {
  trap - EXIT INT TERM
  for p in "${PIDS[@]:-}"; do kill "$p" 2>/dev/null; done
  echo
  echo "CARRIER LOST. OSIRIS stopped."
}
trap cleanup EXIT INT TERM

echo "OSIRIS.EXE // starting from $HOME_DIR"

if [ ! -f "$HOME_DIR/CLAUDE.md" ]; then
  echo "  warning: no CLAUDE.md in $HOME_DIR — OSIRIS has no identity to speak as."
  echo "           run the setup conductor first: claude \"read agent-stack/osiris-setup.md and set me up\""
fi

if [ -d "$HOME_DIR/ai-visualizer" ] && [ "$MODE" != "hands" ]; then
  (cd "$HOME_DIR/ai-visualizer" && exec python3 server.py) &
  PIDS+=($!)
  echo "  face:   starting (browser opens on the visualizer)"
fi

if [ -d "$HOME_DIR/barehands" ] && [ "$MODE" != "voice" ]; then
  (cd "$HOME_DIR/barehands" && exec python3 server.py) &
  PIDS+=($!)
  echo "  hands:  starting (open the printed URL in Chrome when you want the board)"
fi

if [ -d "$HOME_DIR/backtalk" ]; then
  echo "  voice:  starting (hold your talk key and speak; Ctrl-C here stops everything)"
  cd "$HOME_DIR/backtalk" && ./run.sh
else
  echo
  echo "No voice installed; servers are up. Ctrl-C stops everything."
  wait
fi

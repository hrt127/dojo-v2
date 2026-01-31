#!/usr/bin/env bash

set -e

DOJO_ROOT="$HOME/dojo"
DOJO_CLI_REPO="$HOME/dojo-cli"

echo "🔁 Restoring Dojo CLI..."

if [ ! -f "$DOJO_CLI_REPO/dojo" ]; then
  echo "No dojo script found in $DOJO_CLI_REPO"
  exit 1
fi

mkdir -p "$DOJO_ROOT"
cp "$DOJO_CLI_REPO/dojo" "$DOJO_ROOT/dojo"
chmod +x "$DOJO_ROOT/dojo"

if ! grep -q 'export PATH="$HOME/dojo:$PATH"' "$HOME/.bashrc"; then
  echo 'export PATH="$HOME/dojo:$PATH"' >> "$HOME/.bashrc"
  echo "Added Dojo to PATH in ~/.bashrc"
else
  echo "PATH already includes Dojo."
fi

echo "Done. Reload shell with:"
echo "  source ~/.bashrc"
echo ""
echo "Then test:"
echo "  dojo help"

#!/usr/bin/env bash
set -euo pipefail

BLOCK_START="# >>> termai integration >>>"
BLOCK_END="# <<< termai integration <<<"

remove_block() {
  local rc="$1"
  if [ -f "$rc" ]; then
    if grep -q "$BLOCK_START" "$rc"; then
      awk -v start="$BLOCK_START" -v end="$BLOCK_END" 'BEGIN{p=1} $0~start{p=0} p{print} $0~end{p=1}' "$rc" >"$rc.tmp" && mv "$rc.tmp" "$rc"
  echo "Removed TermAI integration from $rc."
    fi
  fi
}

remove_block "$HOME/.bashrc"
remove_block "$HOME/.zshrc"
remove_block "$HOME/.config/fish/config.fish"

echo "Done. Reopen your shell to apply changes."

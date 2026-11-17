#!/usr/bin/env bash
# Install the product-engineer skill into supported agent CLIs.
set -euo pipefail

SKILL_NAME="product-engineer"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=0
TARGETS=()

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

Options:
  --claude       Install for Claude Code      (~/.claude/skills)
  --opencode     Install for OpenCode         (~/.config/opencode/skills)
  --codex        Install for Codex            (~/.codex/skills)
  --antigravity  Install for Antigravity CLI  (~/.gemini/skills)
  --dry-run      Show what would happen, change nothing
  -h, --help     Show this help

Without agent flags, every target whose CLI or config directory exists is
installed. Detected CLIs: claude, opencode, codex, agy.
EOF
}

for arg in "$@"; do
  case "$arg" in
    --claude) TARGETS+=(claude) ;;
    --opencode) TARGETS+=(opencode) ;;
    --codex) TARGETS+=(codex) ;;
    --antigravity) TARGETS+=(antigravity) ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; usage; exit 1 ;;
  esac
done

if [ ${#TARGETS[@]} -eq 0 ]; then
  command -v claude   >/dev/null 2>&1 && TARGETS+=(claude)
  command -v opencode >/dev/null 2>&1 && TARGETS+=(opencode)
  command -v codex    >/dev/null 2>&1 && TARGETS+=(codex)
  { command -v agy >/dev/null 2>&1 || [ -d "$HOME/.gemini" ]; } && TARGETS+=(antigravity)
  if [ ${#TARGETS[@]} -eq 0 ]; then
    echo "No supported CLI detected. Pass a flag, e.g. --claude." >&2
    exit 1
  fi
fi

dest_for() {
  case "$1" in
    claude)      echo "$HOME/.claude/skills/$SKILL_NAME" ;;
    opencode)    echo "$HOME/.config/opencode/skills/$SKILL_NAME" ;;
    codex)       echo "$HOME/.codex/skills/$SKILL_NAME" ;;
    antigravity) echo "$HOME/.gemini/skills/$SKILL_NAME" ;;
  esac
}

copy_skill() {
  local dest="$1"
  mkdir -p "$dest"
  ( cd "$SRC" && tar --exclude=.git --exclude=__pycache__ -cf - . ) | ( cd "$dest" && tar -xf - )
}

register_antigravity() {
  local cfg="$HOME/.gemini/config/skills.json"
  command -v python3 >/dev/null 2>&1 || { echo "  ! python3 not found, add ~/.gemini/skills to $cfg manually"; return 0; }
  python3 - "$cfg" <<'PY'
import json, pathlib, sys

path = pathlib.Path(sys.argv[1]).expanduser()
path.parent.mkdir(parents=True, exist_ok=True)
data = json.loads(path.read_text()) if path.exists() else {}
entries = data.setdefault("entries", [])
if not any(e.get("path") == "~/.gemini/skills" for e in entries):
    entries.append({"path": "~/.gemini/skills", "include_only": ["product-engineer"]})
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"  registered in {path}")
else:
    print(f"  already registered in {path}")
PY
}

echo "Source: $SRC"
for target in "${TARGETS[@]}"; do
  dest="$(dest_for "$target")"
  if [ "$DRY_RUN" = 1 ]; then
    echo "would install $target -> $dest"
    continue
  fi
  copy_skill "$dest"
  echo "installed $target -> $dest"
  [ "$target" = "antigravity" ] && register_antigravity
done

[ "$DRY_RUN" = 1 ] && echo "Dry run: nothing changed."
echo "Done. Start a new agent session to load the skill."

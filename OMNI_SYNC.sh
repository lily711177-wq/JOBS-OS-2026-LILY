#!/usr/bin/env bash
# OMNI_SYNC.sh — Sync AGENTS.md master to all CLI AI tool config locations.
# Run this after editing AGENTS.md to propagate to every tool.
# Usage: bash OMNI_SYNC.sh

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
MASTER="$ROOT/AGENTS.md"

if [ ! -f "$MASTER" ]; then
    echo "ERROR: AGENTS.md not found at $MASTER"
    exit 1
fi

echo "OMNI SYNC: Propagating AGENTS.md to all tool configs..."

# ── Claude Code ──
cp "$MASTER" "$ROOT/CLAUDE.md"
echo "  ✓ CLAUDE.md"

# ── Cursor ──
cp "$MASTER" "$ROOT/.cursorrules"
echo "  ✓ .cursorrules"

# ── Windsurf ──
cp "$MASTER" "$ROOT/.windsurfrules"
echo "  ✓ .windsurfrules"

# ── GitHub Copilot CLI ──
mkdir -p "$ROOT/.github"
cp "$MASTER" "$ROOT/.github/copilot-instructions.md"
echo "  ✓ .github/copilot-instructions.md"

# ── opencode ──
cat > "$ROOT/opencode.json" << 'JSONEOF'
{
  "agents": {
    "AGENTS.md": {
      "description": "Master runtime instructions — OMNI-gnostic for all CLI AI tools"
    }
  }
}
JSONEOF
echo "  ✓ opencode.json"

# ── Cline / Roo Code / Continue ──
mkdir -p "$ROOT/.clinerules"
cp "$MASTER" "$ROOT/.clinerules/AGENTS.md"
echo "  ✓ .clinerules/AGENTS.md"

echo ""
echo "OMNI SYNC complete. Every tool sees the same AGENTS.md."
echo "Next time you edit AGENTS.md, run: bash OMNI_SYNC.sh"

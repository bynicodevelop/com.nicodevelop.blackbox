#!/bin/bash
# yolo-launcher.sh
# Helper script pour lancer claude en mode YOLO dans un worktree
# Usage: ./yolo-launcher.sh <worktree_path> <prompt> <log_file>

set -e

# Convertir tous les chemins en absolus AVANT de changer de repertoire
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

WORKTREE_PATH="$1"
PROMPT="$2"
LOG_FILE="$3"

if [ -z "$WORKTREE_PATH" ] || [ -z "$PROMPT" ] || [ -z "$LOG_FILE" ]; then
    echo "Usage: $0 <worktree_path> <prompt> <log_file>"
    exit 1
fi

# Convertir en chemins absolus
WORKTREE_PATH="$(cd "$REPO_DIR" && cd "$WORKTREE_PATH" && pwd)"
LOG_FILE="$(cd "$REPO_DIR" && mkdir -p "$(dirname "$LOG_FILE")" && cd "$(dirname "$LOG_FILE")" && pwd)/$(basename "$LOG_FILE")"

# Aller dans le worktree
cd "$WORKTREE_PATH" || exit 1

echo "=== YOLO Exploration Started ===" | tee "$LOG_FILE"
echo "Timestamp: $(date)" | tee -a "$LOG_FILE"
echo "Worktree: $WORKTREE_PATH" | tee -a "$LOG_FILE"
echo "Prompt: $PROMPT" | tee -a "$LOG_FILE"
echo "================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Lancer claude en mode YOLO
claude -p "$PROMPT" \
    --dangerously-skip-permissions \
    --max-turns 100 \
    --max-budget-usd 20.00 \
    2>&1 | tee -a "$LOG_FILE"

# Commit automatique a la fin
echo "" | tee -a "$LOG_FILE"
echo "=== Committing changes ===" | tee -a "$LOG_FILE"
git add -A
git commit -m "YOLO exploration complete

Task: $PROMPT

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>" --allow-empty 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "=== YOLO Exploration Complete ===" | tee -a "$LOG_FILE"
echo "Timestamp: $(date)" | tee -a "$LOG_FILE"

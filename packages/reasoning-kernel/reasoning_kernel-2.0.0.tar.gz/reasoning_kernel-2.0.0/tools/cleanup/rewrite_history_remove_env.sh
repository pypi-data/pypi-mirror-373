#!/usr/bin/env bash
set -euo pipefail

# Purpose: Purge committed env files and secrets from git history across all branches/tags.
# Targets: .env, .env.* (including .env.production, .env.development), and any file named ".env" anywhere.
# Notes:
# - Prefer git filter-repo if installed. This script uses filter-branch (index-filter) as a portable fallback.
# - This is destructive: it rewrites history. Coordinate with collaborators.
# - Run from the repo root. Create a backup tag automatically.

TARGET_PATTERNS=(
  ".env"
  ".env.*"
)

confirm() {
  read -r -p "$1 [y/N] " resp || true
  case "$resp" in
    [yY][eE][sS]|[yY]) return 0 ;;
    *) return 1 ;;
  esac
}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: not inside a git repository." >&2
  exit 1
fi

echo "Repository: $(git rev-parse --show-toplevel)"
echo "Current branch: $(git rev-parse --abbrev-ref HEAD)"

# Ensure working tree is clean before rewriting history
if [ -n "$(git status --porcelain)" ]; then
  echo "Error: working tree is not clean. Stash or commit changes before running this script." >&2
  git status --porcelain
  exit 1
fi

backup_tag="pre-rewrite-$(date +%Y%m%d-%H%M%S)"
echo "Creating lightweight backup tag: $backup_tag"
git tag "$backup_tag" || {
  echo "Failed to create tag. Aborting." >&2; exit 1;
}

echo "Checking for git filter-repo..."
if command -v git >/dev/null 2>&1 && git filter-repo --version >/dev/null 2>&1; then
  echo "git filter-repo found. Using it for fast history rewrite."
  # Build arguments to remove target paths wherever they appear
  args=()
  for p in "${TARGET_PATTERNS[@]}"; do
    args+=("--path-glob" "$p")
  done
  # Drop matched paths entirely by inverting (keep everything else)
  git filter-repo --force --invert-paths "${args[@]}" || { echo "git filter-repo failed." >&2; exit 1; }
else
  echo "git filter-repo not found. Falling back to git filter-branch with index-filter (portable)."
  echo "This may take a while on large repos."

  # Use index-filter to avoid checking out files; use git pathspec globs to match nested .env files
  git filter-branch --force --prune-empty --tag-name-filter cat \
    --index-filter "git rm -r --cached --ignore-unmatch ':(glob)**/.env' ':(glob)**/.env.*'" -- --all
fi

echo "Rewrite complete locally. Next steps:"
cat <<EOF
1) Force-push all branches and tags to remote AFTER coordinating with your team:
   git push --force --tags --all origin

2) Instruct all collaborators to:
   - Stop work temporarily
   - Delete local clones or run: git fetch --all && git reset --hard origin/main && git clean -fd
   - Rotate any secrets that were exposed if not already rotated

3) Validate no secrets remain:
   - Fresh clone into a new directory
   - Run secret scanners (detect-secrets, gitleaks)
   - Manually grep for ENV keys

If anything goes wrong, you can restore from tag: $backup_tag
EOF

echo "Done."

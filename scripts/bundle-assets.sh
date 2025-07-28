#!/usr/bin/env bash
#
# bundle-assets.sh
#
# Usage:
#   ./scripts/bundle-assets.sh           # => dist/workshop-assets-YYYYMMDD.tgz
#   VERSION=v0.3 ./scripts/bundle-assets.sh
#
# The resulting archive preserves the directory layout:
#   data/content/raw/...
#   data/content/normalized/...
#   data/embeddings/...
#   data/wasm/...
#
# Add the tgz as a GitHub release asset, then update ASSET_URL in
# scripts/fetch-assets.sh so Codespaces prebuilds pull it automatically.

set -euo pipefail

############################
# 1. Configurable bits
############################
SRC_DIRS=(
  "data/content/raw"
  "data/content/normalized"
  "data/embeddings"
  "data/wasm"
)

# Default version label is today’s date; override with VERSION=... env var
VERSION="${VERSION:-$(date +%Y%m%d)}"
OUT_DIR="dist"
ARCHIVE="workshop-assets-${VERSION}.tgz"

############################
# 2. Sanity checks
############################
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$repo_root" ]]; then
  echo "❌  Must run inside a git repo" >&2
  exit 1
fi

for d in "${SRC_DIRS[@]}"; do
  if [[ ! -d "$repo_root/$d" ]]; then
    echo "❌  Missing directory: $d" >&2
    exit 1
  fi
done

############################
# 3. Archive
############################
mkdir -p "$repo_root/$OUT_DIR"

echo "📦  Creating $OUT_DIR/$ARCHIVE …"
tar -C "$repo_root" \
    --exclude='.gitkeep' \
    --exclude='__pycache__' \
    --exclude='.DS_Store' \
    --exclude='._*' \
    --exclude='*/._*' \
    -czf "$OUT_DIR/$ARCHIVE" \
    "${SRC_DIRS[@]}"

echo "✅  Done. File size:"
du -h "$OUT_DIR/$ARCHIVE"

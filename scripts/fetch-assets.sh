#!/usr/bin/env bash
set -euo pipefail

OWNER="momentohq"
REPO="momento-buffconf-workshop-internal"
ASSET_VERSION="${ASSET_VERSION:-20250725}"
TAG="assets-${ASSET_VERSION}"
FILE="workshop-assets-${ASSET_VERSION}.tgz"

URL="https://github.com/${OWNER}/${REPO}/releases/download/${TAG}/${FILE}"
DEST="${DEST:-/workspaces/$REPO}"

echo "📦  Downloading $FILE …"
mkdir -p "$DEST"
curl -sSL "$URL" | tar -xzv -C "$DEST"
echo "✅  Assets unpacked to $DEST"

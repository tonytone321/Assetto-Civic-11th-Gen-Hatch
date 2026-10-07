#!/usr/bin/env bash
# Install the Blender LTS build used in Phase 2 (official Linux build from download.blender.org),
# verify it against Blender's published SHA-256 and run a headless version check.
set -euo pipefail
VER=5.2.2
SERIES=5.2
DEST=/opt/blender
DL=/opt/blender-dl
mkdir -p "$DL" "$DEST"
cd "$DL"
[ -f "blender-$VER-linux-x64.tar.xz" ] || curl -sS -o "blender-$VER-linux-x64.tar.xz" "https://download.blender.org/release/Blender$SERIES/blender-$VER-linux-x64.tar.xz"
curl -sS -o "blender-$VER.sha256" "https://download.blender.org/release/Blender$SERIES/blender-$VER.sha256"
grep "linux-x64.tar.xz" "blender-$VER.sha256" | sha256sum -c -
[ -x "$DEST/blender-$VER-linux-x64/blender" ] || tar -xJf "blender-$VER-linux-x64.tar.xz" -C "$DEST"
"$DEST/blender-$VER-linux-x64/blender" --version | head -1
echo "export BLENDER=$DEST/blender-$VER-linux-x64/blender"

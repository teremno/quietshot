#!/usr/bin/env bash
set -euo pipefail

version="${QUIETSHOT_VERSION:-0.2.0}"
architecture="${QUIETSHOT_ARCH:?Set QUIETSHOT_ARCH to arm64 or x64}"
mkdir -p build/dmg-root release
cp -R dist/QuietShot.app build/dmg-root/
ln -s /Applications build/dmg-root/Applications
hdiutil create -volname QuietShot -srcfolder build/dmg-root -ov -format UDZO \
  "release/QuietShot-${version}-macOS-${architecture}.dmg"
hdiutil verify "release/QuietShot-${version}-macOS-${architecture}.dmg"

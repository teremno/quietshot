#!/usr/bin/env bash
set -euo pipefail

version="${QUIETSHOT_VERSION:-0.2.0}"
root="$(pwd)/build/deb-root"
mkdir -p "$root/DEBIAN" "$root/opt/quietshot" "$root/usr/share/applications" release
cp -a dist/QuietShot/. "$root/opt/quietshot/"
cat > "$root/DEBIAN/control" <<EOF
Package: quietshot
Version: $version
Section: graphics
Priority: optional
Architecture: amd64
Maintainer: QuietShot contributors <noreply@github.com>
Depends: libegl1, libpulse0, libxkbcommon0, libxkbcommon-x11-0, libxcb-cursor0, libxcb-keysyms1, libxcb-shape0, libxcb-xkb1, libxcb-icccm4
Description: Floating screenshot tool with full-resolution PNG annotations
EOF
cat > "$root/usr/share/applications/quietshot.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=QuietShot
Comment=Capture and annotate full-resolution screenshots
Exec=/opt/quietshot/QuietShot
Terminal=false
Categories=Graphics;Utility;
EOF
dpkg-deb --build "$root" "release/QuietShot-${version}-Linux-x64.deb"
dpkg-deb --info "release/QuietShot-${version}-Linux-x64.deb"

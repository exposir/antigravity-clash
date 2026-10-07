#!/bin/zsh
set -e

if [[ $# -gt 1 || ( $# -eq 1 && "$1" != --direct-launch ) ]]; then
  echo "用法: ./install.sh [--direct-launch]" >&2
  exit 2
fi

ROOT=${0:A:h}
APP="$HOME/Applications/Antigravity-Clash.app"
BIN="$HOME/.local/bin/antigravity-clash"

mkdir -p "$HOME/.local/bin" "$APP/Contents/MacOS" "$APP/Contents/Resources"
install -m 755 "$ROOT/bin/antigravity-clash" "$BIN"
install -m 755 "$ROOT/app/Contents/MacOS/Antigravity-Clash" "$APP/Contents/MacOS/Antigravity-Clash"
install -m 755 "$ROOT/bin/antigravity-clash" "$APP/Contents/Resources/antigravity-clash"
install -m 644 "$ROOT/app/Contents/Info.plist" "$APP/Contents/Info.plist"
install -m 644 "$ROOT/app/Contents/Resources/AppIcon.icns" "$APP/Contents/Resources/AppIcon.icns"
codesign --force --sign - "$APP"

echo "已安装: $APP"
if [[ "${1:-}" == --direct-launch ]]; then
  "$ROOT/direct-launch.sh" enable
fi

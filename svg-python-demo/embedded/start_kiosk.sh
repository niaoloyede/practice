#!/bin/sh
# Local-only boot UI: fullscreen browser loading an SVG from disk (no network).
# Set ROBOT_SVG to the on-disk path baked into your robot image.

SVG="${ROBOT_SVG:-/opt/robot/ui/animation.svg}"
case "$SVG" in
  /*) ;;
  *) echo "ROBOT_SVG must be absolute: $SVG" >&2; exit 1 ;;
esac
URL="file://$SVG"
CHROME_FLAGS="--kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000"

if command -v cage >/dev/null 2>&1; then
  exec cage -- chromium $CHROME_FLAGS --disable-session-crashed-bubble "$URL"
fi

exec chromium $CHROME_FLAGS "$URL" \
  || exec chromium-browser $CHROME_FLAGS "$URL" \
  || exec google-chrome-stable $CHROME_FLAGS "$URL"
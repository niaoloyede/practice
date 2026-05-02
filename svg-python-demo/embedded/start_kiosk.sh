#!/bin/sh
# Local-only boot UI: fullscreen browser loading an SVG from disk (no network).
# Set ROBOT_SVG to the on-disk path baked into your robot image.

SVG="${ROBOT_SVG:-/opt/robot/ui/animation.svg}"
case "$SVG" in
  /*) ;;
  *) echo "ROBOT_SVG must be absolute: $SVG" >&2; exit 1 ;;
esac
URL="file://$SVG"

if command -v cage >/dev/null 2>&1; then
  exec cage -- chromium --kiosk --noerrdialogs --disable-session-crashed-bubble \
    --disable-infobars --check-for-update-interval=31536000 "$URL"
fi
exec chromium --kiosk --noerrdialogs --disable-infobars \
  --check-for-update-interval=31536000 "$URL" \
  || exec chromium-browser --kiosk "$URL" \
  || exec google-chrome-stable --kiosk "$URL"

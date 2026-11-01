#!/usr/bin/env bash
set -e

TARGET="${1:-modern}"
SITE_DIR="$HOME/Sites/sudheerqk"

if [ "$TARGET" != "modern" ] && [ "$TARGET" != "classic" ]; then
    echo "Usage: ./switch-ui.sh [modern|classic]"
    exit 1
fi

if [ ! -f "$SITE_DIR/$TARGET/index.html" ]; then
    echo "Error: $SITE_DIR/$TARGET/index.html not found."
    exit 1
fi

# Copy target version to live root
cp "$SITE_DIR/$TARGET/index.html" "$SITE_DIR/index.html"
echo "✓ Switched root index.html to: $TARGET"

# Reload Caddy to serve the updated live file
caddy reload --config /opt/homebrew/etc/Caddyfile 2>/dev/null || echo "Note: Reload Caddy manually if not running."

echo "✓ Live site updated locally. Ready to push to GitHub when verified."

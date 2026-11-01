#!/usr/bin/env bash
set -e

SITE_DIR="$HOME/Sites/sudheerqk"
cd "$SITE_DIR"

# 1. Create version folders
mkdir -p "$SITE_DIR/classic"
mkdir -p "$SITE_DIR/modern"

# 2. Archive existing live code into classic
if [ -f "$SITE_DIR/index.html" ]; then
    cp "$SITE_DIR/index.html" "$SITE_DIR/classic/index.html"
    echo "✓ Preserved current live code in: ~/Sites/sudheerqk/classic/index.html"
fi

# 3. Create the deployment switch script
cat << 'DEPLOY_SCRIPT' > "$SITE_DIR/switch-ui.sh"
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
DEPLOY_SCRIPT

chmod +x "$SITE_DIR/switch-ui.sh"
echo "✓ Created deploy script: ~/Sites/sudheerqk/switch-ui.sh"

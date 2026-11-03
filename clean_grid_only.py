import os
import re

path = "/Users/sudheerkumar/Sites/sudheerqk/index.html"
if not os.path.exists(path):
    print("Error: index.html not found!")
    exit(1)

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# Target the exact old hardcoded grid container and its contents
# We want to replace it with <div id="dynamicMediaContainer"></div>
old_grid_pattern = r'<div class="media-showcase-grid"[^>]*>[\s\S]*?</div>\s*(?:</div>)?'

if re.search(old_grid_pattern, html):
    html = re.sub(old_grid_pattern, '<div id="dynamicMediaContainer" style="margin-top: 16px;"></div>', html, count=1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("✓ Successfully replaced media-showcase-grid with dynamicMediaContainer!")
else:
    print("Warning: media-showcase-grid pattern not matched exactly, checking alternative.")
    # Fallback: replace mediaGalleryGrid
    alt_pattern = r'<div[^>]*id=["\']mediaGalleryGrid["\'][^>]*>[\s\S]*?</div>'
    if re.search(alt_pattern, html):
        html = re.sub(alt_pattern, '<div id="dynamicMediaContainer" style="margin-top: 16px;"></div>', html, count=1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("✓ Successfully replaced mediaGalleryGrid!")
    else:
        print("Error: Could not find any gallery grid container.")

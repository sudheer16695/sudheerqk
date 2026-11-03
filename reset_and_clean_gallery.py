import os
import re

path = "/Users/sudheerkumar/Sites/sudheerqk/index.html"
if not os.path.exists(path):
    print("Error: index.html not found!")
    exit(1)

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# Cleanly locate the Captured & Visuals section and replace its content container
# We look for the section header comment or title
target_header = "Captured & Visuals"
if target_header in html:
    # Let us find everything from 'Captured & Visuals' up to the next major section (like Footer or Ask AI)
    # and replace the showcase grid with an empty dynamic container.
    print("Found Captured & Visuals section.")

# Build clean dynamic container placeholder
clean_container = '''
            <div class="section-header">
                <h3>Captured & Visuals</h3>
                <p>Personal travels, moments, and technical architecture reels.</p>
            </div>
            <div id="dynamicMediaContainer" style="margin-top: 24px;">
                <div style="color: #666; font-size: 0.9rem; padding: 10px 0;">No media items uploaded in subfolders yet.</div>
            </div>
'''

# Let us replace the entire block containing the old cards
# We target from <div class="media-showcase-grid" up to its closing or subsequent wrapper
old_grid_pattern = r'<div class="media-showcase-grid"[^>]*>.*?</div>(\s*</div>)?(\s*</div>)?'

# Alternatively, let us target the exact block between Captured & Visuals and the next section
section_pattern = r'(<div class="section-header">\s*<h3>Captured & Visuals</h3>.*?)(?=<div class="footer-section"|<footer|<div id="askAi|$)`'

# Let us use a precise replacement for the grid container
if '<div class="media-showcase-grid"' in html:
    # Replace the old grid and everything inside it with our clean container
    # First, let us check what class wraps the media section
    html = re.sub(r'<div class="media-showcase-grid"[^>]*>[\s\S]*?(?=<div class="footer-section"|<footer|\Z)', '<div class="media-showcase-grid" id="dynamicMediaContainer">\n                <div style="color: #666; font-size: 0.9rem; padding: 10px 0;">No media items uploaded in subfolders yet.</div>\n            </div>\n', html, count=1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("✓ Successfully wiped old hardcoded grid from index.html!")
else:
    print("Could not find media-showcase-grid.")

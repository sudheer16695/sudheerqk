import os
import re

path = "/Users/sudheerkumar/Sites/sudheerqk/index.html"
if not os.path.exists(path):
    print("Error: index.html not found")
    exit(1)

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

if "IMG_7800.mp4" in html:
    print("Notice: IMG_7800.mp4 card is already present.")
else:
    new_card = '''                <div class="media-card" onclick="openVideoPlayer('assets/videos/IMG_7800.mp4', 'Travel Reel')">
                    <video playsinline muted loop poster="/avatar.jpg">
                        <source src="assets/videos/IMG_7800.mp4" type="video/mp4">
                    </video>
                    <div class="media-play-indicator">
                        <svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                    </div>
                    <div class="media-card-label">
                        <span>Travel Reel</span>
                        <span class="media-card-sub">assets/videos/IMG_7800.mp4</span>
                    </div>
                </div>'''
    
    target_pattern = r'(<div class="media-showcase-grid" id="mediaGalleryGrid">)'
    if re.search(target_pattern, html):
        html = re.sub(target_pattern, rf'\1\n{new_card}', html, count=1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("✓ Successfully added video card to index.html!")
    else:
        print("Error: mediaGalleryGrid container not found.")

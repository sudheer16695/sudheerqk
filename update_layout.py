import os
import re

path = "/Users/sudheerkumar/Sites/sudheerqk/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

new_script_block = """
<div id="dynamicMediaContainer">
    <!-- Categories and rows will be injected dynamically -->
</div>

<style>
.media-category-section {
    margin-bottom: 48px;
}
.media-category-section h3 {
    color: #fff;
    font-size: 1.25rem;
    margin-bottom: 16px;
    font-weight: 600;
    letter-spacing: -0.01em;
}
.media-showcase-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
    margin-bottom: 24px;
}
</style>

<script>
async function loadCategorizedMedia() {
    const container = document.getElementById('dynamicMediaContainer');
    if (!container) return;

    try {
        const response = await fetch('/api/media');
        const categories = await response.json();
        
        let html = '';

        for (const [catName, files] of Object.entries(categories)) {
            if (!files || files.length === 0) continue;

            const formattedTitle = catName.charAt(0).toUpperCase() + catName.slice(1).replace(/[-_]/g, ' ');

            html += `
                <div class="media-category-section">
                    <h3>${formattedTitle}</h3>
                    <div class="media-showcase-grid">
            `;

            files.forEach(file => {
                const ext = file.split('.').pop().toLowerCase();
                const isVideo = ['mp4', 'mov', 'webm'].includes(ext);
                const title = file.replace(/\\.[^/.]+$/, "").replace(/[-_]/g, ' ');
                const filePath = `assets/${catName}/${file}`;

                if (isVideo) {
                    html += `
                        <div class="media-card" onclick="openVideoPlayer('${filePath}', '${title}')">
                            <video playsinline muted loop poster="/avatar.jpg">
                                <source src="${filePath}" type="video/mp4">
                            </video>
                            <div class="media-play-indicator">
                                <svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                            </div>
                            <div class="media-card-label">
                                <span>${title}</span>
                                <span class="media-card-sub">${filePath}</span>
                            </div>
                        </div>
                    `;
                } else {
                    html += `
                        <div class="media-card" onclick="openImageViewer('${filePath}', '${title}')">
                            <img src="${filePath}" alt="${title}" loading="lazy" style="width: 100%; height: 100%; object-fit: cover;">
                            <div class="media-card-label">
                                <span>${title}</span>
                                <span class="media-card-sub">${filePath}</span>
                            </div>
                        </div>
                    `;
                }
            });

            html += `
                    </div>
                </div>
            `;
        }

        container.innerHTML = html || '<p style="color: #888;">No media categories found.</p>';
    } catch (err) {
        console.error("Error loading media gallery:", err);
    }
}

document.addEventListener('DOMContentLoaded', loadCategorizedMedia);
</script>
"""

# Replace container/scripts
if 'id="dynamicMediaContainer"' in content:
    content = re.sub(r'<div id="dynamicMediaContainer">.*?</div>\s*(<style>.*?</style>)?\s*(<script>.*?</script>)?', new_script_block, content, flags=re.S)
else:
    content += "\n" + new_script_block

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("✓ Updated index.html with clean grid spacing")

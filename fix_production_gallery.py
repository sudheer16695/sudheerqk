import os
import re

path = "/Users/sudheerkumar/Sites/sudheerqk/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

fixed_block = """
<div id="dynamicMediaContainer">
    <!-- Categories and rows will be injected dynamically -->
</div>

<style>
.media-category-section {
    margin-bottom: 40px;
}
.media-category-section h3 {
    color: #fff;
    font-size: 1.25rem;
    margin-bottom: 16px;
    font-weight: 600;
}
.media-showcase-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
}
.media-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.2s ease, border-color 0.2s ease;
    position: relative;
}
.media-card:hover {
    transform: translateY(-4px);
    border-color: rgba(255, 255, 255, 0.2);
}
.media-card video, .media-card img {
    width: 100%;
    height: 180px;
    object-fit: cover;
    display: block;
}
.media-play-indicator {
    position: absolute;
    top: 70px;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 48px;
    height: 48px;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.media-play-indicator svg {
    width: 20px;
    height: 20px;
    fill: #fff;
    margin-left: 2px;
}
.media-card-label {
    padding: 12px 16px;
    background: rgba(0, 0, 0, 0.4);
}
.media-card-label span {
    display: block;
    color: #fff;
    font-size: 0.95rem;
    font-weight: 500;
}
.media-card-label .media-card-sub {
    color: #888;
    font-size: 0.75rem;
    margin-top: 2px;
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
                            <img src="${filePath}" alt="${title}" loading="lazy">
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

        container.innerHTML = html || '<p style="color: #888;">No media categories found in subfolders.</p>';
    } catch (err) {
        console.error("Error loading media gallery:", err);
    }
}

document.addEventListener('DOMContentLoaded', loadCategorizedMedia);
</script>
"""

# Replace existing container/scripts
if 'id="dynamicMediaContainer"' in content:
    content = re.sub(r'<div id="dynamicMediaContainer">.*?</div>\s*(<style>.*?</style>)?\s*(<script>.*?</script>)?', fixed_block, content, flags=re.S)
else:
    content += "\n" + fixed_block

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("✓ Fixed index.html layout and CSS grid styles!")

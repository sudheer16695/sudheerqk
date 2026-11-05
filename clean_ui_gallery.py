import os
import re

# 1. Remove unwanted demo videos and stray files from both directories
paths_to_remove = [
    "/Users/sudheerkumar/Sites/sudheerqk/vault-demo.mp4",
    "/Users/sudheerkumar/Sites/sudheerqk/assets/videos/vault-demo.mp4",
    "/Users/sudheerkumar/Sites/sudheerqk/assets/videos/lab-overview.mp4",
    "/Users/sudheerkumar/Sites/sudheerqk/assets/images/avatar.jpg",
    "/Users/sudheerkumar/Desktop/sudheerqk.com/vault-demo.mp4",
    "/Users/sudheerkumar/Desktop/sudheerqk.com/assets/videos/vault-demo.mp4",
    "/Users/sudheerkumar/Desktop/sudheerqk.com/assets/videos/lab-overview.mp4",
    "/Users/sudheerkumar/Desktop/sudheerqk.com/assets/images/avatar.jpg"
]

for p in paths_to_remove:
    if os.path.exists(p):
        os.remove(p)
        print(f"Deleted unwanted file: {p}")

# 2. Update index.html to remove hardcoded cards and load dynamically
index_path = "/Users/sudheerkumar/Sites/sudheerqk/index.html"
with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

# Replace the entire <section id="visuals"...>...</section> block
new_visuals_section = '''<!-- Captured & Visuals -->
        <section id="visuals" style="margin-bottom: 5.5rem; display: none;">
            <div class="section-header">
                <h2 class="section-title">Captured &amp; Visuals</h2>
                <p class="section-desc">Personal travels, moments, and technical architecture reels.</p>
            </div>
            <div id="dynamicMediaContainer"></div>
        </section>'''

html = re.sub(
    r'<!-- Captured & Visuals -->\s*<section id="visuals"[\s\S]*?</section>',
    new_visuals_section,
    html
)

# Add image lightbox modal and dynamic media loader script before </body>
dynamic_loader_script = '''
    <!-- Image Viewer Modal -->
    <div class="modal-overlay" id="image-viewer-modal" onclick="if(event.target.id==='image-viewer-modal') closeModal('image-viewer-modal')">
        <div class="glass-modal" style="max-width:720px; text-align:center;">
            <button class="modal-close-btn" onclick="closeModal('image-viewer-modal')">&times;</button>
            <span class="hero-badge" style="margin-bottom:0.4rem;">Visual Preview</span>
            <h2 id="imageViewerTitle" class="profile-card-name" style="font-size:1.35rem; margin-bottom:1rem;">Photo</h2>
            <div style="width:100%; max-height:70vh; border-radius:20px; overflow:hidden; background:#000;">
                <img id="dedicatedImageElement" src="" alt="Preview" style="width:100%; height:100%; max-height:70vh; object-fit:contain; display:block;">
            </div>
        </div>
    </div>

    <script>
        function openImageViewer(imgUrl, imgTitle) {
            document.getElementById("imageViewerTitle").textContent = imgTitle || "Photo";
            document.getElementById("dedicatedImageElement").src = imgUrl;
            openModal("image-viewer-modal");
        }

        async function loadDynamicGallery() {
            const section = document.getElementById("visuals");
            const container = document.getElementById("dynamicMediaContainer");
            if (!section || !container) return;

            try {
                const res = await fetch("/api/media");
                if (!res.ok) throw new Error("Media API unavailable");
                const categories = await res.json();

                let html = "";
                for (const [catName, files] of Object.entries(categories)) {
                    if (!files || !files.length) continue;

                    const label = catName.charAt(0).toUpperCase() + catName.slice(1).replace(/[-_]/g, " ");
                    html += `
                        <div style="margin-bottom: 2.5rem;">
                            <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">${label}</h3>
                            <div class="media-showcase-grid" style="margin-bottom: 0;">
                    `;

                    for (const file of files) {
                        const ext = file.split(".").pop().toLowerCase();
                        const isVideo = ["mp4", "mov", "webm"].includes(ext);
                        const title = file.replace(/\\.[^/.]+$/, "").replace(/[-_]/g, " ");
                        const filePath = `assets/${catName}/${file}`;

                        if (isVideo) {
                            html += `
                                <div class="media-card" onclick="openVideoPlayer('${filePath}', '${title}')">
                                    <video playsinline muted preload="metadata" style="width:100%; height:100%; object-fit:cover; background:#0f172a;">
                                        <source src="${filePath}#t=0.5" type="video/mp4">
                                    </video>
                                    <div class="media-play-indicator">
                                        <svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                                    </div>
                                    <div class="media-card-label">
                                        <span>${title}</span>
                                        <span class="media-card-sub">${catName}</span>
                                    </div>
                                </div>
                            `;
                        } else {
                            html += `
                                <div class="media-card" onclick="openImageViewer('${filePath}', '${title}')">
                                    <img src="${filePath}" alt="${title}" loading="lazy">
                                    <div class="media-card-label">
                                        <span>${title}</span>
                                        <span class="media-card-sub">${catName}</span>
                                    </div>
                                </div>
                            `;
                        }
                    }
                    html += `</div></div>`;
                }

                if (html) {
                    container.innerHTML = html;
                    section.style.display = "block";
                } else {
                    container.innerHTML = "";
                    section.style.display = "none";
                }
            } catch (e) {
                section.style.display = "none";
            }
        }
        document.addEventListener("DOMContentLoaded", loadDynamicGallery);
    </script>
'''

# Remove any old loadCategorizedMedia or loadDynamicGallery blocks if present, then inject cleanly
html = re.sub(r'<!-- Image Viewer Modal -->[\s\S]*?</script>\s*(?=</body>)', '', html)
html = html.replace('</body>', dynamic_loader_script + '\n</body>')

with open(index_path, "w", encoding="utf-8") as f:
    f.write(html)

print("✓ Cleaned index.html and enabled auto-hiding dynamic media gallery")

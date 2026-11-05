from pathlib import Path
from datetime import datetime
import re

PROJECT_DIR = Path.home() / "Sites" / "sudheerqk"
HTML_FILE = PROJECT_DIR / "index.html"
ASSET_ROOT = PROJECT_DIR / "assets"

if not HTML_FILE.exists():
    raise SystemExit(f"ERROR: Website not found: {HTML_FILE}")

# Create media folders
(ASSET_ROOT / "images").mkdir(parents=True, exist_ok=True)
(ASSET_ROOT / "videos").mkdir(parents=True, exist_ok=True)

# Backup existing website
backup = HTML_FILE.with_name(
    f"index.html.backup-{datetime.now():%Y%m%d-%H%M%S}"
)
backup.write_text(HTML_FILE.read_text(encoding="utf-8"), encoding="utf-8")

content = HTML_FILE.read_text(encoding="utf-8")

# Remove previous versions of our injected CSS and JS
content = re.sub(
    r'<style id="dynamic-gallery-styles">.*?</style>',
    '',
    content,
    flags=re.S
)

content = re.sub(
    r'<script id="dynamic-gallery-script">.*?</script>',
    '',
    content,
    flags=re.S
)

# Replace the existing Captured & Visuals section
gallery_section = """
<section id="visuals" style="margin-bottom:5.5rem;" hidden>
    <div class="section-header">
        <h2 class="section-title">Captured &amp; Visuals</h2>
        <p class="section-desc">
            Personal travels, moments, and technical architecture reels.
        </p>
    </div>
    <div id="dynamicMediaContainer" class="media-showcase-grid"></div>
</section>
"""

pattern = re.compile(
    r"""<section\b(?=[^>]*\bid=["']visuals["'])[^>]*>.*?</section>""",
    re.I | re.S
)

if not pattern.search(content):
    raise SystemExit(
        "ERROR: Existing #visuals section not found. "
        "No HTML changes made."
    )

content = pattern.sub(lambda _: gallery_section, content, count=1)

# Dynamic gallery CSS
gallery_css = """
<style id="dynamic-gallery-styles">
#visuals[hidden] {
    display: none !important;
}

#dynamicMediaContainer {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 20px;
}

#dynamicMediaContainer .media-card {
    position: relative;
    overflow: hidden;
    border-radius: 16px;
    cursor: pointer;
    border: 1px solid var(--border-color, rgba(128,128,128,.2));
    transition: transform .25s ease;
}

#dynamicMediaContainer .media-card:hover {
    transform: translateY(-4px);
}

#dynamicMediaContainer .media-card img,
#dynamicMediaContainer .media-card video {
    display: block;
    width: 100%;
    height: 180px;
    object-fit: cover;
    background: transparent;
}

#dynamicMediaContainer .media-card-label {
    padding: 12px 15px;
}

#dynamicMediaContainer .media-card-label span {
    display: block;
}

#dynamicMediaContainer .media-card-sub {
    font-size: .75rem;
    opacity: .65;
    margin-top: 4px;
}

#dynamicMediaContainer .media-play-indicator {
    position: absolute;
    top: 65px;
    left: 50%;
    transform: translateX(-50%);
    width: 45px;
    height: 45px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    background: rgba(0,0,0,.65);
    color: white;
    pointer-events: none;
}

@media(max-width:600px) {
    #dynamicMediaContainer {
        grid-template-columns: 1fr;
    }
}
</style>
"""

# Dynamic gallery JavaScript
gallery_js = r"""
<script id="dynamic-gallery-script">
async function loadDynamicGallery() {
    const section = document.getElementById("visuals");
    const container = document.getElementById("dynamicMediaContainer");

    if (!section || !container) return;

    section.hidden = true;
    container.replaceChildren();

    try {
        const response = await fetch("/api/public-media", {
            cache: "no-store"
        });

        if (!response.ok) {
            throw new Error("Media API returned " + response.status);
        }

        const data = await response.json();
        const files = Array.isArray(data.files) ? data.files : [];

        files.forEach(file => {
            if (!file || !file.url ||
                !["image", "video"].includes(file.type)) return;

            // Only allow files served from the website assets directory.
            if (!file.url.startsWith("/assets/")) return;

            const card = document.createElement("div");
            card.className = "media-card";

            if (file.type === "video") {
                const video = document.createElement("video");
                video.src = file.url;
                video.muted = true;
                video.playsInline = true;
                video.preload = "metadata";

                const play = document.createElement("div");
                play.className = "media-play-indicator";
                play.textContent = "▶";

                card.append(video, play);

                card.addEventListener("click", () => {
                    if (typeof openVideoPlayer === "function") {
                        openVideoPlayer(file.url, file.name);
                    } else {
                        window.open(file.url, "_blank", "noopener");
                    }
                });

            } else {
                const img = document.createElement("img");
                img.src = file.url;
                img.alt = file.name || "Photograph";
                img.loading = "lazy";

                card.appendChild(img);

                card.addEventListener("click", () => {
                    window.open(file.url, "_blank", "noopener");
                });
            }

            const label = document.createElement("div");
            label.className = "media-card-label";

            const title = document.createElement("span");
            title.textContent = file.name || "Media";

            const subtitle = document.createElement("span");
            subtitle.className = "media-card-sub";
            subtitle.textContent = file.type;

            label.append(title, subtitle);
            card.appendChild(label);

            container.appendChild(card);
        });

        section.hidden = container.children.length === 0;

    } catch (error) {
        console.error("Gallery loading failed:", error);
        section.hidden = true;
    }
}

document.addEventListener("DOMContentLoaded", loadDynamicGallery);
</script>
"""

# Inject CSS into document head
if "</head>" in content.lower():
    match = re.search(r"</head>", content, re.I)
    content = content[:match.start()] + gallery_css + "\n" + content[match.start():]
else:
    content = gallery_css + content

# Inject JavaScript before closing body
match = re.search(r"</body>", content, re.I)

if match:
    content = content[:match.start()] + gallery_js + "\n" + content[match.start():]
else:
    content += gallery_js

HTML_FILE.write_text(content, encoding="utf-8")

# Generate FastAPI backend endpoint separately
backend_snippet = r'''
# PUBLIC MEDIA GALLERY API
from pathlib import Path
from urllib.parse import quote
from fastapi.staticfiles import StaticFiles

ASSET_ROOT = Path.home() / "Sites" / "sudheerqk" / "assets"

# Serve website assets if not already mounted.
if not any(
    getattr(route, "path", None) == "/assets"
    for route in app.routes
):
    app.mount(
        "/assets",
        StaticFiles(directory=str(ASSET_ROOT)),
        name="assets"
    )

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v"}

@app.get("/api/public-media")
async def public_media():
    files = []

    for folder, media_type, extensions in [
        ("images", "image", IMAGE_EXTENSIONS),
        ("videos", "video", VIDEO_EXTENSIONS)
    ]:
        directory = ASSET_ROOT / folder

        if not directory.exists():
            continue

        for path in sorted(directory.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue

            if path.suffix.lower() not in extensions:
                continue

            relative = path.relative_to(ASSET_ROOT).as_posix()

            files.append({
                "name": path.stem,
                "type": media_type,
                "url": "/assets/" + quote(relative, safe="/")
            })

    return {"files": files}
'''

snippet_file = PROJECT_DIR / "public_media_endpoint_snippet.py"
snippet_file.write_text(backend_snippet, encoding="utf-8")

print("\n======================================")
print("  WEBSITE GALLERY UPDATE COMPLETED")
print("======================================")
print(f"Project: {PROJECT_DIR}")
print(f"HTML:    {HTML_FILE}")
print(f"Backup:  {backup}")
print(f"Images:  {ASSET_ROOT / 'images'}")
print(f"Videos:  {ASSET_ROOT / 'videos'}")
print(f"API snippet: {snippet_file}")
print("\nIMPORTANT:")
print("Add the generated FastAPI endpoint snippet to your")
print("existing backend application before testing the gallery.")
print("Check that your backend uses the variable name 'app'.")
print("======================================\n")

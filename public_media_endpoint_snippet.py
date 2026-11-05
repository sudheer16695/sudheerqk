
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

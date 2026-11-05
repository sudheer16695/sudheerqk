import os
import re

project_dir = "/Users/sudheerkumar/Sites/sudheerqk"
desktop_dir = "/Users/sudheerkumar/Desktop/sudheerqk.com"

# 1. Clean up stray loose video files from root directories so they don't render as giant bars
for d in [project_dir, desktop_dir]:
    for f in ["vault-demo.mp4", "lab-overview.mp4", "IMG_7800.mp4"]:
        f_path = os.path.join(d, f)
        if os.path.exists(f_path):
            os.remove(f_path)
            print(f"Removed stray root file: {f_path}")

# 2. Ensure subfolders exist under assets/
assets_dir = os.path.join(project_dir, "assets")
os.makedirs(os.path.join(assets_dir, "travel"), exist_ok=True)
os.makedirs(os.path.join(assets_dir, "technical"), exist_ok=True)
os.makedirs(os.path.join(assets_dir, "photos"), exist_ok=True)

# 3. Scan subfolders and build clean media cards for index.html
gallery_html = ""
for cat_name in sorted(os.listdir(assets_dir)):
    cat_path = os.path.join(assets_dir, cat_name)
    if os.path.isdir(cat_path) and not cat_name.startswith("."):
        files = []
        for f in sorted(os.listdir(cat_path)):
            if not f.startswith(".") and f.lower() != "avatar.jpg":
                if f.lower().endswith(('.mp4', '.mov', '.webm', '.jpg', '.jpeg', '.png', '.webp', '.gif')):
                    files.append(f)
        
        if files:
            formatted_title = cat_name.capitalize().replace('-', ' ')
            gallery_html += f'''
            <div class="media-category-group" style="margin-bottom: 32px;">
                <h4 style="color: var(--text-primary); font-size: 1.1rem; margin-bottom: 12px; font-weight: 600;">{formatted_title}</h4>
                <div class="media-grid-container" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px;">
            '''
            
            for file in files:
                ext = file.split('.')[-1].lower()
                is_video = ext in ['mp4', 'mov', 'webm']
                title = os.path.splitext(file)[0].replace('-', ' ').replace('_', ' ').title()
                file_path = f"assets/{cat_name}/{file}"
                
                if is_video:
                    # Video card without using avatar.jpg as a poster (clean dark placeholder)
                    gallery_html += f'''
                    <div class="media-card" onclick="openVideoPlayer('{file_path}', '{title}')" style="border-radius: 20px; overflow: hidden; height: 230px; position: relative; cursor: pointer; box-shadow: var(--glass-shadow); border: 1px solid var(--border-glass); background: #0f172a; transition: all 0.3s ease;">
                        <video playsinline muted preload="metadata" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                            <source src="{file_path}" type="video/mp4">
                        </video>
                        <div class="media-play-indicator" style="position: absolute; top: 12px; right: 12px; background: rgba(0,0,0,0.65); backdrop-filter: blur(10px); border-radius: 50%; width: 34px; height: 34px; display: grid; place-items: center; color: #fff; border: 1px solid rgba(255,255,255,0.25);">
                            <svg viewBox="0 0 24 24" style="width: 14px; height: 14px; fill: currentColor; margin-left: 2px;"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                        </div>
                        <div class="media-card-label" style="position: absolute; bottom: 0; inset-inline: 0; padding: 12px 14px; background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, transparent 100%); color: #fff; font-size: 0.82rem; font-weight: 700; display: flex; flex-direction: column;">
                            <span>{title}</span>
                            <span class="media-card-sub" style="font-size: 0.7rem; color: #cbd5e1; font-weight: 500;">{file_path}</span>
                        </div>
                    </div>
                    '''
                else:
                    gallery_html += f'''
                    <div class="media-card" onclick="openImageViewer('{file_path}', '{title}')" style="border-radius: 20px; overflow: hidden; height: 230px; position: relative; cursor: pointer; box-shadow: var(--glass-shadow); border: 1px solid var(--border-glass); background: var(--surface-card); transition: all 0.3s ease;">
                        <img src="{file_path}" alt="{title}" loading="lazy" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                        <div class="media-card-label" style="position: absolute; bottom: 0; inset-inline: 0; padding: 12px 14px; background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, transparent 100%); color: #fff; font-size: 0.82rem; font-weight: 700; display: flex; flex-direction: column;">
                            <span>{title}</span>
                            <span class="media-card-sub" style="font-size: 0.7rem; color: #cbd5e1; font-weight: 500;">{file_path}</span>
                        </div>
                    </div>
                    '''
            gallery_html += '''
                </div>
            </div>
            '''

if not gallery_html:
    gallery_html = '<div style="color: var(--text-tertiary); font-size: 0.9rem; padding: 10px 0;">No media items uploaded in subfolders yet.</div>'

# 4. Inject into index.html inside the visuals section
index_path = os.path.join(project_dir, "index.html")
with open(index_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Replace the contents of the visuals section grid
pattern = r'(<div class="media-showcase-grid" id="mediaGalleryGrid">.*?</div>|<div id="dynamicMediaContainer">.*?</div>|<div class="media-showcase-grid".*?</div>)'

if re.search(pattern, html_content, flags=R:=re.S):
    html_content = re.sub(pattern, f'<div class="media-showcase-grid" id="mediaGalleryGrid">\n{gallery_html}\n</div>', html_content, flags=R)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✓ Successfully updated index.html gallery grid!")
else:
    print("Error: Could not locate gallery grid in index.html.")


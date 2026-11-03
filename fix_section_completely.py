import os
import re

path = "/Users/sudheerkumar/Sites/sudheerqk/index.html"
if not os.path.exists(path):
    print("Error: index.html not found!")
    exit(1)

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# Let's build the clean gallery HTML based on subfolders in assets/
BASE_ASSETS = "/Users/sudheerkumar/Sites/sudheerqk/assets"
gallery_content = ""

if os.path.exists(BASE_ASSETS):
    for cat_name in sorted(os.listdir(BASE_ASSETS)):
        cat_path = os.path.join(BASE_ASSETS, cat_name)
        if os.path.isdir(cat_path) and not cat_name.startswith("."):
            files = []
            for f in sorted(os.listdir(cat_path)):
                if not f.startswith(".") and f.lower() != "avatar.jpg":
                    if f.lower().endswith(('.mp4', '.mov', '.webm', '.jpg', '.jpeg', '.png', '.webp', '.gif')):
                        files.append(f)
            
            if files:
                formatted_title = cat_name.capitalize().replace('-', ' ')
                gallery_content += f'''
                <div class="media-category-group" style="margin-bottom: 32px;">
                    <h4 style="color: #fff; font-size: 1.1rem; margin-bottom: 12px; font-weight: 600;">{formatted_title}</h4>
                    <div class="media-grid-container" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px;">
                '''
                
                for file in files:
                    ext = file.split('.')[-1].lower()
                    is_video = ext in ['mp4', 'mov', 'webm']
                    title = os.path.splitext(file)[0].replace('-', ' ').replace('_', ' ').title()
                    file_path = f"assets/{cat_name}/{file}"
                    
                    if is_video:
                        gallery_content += f'''
                        <div class="media-card-item" onclick="openVideoPlayer('{file_path}', '{title}')" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; overflow: hidden; cursor: pointer; position: relative;">
                            <video playsinline muted loop poster="/avatar.jpg" style="width: 100%; height: 160px; object-fit: cover; display: block;">
                                <source src="{file_path}" type="video/mp4">
                            </video>
                            <div style="position: absolute; top: 80px; left: 50%; transform: translate(-50%, -50%); width: 40px; height: 40px; background: rgba(0,0,0,0.6); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                <svg viewBox="0 0 24 24" style="width: 16px; height: 16px; fill: #fff; margin-left: 2px;"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                            </div>
                            <div style="padding: 12px; background: rgba(0,0,0,0.4);">
                                <span style="display: block; color: #fff; font-size: 0.9rem; font-weight: 500;">{title}</span>
                                <span style="display: block; color: #888; font-size: 0.75rem; margin-top: 2px;">{file_path}</span>
                            </div>
                        </div>
                        '''
                    else:
                        gallery_content += f'''
                        <div class="media-card-item" onclick="openImageViewer('{file_path}', '{title}')" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; overflow: hidden; cursor: pointer; position: relative;">
                            <img src="{file_path}" alt="{title}" loading="lazy" style="width: 100%; height: 160px; object-fit: cover; display: block;">
                            <div style="padding: 12px; background: rgba(0,0,0,0.4);">
                                <span style="display: block; color: #fff; font-size: 0.9rem; font-weight: 500;">{title}</span>
                                <span style="display: block; color: #888; font-size: 0.75rem; margin-top: 2px;">{file_path}</span>
                            </div>
                        </div>
                        '''
                gallery_content += '''
                    </div>
                </div>
                '''

if not gallery_content:
    gallery_content = '<p style="color: #666; font-size: 0.9rem;">No media items uploaded in subfolders yet.</p>'

# We look for the Captured & Visuals section header and replace everything until the next section or container
pattern = r'(<div[^>]*id=["\']mediaGalleryGrid["\'][^>]*>.*?</div>|<div[^>]*id=["\']dynamicMediaContainer["\'][^>]*>.*?</div>)'

if re.search(pattern, html, flags=re.S):
    html = re.sub(pattern, f'<div id="dynamicMediaContainer">\n{gallery_content}\n</div>', html, flags=re.S)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("✓ Successfully replaced gallery container with strict grid layout!")
else:
    print("Error: Could not locate mediaGalleryGrid or dynamicMediaContainer in index.html.")

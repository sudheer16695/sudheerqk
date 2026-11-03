import os
import re

path = "/Users/sudheerkumar/Sites/sudheerqk/index.html"
if not os.path.exists(path):
    print("Error: index.html not found!")
    exit(1)

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# Scan assets subfolders
BASE_ASSETS = "/Users/sudheerkumar/Sites/sudheerqk/assets"
categories_html = ""

if os.path.exists(BASE_ASSETS):
    for cat_name in sorted(os.listdir(BASE_ASSETS)):
        cat_path = os.path.join(BASE_ASSETS, cat_name)
        if os.path.isdir(cat_path) and not cat_name.startswith(".") and cat_name.lower() not in ["videos", "images"]:
            files = []
            for f in sorted(os.listdir(cat_path)):
                if not f.startswith(".") and f.lower() != "avatar.jpg":
                    if f.lower().endswith(('.mp4', '.mov', '.webm', '.jpg', '.jpeg', '.png', '.webp', '.gif')):
                        files.append(f)
            
            if files:
                formatted_title = cat_name.charAt(0).toUpperCase() + cat_name.slice(1) if hasattr(str, 'charAt') else cat_name.capitalize().replace('-', ' ')
                categories_html += f'''
                <div class="media-category-section" style="margin-bottom: 40px;">
                    <h3 style="color: #fff; font-size: 1.25rem; margin-bottom: 16px; font-weight: 600;">{formatted_title}</h3>
                    <div class="media-showcase-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px;">
                '''
                
                for file in files:
                    ext = file.split('.')[-1].lower()
                    is_video = ext in ['mp4', 'mov', 'webm']
                    title = os.path.splitext(file)[0].replace('-', ' ').replace('_', ' ').title()
                    file_path = f"assets/{cat_name}/{file}"
                    
                    if is_video:
                        categories_html += f'''
                        <div class="media-card" onclick="openVideoPlayer('{file_path}', '{title}')" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; overflow: hidden; cursor: pointer; position: relative; transition: transform 0.2s;">
                            <video playsinline muted loop poster="/avatar.jpg" style="width: 100%; height: 180px; object-fit: cover; display: block;">
                                <source src="{file_path}" type="video/mp4">
                            </video>
                            <div class="media-play-indicator" style="position: absolute; top: 90px; left: 50%; transform: translate(-50%, -50%); width: 44px; height: 44px; background: rgba(0,0,0,0.6); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                <svg viewBox="0 0 24 24" style="width: 18px; height: 18px; fill: #fff; margin-left: 2px;"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                            </div>
                            <div class="media-card-label" style="padding: 12px 16px; background: rgba(0,0,0,0.4);">
                                <span style="display: block; color: #fff; font-size: 0.95font-weight: 500;">{title}</span>
                                <span style="display: block; color: #888; font-size: 0.75rem; margin-top: 2px;">{file_path}</span>
                            </div>
                        </div>
                        '''
                    else:
                        categories_html += f'''
                        <div class="media-card" onclick="openImageViewer('{file_path}', '{title}')" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; overflow: hidden; cursor: pointer; position: relative; transition: transform 0.2s;">
                            <img src="{file_path}" alt="{title}" loading="lazy" style="width: 100%; height: 180px; object-fit: cover; display: block;">
                            <div class="media-card-label" style="padding: 12px 16px; background: rgba(0,0,0,0.4);">
                                <span style="display: block; color: #fff; font-size: 0.95rem; font-weight: 500;">{title}</span>
                                <span style="display: block; color: #888; font-size: 0.75rem; margin-top: 2px;">{file_path}</span>
                            </div>
                        </div>
                        '''
                categories_html += '''
                    </div>
                </div>
                '''

# Target container in index.html and replace it
target_pattern = r'(<div class="media-showcase-grid" id="mediaGalleryGrid">.*?</div>|<div id="dynamicMediaContainer">.*?</div>)'

if re.search(target_pattern, html, flags=re.S):
    html = re.sub(target_pattern, f'<div id="dynamicMediaContainer">\n{categories_html}\n</div>', html, flags=re.S)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("✓ Successfully built and injected static gallery cards into index.html!")
else:
    print("Error: Could not find gallery container in index.html.")

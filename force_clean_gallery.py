import os

path = "/Users/sudheerkumar/Sites/sudheerqk/index.html"
if not os.path.exists(path):
    print("Error: index.html not found!")
    exit(1)

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# Let us find where "Captured & Visuals" starts
start_idx = html.find("Captured & Visuals")
if start_idx == -1:
    print("Error: Could not find 'Captured & Visuals' in index.html")
    exit(1)

# Let us look a bit before it to catch the container <div> opening tag
# We will find the section/div wrapper preceding "Captured & Visuals"
section_start = html.rfind("<div", 0, start_idx)

# Let us find where the next major section or footer begins (e.g., footer-section or Designed & Developed)
end_markers = ['<div class="footer-section"', '<footer', '<div class="footer"', 'Designed & Developed']
section_end = -1
for marker in end_markers:
    pos = html.find(marker, start_idx)
    if pos != -1:
        section_end = pos
        break

if section_end == -1:
    print("Warning: Could not find clear section end marker, using fallback.")
    section_end = start_idx + 2000 # fallback length

# Extract what is currently there for debugging
print(f"Found section span from index {section_start} to {section_end}")

# Construct the clean replacement block
clean_replacement = '''<div class="section-container">
            <div class="section-header">
                <h3>Captured & Visuals</h3>
                <p>Personal travels, moments, and technical architecture reels.</p>
            </div>
            <div id="dynamicMediaContainer" style="margin-top: 24px;">
                <div style="color: #666; font-size: 0.9rem; padding: 10px 0;">No media items uploaded in subfolders yet.</div>
            </div>
        </div>'''

# Replace from section_start to section_end with our clean block
# (We want to make sure we preserve the footer and everything after section_end)
new_html = html[:section_start] + clean_replacement + "\n\n        " + html[section_end:]

with open(path, "w", encoding="utf-8") as f:
    f.write(new_html)

print("✓ Successfully forced clean replacement of the Captured & Visuals section!")

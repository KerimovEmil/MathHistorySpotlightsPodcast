import os

# The path to the directory containing the episode images
image_dir = "assets/images/episodes"

# Get a list of all files in the directory
try:
    image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
except FileNotFoundError:
    print(f"Error: The directory '{image_dir}' was not found.")
    exit()

# Start building the HTML for the gallery grid
gallery_html = '<div class="gallery-grid">'

# Create a gallery item for each image
if image_files:
    gallery_html += '\n'
    for image_file in image_files:
        # alt attribute should be the name of the file without the extension
        alt_text = os.path.splitext(image_file)[0]
        image_path = f"assets/images/episodes/{image_file}"
        gallery_html += f'          <div class="gallery-item"><img src="{image_path}" alt="{alt_text}"></div>\n'

# Close the gallery grid div
gallery_html += '        </div>'

# Read the entire gallery.html file
try:
    with open("gallery.html", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print("Error: gallery.html not found.")
    exit()

# Find the start and end of the gallery-grid div
start_tag = '<div class="gallery-grid">'
end_tag = '</div>'

# Find the start and end of the gallery-grid div
start_index = content.find(start_tag)
# We add len(start_tag) to start looking for the end tag only after the start tag
end_index = content.find(end_tag, start_index + len(start_tag))


if start_index != -1 and end_index != -1:
    # Find the end of the div tag (including any attributes)
    start_of_content_index = start_index + len(start_tag)

    # The content to replace is everything between the start and end tag
    # but we will replace the tags themselves as well
    content_to_replace = content[start_index:end_index + len(end_tag)]
    
    # Replace the old gallery grid with the new one
    new_content = content.replace(content_to_replace, gallery_html)

    # Write the updated content back to the file
    with open("gallery.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Gallery updated successfully.")
else:
    print("Error: Could not find the gallery-grid div in gallery.html.")

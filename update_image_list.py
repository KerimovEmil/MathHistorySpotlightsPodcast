import os
import json

# Path to the directory containing the episode images
image_dir = "assets/images/episodes"
json_file_path = os.path.join(image_dir, "image-list.json")

# Get a list of all files in the directory
try:
    image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f)) and f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
except FileNotFoundError:
    print(f"Error: The directory '{image_dir}' was not found.")
    exit()

# Write the list of image files to the JSON file
with open(json_file_path, "w") as f:
    json.dump(image_files, f, indent=2)

print(f"Image list updated successfully in '{json_file_path}'")

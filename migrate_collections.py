import os
import re
import json

ROOT = os.path.dirname(__file__)
COLLECTIONS_FILE = os.path.join(ROOT, "collections.html")
OUTPUT_JSON = os.path.join(ROOT, "collections.json")

def main():
    if not os.path.exists(COLLECTIONS_FILE):
        print(f"Error: {COLLECTIONS_FILE} not found.")
        return

    with open(COLLECTIONS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by collection-group blocks
    groups = re.split(r'<!-- Collection \d+: [^>]+ -->\s*<div class="collection-group"', content)
    
    # The first split is the header, skip it.
    collections_data = []
    
    # We need a more robust way to find groups.
    # Let's use a regex that matches the whole div.collection-group
    group_pattern = re.compile(
        r'<div class="collection-group" id="(?P<id>[^"]+)">\s*'
        r'<div class="group-header">\s*'
        r'<h2 class="group-title">(?P<title>[^<]+)</h2>\s*'
        r'<span class="group-tag">(?P<tag>[^<]+)</span>\s*'
        r'</div>\s*'
        r'<p class="group-description">\s*(?P<description>.*?)\s*</p>\s*'
        r'<div class="mathematician-grid">(?P<grid_content>.*?)</div>\s*</div>',
        re.DOTALL
    )

    for match in group_pattern.finditer(content):
        group_id = match.group("id")
        title = match.group("title").strip()
        tag = match.group("tag").strip()
        description = match.group("description").strip()
        grid_content = match.group("grid_content")

        # Extract mathematicians from the grid
        math_pattern = re.compile(
            r'<a href="/mathematicians/(?P<slug>[^"]+)\.html" class="math-card">.*?'
            r'<img src="(?P<image>[^"]+)" alt="(?P<alt>[^"]+)">.*?'
            r'<h3 class="card-name">(?P<name>[^<]+)</h3>\s*'
            r'<p class="card-role">(?P<role>[^<]+)</p>',
            re.DOTALL
        )

        mathematicians = []
        for math_match in math_pattern.finditer(grid_content):
            mathematicians.append({
                "slug": math_match.group("slug"),
                "name": math_match.group("name").strip(),
                "role": math_match.group("role").strip(),
                "image": math_match.group("image")
            })

        collections_data.append({
            "id": group_id,
            "title": title,
            "tag": tag,
            "description": description,
            "mathematicians": mathematicians
        })

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(collections_data, f, indent=2)

    print(f"Successfully migrated {len(collections_data)} collections to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()

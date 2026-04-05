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
    groups = re.split(r'<div class="collection-group"', content)
    
    collections_data = []
    for group in groups[1:]:
        # Find id, title, tag, description
        group_id = re.search(r'id="([^"]+)"', group).group(1)
        title = re.search(r'<h2 class="group-title">([^<]+)</h2>', group).group(1).strip()
        tag = re.search(r'<span class="group-tag">([^<]+)</span>', group).group(1).strip()
        
        # Description is trickier due to potential newlines
        desc_match = re.search(r'<p class="group-description">\s*(.*?)\s*</p>', group, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # Find all mathematicians in this group
        math_matches = re.finditer(r'<a href="/mathematicians/([^"]+)\.html" class="math-card">(.*?)</a>', group, re.DOTALL)
        
        mathematicians = []
        for match in math_matches:
            slug = match.group(1)
            inner = match.group(2)
            
            name = re.search(r'<h3 class="card-name">([^<]+)</h3>', inner).group(1).strip()
            role = re.search(r'<p class="card-role">([^<]+)</p>', inner).group(1).strip()
            image = re.search(r'<img src="([^"]+)"', inner).group(1)
            
            mathematicians.append({
                "slug": slug,
                "name": name,
                "role": role,
                "image": image
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

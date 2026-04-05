import os
import re
import json

ROOT = os.path.dirname(__file__)
FRAGMENTS_DIR = os.path.join(ROOT, "assets", "fragments_migrated")
EQUATIONS_FILE = os.path.join(ROOT, "famous_equations.json")

def parse_fragment(content):
    """
    Parses a fragment HTML like:
    <h4><a href="URL">Title</a></h4>
    <p>Description</p>
    $$ EQUATION $$
    """
    # Regex to find each equation group
    # We look for h4 containing the optional link, then p, then $$ equation $$
    # Note: Regex can be fragile for HTML, but these fragments are very consistent.
    
    # Pattern to find h4, p, and $$ sections. We use re.DOTALL to match across lines.
    pattern = r'<h4>\s*(?:<a href="([^"]+)"[^>]*>)?\s*(?:[\d\.]+\s+)?([^<]+?)(?:\s*</a>)?\s*</h4>\s*<p>([^<]+?)</p>\s*\$\$\s*(.+?)\s*\$\$'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    equations = []
    for m in matches:
        wikipedia = m.group(1) or ""
        label = m.group(2).strip()
        description = m.group(3).strip()
        equation = m.group(4).strip()
        
        # Unescape LaTeX if needed (here it's probably raw)
        equations.append({
            "label": label,
            "description": description,
            "equation": equation,
            "wikipedia": wikipedia
        })
    
    return equations

def main():
    if not os.path.exists(EQUATIONS_FILE):
        print("Equations file not found.")
        return
        
    with open(EQUATIONS_FILE, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
        
    # We will update the structure for EVERYONE to be a list.
    new_data = {}
    
    # Process fragments
    for filename in os.listdir(FRAGMENTS_DIR):
        if not filename.endswith(".html"):
            continue
            
        slug = filename[:-5]
        with open(os.path.join(FRAGMENTS_DIR, filename), "r", encoding="utf-8") as f:
            content = f.read()
            
        equations = parse_fragment(content)
        if equations:
            new_data[slug] = equations
            print(f"Extracted {len(equations)} equations for {slug}.")
        else:
            print(f"No equations found in {filename} (might be regular HTML).")

    # For slugs not in fragments, but in existing_data, ensure they are in the new format
    # (If they had manually added something in the previous step, we keep it but and convert it)
    for slug, val in existing_data.items():
        if slug not in new_data:
            if isinstance(val, dict) and val.get("equation"):
                new_data[slug] = [val]
            elif isinstance(val, list):
                new_data[slug] = val
            else:
                new_data[slug] = []
        else:
            # If we found in fragments AND had existing data, fragments probably have more info.
            # But just to be safe, if existing data had a real equation, we could merge?
            # Actually the fragments are the source of truth the user pointed to.
            pass

    with open(EQUATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2)
    print(f"Successfully migrated data to {EQUATIONS_FILE}")

if __name__ == "__main__":
    main()

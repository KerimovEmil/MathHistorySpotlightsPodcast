import os
import re
import urllib.request
import xml.etree.ElementTree as ET
import unicodedata

RSS_URL = "https://anchor.fm/s/10cdf4708/podcast/rss"
ROOT = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(ROOT, "assets", "images", "episodes")
OUT_FEED = os.path.join(ROOT, "assets", "feed.xml")

# Register namespaces to preserve them in output
ET.register_namespace('itunes', "http://www.itunes.com/dtds/podcast-1.0.dtd")
ET.register_namespace('dc', "http://purl.org/dc/elements/1.1/")
ET.register_namespace('content', "http://purl.org/rss/1.0/modules/content/")
ET.register_namespace('atom', "http://www.w3.org/2005/Atom")
ET.register_namespace('media', "http://search.yahoo.com/mrss/")

def normalize_text(s):
    s = s or ""
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def strip_years(s):
    if not s:
        return s
    return re.sub(r"[\s\d\-–—]+$", "", s).strip()

def list_image_files():
    try:
        return os.listdir(IMAGES_DIR)
    except Exception:
        return []

def find_image_for_title(title, image_files):
    norm_title = normalize_text(title)
    for f in image_files:
        name, _ = os.path.splitext(f)
        if normalize_text(name) == norm_title:
             # Use absolute path from root for the local server / website
             # Note: standard RSS readers need a full domain, but for internal use relative might work
             # or we rely on the implementation knowing how to handle it.
             # However, podcast-section.js renders it directly into <img src>.
             return f"/assets/images/episodes/{f}"
    return None

def main():
    print(f"Fetching RSS from {RSS_URL}...")
    with urllib.request.urlopen(RSS_URL) as resp:
        xml_data = resp.read()
    
    root = ET.fromstring(xml_data)
    image_files = list_image_files()
    
    channel = root.find("channel")
    if channel is None:
        print("Error: No channel element found")
        return

    print("Processing episodes...")
    count = 0
    for item in channel.findall("item"):
        title_el = item.find("title")
        if title_el is None or not title_el.text:
            continue

        raw_title = title_el.text.strip()
        name = strip_years(raw_title)
        local_image = find_image_for_title(name, image_files)
        
        if local_image:
            # Update itunes:image
            itunes_image = item.find("{http://www.itunes.com/dtds/podcast-1.0.dtd}image")
            if itunes_image is not None:
                itunes_image.set("href", local_image)
            else:
                # Create if missing (though typically anchor feeds have it)
                itunes_image = ET.SubElement(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}image")
                itunes_image.set("href", local_image)
            
            # Update media:content / media:thumbnail if present (Anchor usually uses itunes:image)
            # Actually, let's just ensure itunes:image is set efficiently.
            count += 1
    
    print(f"Updated images for {count} episodes.")
    
    with open(OUT_FEED, "wb") as f:
        f.write(ET.tostring(root, encoding="utf-8", xml_declaration=True))
    
    print(f"Saved updated feed to {OUT_FEED}")

if __name__ == "__main__":
    main()

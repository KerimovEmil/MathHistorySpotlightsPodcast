import os
import re
import urllib.request
import xml.etree.ElementTree as ET
import unicodedata
import json
import random

RSS_URL = "https://anchor.fm/s/10cdf4708/podcast/rss"
ROOT = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(ROOT, "assets", "images", "episodes")
OUT_DIR = os.path.join(ROOT, "mathematicians")
CSS_PATH = "../assets/css/mathematicians.css"
SITE_STYLE = "../assets/css/style.css"
COLLECTIONS_JSON = os.path.join(ROOT, "collections.json")
COLLECTIONS_PAGE = os.path.join(ROOT, "collections.html")
SEARCH_INDEX_FILE = os.path.join(ROOT, "search.json")
OVERRIDES_FILE = os.path.join(ROOT, "see_also_overrides.json")
EQUATIONS_FILE = os.path.join(ROOT, "famous_equations.json")


def normalize_text(s):
        s = s or ""
        s = unicodedata.normalize("NFKD", s)
        s = s.encode("ascii", "ignore").decode("ascii")
        s = s.lower()
        s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        return s


def load_see_also_overrides():
        """Loads see_also_overrides.json, returning a dict of slug -> [list of slugs]."""
        if not os.path.exists(OVERRIDES_FILE):
                return {}
        try:
                with open(OVERRIDES_FILE, "r", encoding="utf-8") as f:
                        return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
                print(f"Warning: Error loading {OVERRIDES_FILE}: {e}")
                return {}


def load_equations():
        """Loads famous_equations.json, returning a dict of slug -> {equation: str, label: str}."""
        if not os.path.exists(EQUATIONS_FILE):
                return {}
        try:
                with open(EQUATIONS_FILE, "r", encoding="utf-8") as f:
                        return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
                print(f"Warning: Error loading {EQUATIONS_FILE}: {e}")
                return {}


def sync_metadata_placeholders(all_slugs):
        """Ensures see_also_overrides.json and famous_equations.json have entries for all slugs."""
        # 1. Sync See Also Overrides
        overrides = load_see_also_overrides()
        changed_overrides = False
        for slug in all_slugs:
                if slug not in overrides:
                        overrides[slug] = []
                        changed_overrides = True
        
        if changed_overrides:
                with open(OVERRIDES_FILE, "w", encoding="utf-8") as f:
                        json.dump(overrides, f, indent=2, sort_keys=True)
                print(f"Updated {OVERRIDES_FILE} with missing placeholders.")

        # 2. Sync Famous Equations
        equations = load_equations()
        changed_equations = False
        for slug in all_slugs:
                if slug not in equations:
                        equations[slug] = []
                        changed_equations = True
        
        if changed_equations:
                # To maintain existing data, we only add missing ones.
                with open(EQUATIONS_FILE, "w", encoding="utf-8") as f:
                        json.dump(equations, f, indent=2, sort_keys=True)
                print(f"Updated {EQUATIONS_FILE} with missing placeholders.")


def load_collections_data():
        """Loads collections data from collections.json."""
        if not os.path.exists(COLLECTIONS_JSON):
             print(f"Warning: {COLLECTIONS_JSON} not found.")
             return []
        with open(COLLECTIONS_JSON, "r", encoding="utf-8") as f:
             return json.load(f)

def load_related_map(collections):
        """Returns a dictionary mapping slugs to a set of related slugs from the same collections."""
        related_map = {}
        for coll in collections:
             slugs = [m['slug'] for m in coll.get('mathematicians', [])]
             for s in slugs:
                  if s not in related_map:
                       related_map[s] = set()
                  for other in slugs:
                       if other != s:
                            related_map[s].add(other)
        return related_map


def build_collections_page(collections):
        """Generates collections.html from collections data."""
        toc_items = "\n".join([f'                            <li><a href="#{c["id"]}">{c["title"]}</a></li>' for c in collections])
        
        groups_html = []
        for i, c in enumerate(collections, 1):
            math_cards = []
            for m in c.get('mathematicians', []):
                math_cards.append(f'''
                        <a href="/mathematicians/{m['slug']}.html" class="math-card">
                            <div class="card-image-wrapper">
                                <img src="{m['image']}" alt="{m['name']}" loading="lazy">
                                <div class="card-overlay"></div>
                            </div>
                            <div class="card-content">
                                <h3 class="card-name">{m['name']}</h3>
                                <p class="card-role">{m['role']}</p>
                            </div>
                        </a>''')
            
            groups_html.append(f'''
                <!-- Collection {i}: {c['title']} -->
                <div class="collection-group" id="{c['id']}">
                    <div class="group-header">
                        <h2 class="group-title">{c['title']}</h2>
                        <span class="group-tag">{c['tag']}</span>
                    </div>
                    <p class="group-description">
                        {c['description']}
                    </p>

                    <div class="mathematician-grid">
                        {"".join(math_cards)}
                    </div>
                </div>''')

        html = f'''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Collections — Math History Spotlights</title>
    <meta name="description" content="Curated collections of mathematicians to listen to as a group.">

    <!-- favicon link -->
    <link rel="shortcut icon" href="./favicon.svg" type="image/svg+xml">

    <!-- custom css link -->
    <link rel="stylesheet" href="./assets/css/style.css">
    <link rel="stylesheet" href="./assets/css/collections.css">

    <!-- google font link -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@400;500;700&display=swap" rel="stylesheet">
</head>

<body id="top" class="no-intro">

    <!-- #HEADER -->
    <site-header></site-header>

    <main>
        <article class="container">

            <section class="collections">

                <div class="collections-header">
                    <h1 class="collections-title">Curated Collections</h1>
                    <p class="collections-subtitle">
                        Explore themed groups of mathematicians. Listen to their stories together to understand the deep
                        connections in mathematical history.
                    </p>

                    <nav class="toc-nav">
                        <ul>
{toc_items}
                        </ul>
                    </nav>
                </div>

                {"".join(groups_html)}

            </section>

        </article>
    </main>

    <!-- footer component -->
    <site-footer></site-footer>

    <!-- ionicon link -->
    <script type="module" src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.esm.js"></script>
    <script nomodule src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.js"></script>

    <!-- web components -->
    <script type="module" src="./assets/js/site-header.js"></script>
    <script type="module" src="./assets/js/site-footer.js"></script>

</body>

</html>
'''
        with open(COLLECTIONS_PAGE, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated {COLLECTIONS_PAGE}")


def extract_years(title):
        """Extracts birth and death years from title string, e.g. "Name 1643 - 1727" -> (1643, 1727)"""
        if not title:
                return None, None
        # Look for pattern like "1643 - 1727" or "1643-1727"
        m = re.search(r"(\d{3,4})\s*[\-–—]\s*(\d{3,4})", title)
        if m:
                return int(m.group(1)), int(m.group(2))
        return None, None


def strip_years(s):
        if not s:
                return s
        # remove trailing year ranges and stray digits/hyphens, e.g. " 1877 - 1947"
        return re.sub(r"[\s\d\-–—]+$", "", s).strip()


def extract_audio_url(item):
        # prefer <enclosure url="..."/>
        enc = item.find("enclosure")
        if enc is not None and enc.get("url"):
                return enc.get("url")
        # look for media:content or any child with url attribute
        for child in item:
                url = child.get("url")
                if url:
                        t = (child.get("type") or "").lower()
                        if "audio" in t or url.lower().endswith(('.mp3', '.m4a', '.ogg')):
                                return url
        return None


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
                               # use root-relative forward-slash path for web compatibility
                               return f"/assets/images/episodes/{f}"
        return None


def extract_source_link(description):
        if not description:
                return None
        m = re.search(r"Sources[:\s]*([\s\S]+)", description, re.IGNORECASE)
        target = description if not m else m.group(1)
        m2 = re.search(r"https?://[^\s'\"<]+", target)
        if m2:
                return m2.group(0)
        m3 = re.search(r'href=["\']([^"\']+)["\']', description)
        if m3:
                return m3.group(1)
        return None


def build_page(title, description, source_link, image_path, audio_url, out_path, related_pages=None, equation_data=None):
        audio_html = f'<audio controls src="{audio_url}">Your browser does not support the audio element.</audio>' if audio_url else ''
        
        see_also_html = ""
        if related_pages:
                items_html = ""
                for p in related_pages:
                        img_tag = f'<img src="{p["image"]}" alt="{p["title"]}" loading="lazy"/>' if p.get("image") else ''
                        items_html += f'<li><a href="{p["file"]}">{img_tag}<span>{p["title"]}</span></a></li>'
                see_also_html = f'''
                <div class="see-also" style="margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px;">
                        <h3 style="color:var(--accent); margin-bottom: 20px;">See Also</h3>
                        <ul class="grid" style="padding: 0; margin: 0; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); box-shadow: none; border: none; background: none;">
                                {items_html}
                        </ul>
                </div>
                '''

        equation_html = ""
        if equation_data:
                # If it's a single dict (old style), wrap it
                if isinstance(equation_data, dict):
                    equation_data = [equation_data]
                
                items = []
                for eq in equation_data:
                    if not eq.get("equation"): continue
                    
                    label = eq.get("label", "Famous Equation")
                    desc = f'<p style="margin: 5px 0 10px 0; opacity: 0.8; font-size: 0.9em;">{eq["description"]}</p>' if eq.get("description") else ""
                    
                    label_html = label
                    if eq.get("wikipedia"):
                         label_html = f'<a href="{eq["wikipedia"]}" target="_blank" style="color:inherit; text-decoration: none; border-bottom: 1px dotted rgba(255,255,255,0.2);">{label}</a>'
                    
                    items.append(f'''
                    <div class="equation-item" style="margin-bottom: 25px; text-align: center;">
                        <h3 style="color:var(--accent); margin: 0; font-size: 0.85em; text-transform: uppercase; letter-spacing: 1.2px; text-align: left;">
                            {label_html}
                        </h3>
                        {desc}
                        <div style="font-size: 1.3em; padding: 15px 0; overflow-x: auto; background: rgba(255,255,255,0.03); border-radius: 4px; margin-top: 10px;">
                            \\[ {eq["equation"]} \\]
                        </div>
                    </div>
                    ''')

                if items:
                    equation_html = f'''
                    <div class="equations-section" style="margin: 40px 0; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 30px;">
                        {"".join(items)}
                    </div>
                    '''

        # Prepare SEO meta description (strip HTML tags)
        meta_desc = re.sub(r'<[^>]+>', '', description or '').strip()
        if len(meta_desc) > 160:
            meta_desc = meta_desc[:157] + "..."
        
        # Open Graph image URL (absolute path would be better, but root-relative works for some crawlers)
        og_image = f"https://www.mathhistoryspotlights.com{image_path}" if image_path else ""

        html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title} - Math History Spotlights</title>
  <meta name="description" content="{meta_desc}" />
  <meta property="og:title" content="{title} - Math History Spotlights" />
  <meta property="og:description" content="{meta_desc}" />
  {f'<meta property="og:image" content="{og_image}" />' if og_image else ''}
  <meta property="og:type" content="article" />
  <link rel="shortcut icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{SITE_STYLE}">
  <link rel="stylesheet" href="{CSS_PATH}">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/photoswipe/5.3.8/photoswipe.min.css">
  <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body id="top">

                <site-header></site-header>

        <main class="card">
                <a class="back" href="/mathematicians/index.html">← Back to Mathematicians</a>
        <div class="media" id="gallery">
          {f'<img src="{image_path}" alt="{title}" class="hero-image"/>' if image_path else ''}
        </div>
        {audio_html}
        <h1 class="name">{title}</h1>
        <div class="desc">{description or ''}</div>
        {equation_html}
        <p class="sources">Sources: {f'<a href="{source_link}" target="_blank" rel="noopener">{source_link}</a>' if source_link else '—'}</p>
        {see_also_html}
  </main>

  <site-footer></site-footer>

  <script type="module" src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.esm.js"></script>
  <script nomodule src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.js"></script>
  <script type="module" src="../assets/js/site-header.js"></script>
  <script type="module" src="../assets/js/site-footer.js"></script>
  
  <script type="module">
    import PhotoSwipeLightbox from 'https://cdnjs.cloudflare.com/ajax/libs/photoswipe/5.3.8/photoswipe-lightbox.esm.min.js';
    import PhotoSwipe from 'https://cdnjs.cloudflare.com/ajax/libs/photoswipe/5.3.8/photoswipe.esm.min.js';

    const img = document.querySelector('.hero-image');
    if (img) {{
        const lightbox = new PhotoSwipeLightbox({{
            pswpModule: PhotoSwipe,
            dataSource: [
                {{
                    src: img.src,
                    w: img.naturalWidth || 1000,
                    h: img.naturalHeight || 1000,
                    alt: img.alt
                }}
            ]
        }});
        
        lightbox.init();
        
        img.onclick = () => {{
            // Updates dimensions just in case they weren't loaded at init
            lightbox.options.dataSource[0].w = img.naturalWidth;
            lightbox.options.dataSource[0].h = img.naturalHeight;
            lightbox.loadAndOpen(0);
        }};
        img.style.cursor = 'zoom-in';
    }}
  </script>
</body>
</html>
'''
        with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)


def build_index(pages, out_index):
        items = []
        for p in pages:
                items.append(f'<li><a href="{p["file"]}"><img src="{p.get("image","")}"/><span>{p["title"]}</span></a></li>')
        html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Mathematicians</title>
  <link rel="shortcut icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{SITE_STYLE}">
  <link rel="stylesheet" href="{CSS_PATH}">
</head>
<body id="top">

  <site-header></site-header>

  <div class="index-header">
        <h1>Mathematicians</h1>
        <p class="lead">Episodes and quick links to images and sources</p>
  </div>
  <ul class="grid">
        {"\n    ".join(items)}
  </ul>

  <site-footer></site-footer>

  <script type="module" src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.esm.js"></script>
  <script nomodule src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.js"></script>
  <script type="module" src="../assets/js/site-header.js"></script>
  <script type="module" src="../assets/js/site-footer.js"></script>
</body>
</html>
'''
        with open(out_index, "w", encoding="utf-8") as f:
                f.write(html)


OUT_FEED = os.path.join(ROOT, "assets", "feed.xml")

def main():
        os.makedirs(OUT_DIR, exist_ok=True)
        image_files = list_image_files()

        print(f"Reading RSS from {OUT_FEED}...")
        if os.path.exists(OUT_FEED):
             with open(OUT_FEED, "r", encoding="utf-8") as f:
                 xml = f.read()
        else:
             print("Local feed not found, fetching from remote...")
             with urllib.request.urlopen(RSS_URL) as resp:
                 xml = resp.read()
        
        root = ET.fromstring(xml)

        all_pages_data = []

        # Load manual See Also overrides
        see_also_overrides = load_see_also_overrides()

        # Parse collections for relationships
        collections = load_collections_data()
        collections_map = load_related_map(collections)
        build_collections_page(collections)

        for item in root.findall("./channel/item"):
                title_el = item.find("title")
                desc_el = item.find("description")
                raw_title = title_el.text.strip() if title_el is not None and title_el.text else "untitled"
                
                birth_year, death_year = extract_years(raw_title)

                # strip trailing years for display and matching
                name = strip_years(raw_title)
                desc = desc_el.text if desc_el is not None else ''
                # remove unlinked Sources section from description (keep content before Sources)
                desc_clean = re.split(r"\bSources[:\s]", desc, flags=re.IGNORECASE)[0].strip()
                source_link = extract_source_link(desc)
                image = find_image_for_title(name, image_files)
                slug = normalize_text(name)

                out_file = os.path.join(OUT_DIR, f"{slug}.html")
                page_rel = f"{slug}.html"
                audio_url = extract_audio_url(item)
                
                all_pages_data.append({
                    "title": name,
                    "description": desc_clean,
                    "source_link": source_link,
                    "image": image,
                    "audio_url": audio_url,
                    "out_file": out_file,
                    "file": page_rel,
                    "slug": slug,
                    "birth_year": birth_year
                })

        # Get all slugs for synchronization
        all_slugs = [p["slug"] for p in all_pages_data]
        sync_metadata_placeholders(all_slugs)
        
        # Reload metadata after synchronization
        see_also_overrides = load_see_also_overrides()
        famous_equations = load_equations()

        pages_for_index = []

        for page in all_pages_data:
                related = []

                # 0. Check for manual overrides
                if page["slug"] in see_also_overrides:
                        override_slugs = see_also_overrides[page["slug"]]
                        slug_to_page = {p["slug"]: p for p in all_pages_data}
                        related = [slug_to_page[s] for s in override_slugs if s in slug_to_page]
                else:
                        # 1. Prioritize Collection Peers
                        collection_peers_slugs = collections_map.get(page["slug"], set())
                        for other in all_pages_data:
                             if other["slug"] in collection_peers_slugs:
                                  related.append(other)
                        
                        # 2. Fill remaining slots with time-proximity peers
                        needed = 3 - len(related)
                        if needed > 0:
                                candidates = []
                                for other in all_pages_data:
                                        if other["slug"] == page["slug"]:
                                                continue
                                        if other in related:
                                                continue
                                        
                                        if page["birth_year"] and other["birth_year"]:
                                                diff = abs(other["birth_year"] - page["birth_year"])
                                                candidates.append((diff, other))
                                        else:
                                                candidates.append((9999, other))
                                
                                candidates.sort(key=lambda x: x[0])
                                # Add up to 'needed' more items
                                related.extend([c[1] for c in candidates[:needed]])

                build_page(
                        page["title"], 
                        page["description"], 
                        page["source_link"], 
                        page["image"], 
                        page["audio_url"], 
                        page["out_file"],
                        related_pages=related,
                        equation_data=famous_equations.get(page["slug"])
                )
                
                if page["slug"] != "renaissance-cubic-equation-wars":
                    pages_for_index.append({
                        "title": page["title"], 
                        "file": page["file"], 
                        "image": page["image"], 
                        "description": page["description"]
                    })

        build_index(pages_for_index, os.path.join(OUT_DIR, "index.html"))

        search_data = []
        for p in pages_for_index:
                # Strip HTML tags from description for search index
                clean_desc = re.sub(r'<[^>]+>', '', p["description"]).strip()
                search_data.append({
                        "title": p["title"],
                        "url": f"/mathematicians/{p['file']}",
                        "description": clean_desc,
                        "image": p["image"]
                })
    
        with open(os.path.join(ROOT, "assets", "search.json"), "w", encoding="utf-8") as f:
                json.dump(search_data, f, indent=2)



if __name__ == "__main__":
        main()

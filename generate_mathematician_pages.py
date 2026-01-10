import os
import re
import urllib.request
import xml.etree.ElementTree as ET
import unicodedata

RSS_URL = "https://anchor.fm/s/10cdf4708/podcast/rss"
ROOT = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(ROOT, "assets", "images", "episodes")
OUT_DIR = os.path.join(ROOT, "mathematicians")
CSS_PATH = "../assets/css/mathematicians.css"
SITE_STYLE = "../assets/css/style.css"


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


def build_page(title, description, source_link, image_path, audio_url, out_path):
        audio_html = f'<audio controls src="{audio_url}">Your browser does not support the audio element.</audio>' if audio_url else ''
        html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title}</title>
  <link rel="stylesheet" href="{SITE_STYLE}">
  <link rel="stylesheet" href="{CSS_PATH}">
</head>
<body id="top">

                <site-header></site-header>

        <main class="card">
                <a class="back" href="/index.html">← Back</a>
        <div class="media">
          {f'<img src="{image_path}" alt="{title}"/>' if image_path else ''}
        </div>
        {audio_html}
        <h1 class="name">{title}</h1>
        <div class="desc">{description or ''}</div>
        <p class="sources">Sources: {f'<a href="{source_link}" target="_blank" rel="noopener">{source_link}</a>' if source_link else '—'}</p>
  </main>

  <site-footer></site-footer>

  <script type="module" src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.esm.js"></script>
  <script nomodule src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.js"></script>
  <script type="module" src="../assets/js/site-header.js"></script>
  <script type="module" src="../assets/js/site-footer.js"></script>
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
  <link rel="stylesheet" href="{SITE_STYLE}">
  <link rel="stylesheet" href="{CSS_PATH}">
</head>
<body id="top">

  <site-header></site-header>

  <header class="index-header">
        <h1>Mathematicians</h1>
        <p class="lead">Episodes and quick links to images and sources</p>
  </header>
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


def main():
        os.makedirs(OUT_DIR, exist_ok=True)
        image_files = list_image_files()

        with urllib.request.urlopen(RSS_URL) as resp:
                xml = resp.read()
        root = ET.fromstring(xml)

        pages = []
        for item in root.findall("./channel/item"):
                title_el = item.find("title")
                desc_el = item.find("description")
                raw_title = title_el.text.strip() if title_el is not None and title_el.text else "untitled"
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
                build_page(name, desc_clean, source_link, image, audio_url, out_file)
                pages.append({"title": name, "file": page_rel, "image": image})

        build_index(pages, os.path.join(OUT_DIR, "index.html"))


if __name__ == "__main__":
        main()

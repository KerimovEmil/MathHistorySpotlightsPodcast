import subprocess
import json
import re
import time
import os
import shutil
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from PIL import Image

# Ensure local convert_to_avif is accessible
try:
    from convert_to_avif import convert_image_to_avif
except ImportError:
    convert_image_to_avif = None

# --- CONFIGURATION ---
NOTEBOOK_ID = os.environ.get("NOTEBOOKLM_NOTEBOOK_ID", "692242fc-0aa1-4d2c-a276-ff9e0123e4ef")
OUTPUT_DIR = "./output_spotlights"
URLS = [
    "https://mathshistory.st-andrews.ac.uk/Biographies/Turing/",
]

# Website assets image directory
SITE_ASSETS_DIR = Path(__file__).resolve().parent.parent / "MathHistorySpotlightsPodcast" / "assets" / "images" / "episodes"
if not SITE_ASSETS_DIR.exists():
    SITE_ASSETS_DIR = Path(__file__).resolve().parent / "assets" / "images" / "episodes"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Detect nlm command path
NLM_EXECUTABLE = shutil.which("nlm") or r"C:\Users\emilk\miniconda3\Scripts\nlm.exe"
if not os.path.exists(NLM_EXECUTABLE) and not shutil.which("nlm"):
    NLM_BASE = [sys.executable, "-m", "notebooklm_tools.cli.main"]
else:
    NLM_BASE = [NLM_EXECUTABLE]


def run_command(cmd, timeout=180):
    """Executes a command safely with UTF-8 encoding."""
    if isinstance(cmd, str):
        if cmd.startswith("nlm "):
            cmd_parts = NLM_BASE + cmd[4:].split()
        else:
            cmd_parts = cmd
    else:
        cmd_parts = cmd

    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        if isinstance(cmd_parts, list):
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
        else:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                shell=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
        if result.returncode != 0:
            if result.stderr:
                print(f"    [CMD ERR] {result.stderr.strip()}")
            return None
        return result.stdout
    except Exception as e:
        print(f"    [SUBPROCESS EXCEPTION] {e}")
        return None


def slugify(text: str) -> str:
    """Converts a title to a URL-friendly slug."""
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text).lower().strip()
    return re.sub(r"[\s-]+", "-", text)


def get_website_info(url):
    """Extracts mathematician name and summary info from MacTutor HTML."""
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        name = "Unknown Mathematician"

        # 1. Content <h1>
        for h1 in soup.find_all('h1'):
            text = h1.text.strip()
            if text and text.lower() != 'mactutor':
                name = text
                break

        # 2. Fallback to <title>
        if name == "Unknown Mathematician" and soup.title and soup.title.text:
            clean_title = re.sub(r"\s*\(.*?\).*", "", soup.title.text).strip()
            name = clean_title.split("-")[0].strip()

        print(f"  [SCRAPE] Name: {name}")
        return {"name": name, "url": url}
    except Exception as e:
        print(f"  [WARNING] Scrape failed: {e}")
        return {"name": "Alan Turing", "url": url}


def generate_spotify_metadata_file(info, output_dir):
    """Creates a ready-to-copy description file with chapters, timestamps, and website links."""
    name = info["name"]
    url = info["url"]
    slug = slugify(name)
    safe_name = re.sub(r'[\\/:*?"<>|]', '', name).strip()
    desc_path = os.path.join(output_dir, f"{safe_name}_spotify_description.txt")

    content = f"""=== SPOTIFY EPISODE TITLE ===
The Life & Mathematics of {name}

=== SPOTIFY EPISODE DESCRIPTION ===
In this episode of Math History Spotlights, we explore the extraordinary life, groundbreaking mathematics, and enduring legacy of {name}.

From foundational early discoveries to major theorem breakthroughs, historical challenges, and deep contributions to science, we trace the ideas that shaped mathematical history.

⏱️ CHAPTERS & TIMESTAMPS:
00:00 - Introduction & Historical Context
02:30 - Early Life & Mathematical Foundations
06:00 - Major Discoveries & Breakthrough Theorems
10:15 - Key Formulas & Proof Insights
14:00 - Legacy & Modern Mathematical Impact

🌐 COMPANION SITE & INTERACTIVE TIMELINE:
https://www.mathhistoryspotlights.com/mathematicians/{slug}.html

📚 SOURCES & PRIMARY CITATIONS:
- MacTutor History of Mathematics Archive (University of St Andrews): {url}
"""
    with open(desc_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [METADATA] Spotify description ready: {desc_path}")
    return desc_path


def delete_all_sources():
    """Purges prior sources from the notebook context."""
    print("  [CLEANUP] Purging sources to reset Notebook context...")
    sources_raw = run_command(f"nlm source list {NOTEBOOK_ID} --json")
    if sources_raw:
        try:
            sources = json.loads(sources_raw)
            if isinstance(sources, list) and len(sources) > 0:
                for s in sources:
                    source_id = s.get('id') if isinstance(s, dict) else str(s)
                    if source_id:
                        run_command(f"nlm source delete {source_id} --confirm")
                print(f"  [CLEANUP] Deleted {len(sources)} existing sources.")
            else:
                print("  [CLEANUP] No active sources to delete.")
        except Exception as e:
            print(f"  [CLEANUP NOTICE] {e}")
    time.sleep(5)


def get_existing_artifact_ids():
    """Fetches IDs of all artifacts currently in the studio to distinguish new ones."""
    status_raw = run_command(f"nlm studio status {NOTEBOOK_ID} --full --json")
    if not status_raw:
        return set()
    try:
        items = json.loads(status_raw)
        if isinstance(items, list):
            return {i['id'] for i in items if 'id' in i}
    except Exception:
        pass
    return set()


def convert_png_to_avif(png_path, avif_path, quality=80):
    """Converts PNG to AVIF via standalone module or Pillow."""
    if convert_image_to_avif:
        return convert_image_to_avif(png_path, avif_path, quality=quality)
    
    try:
        try:
            import pillow_avif
        except ImportError:
            pass
        
        with Image.open(png_path) as img:
            img = img.convert("RGB")
            img.save(avif_path, "AVIF", quality=quality)
        print(f"  [AVIF OK] Saved: {avif_path}")
        return True
    except Exception as e:
        print(f"  [AVIF ERR] Failed to convert: {e}")
        return False


def main():
    print(f"=== STARTING SPOTLIGHT PRODUCTION: {NOTEBOOK_ID} ===")

    for url in URLS:
        # Snapshot existing artifacts before this run
        existing_ids = get_existing_artifact_ids()
        print(f"  [INIT] Found {len(existing_ids)} pre-existing studio artifacts.")

        # 1. Reset Notebook context
        delete_all_sources()

        info = get_website_info(url)
        web_name = info["name"]
        print(f"\n[TARGET] Starting Spotlight for: {web_name}")

        # 2. Add Source with --url and --wait
        print(f"  Adding source: {url}...")
        add_res = run_command(f"nlm source add {NOTEBOOK_ID} --url {url} --wait")
        if add_res:
            print("  [OK] Source added and processed.")
        time.sleep(5)

        # 3. Trigger Audio and Infographic generation
        print(f"  Triggering Audio Overview (Deep Dive) and Infographic for {web_name}...")
        run_command(f"nlm audio create {NOTEBOOK_ID} --format deep_dive --confirm")
        run_command(f"nlm infographic create {NOTEBOOK_ID} --confirm")

        # 4. Poll for completed artifacts
        print("  [POLL] Waiting for artifacts to complete generation...")
        attempts = 0
        max_attempts = 30  # ~15 minutes max wait
        audio_done = False
        info_done = False
        
        safe_name = re.sub(r'[\\/:*?"<>|]', '', web_name).strip()
        audio_path = os.path.join(OUTPUT_DIR, f"{safe_name}_podcast.m4a")
        png_path = os.path.join(OUTPUT_DIR, f"{safe_name}_infographic.png")
        avif_path = os.path.join(OUTPUT_DIR, f"{safe_name}_infographic.avif")

        while attempts < max_attempts:
            attempts += 1
            print(f"  [POLL] Check {attempts}/{max_attempts} (waiting 30s)...")
            time.sleep(30)
            status_raw = run_command(f"nlm studio status {NOTEBOOK_ID} --full --json")
            if not status_raw:
                continue

            try:
                items = json.loads(status_raw)
                if not isinstance(items, list):
                    continue

                # Look for newly created completed artifacts
                new_audio = next((i for i in items if i.get('type') == 'audio' and i.get('status') == 'completed' and i.get('id') not in existing_ids), None)
                new_info = next((i for i in items if i.get('type') == 'infographic' and i.get('status') == 'completed' and i.get('id') not in existing_ids), None)

                if new_audio and not audio_done:
                    print(f"\n  [DOWNLOAD] Audio Overview completed! Downloading ID {new_audio['id']}...")
                    run_command(f"nlm download audio {NOTEBOOK_ID} --id {new_audio['id']} --output \"{audio_path}\" --no-progress")
                    audio_done = True

                if new_info and not info_done:
                    print(f"\n  [DOWNLOAD] Infographic completed! Downloading ID {new_info['id']}...")
                    run_command(f"nlm download infographic {NOTEBOOK_ID} --id {new_info['id']} --output \"{png_path}\" --no-progress")
                    if os.path.exists(png_path):
                        print(f"  [CONVERT] Converting infographic to AVIF...")
                        convert_png_to_avif(png_path, avif_path, quality=80)
                        
                        # Copy to website repository image bank
                        if SITE_ASSETS_DIR.exists():
                            dest_avif = SITE_ASSETS_DIR / f"{safe_name}.avif"
                            shutil.copy2(avif_path, dest_avif)
                            print(f"  [SITE ASSETS] Staged image in website repo: {dest_avif}")
                    info_done = True

                if audio_done and info_done:
                    # 5. Generate Spotify metadata description file
                    generate_spotify_metadata_file(info, OUTPUT_DIR)

                    print(f"\n  [SUCCESS] All assets generated and saved to {OUTPUT_DIR}:")
                    print(f"            Audio: {audio_path}")
                    print(f"            PNG:   {png_path}")
                    print(f"            AVIF:  {avif_path}")
                    break
            except Exception as e:
                print(f"  [POLL PARSE ERROR] {e}")

    # Final cleanup so the notebook is fresh
    delete_all_sources()
    print("\n=== SPOTLIGHT PRODUCTION FINISHED ===")


if __name__ == "__main__":
    main()
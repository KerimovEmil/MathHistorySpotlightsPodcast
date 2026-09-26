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


def load_env_var(var_name: str, default: str = None) -> str:
    """
    Loads an environment variable from system environment or a local .env file.
    Never falls back to hardcoded secret IDs.
    """
    # 1. System environment
    val = os.environ.get(var_name)
    if val:
        return val.strip()

    # 2. Local .env file in script dir or current working dir
    for env_path in [Path(".env"), Path(__file__).resolve().parent / ".env"]:
        if env_path.exists():
            try:
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() == var_name:
                            return v.strip().strip("'\"")
            except Exception:
                pass

    return default


# --- CONFIGURATION ---
NOTEBOOK_ID = load_env_var("NOTEBOOKLM_NOTEBOOK_ID")
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
    """
    Extracts the exact full mathematician name and birth-death years from MacTutor HTML.
    Raises RuntimeError on failure rather than returning dummy fallbacks.
    """
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"HTTP request failed for URL '{url}': {e}")

    soup = BeautifulSoup(response.text, 'html.parser')
    full_name = None
    years = ""

    # 1. Exact Full Name from content <h1> (skipping site branding 'MacTutor')
    for h1 in soup.find_all('h1'):
        text = h1.text.strip()
        if text and text.lower() != 'mactutor':
            full_name = text
            break

    # 2. Extract Birth & Death Years from <title> tag (e.g. '(1912 - 1954)')
    if soup.title and soup.title.text:
        title_text = soup.title.text
        match = re.search(r"\((\d{3,4}\s*[-–—]\s*\d{3,4}|\d{3,4}\s*[-–—]\s*present|\d{3,4})\)", title_text)
        if match:
            years = match.group(1).replace("–", "-").replace("—", "-")
            years = re.sub(r"\s*-\s*", " - ", years).strip()

        # Fallback for full name if h1 was not found
        if not full_name:
            clean_title = re.sub(r"\s*\(.*?\).*", "", title_text).strip()
            clean_title = clean_title.split("-")[0].strip()
            if clean_title:
                full_name = clean_title

    # Fail explicitly if name could not be resolved
    if not full_name:
        raise RuntimeError(f"Could not extract mathematician name from page: {url}")

    # Format Spotify Episode Title: <FULL NAME> <BIRTH YEAR - DEATH YEAR>
    spotify_title = f"{full_name} {years}".strip() if years else full_name

    print(f"  [SCRAPE] Full Name: {full_name}")
    print(f"  [SCRAPE] Years:     {years}")
    print(f"  [SCRAPE] Ep Title:  {spotify_title}")

    return {
        "name": full_name,
        "years": years,
        "spotify_title": spotify_title,
        "url": url,
    }


def generate_spotify_metadata_file(info, output_dir):
    """Creates a clean, emoji-free description file with chapters, timestamps, and sources."""
    name = info["name"]
    spotify_title = info["spotify_title"]
    url = info["url"]
    desc_path = os.path.join(output_dir, f"{name}_spotify_description.txt")

    content = f"""=== SPOTIFY EPISODE TITLE ===
{spotify_title}

=== SPOTIFY EPISODE DESCRIPTION ===
In this episode of Math History Spotlights, we explore the life, mathematical breakthroughs, and enduring legacy of {name}.

From foundational early discoveries to major theorem breakthroughs, historical challenges, and deep contributions to science, we trace the ideas that shaped mathematical history.

CHAPTERS & TIMESTAMPS:
00:00 - Introduction & Historical Context
02:30 - Early Life & Mathematical Foundations
06:00 - Major Discoveries & Breakthrough Theorems
10:15 - Key Formulas & Proof Insights
14:00 - Legacy & Modern Mathematical Impact

SOURCES:
- MacTutor History of Mathematics Archive (University of St Andrews): {url}
"""
    with open(desc_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [METADATA] Spotify description ready (no emojis): {desc_path}")
    return desc_path


def delete_all_sources(notebook_id):
    """Purges prior sources from the notebook context."""
    print("  [CLEANUP] Purging sources to reset Notebook context...")
    sources_raw = run_command(f"nlm source list {notebook_id} --json")
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


def get_existing_artifact_ids(notebook_id):
    """Fetches IDs of all artifacts currently in the studio to distinguish new ones."""
    status_raw = run_command(f"nlm studio status {notebook_id} --full --json")
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
    if not NOTEBOOK_ID:
        print("\n[ERROR] NOTEBOOKLM_NOTEBOOK_ID is not set.")
        print("Please set NOTEBOOKLM_NOTEBOOK_ID in your environment variables or in a local .env file.")
        sys.exit(1)

    print(f"=== STARTING SPOTLIGHT PRODUCTION ===")
    print(f"Target Notebook ID: {NOTEBOOK_ID[:8]}...{NOTEBOOK_ID[-4:] if len(NOTEBOOK_ID) > 12 else ''}")

    for url in URLS:
        # Snapshot existing artifacts before this run
        existing_ids = get_existing_artifact_ids(NOTEBOOK_ID)
        print(f"  [INIT] Found {len(existing_ids)} pre-existing studio artifacts.")

        # 1. Reset Notebook context
        delete_all_sources(NOTEBOOK_ID)

        info = get_website_info(url)
        full_name = info["name"]
        print(f"\n[TARGET] Starting Spotlight for: {full_name}")

        # 2. Add Source with --url and --wait
        print(f"  Adding source: {url}...")
        add_res = run_command(f"nlm source add {NOTEBOOK_ID} --url {url} --wait")
        if add_res:
            print("  [OK] Source added and processed.")
        time.sleep(5)

        # 3. Trigger Audio and Infographic generation
        print(f"  Triggering Audio Overview (Deep Dive) and Infographic for {full_name}...")
        run_command(f"nlm audio create {NOTEBOOK_ID} --format deep_dive --confirm")
        run_command(f"nlm infographic create {NOTEBOOK_ID} --confirm")

        # 4. Poll for completed artifacts
        print("  [POLL] Waiting for artifacts to complete generation...")
        attempts = 0
        max_attempts = 30  # ~15 minutes max wait
        audio_done = False
        info_done = False
        
        # Files are named with the EXACT FULL NAME of the mathematician
        audio_path = os.path.join(OUTPUT_DIR, f"{full_name}_podcast.m4a")
        png_path = os.path.join(OUTPUT_DIR, f"{full_name}.png")
        avif_path = os.path.join(OUTPUT_DIR, f"{full_name}.avif")

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
                        
                        # Copy to website repository image bank with exact full name
                        if SITE_ASSETS_DIR.exists():
                            dest_avif = SITE_ASSETS_DIR / f"{full_name}.avif"
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
    delete_all_sources(NOTEBOOK_ID)
    print("\n=== SPOTLIGHT PRODUCTION FINISHED ===")


if __name__ == "__main__":
    main()
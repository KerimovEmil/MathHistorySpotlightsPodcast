import subprocess
import json
import re
import time
import os
import shutil
import sys
import requests
from bs4 import BeautifulSoup
from PIL import Image

# Ensure local convert_to_avif is accessible
try:
    from convert_to_avif import convert_image_to_avif
except ImportError:
    convert_image_to_avif = None

# --- CONFIGURATION ---
NOTEBOOK_ID = "692242fc-0aa1-4d2c-a276-ff9e0123e4ef"
OUTPUT_DIR = "./output_spotlights"
URLS = [
    "https://mathshistory.st-andrews.ac.uk/Biographies/Turing/",
]

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
        # On Windows, enforce utf-8 environment
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


def get_website_title(url):
    """Extracts mathematician name reliably from MacTutor HTML."""
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Look for content <h1> that is not the site branding 'MacTutor'
        for h1 in soup.find_all('h1'):
            text = h1.text.strip()
            if text and text.lower() != 'mactutor':
                print(f"  [SCRAPE] Extracted Name from <h1>: {text}")
                return text

        # 2. Fallback: Parse <title> tag
        if soup.title and soup.title.text:
            clean_title = re.sub(r"\s*\(.*?\).*", "", soup.title.text).strip()
            clean_title = clean_title.split("-")[0].strip()
            if clean_title:
                print(f"  [SCRAPE] Extracted Name from <title>: {clean_title}")
                return clean_title

        # 3. Fallback to URL slug
        fallback_name = url.rstrip('/').split('/')[-1].replace('-', ' ')
        return fallback_name
    except Exception as e:
        print(f"  [WARNING] Scrape failed: {e}")
        return "Alan Turing"


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

        web_name = get_website_title(url)
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
                    info_done = True

                if audio_done and info_done:
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
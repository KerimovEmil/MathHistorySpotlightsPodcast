# Math History Spotlights — Master Episode Creation & Automation Guide

This document is the **single source of truth** for creating and publishing new episodes of the **Math History Spotlights** podcast and companion website.

> **Instruction for AI Assistants**: When the user asks to *"make an episode about [Mathematician Name] [URL]"*, follow the automated execution steps below sequentially.

---

## High-Level Pipeline Overview

```
 [0. Git Pull Repo] ──▶ [1. Run create_podcast_episodes.py] ──▶ [2. Present Spotify Details] ──▶ [3. User Publishes] ──▶ [4. update_website.py]
  • Ensures latest        • Cleans Notebook context               • Copy title & desc             • User uploads audio     • Pulls Anchor RSS
    code & website          • Ingests source with --wait            • Link audio & artwork          • User moves .m4a        • Builds HTML bio page
    are in sync             • Generates audio (deep dive)                                             to private server      • Syncs search & graph
                            • Generates infographic                                                                          • Deploys to GitHub
                            • Converts to .avif & stages to repo
                            • Syncs .avif to Google Drive
```

---

## Detailed Step-by-Step Instructions

### Step 0: Pull Latest Repository Version (Always First)
Before doing any operations or generating new episodes, ensure the Git repository is up-to-date:
```powershell
git -C "C:\Users\emilk\GIT\MathHistorySpotlightsPodcast" pull
```

---

### Step 1: Execution of `create_podcast_episodes.py`

When a new mathematician URL is provided (e.g., `https://mathshistory.st-andrews.ac.uk/Biographies/Turing/`):

1. **Run the Script from the Staging Folder**:
   Execute the script from `C:\Users\emilk\GIT\llm\math podcast` so that newly generated audio and staging files stay isolated in the local staging directory:
   ```powershell
   # Working Directory: C:\Users\emilk\GIT\llm\math podcast
   python "C:\Users\emilk\GIT\MathHistorySpotlightsPodcast\create_podcast_episodes.py" "<MacTutor_URL>"
   ```
   *(Multiple URLs can also be passed separated by spaces).*

2. **What the script automatically performs**:
   - **Extracts metadata**: Scrapes the **exact full name** (e.g. `Alan Mathison Turing`) and **birth-death years** (e.g. `1912 - 1954`).
   - **NotebookLM Ingestion**: Purges prior sources (`nlm source delete <id> --confirm`) and adds the new URL (`nlm source add <notebook_id> --url <url> --wait`).
   - **Generation**: Triggers `nlm audio create <notebook_id> --format deep_dive --confirm` and `nlm infographic create <notebook_id> --confirm`.
   - **Polling & Safe Download**: Polls `nlm studio status --full --json` and downloads artifacts with `--no-progress` to prevent Windows encoding errors.
   - **Naming Standard**: Saves all files under the exact full name:
     - `output_spotlights/<Full Name>_podcast.m4a`
     - `output_spotlights/<Full Name>.png`
     - `output_spotlights/<Full Name>.avif`
     - `output_spotlights/<Full Name>_spotify_description.txt`
   - **Auto-Staging**: 
     - Copies `<Full Name>.avif` directly into `C:\Users\emilk\GIT\MathHistorySpotlightsPodcast\assets\images\episodes\<Full Name>.avif`.
     - Automatically mirrors `<Full Name>.avif` to `G:\My Drive\MathHistory\Visuals\<Full Name>.avif` if Google Drive is available.
   - **Clean Metadata Generation**: Writes an emoji-free Spotify description with clean chapter markers and citations.

---

### Step 2: Present Generated Assets & Spotify Instructions to User

Once Step 1 completes, present the user with:
1. Clickable links to:
   - Audio file (`.m4a` in `output_spotlights/`)
   - Infographic artwork (`.png` / `.avif`)
   - Description text (`.txt`)
2. The exact text to copy into the **Spotify for Creators** dashboard:
   - **Episode Title Format**: `<FULL NAME> <BIRTH YEAR> - <DEATH YEAR>` (e.g. `Alan Mathison Turing 1912 - 1954`)
   - **Description**: Clean, professional plaintext with chapters, timestamps, and sources (NO emojis, NO redundant companion site links).
3. A reminder that the `.m4a` audio file is ready in `C:\Users\emilk\GIT\llm\math podcast\output_spotlights\` for manual transfer to the private server.

---

### Step 3: User Publishes on Spotify for Creators
The user uploads the audio + artwork, pastes the title & description, and clicks **Publish** on [Spotify for Creators](https://podcasters.spotify.com/).

---

### Step 4: Website Sync & Deployment

Once the episode is published and propagated to the public Anchor RSS feed (`https://anchor.fm/s/10cdf4708/podcast/rss`):

1. **Run the Master Update Script**:
   ```powershell
   python "C:\Users\emilk\GIT\MathHistorySpotlightsPodcast\update_website.py"
   ```
2. **What this script performs**:
   - Fetches the latest RSS feed from Anchor.
   - Updates `assets/feed.xml` with local `.avif` image mapping.
   - Generates the dedicated HTML biography page in `mathematicians/<slug>.html`.
   - Strips any unwanted website references from the rendered HTML bio.
   - Rebuilds `search.json` and `collections.html`.
   - Commits and pushes the updates live to GitHub Pages.

---

## Key Maintenance Rules & Conventions

1. **Naming Standard**:
   - Image files in `assets/images/episodes/` **must** match the exact full name of the mathematician (e.g., `Alan Mathison Turing.avif`).
   - Spotify episode titles **must** follow the format: `<FULL NAME> <BIRTH YEAR> - <DEATH YEAR>`.
2. **No AI-Fluff / No Emojis**:
   - Spotify descriptions must be clean plaintext without emojis (`⏱️`, `🌐`, `📚`, etc.).
3. **No Redundant Companion Links in Web Bio**:
   - `generate_mathematician_pages.py` automatically strips any companion website mentions so they do not show up inside the website itself.
4. **NotebookLM CLI Requirements**:
   - If authentication expires, run `python -m notebooklm_tools.cli.main login` or `C:\Users\emilk\miniconda3\Scripts\nlm.exe login`.

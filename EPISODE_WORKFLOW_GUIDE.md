# Math History Spotlights — Master Episode Creation & Automation Guide

This document is the **single source of truth** for creating and publishing new episodes of the **Math History Spotlights** podcast and companion website.

> **Instruction for AI Assistants**: When the user asks to *"make an episode about [Mathematician Name] [URL]"*, follow the automated execution steps below sequentially.

---

## High-Level Pipeline Overview

```
 [1. URL / Subject Provided] ──▶ [2. create_podcast_episodes.py] ──▶ [3. User Publishes on Spotify] ──▶ [4. update_website.py]
                                  • Cleans Notebook context          • Copies audio & artwork              • Pulls Anchor RSS
                                  • Ingests source with --wait       • Pastes title & description          • Builds HTML bio page
                                  • Generates audio (deep dive)                                            • Syncs equations & search
                                  • Generates infographic                                                  • Deploys to GitHub
                                  • Converts to .avif
                                  • Stages image to repo
                                  • Outputs clean description
```

---

## Detailed Step-by-Step Instructions

### Step 1: Execution of `create_podcast_episodes.py`

When a new mathematician URL is provided (e.g., `https://mathshistory.st-andrews.ac.uk/Biographies/Turing/`):

1. **Verify / Set URL in `create_podcast_episodes.py`**:
   Ensure `URLS` contains the target MacTutor link (or pass via command line if parameterized).

2. **Run the Episode Generator Script**:
   ```bash
   python create_podcast_episodes.py
   ```

3. **What the script automatically performs**:
   - **Extracts metadata**: Scrapes the **exact full name** (e.g. `Alan Mathison Turing`) and **birth-death years** (e.g. `1912 - 1954`).
   - **NotebookLM Ingestion**: Purges prior sources (`nlm source delete <id> --confirm`) and adds the new URL (`nlm source add <notebook_id> --url <url> --wait`).
   - **Generation**: Triggers `nlm audio create <notebook_id> --format deep_dive --confirm` and `nlm infographic create <notebook_id> --confirm`.
   - **Polling & Safe Download**: Polls `nlm studio status --full --json` and downloads artifacts with `--no-progress` to prevent Windows charmap encoding errors.
   - **Naming Standard**: Saves all files under the exact full name:
     - `output_spotlights/<Full Name>_podcast.m4a`
     - `output_spotlights/<Full Name>.png`
     - `output_spotlights/<Full Name>.avif`
     - `output_spotlights/<Full Name>_spotify_description.txt`
   - **Auto-Staging**: Copies `<Full Name>.avif` directly into `assets/images/episodes/<Full Name>.avif`.
   - **Clean Metadata Generation**: Writes an emoji-free Spotify description with clean chapter markers and citations.

---

### Step 2: Present Generated Assets & Spotify Instructions to User

Once Step 1 completes, present the user with:
1. Clickable links to:
   - Audio file (`.m4a`)
   - Infographic artwork (`.png` / `.avif`)
   - Description text (`.txt`)
2. The exact text to copy into the **Spotify for Creators** dashboard:
   - **Episode Title Format**: `<FULL NAME> <BIRTH YEAR> - <DEATH YEAR>` (e.g. `Alan Mathison Turing 1912 - 1954`)
   - **Description**: Clean, professional plaintext with chapters, timestamps, and sources (NO emojis, NO redundant companion site links).

---

### Step 3: User Publishes on Spotify for Creators
The user uploads the audio + artwork, pastes the title & description, and clicks **Publish** on [Spotify for Creators](https://podcasters.spotify.com/).

---

### Step 4: Website Sync & Deployment

Once the episode is published and propagated to the public Anchor RSS feed (`https://anchor.fm/s/10cdf4708/podcast/rss`):

1. **Run the Master Update Script**:
   ```bash
   python update_website.py
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

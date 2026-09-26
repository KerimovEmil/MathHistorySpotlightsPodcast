# Math History Spotlights — Full Episode Creation Workflow

This document outlines the complete lifecycle for researching, generating, packaging, and publishing a new episode of the **Math History Spotlights** podcast and its companion website.

---

```
                                 [ Episode Lifecycle ]
                                           │
  1. Research & Staging                    ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ • Curate MacTutor biographies, papers, original proofs, and notes     │
  │ • Stage URLs, text files, and high-res diagram assets                  │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
  2. Pipeline Automation              ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ • Run create_podcast_episodes.py                                       │
  │ • Ingest sources into Google NotebookLM                                │
  │ • Generate & poll NotebookLM Audio Overview (Deep Dive)                │
  │ • Download final episode audio (.mp3)                                  │
  │ • Convert & optimize diagrams/artwork to modern .avif with Pillow      │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
  3. Spotify Packaging & Publishing   ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ • Formulate summary, bio, proof citations, and companion site links    │
  │ • Add timestamps / chapter markers in Spotify for Creators             │
  │ • Publish episode & artwork to Spotify/Anchor RSS feed                 │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
  4. Companion Site Deployment        ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ • Run python update_website.py                                         │
  │ • Pull updated RSS feed, generate mathematician HTML page,             │
  │   sync equations & search index, and deploy to GitHub Pages            │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Source Research & Material Preparation

1. **Curate Sources**:
   - Deep-dive biographical and mathematical sources (e.g., [MacTutor History of Mathematics Archive](https://mathshistory.st-andrews.ac.uk/), primary historical papers, original theorem proofs).
2. **Stage Research Assets**:
   - Collect source URLs and clean text/PDF notes into an episode staging folder (e.g., `staging/<mathematician-slug>/`).
   - Gather or create high-resolution diagram/cover-art files (`.png`).

---

## 2. Pipeline Script (`create_podcast_episodes.py`)

Run the automation script to handle Google NotebookLM ingestion, audio generation, and web asset optimization:

```bash
python create_podcast_episodes.py --name "John Wallis" \
  --urls "https://mathshistory.st-andrews.ac.uk/Biographies/Wallis/" \
  --sources "staging/john_wallis/notes.txt" \
  --image "staging/john_wallis/portrait.png"
```

### Script Responsibilities:
* **CLI Wrapper / Automation:**
  * Uses Python / `notebooklm-mcp-cli` tools to interface with NotebookLM.
  * Creates or selects a dedicated episode notebook:
    ```bash
    notebooklm create --title "Math History Spotlights - [Mathematician Name]"
    ```
* **Source Ingestion:**
  * Iterates over curated URLs and local research text files.
  * Adds sources sequentially:
    ```bash
    notebooklm source add --notebook-id <ID> --url <URL>
    notebooklm source add --notebook-id <ID> --file <PATH>
    ```
* **Audio Overview Generation:**
  * Triggers NotebookLM's Audio Overview (Deep Dive) generation.
  * Polls generation status until complete, then downloads/exports the final audio file (`.mp3`).
* **Visual Asset Conversion (Pillow + AVIF):**
  * Reads newly created high-resolution diagram/cover-art files (`.png`/`.jpg`).
  * Optimizes and converts images to modern web format (`.avif`):
    * Compresses file size while maintaining diagram and portrait fidelity.
    * Saves converted `.avif` files directly into [`assets/images/episodes/`](assets/images/episodes/).
* **Output Staging:**
  * Organizes exported audio, converted `.avif` visuals, and markdown drafts into the staging directory.

---

## 3. Spotify Packaging & Publishing

* **Metadata & Description:**
  * Formulate episode summary, mathematician bio, and citations back to original papers.
  * Include a link to the companion site entry on `https://www.mathhistoryspotlights.com/mathematicians/<slug>.html`.
* **Chapters & Timestamps:**
  * Format clickable timestamps in the description:
    ```text
    00:00 - Introduction & Historical Context
    03:45 - Early Life & Education
    12:10 - Core Theorem & Historical Proof
    22:30 - Legacy & Modern Impact
    ```
* **Distribution:**
  * Upload final audio overview and episode artwork to the **Spotify for Creators** dashboard.
  * Set release date/time and publish.
  * Publishing automatically updates the public Anchor RSS feed: `https://anchor.fm/s/10cdf4708/podcast/rss`.

---

## 4. Companion Website Updates (GitHub Pages)

* **Repository:** `KerimovEmil/MathHistorySpotlightsPodcast`
* **Live Site:** [https://www.mathhistoryspotlights.com/](https://www.mathhistoryspotlights.com/)
* **Steps:**
  1. Once the episode is published on Spotify/Anchor, run:
     ```bash
     python update_website.py
     ```
  2. The automated script will:
     - Fetch the latest podcast RSS feed and update [`assets/feed.xml`](assets/feed.xml).
     - Generate new mathematician biography pages in [`mathematicians/`](mathematicians/).
     - Update [`search.json`](search.json), [`famous_equations.json`](famous_equations.json), and [`see_also_overrides.json`](see_also_overrides.json).
     - Commit and push changes directly to GitHub Pages (`main` branch).

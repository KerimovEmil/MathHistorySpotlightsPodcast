# Math History Spotlights — Podcast Website

This repository is the source code for the [Math History Spotlights](https://www.mathhistoryspotlights.com/) website. It features a dynamically updated podcast player, an image gallery, and dedicated biography pages for each mathematician, all powered by the podcast's RSS feed.

## Features

- **Automated Content Generation**: The website content (episodes, biography pages, gallery) is generated automatically from the podcast RSS feed.
- **Enhanced Visuals**: Matches podcast episodes with high-quality local images stored in the repository.
- **Search**: Fully functional client-side search for mathematicians.
- **Responsive Design**: Fast, accessible, and mobile-friendly design using standard Web Components.

## Project Structure

- `index.html`: The homepage featuring the podcast player.
- `gallery.html`: A lightbox gallery of all mathematician portraits.
- `timeline.html`: A timeline view of the mathematicians.
- `mathematicians/`: Generated individual pages for each mathematician.
- `assets/`: Contains styles, scripts, and the image bank (`assets/images/episodes`).
- `generate_*.py`: Python scripts used for building the site.

## How to Update the Website

When you publish a new episode on Anchor/Spotify, follow these steps to update the website:

1. **Add the Image**:
   - Save the portrait of the mathematician in `assets/images/episodes/`.
   - Ensure the filename roughly matches the episode title (e.g., for "The life of John Wallis", name the file `John Wallis.avif` or `.jpg`).

2. **Run the Update Script**:
   open a terminal in the project root and run:
   ```bash
   python update_website.py
   ```
   
   This master script automates the entire process:
   - **Fetches** the latest RSS feed from Anchor.
   - **Updates** `assets/feed.xml` to link episodes with your high-quality local images.
   - **Generates** new HTML pages for any new mathematicians.
   - **Rebuilds** the search index (`assets/search.json`).
   - **Deploys** the changes by running `git add`, `git commit`, and `git push` automatically.

## Local Development

To preview changes locally:

1. Run the local server:
   ```bash
   python -m http.server 8000
   ```
2. Open [http://localhost:8000](http://localhost:8000) in your browser.

## Scripts Overview

- `update_website.py`: The master script that orchestrates the update and deployment.
- `generate_updated_rss.py`: Fetches the external RSS feed and creates a local version (`assets/feed.xml`) with corrected image paths.
- `generate_mathematician_pages.py`: Parses the local RSS feed to generate static HTML pages for each episode and the search index.

## Credits

- **Podcast Host**: Emil Kerimov
- **Content**: Resources from St Andrews Biographies and Google Notebook LLM.
- **Design**: Custom CSS/JS implementation.

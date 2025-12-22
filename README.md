# Math History Spotlights — Podcast Website

This repository is the static homepage for the "Math History Spotlights" podcast. The site lists episodes with playable audio and episode thumbnails.

## Local preview
Serve the project folder and open the site in your browser:

PowerShell (repo root):

```powershell
python -m http.server 8000
# then open http://localhost:8000/index.html
```

## Deployment
- The project is currently hosted on GitHub Pages at https://kerimovemil.github.io/MathHistorySpotlightsPodcast/
- To publish updates: commit and push to the `master` branch.

## Update episodes
- Episodes are currently embedded in `index.html` using the RSS enclosure audio URLs and local thumbnails in `assets/images/`.
- To keep content in sync with Anchor, consider adding a small client-side script to fetch and render the RSS feed dynamically (requires a CORS proxy or a server-side fetch).

## Notes
- CSS is in `assets/css/style.css`.
- Images are in `assets/images/`.

---

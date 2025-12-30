class PodcastSection extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    this.src = this.getAttribute('src');
    this.innerHTML = '<ul class="podcast-list"><li class="loading">Loading episodes...</li></ul>';
    this.list = this.querySelector('.podcast-list');
    if (!this.src) {
      this.showError('No RSS src provided');
      return;
    }
    this.fetchFeed();
  }

  async fetchFeed() {
    try {
      const res = await fetch(this.src);
      if (!res.ok) throw new Error('Network response was not ok');
      const text = await res.text();
      const parser = new DOMParser();
      const xml = parser.parseFromString(text, 'application/xml');
      const items = Array.from(xml.querySelectorAll('item'));
      if (!items.length) {
        this.showError('No episodes found in feed');
        return;
      }

      this.list.innerHTML = '';

      items.forEach((item) => {
        const title = (item.querySelector('title')?.textContent || '').trim();
        const pubDate = item.querySelector('pubDate')?.textContent || '';
        const dateISO = pubDate ? new Date(pubDate).toISOString() : '';
        const displayDate = pubDate
          ? new Date(pubDate).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
          : '';
        const itunesDurationEl = item.getElementsByTagName('itunes:duration')[0];
        const durationEl = itunesDurationEl || item.getElementsByTagName('duration')[0];
        const duration = durationEl ? durationEl.textContent : '';

        const enclosure = item.querySelector('enclosure')?.getAttribute('url') || item.querySelector('link')?.textContent || '';

        const itunesImageEl = item.getElementsByTagName('itunes:image')[0];
        const mediaThumbEl = item.getElementsByTagName('media:thumbnail')[0];
        let image = (itunesImageEl && itunesImageEl.getAttribute('href'))
          || (mediaThumbEl && mediaThumbEl.getAttribute('url'))
          || xml.querySelector('channel > image > url')?.textContent
          || './assets/images/math_history_logo.png';

        const alt = title || 'Episode';
        const epiLabel = this.extractEpisodeLabel(item) || '';

        const li = document.createElement('li');
        const article = document.createElement('article');
        article.className = 'podcast-card';

        article.innerHTML = `
          <figure class="card-banner">
            <img src="${image}" alt="${this.escapeHtml(alt)}">
          </figure>
          <div class="card-content">
            <div class="card-meta">
              <time datetime="${dateISO}">${displayDate}</time>
              <p class="pod-epi">${epiLabel}${duration ? ' • ' + duration : ''}</p>
            </div>
            <h3 class="h3 card-title">${this.escapeHtml(title)}</h3>
            ${enclosure ? `<audio controls preload="none" src="${enclosure}"></audio>` : ''}
          </div>
        `;

        const img = article.querySelector('img');
        img.addEventListener('error', () => { img.src = './assets/images/math_history_logo.png'; });

        li.appendChild(article);
        this.list.appendChild(li);
      });
    } catch (err) {
      this.showError(err.message || 'Failed to load feed');
    }
  }

  extractEpisodeLabel(item) {
    const title = item.querySelector('title')?.textContent || '';
    const m = title.match(/Episode\s*(\d+)/i);
    if (m) return 'Episode ' + m[1];
    const itEpEl = item.getElementsByTagName('itunes:episode')[0];
    const itEp = itEpEl ? itEpEl.textContent : null;
    if (itEp) return 'Episode ' + itEp;
    return '';
  }

  showError(msg) {
    this.innerHTML = `<div class="podcast-error">Failed to load episodes: ${this.escapeHtml(msg)}</div>`;
  }

  escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"})[c]);
  }
}

customElements.define('podcast-section', PodcastSection);

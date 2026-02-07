class SiteHeader extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
<style>
  .search-modal {
    position: fixed;
    inset: 0;
    background: hsla(0, 0%, 0%, 0.6);
    z-index: 20;
    opacity: 0;
    pointer-events: none;
    transition: 0.25s ease;
    display: flex;
    justify-content: center;
    align-items: start;
    padding-top: 120px;
    backdrop-filter: blur(5px);
  }
  .search-modal.active {
    opacity: 1;
    pointer-events: all;
  }
  .search-inner {
    background: var(--russian-violet);
    width: 90%;
    max-width: 600px;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    transform: translateY(-20px);
    transition: 0.25s ease;
    border: 1px solid hsla(0, 0%, 100%, 0.1);
  }
  .search-modal.active .search-inner {
    transform: translateY(0);
  }
  .search-input-wrapper {
    position: relative;
    margin-bottom: 20px;
    border-bottom: 1px solid hsla(0, 0%, 100%, 0.1);
  }
  .search-input {
    width: 100%;
    background: transparent;
    border: none;
    color: var(--white);
    font-size: 1.2rem;
    padding: 10px 40px 10px 0;
    outline: none;
    font-family: var(--ff-josefin);
  }
  .search-input::placeholder {
    color: hsla(0, 0%, 100%, 0.4);
  }
  .search-close-btn {
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    color: var(--white);
    font-size: 24px;
    cursor: pointer;
  }
  .search-results {
    max-height: 50vh;
    overflow-y: auto;
    padding-right: 5px;
  }
  .search-results::-webkit-scrollbar {
    width: 5px;
  }
  .search-results::-webkit-scrollbar-thumb {
    background: hsla(0, 0%, 100%, 0.2);
    border-radius: 5px;
  }
  .search-result-item {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 12px;
    border-radius: 8px;
    transition: 0.2s;
    text-decoration: none !important;
  }
  .search-result-item:hover {
    background: hsla(0, 0%, 100%, 0.08);
  }
  .search-result-img {
    width: 50px;
    height: 50px;
    object-fit: cover;
    border-radius: 6px;
    flex-shrink: 0;
    background: #333;
  }
  .search-result-info {
    flex: 1;
    min-width: 0;
  }
  .search-result-info h3 {
    font-size: 1rem;
    color: var(--white);
    margin-bottom: 4px;
    font-weight: 500;
  }
  .search-result-info p {
    font-size: 0.85rem;
    color: var(--heliotrope-gray);
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin: 0;
  }
  .no-results {
    text-align: center;
    color: var(--heliotrope-gray);
    padding: 20px 0;
  }
</style>
<header class="active" data-header>
  <div class="container">
    <div class="overlay" data-overlay></div>

    <a href="/index.html" class="logo">
      <img src="${location.origin}/assets/images/logo.svg" alt="Micro logo">
    </a>

    <button class="nav-toggle-btn" data-nav-toggle-btn>
      <ion-icon name="menu-outline"></ion-icon>
    </button>

    <nav class="navbar" data-navbar>
      <ul class="navbar-list">
        <li class="navbar-item"><a href="/index.html" class="navbar-link">Home</a></li>
        <li class="navbar-item"><a href="/timeline.html" class="navbar-link">Timeline</a></li>
        <li class="navbar-item"><a href="/index.html#podcast" class="navbar-link">Podcast</a></li>
        <li class="navbar-item"><a href="/collections.html" class="navbar-link">Collections</a></li>
        <li class="navbar-item"><a href="/gallery.html" class="navbar-link">Gallery</a></li>
        <li class="navbar-item"><a href="/mathematicians/index.html" class="navbar-link">Mathematicians</a></li>
        <li class="navbar-item"><a href="/about.html" class="navbar-link">About</a></li>
      </ul>

      <div class="navbar-actions">
        <button class="navbar-btn" data-search-trigger title="Search">
          <ion-icon name="search-outline"></ion-icon>
        </button>
      </div>
    </nav>
  </div>
</header>

<div class="search-modal" data-search-modal>
  <div class="search-inner">
    <div class="search-input-wrapper">
       <input type="text" class="search-input" data-search-input placeholder="Search mathematicians...">
       <button class="search-close-btn" data-search-close-btn>
         <ion-icon name="close-outline"></ion-icon>
       </button>
    </div>
    <div class="search-results" data-search-results></div>
  </div>
</div>
`;
    // Existing link fixups
    try {
      const logoImg = this.querySelector('.logo img');
      if (logoImg) logoImg.src = location.origin + '/assets/images/logo.svg';

      const navLinks = this.querySelectorAll('.navbar-link');
      const currentPath = window.location.pathname;
      navLinks.forEach((a) => {
        let h = a.getAttribute('href') || '#';
        if (!h.startsWith('http') && !h.startsWith('/')) {
            h = '/' + h;
            a.setAttribute('href', h);
        }
        if (h === currentPath || (h === '/index.html' && currentPath === '/')) {
            a.classList.add('active');
        }
      });
    } catch (e) { }

    // Header logic
    const elemToggleFunc = (elem) => elem.classList.toggle("active");
    const navbar = this.querySelector("[data-navbar]");
    const navToggleBtn = this.querySelector("[data-nav-toggle-btn]");
    const overlay = this.querySelector("[data-overlay]");

    if (navToggleBtn && overlay && navbar) {
      this._navClickHandler = function () {
        elemToggleFunc(navbar);
        elemToggleFunc(overlay);
      };
      navToggleBtn.addEventListener("click", this._navClickHandler);
      overlay.addEventListener("click", this._navClickHandler);
    }

    const header = this.querySelector("[data-header]") || this;
    let lastScrollPosition = 0;
    this._onScroll = () => {
      const scrollPosition = window.pageYOffset;
      if (scrollPosition > lastScrollPosition) {
        header.classList.remove("active");
      } else {
        header.classList.add("active");
      }
      lastScrollPosition = scrollPosition <= 0 ? 0 : scrollPosition;
    };
    window.addEventListener("scroll", this._onScroll);

    // SEARCH LOGIC
    this.initSearch();
  }

  initSearch() {
    const searchModal = this.querySelector("[data-search-modal]");
    const searchTrigger = this.querySelector("[data-search-trigger]");
    const closeBtn = this.querySelector("[data-search-close-btn]");
    const input = this.querySelector("[data-search-input]");
    const resultsContainer = this.querySelector("[data-search-results]");

    let searchIndex = [];

    const openSearch = async () => {
      searchModal.classList.add("active");
      input.focus();
      if (searchIndex.length === 0) {
        try {
          const res = await fetch('/assets/search.json');
          if (res.ok) searchIndex = await res.json();
        } catch (err) {
          console.error("Failed to load search index", err);
        }
      }
    };

    const closeSearch = () => {
      searchModal.classList.remove("active");
      input.value = "";
      resultsContainer.innerHTML = "";
    };

    if (searchTrigger) searchTrigger.addEventListener("click", openSearch);
    if (closeBtn) closeBtn.addEventListener("click", closeSearch);

    // Close on click outside
    searchModal.addEventListener("click", (e) => {
      if (e.target === searchModal) closeSearch();
    });

    // Filtering
    input.addEventListener("input", (e) => {
      const term = e.target.value.toLowerCase().trim();
      if (!term) {
        resultsContainer.innerHTML = "";
        return;
      }

      const results = searchIndex.filter(item => {
        return (item.title && item.title.toLowerCase().includes(term)) ||
          (item.description && item.description.toLowerCase().includes(term));
      });

      this.renderResults(results, resultsContainer);
    });
  }

  renderResults(results, container) {
    if (results.length === 0) {
      container.innerHTML = '<div class="no-results">No results found</div>';
      return;
    }

    container.innerHTML = results.map(item => `
        <a href="${item.url}" class="search-result-item">
          ${item.image ? `<img src="${item.image}" class="search-result-img" alt="${item.title}">` : ''}
          <div class="search-result-info">
             <h3>${item.title}</h3>
             <p>${item.description || ''}</p>
          </div>
        </a>
      `).join('');
  }

  disconnectedCallback() {
    const navToggleBtn = this.querySelector("[data-nav-toggle-btn]");
    const overlay = this.querySelector("[data-overlay]");
    if (navToggleBtn && this._navClickHandler) navToggleBtn.removeEventListener("click", this._navClickHandler);
    if (overlay && this._navClickHandler) overlay.removeEventListener("click", this._navClickHandler);
    if (this._onScroll) window.removeEventListener("scroll", this._onScroll);
  }
}

customElements.define('site-header', SiteHeader);

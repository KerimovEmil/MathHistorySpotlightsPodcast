class SiteHeader extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
<header class="active" data-header>
  <div class="container">

    <!-- 
      - overlay
    -->
    <div class="overlay" data-overlay></div>

    <a href="/index.html" class="logo">
      <img src="${location.origin}/assets/images/logo.svg" alt="Micro logo">
    </a>

    <button class="nav-toggle-btn" data-nav-toggle-btn>
      <ion-icon name="menu-outline"></ion-icon>
    </button>

    <nav class="navbar" data-navbar>
      <ul class="navbar-list">

        <li class="navbar-item">
          <a href="/index.html#hero" class="navbar-link">Home</a>
        </li>

        <li class="navbar-item">
          <a href="/index.html#podcast" class="navbar-link">Podcast</a>
        </li>

        <li class="navbar-item">
          <a href="/about.html" class="navbar-link">About</a>
        </li>

        <li class="navbar-item">
          <a href="/gallery.html" class="navbar-link">Gallery</a>
        </li>

        <li class="navbar-item">
          <a href="/timeline.html" class="navbar-link">Timeline</a>
        </li>

        <li class="navbar-item">
          <a href="/mathematicians/index.html" class="navbar-link">Mathematicians</a>
        </li>

      </ul>


      <div class="navbar-actions">

        <button class="navbar-btn" title="Search">
          <ion-icon name="search-outline"></ion-icon>
        </button>

      </div>
    </nav>

  </div>
</header>
`;
    // Ensure key asset/link URLs are absolute to avoid relative-path duplication
    try {
      const logoImg = this.querySelector('.logo img');
      if (logoImg) logoImg.src = location.origin + '/assets/images/logo.svg';

      const navLinks = this.querySelectorAll('.navbar-link');
      navLinks.forEach((a) => {
        const h = a.getAttribute('href') || '';
        if (!h.startsWith('http') && !h.startsWith('/')) {
          a.setAttribute('href', '/' + h);
        }
      });
    } catch (e) {
      // ignore
    }
    // header / navbar behavior moved into component
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

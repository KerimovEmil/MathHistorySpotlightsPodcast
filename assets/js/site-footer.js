class SiteFooter extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
<footer>
    <div class="footer-bottom">
      <div class="container">
        <p class="copyright">
          &copy; Template from 2022 <a href="#">codewithsadee</a>. All Rights Reserved
        </p>
        <p class="footer-actions">
            <a href="#top" class="go-top" data-go-top title="Go to top">
                <ion-icon name="chevron-up-outline"></ion-icon>
            </a>
        </p>
      </div>
    </div>
     
  </footer>
`;


   

    const goTop = this.querySelector('[data-go-top]');
    this._goTopHandler = (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    if (goTop) {
      // Toggle visibility using the existing CSS (.go-top.active)
      const onScroll = () => {
        const sc = window.pageYOffset || document.documentElement.scrollTop;
        if (sc > 0) goTop.classList.add('active');
        else goTop.classList.remove('active');
      };

      // initial state
      onScroll();

      window.addEventListener('scroll', onScroll);
      this._goTopScrollHandler = onScroll;

      goTop.addEventListener('click', this._goTopHandler);
    }
  }

  disconnectedCallback() {
    const goTop = this.querySelector('[data-go-top]');
    if (goTop && this._goTopHandler) goTop.removeEventListener('click', this._goTopHandler);
    if (this._goTopScrollHandler) window.removeEventListener('scroll', this._goTopScrollHandler);
  }
}

customElements.define('site-footer', SiteFooter);

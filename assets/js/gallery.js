// Gallery implementation using PhotoSwipe

document.addEventListener('DOMContentLoaded', () => {
  const galleryGrid = document.getElementById('gallery-grid');
  const feedUrl = '/assets/feed.xml';

  // Fetch the RSS feed
  fetch(feedUrl)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.text();
    })
    .then(str => new DOMParser().parseFromString(str, "text/xml"))
    .then(data => {
      loadGalleryFromFeed(data);
    })
    .catch(error => {
      console.error('Error loading gallery feed:', error);
      galleryGrid.innerHTML = '<p class="error-msg">Sorry, the gallery could not be loaded.</p>';
    });

  function loadGalleryFromFeed(xml) {
    const items = Array.from(xml.querySelectorAll("item"));
    if (!items.length) {
      galleryGrid.innerHTML = '<p>No images found in feed.</p>';
      return;
    }

    const processedImages = new Set();
    const galleryItems = [];

    items.forEach((item, index) => {
      // Extract image
      const itunesImage = item.getElementsByTagName("itunes:image")[0];
      const mediaThumb = item.getElementsByTagName("media:thumbnail")[0];
      const imgUrl = (itunesImage && itunesImage.getAttribute("href")) ||
        (mediaThumb && mediaThumb.getAttribute("url"));

      if (imgUrl && !processedImages.has(imgUrl)) {
        processedImages.add(imgUrl);

        const title = item.querySelector("title")?.textContent || "Untitled";

        const itemDiv = document.createElement('div');
        itemDiv.className = 'gallery-item';

        const img = document.createElement('img');
        img.src = imgUrl; // The feed.xml contains relative local paths now
        img.alt = title;
        img.loading = "lazy";

        const figure = document.createElement('figure');
        figure.appendChild(img);
        itemDiv.appendChild(figure);
        galleryGrid.appendChild(itemDiv);

        // Add to lightbox list
        galleryItems.push({
          src: imgUrl,
          title: title,
          element: img
        });

        // Click handler
        img.addEventListener('click', (e) => {
          e.preventDefault();
          // Find the current index in the filtered list
          const idx = galleryItems.findIndex(i => i.src === imgUrl);
          openPhotoSwipe(galleryItems, idx);
        });
      }
    });

    if (galleryItems.length === 0) {
      galleryGrid.innerHTML = '<p>No images found.</p>';
    }
  }

  function openPhotoSwipe(items, startIndex) {
    const dataSource = items.map(i => ({
      src: i.src,
      w: i.element.naturalWidth || 1000,
      h: i.element.naturalHeight || 750,
      alt: i.title
    }));

    const options = {
      dataSource: dataSource,
      pswpModule: window.PhotoSwipe
    };

    const lightbox = new window.PhotoSwipeLightbox(options);
    lightbox.init();
    lightbox.loadAndOpen(startIndex);
  }
});
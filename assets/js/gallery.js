// Gallery implementation using PhotoSwipe

document.addEventListener('DOMContentLoaded', () => {
  const galleryGrid = document.getElementById('gallery-grid');
  const imageListUrl = './assets/images/episodes/image-list.json';
  const imageFolder = './assets/images/episodes/';

  // Fetch the list of images
  fetch(imageListUrl)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(images => {
      loadGallery(images);
    })
    .catch(error => {
      console.error('Error loading gallery manifest:', error);
      galleryGrid.innerHTML = '<p class="error-msg">Sorry, the gallery could not be loaded.</p>';
    });

  function loadGallery(images) {
    if (!images || images.length === 0) {
      galleryGrid.innerHTML = '<p>No images found.</p>';
      return;
    }

    const items = [];

    images.forEach((filename, index) => {
      // Create HTML structure
      const validFilename = filename; // Assuming filename is safe or sanitized

      const itemDiv = document.createElement('div');
      itemDiv.className = 'gallery-item';

      const img = document.createElement('img');
      img.src = `${imageFolder}${validFilename}`;
      img.alt = validFilename.replace(/\.[^/.]+$/, ""); // Remove extension for alt text
      img.loading = "lazy"; // Native lazy loading

      // We wrap the image in a figure for semantic correctness and PhotoSwipe usage potentially
      const figure = document.createElement('figure');
      figure.appendChild(img);
      itemDiv.appendChild(figure);
      galleryGrid.appendChild(itemDiv);

      // Add click event to open lightbox
      img.addEventListener('click', (e) => {
        e.preventDefault();
        openPhotoSwipe(index);
      });
    });
  }

  function openPhotoSwipe(startIndex) {
    const domImages = document.querySelectorAll('.gallery-item img');

    // Create the items array for PhotoSwipe
    // We must read current dimensions from the loaded images
    const items = Array.from(domImages).map(img => {
      return {
        src: img.src,
        w: img.naturalWidth || 1000,
        h: img.naturalHeight || 750,
        alt: img.alt
      };
    });

    const options = {
      dataSource: items,
      pswpModule: window.PhotoSwipe
    };

    const lightbox = new window.PhotoSwipeLightbox(options);

    lightbox.init();
    lightbox.loadAndOpen(startIndex); // Correctly triggers the opening at the specific index
  }
});
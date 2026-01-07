document.addEventListener('DOMContentLoaded', () => {
  const galleryGrid = document.querySelector('.gallery-grid');
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightbox-img');
  const closeBtn = document.querySelector('.close-btn');
  const prevBtn = document.querySelector('.prev-btn');
  const nextBtn = document.querySelector('.next-btn');

  let galleryItems;
  let currentImageIndex;

  function initializeGallery() {
    galleryItems = document.querySelectorAll('.gallery-item img');
    galleryItems.forEach((item, index) => {
      item.addEventListener('click', () => {
        lightbox.style.display = 'block';
        lightboxImg.src = item.src;
        currentImageIndex = index;
      });
    });
  }

  fetch('./assets/images/episodes/image-list.json')
    .then(response => response.json())
    .then(images => {
      images.forEach(imageFile => {
        const galleryItem = document.createElement('div');
        galleryItem.className = 'gallery-item';

        const img = document.createElement('img');
        img.src = `./assets/images/episodes/${imageFile}`;
        img.alt = imageFile.split('.').slice(0, -1).join('.');

        galleryItem.appendChild(img);
        galleryGrid.appendChild(galleryItem);
      });
      initializeGallery();
    })
    .catch(error => console.error('Error fetching gallery images:', error));

  closeBtn.addEventListener('click', () => {
    lightbox.style.display = 'none';
  });

  function showImage(index) {
    if (index >= galleryItems.length) {
      currentImageIndex = 0;
    } else if (index < 0) {
      currentImageIndex = galleryItems.length - 1;
    } else {
      currentImageIndex = index;
    }
    lightboxImg.src = galleryItems[currentImageIndex].src;
  }

  prevBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    showImage(currentImageIndex - 1);
  });

  nextBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    showImage(currentImageIndex + 1);
  });

  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) {
      lightbox.style.display = 'none';
    }
  });
});
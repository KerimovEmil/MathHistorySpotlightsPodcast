document.addEventListener('DOMContentLoaded', () => {
  const galleryItems = document.querySelectorAll('.gallery-item img');
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightbox-img');
  const closeBtn = document.querySelector('.close-btn');
  const prevBtn = document.querySelector('.prev-btn');
  const nextBtn = document.querySelector('.next-btn');

  let currentImageIndex;

  galleryItems.forEach((item, index) => {
    item.addEventListener('click', () => {
      lightbox.style.display = 'block';
      lightboxImg.src = item.src;
      currentImageIndex = index;
    });
  });

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

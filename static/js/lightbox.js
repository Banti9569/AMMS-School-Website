/**
 * Al Majid Mission School - Gallery Lightbox
 */

document.addEventListener('DOMContentLoaded', () => {
  const galleryCards = document.querySelectorAll('.gallery-card');
  const modal = document.getElementById('lightboxModal');
  if (!modal || galleryCards.length === 0) return;

  const modalImg = modal.querySelector('.lightbox-img');
  const modalCaption = modal.querySelector('.lightbox-caption');
  const closeBtn = modal.querySelector('.lightbox-close');
  const prevBtn = modal.querySelector('.lightbox-prev');
  const nextBtn = modal.querySelector('.lightbox-next');

  let items = [];
  galleryCards.forEach((card, idx) => {
    const img = card.querySelector('img');
    const title = card.querySelector('.gallery-title')?.textContent || '';
    const caption = card.getAttribute('data-caption') || title;
    const src = card.getAttribute('data-full-img') || img?.src || '';
    items.push({ src, caption, alt: img?.alt || title });

    card.addEventListener('click', () => {
      openLightbox(idx);
    });
  });

  let currentIdx = 0;

  function openLightbox(idx) {
    currentIdx = idx;
    updateLightbox();
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }

  function updateLightbox() {
    if (items[currentIdx]) {
      modalImg.src = items[currentIdx].src;
      modalImg.alt = items[currentIdx].alt;
      modalCaption.textContent = items[currentIdx].caption;
    }
  }

  function nextItem() {
    currentIdx = (currentIdx + 1) % items.length;
    updateLightbox();
  }

  function prevItem() {
    currentIdx = (currentIdx - 1 + items.length) % items.length;
    updateLightbox();
  }

  if (closeBtn) closeBtn.addEventListener('click', closeLightbox);
  if (nextBtn) nextBtn.addEventListener('click', nextItem);
  if (prevBtn) prevBtn.addEventListener('click', prevItem);

  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeLightbox();
  });

  document.addEventListener('keydown', (e) => {
    if (!modal.classList.contains('active')) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowRight') nextItem();
    if (e.key === 'ArrowLeft') prevItem();
  });
});

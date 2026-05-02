document.addEventListener('DOMContentLoaded', () => {

    // 1. File Preview on Upload Page
    const imageUpload = document.getElementById('imageUpload');
    const imagePreview = document.getElementById('imagePreview');
    const dropZone = document.getElementById('dropZone');
    const uploadIconContainer = document.getElementById('uploadIconContainer');
    const submitBtn = document.getElementById('submitBtn');
    
    if (imageUpload && imagePreview) {
        imageUpload.addEventListener('change', function(e) {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.classList.remove('hidden');
                    if(uploadIconContainer) uploadIconContainer.classList.add('hidden');
                    if(dropZone) dropZone.classList.add('active');
                    if(submitBtn) {
                        submitBtn.removeAttribute('disabled');
                    }
                }
                reader.readAsDataURL(file);
            } else {
                if(submitBtn) submitBtn.setAttribute('disabled', 'true');
            }
        });
    }

    // 2. Confidence Bar Animation on Result Page
    const confidenceBar = document.getElementById('confidenceBar');
    if (confidenceBar) {
        const targetWidth = confidenceBar.getAttribute('data-width');
        setTimeout(() => {
            confidenceBar.style.width = targetWidth + '%';
        }, 300);
    }
});

document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const filter = btn.dataset.filter;
    document.querySelectorAll('.history-card').forEach(card => {
      if (filter === 'all' || card.dataset.result === filter) {
        card.style.display = 'flex';
        card.style.animation = 'none'; // reset animation
        card.offsetHeight; // trigger reflow
        card.style.animation = 'fadeIn 0.3s ease forwards';
      } else {
        card.style.display = 'none';
      }
    });
  });
});

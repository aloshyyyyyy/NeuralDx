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

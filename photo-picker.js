/*
Copyright 2026 NorCalRobotics
Unmodified use and code review only. No AI/ML training or redistribution rights.
*/
const photoPicker = document.getElementById('photo-picker');
const thumbnailsContainer = document.getElementById('thumbnails-container');
const photoCount = document.getElementById('photo-count');

photoPicker.addEventListener('change', function(event) {
    const files = event.target.files;
    thumbnailsContainer.innerHTML = ''; // Clear existing thumbnails
    
    if (files.length === 0) {
        photoCount.textContent = '';
        return;
    }

    photoCount.textContent = `${files.length} photo(s) selected`;

    // Create thumbnails for each selected file
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Only process image files
        if (!file.type.startsWith('image/')) {
            continue;
        }

        const reader = new FileReader();
        
        reader.onload = function(e) {
            const thumbnailItem = document.createElement('div');
            thumbnailItem.className = 'thumbnail-item';
            
            const img = document.createElement('img');
            img.src = e.target.result;
            
            const label = document.createElement('div');
            label.className = 'thumbnail-label';
            label.textContent = file.name;
            
            thumbnailItem.appendChild(img);
            thumbnailItem.appendChild(label);
            thumbnailsContainer.appendChild(thumbnailItem);
        };
        
        reader.readAsDataURL(file);
    }
});

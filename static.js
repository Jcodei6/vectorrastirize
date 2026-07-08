const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const form = document.getElementById('vectorForm');
const loading = document.getElementById('loading');
const resultArea = document.getElementById('resultArea');
const downloadBtn = document.getElementById('downloadBtn');

// Trigger file selector when clicking the drop zone
dropZone.addEventListener('click', () => fileInput.click());

// Drag and drop styling
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#4CAF50';
});
dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = '#ccc';
});

// Handle file drop
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#ccc';
    if (e.dataTransfer.files.length > 0) {
        processImage(e.dataTransfer.files[0]);
    }
});

// Handle manual file selection
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        processImage(e.target.files[0]);
    }
});

function processImage(file) {
    // Show loading state
    dropZone.classList.add('hidden');
    resultArea.classList.add('hidden');
    loading.classList.remove('hidden');

    // Build the data payload (Image + Sliders)
    const formData = new FormData(form);
    formData.append('image', file);

    // Send to Python backend
    fetch('/vectorize', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        loading.classList.add('hidden');
        if (data.success) {
            // Show the download button and attach the SVG URL
            downloadBtn.href = data.svg_url;
            resultArea.classList.remove('hidden');
        } else {
            alert('Error: ' + data.error);
            dropZone.classList.remove('hidden');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        loading.classList.add('hidden');
        dropZone.classList.remove('hidden');
        alert('Upload failed.');
    });
}

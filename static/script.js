const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const loading = document.getElementById('loading');
const resultZone = document.getElementById('result-zone');
const svgContainer = document.getElementById('svg-container');
const downloadBtn = document.getElementById('download-btn');

// Update the visual numbers on the sliders in real-time
document.getElementById('corner_threshold').addEventListener('input', (e) => document.getElementById('corner_val').innerText = e.target.value);
document.getElementById('filter_speckle').addEventListener('input', (e) => document.getElementById('speckle_val').innerText = e.target.value);

// Drag and drop mechanics
dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('click', () => fileInput.click()); // Clicking the box opens file explorer
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if(e.dataTransfer.files.length) {
        processFile(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if(e.target.files.length) {
        processFile(e.target.files[0]);
    }
});

async function processFile(file) {
    // Validate file type
    if (!file.type.match('image.*')) {
        alert('Please upload a valid raster image (PNG, JPG, WebP).');
        return;
    }

    // Package the file and the slider settings to send to Python
    const formData = new FormData();
    formData.append('image', file);
    formData.append('color_mode', document.getElementById('color_mode').value);
    formData.append('corner_threshold', document.getElementById('corner_threshold').value);
    formData.append('filter_speckle', document.getElementById('filter_speckle').value);

    // Switch UI to loading state
    dropZone.classList.add('hidden');
    resultZone.classList.add('hidden');
    loading.classList.remove('hidden');

    try {
        // Send request to Flask app.py backend
        const response = await fetch('/vectorize', { method: 'POST', body: formData });
        
        if (!response.ok) throw new Error('Server processing error');

        const svgText = await response.text();
        
        // Display the SVG code on the screen
        svgContainer.innerHTML = svgText;
        
        // Setup the download button logic
        const blob = new Blob([svgText], {type: 'image/svg+xml'});
        const url = URL.createObjectURL(blob);
        downloadBtn.onclick = () => {
            const a = document.createElement('a');
            a.href = url;
            a.download = file.name.split('.')[0] + '_clean.svg';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        };

        // Switch UI to results state
        loading.classList.add('hidden');
        resultZone.classList.remove('hidden');
        dropZone.classList.remove('hidden'); 

    } catch (error) {
        alert('An error occurred during vectorization. Check the console.');
        console.error(error);
        loading.classList.add('hidden');
        dropZone.classList.remove('hidden');
    }
}

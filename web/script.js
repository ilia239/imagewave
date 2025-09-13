class ImageWaveApp {
    constructor() {
        this.currentData = null;
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.loading = document.getElementById('loading');
        this.viewerSection = document.getElementById('viewerSection');
        this.originalImage = document.getElementById('originalImage');
        this.svgViewer = document.getElementById('svgViewer');
        this.imageDimensions = document.getElementById('imageDimensions');
        this.linesCount = document.getElementById('linesCount');
        this.downloadBtn = document.getElementById('downloadSvg');
    }

    bindEvents() {
        // File input change
        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            
            if (e.dataTransfer.files.length > 0) {
                this.handleFileUpload(e.dataTransfer.files[0]);
            }
        });

        // Click to upload
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        // Download button
        this.downloadBtn.addEventListener('click', () => {
            if (this.currentData && this.currentData.svg_file) {
                window.open(this.currentData.svg_file, '_blank');
            }
        });
    }

    async handleFileUpload(file) {
        if (!this.isValidImageFile(file)) {
            alert('Please select a valid image file (PNG, JPG, JPEG, GIF, BMP, TIFF)');
            return;
        }

        this.showLoading();

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            this.currentData = data;
            this.displayResults(data);

        } catch (error) {
            console.error('Upload error:', error);
            alert(`Error: ${error.message}`);
            this.hideLoading();
        }
    }

    isValidImageFile(file) {
        const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/tiff'];
        return validTypes.includes(file.type);
    }

    showLoading() {
        this.viewerSection.style.display = 'none';
        this.loading.style.display = 'block';
    }

    hideLoading() {
        this.loading.style.display = 'none';
    }

    async displayResults(data) {
        this.hideLoading();

        // Set original image
        this.originalImage.src = data.original_image;
        
        // Load and display SVG
        try {
            const svgResponse = await fetch(data.svg_file);
            const svgContent = await svgResponse.text();
            this.svgViewer.innerHTML = svgContent;
        } catch (error) {
            console.error('Error loading SVG:', error);
            this.svgViewer.innerHTML = '<p>Error loading SVG</p>';
        }

        // Update info
        this.imageDimensions.textContent = `${data.width} × ${data.height}`;
        this.linesCount.textContent = data.num_lines;

        // Show viewer
        this.viewerSection.style.display = 'block';

        // Initialize viewer controls
        if (window.viewer) {
            window.viewer.initialize();
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ImageWaveApp();
});
class ImageWaveApp {
    constructor() {
        this.currentData = null;
        this.initializeElements();
        this.bindEvents();
        this.loadConfiguration();
    }

    initializeElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.chooseFileBtn = document.getElementById('chooseFileBtn');
        this.loading = document.getElementById('loading');
        this.viewerSection = document.getElementById('viewerSection');
        this.originalImage = document.getElementById('originalImage');
        this.svgViewer = document.getElementById('svgViewer');
        this.imageDimensions = document.getElementById('imageDimensions');
        this.linesCount = document.getElementById('linesCount');
        this.downloadBtn = document.getElementById('downloadSvg');
        this.saveSvgBtn = document.getElementById('saveSvg');

        // Configuration elements
        this.toggleConfigBtn = document.getElementById('toggleConfig');
        this.configPanel = document.getElementById('configPanel');
        this.frequencyMinInput = document.getElementById('frequencyMin');
        this.frequencyMaxInput = document.getElementById('frequencyMax');
        this.amplitudeMinInput = document.getElementById('amplitudeMin');
        this.amplitudeMaxInput = document.getElementById('amplitudeMax');
        this.lineHeightInput = document.getElementById('lineHeight');
        this.updateConfigBtn = document.getElementById('updateConfig');
        this.computeAgainBtn = document.getElementById('computeAgain');
        this.resetConfigBtn = document.getElementById('resetConfig');

        // Default configuration values
        this.defaultConfig = {
            frequency_min: 0.001,
            frequency_max: 3.0,
            amplitude_min: 0.01,
            amplitude_max: 0.9,
            line_height: 32
        };
    }

    bindEvents() {
        // File input change
        this.fileInput.addEventListener('change', (e) => {
            console.log('File input changed:', e.target.files.length, 'files');
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

        // Choose file button
        this.chooseFileBtn.addEventListener('click', (e) => {
            console.log('Choose file button clicked');
            e.stopPropagation(); // Prevent event bubbling
            // Clear the input value before opening dialog to allow reselection of same file
            this.fileInput.value = '';
            this.fileInput.click();
        });

        // Click to upload (but not on button)
        this.uploadArea.addEventListener('click', (e) => {
            // Only trigger if not clicking on the button
            if (e.target !== this.chooseFileBtn && !this.chooseFileBtn.contains(e.target)) {
                console.log('Upload area clicked');
                // Clear the input value before opening dialog to allow reselection of same file
                this.fileInput.value = '';
                this.fileInput.click();
            }
        });

        // Download button (view in browser)
        this.downloadBtn.addEventListener('click', () => {
            if (this.currentData && this.currentData.svg_file) {
                window.open(this.currentData.svg_file, '_blank');
            }
        });

        // Save SVG button (download with enhanced filename)
        this.saveSvgBtn.addEventListener('click', () => {
            if (this.currentData && this.currentData.id) {
                window.open(`/download/${this.currentData.id}`, '_blank');
            }
        });

        // Configuration events
        this.toggleConfigBtn.addEventListener('click', () => {
            this.toggleConfigPanel();
        });

        this.updateConfigBtn.addEventListener('click', () => {
            this.updateConfiguration();
        });

        this.computeAgainBtn.addEventListener('click', () => {
            this.reprocessImage();
        });

        this.resetConfigBtn.addEventListener('click', () => {
            this.resetConfiguration();
        });
    }

    async handleFileUpload(file) {
        console.log('handleFileUpload called with:', file.name, file.type, file.size);
        
        if (!this.isValidImageFile(file)) {
            alert('Please select a valid image file (PNG, JPG, JPEG, GIF, BMP, TIFF)');
            return;
        }

        console.log('File is valid, starting upload...');
        this.showLoading();

        try {
            const formData = new FormData();
            formData.append('file', file);

            console.log('Sending request to /upload...');
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            console.log('Response received:', response.status, response.statusText);

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('Response data:', data);
            
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
            // Add cache-busting timestamp to prevent browser caching issues
            const svgUrl = `${data.svg_file}?t=${Date.now()}`;
            const svgResponse = await fetch(svgUrl);
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

        // Show compute again button if we have data
        if (this.currentData) {
            this.computeAgainBtn.style.display = 'inline-block';
        }

        // Initialize viewer controls after SVG is loaded
        if (window.viewer) {
            // Clear any existing transforms on SVG before reinitializing
            const svgElement = this.svgViewer.querySelector('svg');
            if (svgElement) {
                svgElement.style.transform = '';
                svgElement.style.transformOrigin = '';
            }

            // Use setTimeout to ensure SVG is fully rendered in DOM
            setTimeout(() => {
                window.viewer.initialize();
            }, 100);
        }
    }

    async loadConfiguration() {
        console.log('Loading configuration...');
        try {
            const response = await fetch('/config');
            console.log('Config response status:', response.status);
            if (response.ok) {
                const config = await response.json();
                console.log('Received configuration:', config);
                this.populateConfigInputs(config);
            } else {
                console.warn('Failed to load configuration, using defaults');
                this.populateConfigInputs(this.defaultConfig);
            }
        } catch (error) {
            console.error('Error loading configuration:', error);
            this.populateConfigInputs(this.defaultConfig);
        }
    }

    populateConfigInputs(config) {
        console.log('Populating config inputs with:', config);
        this.frequencyMinInput.value = config.frequency_min;
        this.frequencyMaxInput.value = config.frequency_max;
        this.amplitudeMinInput.value = config.amplitude_min;
        this.amplitudeMaxInput.value = config.amplitude_max;
        this.lineHeightInput.value = config.line_height;
        console.log('Config inputs populated');
    }

    toggleConfigPanel() {
        this.configPanel.classList.toggle('hidden');
    }

    async updateConfiguration() {
        console.log('Update configuration button clicked');
        const config = {
            frequency_min: parseFloat(this.frequencyMinInput.value),
            frequency_max: parseFloat(this.frequencyMaxInput.value),
            amplitude_min: parseFloat(this.amplitudeMinInput.value),
            amplitude_max: parseFloat(this.amplitudeMaxInput.value),
            line_height: parseInt(this.lineHeightInput.value)
        };

        console.log('Configuration to send:', config);

        // Validate configuration
        if (config.frequency_min >= config.frequency_max) {
            alert('Frequency Min must be less than Frequency Max');
            return;
        }

        if (config.amplitude_min >= config.amplitude_max) {
            alert('Amplitude Min must be less than Amplitude Max');
            return;
        }

        try {
            console.log('Sending POST request to /config');
            const response = await fetch('/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });

            console.log('Response status:', response.status);
            if (response.ok) {
                const result = await response.json();
                console.log('Update result:', result);
                alert('Configuration updated successfully!');
                // Show compute again button if we have data
                if (this.currentData) {
                    this.computeAgainBtn.style.display = 'inline-block';
                }
            } else {
                const error = await response.text();
                console.error('Update failed:', error);
                alert('Failed to update configuration');
            }
        } catch (error) {
            console.error('Error updating configuration:', error);
            alert('Error updating configuration');
        }
    }

    async reprocessImage() {
        if (!this.currentData || !this.currentData.id) {
            alert('No image to reprocess');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch(`/reprocess/${this.currentData.id}`, {
                method: 'POST'
            });

            if (response.ok) {
                const data = await response.json();
                this.currentData = { ...this.currentData, ...data };
                await this.displayResults(this.currentData);
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Reprocessing failed');
            }
        } catch (error) {
            console.error('Reprocessing error:', error);
            alert(`Error: ${error.message}`);
            this.hideLoading();
        }
    }

    async resetConfiguration() {
        this.populateConfigInputs(this.defaultConfig);
        await this.updateConfiguration();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ImageWaveApp();
});
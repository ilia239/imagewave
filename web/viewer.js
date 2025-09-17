class DualViewer {
    constructor() {
        this.currentZoom = 1;
        this.panX = 0;
        this.panY = 0;
        this.isDragging = false;
        this.lastMouseX = 0;
        this.lastMouseY = 0;
        
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.zoomSlider = document.getElementById('zoomSlider');
        this.zoomValue = document.getElementById('zoomValue');
        this.resetViewBtn = document.getElementById('resetView');
        this.originalContainer = document.getElementById('originalContainer');
        this.svgContainer = document.getElementById('svgContainer');
        this.originalImage = document.getElementById('originalImage');
        this.svgViewer = document.getElementById('svgViewer');
    }

    bindEvents() {
        // Zoom slider
        this.zoomSlider.addEventListener('input', (e) => {
            this.setZoom(parseFloat(e.target.value));
        });

        // Reset view button
        this.resetViewBtn.addEventListener('click', () => {
            this.resetView();
        });

        // Mouse events for panning
        this.bindPanEvents(this.originalContainer, 'original');
        this.bindPanEvents(this.svgContainer, 'svg');

        // Wheel events for zooming
        this.originalContainer.addEventListener('wheel', (e) => {
            e.preventDefault();
            this.handleWheelZoom(e);
        });

        this.svgContainer.addEventListener('wheel', (e) => {
            e.preventDefault();
            this.handleWheelZoom(e);
        });

        // Synchronized scrolling
        this.originalContainer.addEventListener('scroll', () => {
            this.syncScroll(this.originalContainer, this.svgContainer);
        });

        this.svgContainer.addEventListener('scroll', () => {
            this.syncScroll(this.svgContainer, this.originalContainer);
        });
    }

    bindPanEvents(container, type) {
        let isDragging = false;
        let startX, startY;
        let startScrollLeft, startScrollTop;

        container.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            startScrollLeft = container.scrollLeft;
            startScrollTop = container.scrollTop;
            container.style.cursor = 'grabbing';
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            
            container.scrollLeft = startScrollLeft - deltaX;
            container.scrollTop = startScrollTop - deltaY;
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                container.style.cursor = 'grab';
            }
        });
    }

    setZoom(zoom) {
        this.currentZoom = zoom;
        this.zoomValue.textContent = Math.round(zoom * 100) + '%';
        this.applyTransformations();
    }

    applyTransformations() {
        const transform = `scale(${this.currentZoom})`;
        
        // Apply to original image
        if (this.originalImage) {
            this.originalImage.style.transform = transform;
            this.originalImage.style.transformOrigin = 'top left';
        }

        // Apply to SVG
        const svgElement = this.svgViewer.querySelector('svg');
        if (svgElement) {
            svgElement.style.transform = transform;
            svgElement.style.transformOrigin = 'top left';
        }
    }

    handleWheelZoom(e) {
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        const newZoom = Math.max(0.1, Math.min(3, this.currentZoom + delta));
        
        this.zoomSlider.value = newZoom;
        this.setZoom(newZoom);
    }

    syncScroll(source, target) {
        // Prevent infinite loop
        if (source.dataset.syncing) return;
        
        target.dataset.syncing = true;
        target.scrollLeft = source.scrollLeft;
        target.scrollTop = source.scrollTop;
        
        setTimeout(() => {
            delete target.dataset.syncing;
        }, 10);
    }

    resetView() {
        this.setZoom(1);
        this.zoomSlider.value = 1;
        this.originalContainer.scrollLeft = 0;
        this.originalContainer.scrollTop = 0;
        this.svgContainer.scrollLeft = 0;
        this.svgContainer.scrollTop = 0;
    }

    initialize() {
        // Called when new content is loaded
        this.resetView();

        // Ensure images are loaded before applying transformations
        this.originalImage.addEventListener('load', () => {
            this.applyTransformations();
        });

        // Apply transformations to SVG immediately
        setTimeout(() => {
            this.applyTransformations();
        }, 100);
    }

    preserveViewState() {
        // Save current view state for restoration after recomputation
        return {
            zoom: this.currentZoom,
            scrollLeft: this.originalContainer.scrollLeft,
            scrollTop: this.originalContainer.scrollTop
        };
    }

    restoreViewState(viewState) {
        if (!viewState) return;

        // Restore zoom
        this.setZoom(viewState.zoom);
        this.zoomSlider.value = viewState.zoom;

        // Restore scroll position after a brief delay to ensure content is loaded
        setTimeout(() => {
            this.originalContainer.scrollLeft = viewState.scrollLeft;
            this.originalContainer.scrollTop = viewState.scrollTop;
            this.svgContainer.scrollLeft = viewState.scrollLeft;
            this.svgContainer.scrollTop = viewState.scrollTop;
        }, 100);
    }

    initializeWithViewState(viewState = null) {
        // Called when new content is loaded, optionally preserving view state
        if (viewState) {
            // Don't reset view, preserve the current state
            this.restoreViewState(viewState);
        } else {
            this.resetView();
        }

        // Ensure images are loaded before applying transformations
        this.originalImage.addEventListener('load', () => {
            this.applyTransformations();
            if (viewState) {
                // Re-apply view state after image loads
                setTimeout(() => this.restoreViewState(viewState), 50);
            }
        });

        // Apply transformations to SVG immediately
        setTimeout(() => {
            this.applyTransformations();
            if (viewState) {
                // Re-apply view state after SVG loads
                setTimeout(() => this.restoreViewState(viewState), 50);
            }
        }, 100);
    }
}

// Initialize the viewer when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.viewer = new DualViewer();
});
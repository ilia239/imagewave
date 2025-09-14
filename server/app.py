from flask import Flask, request, send_file, jsonify, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
from pathlib import Path

from image_processor import ImageProcessor
from sine_generator import SineGenerator
from svg_generator import SVGGenerator

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 2024 * 2024  # 16MB max file size

# Initialize processors
image_processor = ImageProcessor(line_height=16)
sine_generator = SineGenerator(line_height=16)
svg_generator = SVGGenerator()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def serve_index():
    """Serve the web interface"""
    return send_from_directory('../web', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from web directory"""
    return send_from_directory('../web', filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle image upload and conversion"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        # Save uploaded file
        upload_path = f"uploads/{file_id}.{file_ext}"
        file.save(upload_path)
        
        # Process image
        processed_data = image_processor.process_image(upload_path)
        
        # Generate sine waves
        sine_waves = sine_generator.generate_sine_waves(processed_data)
        
        # Generate SVG
        svg_content = svg_generator.generate_optimized_svg(
            sine_waves, 
            processed_data['width'], 
            processed_data['height']
        )
        
        # Save SVG file
        svg_path = f"uploads/{file_id}.svg"
        with open(svg_path, 'w') as f:
            f.write(svg_content)
        
        return jsonify({
            'id': file_id,
            'original_image': f'/uploads/{file_id}.{file_ext}',
            'svg_file': f'/uploads/{file_id}.svg',
            'width': processed_data['width'],
            'height': processed_data['height'],
            'num_lines': processed_data['num_lines']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory('uploads', filename)

@app.route('/convert/<file_id>')
def get_conversion_status(file_id):
    """Get conversion status and results"""
    svg_path = f"uploads/{file_id}.svg"
    if os.path.exists(svg_path):
        return jsonify({
            'status': 'completed',
            'svg_file': f'/uploads/{file_id}.svg'
        })
    else:
        return jsonify({'status': 'processing'})

@app.route('/download/<file_id>')
def download_svg(file_id):
    """Download generated SVG file"""
    svg_path = f"uploads/{file_id}.svg"
    if os.path.exists(svg_path):
        return send_file(svg_path, as_attachment=True, download_name=f'{file_id}.svg')
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/config', methods=['GET', 'POST'])
def handle_config():
    """Get or update configuration"""
    if request.method == 'GET':
        return jsonify({
            'line_height': image_processor.line_height,
            'amplitude_factor': sine_generator.amplitude / sine_generator.line_height,
            'samples_per_pixel': sine_generator.samples_per_pixel
        })
    
    elif request.method == 'POST':
        config = request.get_json()
        
        if 'line_height' in config:
            line_height = int(config['line_height'])
            image_processor.line_height = line_height
            sine_generator.line_height = line_height
            sine_generator.amplitude = line_height * (sine_generator.amplitude / sine_generator.line_height)
        
        if 'amplitude_factor' in config:
            amplitude_factor = float(config['amplitude_factor'])
            sine_generator.amplitude = sine_generator.line_height * amplitude_factor
        
        if 'samples_per_pixel' in config:
            sine_generator.samples_per_pixel = int(config['samples_per_pixel'])
        
        return jsonify({'status': 'updated'})

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5002)
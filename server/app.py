from flask import Flask, request, send_file, jsonify, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
from pathlib import Path

from image_processor import ImageProcessor
from sine_generator import SineGenerator
from svg_generator import SVGGenerator
from config import config

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 2024 * 2024  # 16MB max file size

# Initialize processors
image_processor = ImageProcessor()
sine_generator = SineGenerator(
    width_min=config.STROKE_WIDTH_MIN,
    width_max=config.STROKE_WIDTH_MAX
)
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
    """Download generated SVG file with configuration settings in filename"""
    svg_path = f"uploads/{file_id}.svg"
    if os.path.exists(svg_path):
        # Create filename with current configuration settings
        config_suffix = f"_fm{config.FREQUENCY_MIN}_fx{config.FREQUENCY_MAX}_am{config.AMPLITUDE_MIN}_ax{config.AMPLITUDE_MAX}_sm{config.STROKE_WIDTH_MIN}_sx{config.STROKE_WIDTH_MAX}_lh{config.LINE_HEIGHT}"
        # Replace dots with 'p' to avoid file extension confusion
        config_suffix = config_suffix.replace('.', 'p')
        download_filename = f"{file_id}{config_suffix}.svg"

        return send_file(svg_path, as_attachment=True, download_name=download_filename)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/config', methods=['GET', 'POST'])
def handle_config():
    """Get or update configuration"""
    if request.method == 'GET':
        return jsonify({
            'line_height': config.LINE_HEIGHT,
            'amplitude_min': config.AMPLITUDE_MIN,
            'amplitude_max': config.AMPLITUDE_MAX,
            'frequency_min': config.FREQUENCY_MIN,
            'frequency_max': config.FREQUENCY_MAX,
            'stroke_width_min': config.STROKE_WIDTH_MIN,
            'stroke_width_max': config.STROKE_WIDTH_MAX
        })

    elif request.method == 'POST':
        data = request.get_json()

        # Update configuration values
        if 'amplitude_min' in data:
            config.AMPLITUDE_MIN = float(data['amplitude_min'])
        if 'amplitude_max' in data:
            config.AMPLITUDE_MAX = float(data['amplitude_max'])
        if 'frequency_min' in data:
            config.FREQUENCY_MIN = float(data['frequency_min'])
        if 'frequency_max' in data:
            config.FREQUENCY_MAX = float(data['frequency_max'])
        if 'stroke_width_min' in data:
            config.STROKE_WIDTH_MIN = float(data['stroke_width_min'])
        if 'stroke_width_max' in data:
            config.STROKE_WIDTH_MAX = float(data['stroke_width_max'])
        if 'line_height' in data:
            config.LINE_HEIGHT = int(data['line_height'])

        # Reinitialize processors with new configuration
        global image_processor, sine_generator, svg_generator
        image_processor = ImageProcessor(line_height=config.LINE_HEIGHT)
        sine_generator = SineGenerator(
            line_height=config.LINE_HEIGHT,
            frequency_min=config.FREQUENCY_MIN,
            frequency_max=config.FREQUENCY_MAX,
            amplitude_min=config.AMPLITUDE_MIN,
            amplitude_max=config.AMPLITUDE_MAX,
            width_min=config.STROKE_WIDTH_MIN,
            width_max=config.STROKE_WIDTH_MAX
        )
        svg_generator = SVGGenerator()

        return jsonify({'status': 'updated'})

@app.route('/reprocess/<file_id>', methods=['POST'])
def reprocess_image(file_id):
    """Reprocess an existing image with current configuration"""
    try:
        # Find the original image file
        original_files = [f for f in os.listdir('uploads') if f.startswith(file_id) and not f.endswith('.svg')]
        if not original_files:
            return jsonify({'error': 'Original image not found'}), 404

        original_path = f"uploads/{original_files[0]}"

        # Process image with current configuration
        processed_data = image_processor.process_image(original_path)

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
            'svg_file': f'/uploads/{file_id}.svg',
            'width': processed_data['width'],
            'height': processed_data['height'],
            'num_lines': processed_data['num_lines']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5002)
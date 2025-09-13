from PIL import Image
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self, line_height=8):
        self.line_height = line_height
    
    def load_image(self, image_path):
        """Load and convert image to grayscale"""
        image = Image.open(image_path)
        grayscale = image.convert('L')
        image_array = np.array(grayscale)
        
        logger.debug(f"Loaded image: {image_path}")
        logger.debug(f"Original image size: {image.size}")
        logger.debug(f"Image array shape: {image_array.shape}")
        logger.debug(f"Pixel intensity range: {image_array.min()} - {image_array.max()}")
        logger.debug(f"Average image intensity: {np.mean(image_array):.2f}")
        
        return image_array
    
    def segment_into_lines(self, image_array):
        """Split image into horizontal lines of specified height"""
        height, width = image_array.shape
        lines = []
        
        logger.debug(f"Segmenting image into lines with height: {self.line_height}")
        logger.debug(f"Image dimensions: {width}x{height}")
        
        for y in range(0, height, self.line_height):
            # Handle last line that might be smaller than line_height
            end_y = min(y + self.line_height, height)
            line = image_array[y:end_y, :]
            lines.append(line)
        
        logger.debug(f"Total lines created: {len(lines)}")
        return lines
    
    def calculate_line_intensities(self, lines):
        """Calculate average intensity for each vertical column within each line"""
        line_intensities = []
        
        logger.debug("Calculating column intensities for each line...")
        
        for line_idx, line in enumerate(lines):
            # Calculate average intensity for each vertical column in the line
            line_height, width = line.shape
            column_intensities = []
            
            for col_idx in range(width):
                # Extract vertical column (all rows for this x position)
                column = line[:, col_idx]
                avg_intensity = np.mean(column)
                column_intensities.append(avg_intensity)
                
                if line_idx < 3 and col_idx < 10:  # Log first few for debugging
                    logger.debug(f"Line {line_idx}, Column {col_idx}: intensity = {avg_intensity:.2f}")
            
            line_intensities.append(column_intensities)
            line_avg = np.mean(column_intensities)
            logger.debug(f"Line {line_idx} overall average: {line_avg:.2f} (from {len(column_intensities)} columns)")
        
        return line_intensities
    
    def process_image(self, image_path):
        """Complete processing pipeline: load -> segment -> calculate intensities"""
        image_array = self.load_image(image_path)
        lines = self.segment_into_lines(image_array)
        intensities = self.calculate_line_intensities(lines)
        
        return {
            'image_array': image_array,
            'lines': lines,
            'intensities': intensities,
            'width': image_array.shape[1],
            'height': image_array.shape[0],
            'num_lines': len(lines)
        }
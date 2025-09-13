from PIL import Image
import numpy as np

class ImageProcessor:
    def __init__(self, line_height=8):
        self.line_height = line_height
    
    def load_image(self, image_path):
        """Load and convert image to grayscale"""
        image = Image.open(image_path)
        grayscale = image.convert('L')
        return np.array(grayscale)
    
    def segment_into_lines(self, image_array):
        """Split image into horizontal lines of specified height"""
        height, width = image_array.shape
        lines = []
        
        for y in range(0, height, self.line_height):
            # Handle last line that might be smaller than line_height
            end_y = min(y + self.line_height, height)
            line = image_array[y:end_y, :]
            lines.append(line)
        
        return lines
    
    def calculate_line_intensities(self, lines):
        """Calculate average intensity for each row within each line"""
        line_intensities = []
        
        for line in lines:
            # Calculate average intensity for each row in the line
            row_intensities = []
            for row in line:
                avg_intensity = np.mean(row)
                row_intensities.append(avg_intensity)
            line_intensities.append(row_intensities)
        
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
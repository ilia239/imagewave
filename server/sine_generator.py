import numpy as np
from frequency_mapper import FrequencyMapper

class SineGenerator:
    def __init__(self, line_height=8, amplitude_factor=0.25, samples_per_pixel=2):
        self.line_height = line_height
        self.amplitude = line_height * amplitude_factor  # Wave amplitude
        self.samples_per_pixel = samples_per_pixel
        self.frequency_mapper = FrequencyMapper()
    
    def generate_sine_waves(self, processed_data):
        """Generate sine wave data for all lines in the image"""
        intensities = processed_data['intensities']
        width = processed_data['width']
        num_lines = processed_data['num_lines']
        
        sine_waves = []
        
        for line_idx, line_intensities in enumerate(intensities):
            base_y = line_idx * self.line_height + self.line_height / 2
            wave_data = self._generate_line_wave(line_intensities, width, base_y)
            sine_waves.append(wave_data)
        
        return sine_waves
    
    def _generate_line_wave(self, line_intensities, width, base_y):
        """Generate sine wave for a single line"""
        # Average intensity for the entire line (or use first row if needed)
        avg_intensity = np.mean(line_intensities)
        frequency = self.frequency_mapper.get_frequency(avg_intensity)
        
        # Generate x coordinates with high resolution for smooth curves
        num_samples = width * self.samples_per_pixel
        x_coords = np.linspace(0, width, num_samples)
        
        # Calculate sine wave
        # Scale frequency to image width for appropriate wave count
        wave_frequency = frequency * 2 * np.pi / width
        y_coords = base_y + self.amplitude * np.sin(wave_frequency * x_coords)
        
        return {
            'x_coords': x_coords,
            'y_coords': y_coords,
            'base_y': base_y,
            'frequency': frequency,
            'intensity': avg_intensity
        }
    
    def generate_varying_sine_wave(self, line_intensities, width, base_y):
        """Generate sine wave with varying frequency based on row intensities"""
        # This method creates waves where frequency can change along the line
        # based on individual row intensities rather than line average
        
        num_samples = width * self.samples_per_pixel
        x_coords = np.linspace(0, width, num_samples)
        y_coords = np.zeros(num_samples)
        
        rows_per_line = len(line_intensities)
        
        for i, x in enumerate(x_coords):
            # Determine which row this x position corresponds to
            progress = x / width
            row_idx = min(int(progress * rows_per_line), rows_per_line - 1)
            
            intensity = line_intensities[row_idx]
            frequency = self.frequency_mapper.get_frequency(intensity)
            
            # Calculate sine value for this position
            wave_frequency = frequency * 2 * np.pi / width
            y_coords[i] = base_y + self.amplitude * np.sin(wave_frequency * x)
        
        return {
            'x_coords': x_coords,
            'y_coords': y_coords,
            'base_y': base_y,
            'varying_frequencies': True
        }
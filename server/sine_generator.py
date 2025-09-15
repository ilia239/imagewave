import numpy as np
import logging
from frequency_mapper import FrequencyMapper
from amplitude_mapper import AmplitudeMapper
from config.config import LINE_HEIGHT, AMPLITUDE, FREQUENCY_MIN, FREQUENCY_MAX, AMPLITUDE_MIN, AMPLITUDE_MAX

logger = logging.getLogger(__name__)

class SineGenerator:
    def __init__(self, line_height=None, amplitude_factor=None, samples_per_pixel=1,
                 frequency_min=None, frequency_max=None, amplitude_min=None, amplitude_max=None):
        self.line_height = line_height or LINE_HEIGHT
        self.base_amplitude = amplitude_factor or AMPLITUDE
        self.samples_per_pixel = samples_per_pixel

        # Use provided parameters or fall back to config values
        freq_min = frequency_min if frequency_min is not None else FREQUENCY_MIN
        freq_max = frequency_max if frequency_max is not None else FREQUENCY_MAX
        amp_min = amplitude_min if amplitude_min is not None else AMPLITUDE_MIN
        amp_max = amplitude_max if amplitude_max is not None else AMPLITUDE_MAX

        self.frequency_mapper = FrequencyMapper(freq_min, freq_max)
        self.amplitude_mapper = AmplitudeMapper(amp_min, amp_max)
    
    def generate_sine_waves(self, processed_data):
        """Generate sine wave data for all lines in the image"""
        intensities = processed_data['intensities']
        width = processed_data['width']
        num_lines = processed_data['num_lines']
        
        logger.debug(f"Generating sine waves for {num_lines} lines, width={width}")
        logger.debug(f"Line height: {self.line_height}, Base amplitude: {self.base_amplitude}")
        
        sine_waves = []
        
        for line_idx, line_intensities in enumerate(intensities):
            base_y = line_idx * self.line_height + self.line_height / 2
            wave_data = self._generate_varying_line_wave(line_intensities, width, base_y, line_idx)
            logger.debug(f"Line {line_idx}: wave_data.len={len(wave_data)}")

            sine_waves.append(wave_data)
        
        logger.debug(f"Generated {len(sine_waves)} sine waves")
        return sine_waves
    
    def _generate_line_wave(self, line_intensities, width, base_y, line_idx=None):
        """Generate sine wave for a single line"""
        # Average intensity for the entire line (or use first row if needed)
        avg_intensity = np.mean(line_intensities)
        frequency = self.frequency_mapper.get_frequency(avg_intensity)
        
        if line_idx is not None and line_idx < 5:  # Log first few lines
            logger.debug(f"Line {line_idx}: avg_intensity={avg_intensity:.2f} -> frequency={frequency:.2f}")
            logger.debug(f"Line {line_idx}: row intensities={[round(x, 1) for x in line_intensities[:5]]}")
        
        # Generate x coordinates with high resolution for smooth curves
        num_samples = width * self.samples_per_pixel
        x_coords = np.linspace(0, width, num_samples)
        
        # Calculate sine wave
        # Scale frequency to image width for appropriate wave count
        wave_frequency = frequency * 2 * np.pi / width
        amplitude_factor = self.amplitude_mapper.get_amplitude_factor(avg_intensity)
        amplitude = self.line_height * amplitude_factor
        y_coords = base_y + amplitude * np.sin(wave_frequency * x_coords)
        
        if line_idx is not None and line_idx < 5:
            logger.debug(f"Line {line_idx}: wave_frequency={wave_frequency:.4f}, base_y={base_y:.2f}")
            logger.debug(f"Line {line_idx}: y_coord range={y_coords.min():.2f} to {y_coords.max():.2f}")
        
        return {
            'x_coords': x_coords,
            'y_coords': y_coords,
            'base_y': base_y,
            'frequency': frequency,
            'intensity': avg_intensity
        }
    
    def _generate_varying_line_wave(self, column_intensities, width, base_y, line_idx=None):
        """Generate sine wave with varying frequency based on column intensities"""
        # Each vertical column has its own intensity -> frequency
        # This creates wave segments where frequency varies along x-axis
        
        if line_idx is not None and line_idx < 3:
            logger.debug(f"Line {line_idx}: Processing {len(column_intensities)} columns")
            logger.debug(f"Line {line_idx}: Column intensities (first 5): {[round(x, 1) for x in column_intensities[:5]]}")
        
        # Generate high-resolution coordinates for smooth wave rendering
        num_samples = width * self.samples_per_pixel
        x_coords = np.linspace(0, width-1, num_samples)
        y_coords = np.zeros(num_samples)

        logger.debug(f"num_samples: {num_samples}, width: {width}, samples_per_pixel: {self.samples_per_pixel}, len(x_coords): {len(x_coords)} size of y_coords: {len(y_coords)}")

        
        # Calculate cumulative phase for continuous wave generation
        phase = 0.0
        prev_frequency = None
        
        for sample_idx, x_pos in enumerate(x_coords):
            # Find which column this x position corresponds to
            col_idx = min(int(x_pos), width - 1)
            intensity = column_intensities[col_idx]
            frequency = self.frequency_mapper.get_frequency(intensity)
            

            logger.debug(f"Line {line_idx}: x={x_pos:.2f}, col={col_idx}, intensity={intensity:.2f}, freq={frequency:.2f}")

            # Calculate wave frequency scaled for image width
            wave_frequency = frequency #* 2 * np.pi / width
            logger.debug(f"Freq: {frequency}, Wave Freq: {wave_frequency}")

            # For smooth transitions, accumulate phase based on x position
            if sample_idx > 0:
                dx = x_coords[sample_idx] - x_coords[sample_idx - 1]
                if prev_frequency is not None:
                    # Use average frequency for this segment
                    avg_frequency = (frequency + prev_frequency) / 2
                    avg_wave_frequency = avg_frequency #@ * 2 * np.pi / width
                    phase += avg_wave_frequency * dx
                else:
                    phase += wave_frequency * dx

            logger.debug(f"Phase: {phase}")            
            # Calculate sine value using accumulated phase with variable amplitude
            amplitude_factor = self.amplitude_mapper.get_amplitude_factor(intensity)
            amplitude = self.line_height * amplitude_factor
            y_coords[sample_idx] = base_y + amplitude * np.sin(phase)
            
            logger.debug(f"y_coord[{sample_idx}] = {y_coords[sample_idx]:.2f}")
            prev_frequency = frequency
            
            # if line_idx is not None and line_idx < 3 and col_idx < 5 and sample_idx % self.samples_per_pixel == 0:
            #     logger.debug(f"Line {line_idx}, Col {col_idx}: intensity={intensity:.2f} -> freq={frequency:.2f} -> y={y_coords[sample_idx]:.2f}")
            logger.debug(f"---\n")
        
        return {
            'x_coords': x_coords,
            'y_coords': y_coords,
            'base_y': base_y,
            'varying_frequencies': True,
            'column_count': len(column_intensities)
        }

    # def generate_varying_sine_wave(self, line_intensities, width, base_y):
    #     """Legacy method - kept for compatibility"""
    #     return self._generate_varying_line_wave(line_intensities, width, base_y)
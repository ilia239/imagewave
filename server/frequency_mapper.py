import logging
import numpy as np
from config.config import FREQUENCY_MIN, FREQUENCY_MAX

logger = logging.getLogger(__name__)

class FrequencyMapper:
    def __init__(self):
        self.min_frequency = FREQUENCY_MIN
        self.max_frequency = FREQUENCY_MAX
        self.frequency_range = self.max_frequency - self.min_frequency
        
        logger.debug(f"FrequencyMapper initialized with range: {self.min_frequency} - {self.max_frequency}")
    
    def get_frequency(self, intensity):
        """Convert pixel intensity (0-255) to sine wave frequency using linear interpolation
        
        Args:
            intensity: Pixel intensity (0-255)
            
        Returns:
            frequency: Linear interpolation between FREQUENCY_MAX (intensity 0) 
                      and FREQUENCY_MIN (intensity 255)
        """
        # Clamp intensity to valid range
        intensity = max(0, min(255, intensity))
        
        # Linear interpolation: higher intensity (brighter) = lower frequency
        # intensity 0 (black) -> FREQUENCY_MAX
        # intensity 255 (white) -> FREQUENCY_MIN
        normalized_intensity = intensity / 255.0
        frequency = self.max_frequency - (normalized_intensity * self.frequency_range)
        
        return frequency
    
    def get_frequencies_batch(self, intensities):
        """Convert multiple intensities to frequencies efficiently"""
        # Clamp intensities to valid range
        intensities = np.clip(intensities, 0, 255)
        
        # Linear interpolation for batch processing
        normalized_intensities = intensities / 255.0
        frequencies = self.max_frequency - (normalized_intensities * self.frequency_range)
        
        return frequencies
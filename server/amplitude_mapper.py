import logging
from config.config import AMPLITUDE_MIN, AMPLITUDE_MAX

logger = logging.getLogger(__name__)

class AmplitudeMapper:
    def __init__(self, min_amplitude=None, max_amplitude=None):
        self.min_amplitude = min_amplitude if min_amplitude is not None else AMPLITUDE_MIN
        self.max_amplitude = max_amplitude if max_amplitude is not None else AMPLITUDE_MAX
        self.amplitude_range = self.max_amplitude - self.min_amplitude

        logger.debug(f"AmplitudeMapper initialized with range: {self.min_amplitude} - {self.max_amplitude}")
    
    def get_amplitude_factor(self, intensity):
        """Get amplitude factor for given intensity with linear interpolation
        
        Args:
            intensity: Pixel intensity (0-255)
            
        Returns:
            amplitude_factor: Linear interpolation between AMPLITUDE_MAX (intensity 0) 
                            and AMPLITUDE_MIN (intensity 255)
        """
        # Clamp intensity to valid range
        intensity = max(0, min(255, intensity))
        
        # Linear interpolation: higher intensity (brighter) = lower amplitude
        # intensity 0 (black) -> AMPLITUDE_MAX
        # intensity 255 (white) -> AMPLITUDE_MIN
        normalized_intensity = intensity / 255.0
        amplitude_factor = self.max_amplitude - (normalized_intensity * self.amplitude_range)
        
        return amplitude_factor
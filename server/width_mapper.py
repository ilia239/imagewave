import numpy as np

class WidthMapper:
    """Maps pixel intensity values to line width values"""

    def __init__(self, width_min, width_max):
        self.width_min = width_min
        self.width_max = width_max

    def get_width(self, pixel_intensity):
        """
        Map pixel intensity to line width
        - Higher intensity (bright pixels) -> smaller width (width_min)
        - Lower intensity (dark pixels) -> larger width (width_max)
        """
        # Normalize intensity from 0-255 to 0-1
        normalized_intensity = pixel_intensity / 255.0

        # Invert: bright pixels (high intensity) get thin lines
        inverted_intensity = 1.0 - normalized_intensity

        # Linear interpolation between width_min and width_max
        width = self.width_min + (inverted_intensity * (self.width_max - self.width_min))

        return width
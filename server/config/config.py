# ImageWave Configuration Parameters

# Image Processing Parameters
LINE_HEIGHT = 32  # Height of each horizontal line in pixels (default: 16)
AMPLITUDE = 2.0   # Base amplitude of the sine waves (default: 2.0)

# Amplitude and Frequency Mapping
AMPLITUDE_MIN = 0.1   # Minimum amplitude factor (for intensity 255)
AMPLITUDE_MAX = 0.5  # Maximum amplitude factor (for intensity 0)
FREQUENCY_MIN = 0.9   # Minimum frequency (for intensity 255)
FREQUENCY_MAX = 2.0   # Maximum frequency (for intensity 0)

# SVG Generation Parameters
SVG_STROKE_WIDTH = 1    # SVG stroke width (default: 1)
SVG_STROKE_COLOR = "black"  # SVG stroke color (default: "black")
SVG_FILL = "none"       # SVG fill (default: "none")

# Frequency Mapping
FREQUENCY_MAP_FILE = "config/frequency_map.csv"  # Path to frequency mapping file

# Debug Settings
DEBUG_LOGGING = True    # Enable debug logging (default: True)
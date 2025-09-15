# ImageWave Configuration Parameters

# Image Processing Parameters
LINE_HEIGHT = 4  # Height of each horizontal line in pixels (default: 16)
AMPLITUDE = 2.0   # Base amplitude of the sine waves (default: 2.0)

# Amplitude and Frequency Mapping
AMPLITUDE_MIN = 0.01   # Minimum amplitude factor (for intensity 255)
AMPLITUDE_MAX = 0.5  # Maximum amplitude factor (for intensity 0)
FREQUENCY_MIN = 0.001   # Minimum frequency (for intensity 255)
FREQUENCY_MAX = 1.0   # Maximum frequency (for intensity 0)

# SVG Generation Parameters
SVG_STROKE_WIDTH = 1    # SVG stroke width (default: 1)
SVG_STROKE_COLOR = "black"  # SVG stroke color (default: "black")
SVG_FILL = "none"       # SVG fill (default: "none")

# Debug Settings
DEBUG_LOGGING = True    # Enable debug logging (default: True)
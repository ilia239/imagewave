#!/usr/bin/env python3
"""
Create test grayscale images for ImageWave testing
"""
import numpy as np
from PIL import Image
import os

def create_horizontal_gradient(width=400, height=200):
    """Create horizontal gradient from black (left) to white (right)"""
    gradient = np.zeros((height, width), dtype=np.uint8)
    for x in range(width):
        # Linear gradient from 0 (black) to 255 (white)
        intensity = int((x / (width - 1)) * 255)
        gradient[:, x] = intensity
    return gradient

def create_vertical_gradient(width=200, height=400):
    """Create vertical gradient from black (top) to white (bottom)"""
    gradient = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        # Linear gradient from 0 (black) to 255 (white)
        intensity = int((y / (height - 1)) * 255)
        gradient[y, :] = intensity
    return gradient

def create_step_pattern(width=400, height=200, steps=8):
    """Create step pattern with distinct gray levels"""
    pattern = np.zeros((height, width), dtype=np.uint8)
    step_width = width // steps
    
    for i in range(steps):
        start_x = i * step_width
        end_x = min((i + 1) * step_width, width)
        # Gray levels from black to white
        intensity = int((i / (steps - 1)) * 255)
        pattern[:, start_x:end_x] = intensity
    
    return pattern

def create_circular_gradient(width=300, height=300):
    """Create circular gradient from black center to white edges"""
    gradient = np.zeros((height, width), dtype=np.uint8)
    center_x, center_y = width // 2, height // 2
    max_distance = np.sqrt(center_x**2 + center_y**2)
    
    for y in range(height):
        for x in range(width):
            # Distance from center
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            # Normalize to 0-1 and convert to intensity
            normalized = min(distance / max_distance, 1.0)
            intensity = int(normalized * 255)
            gradient[y, x] = intensity
    
    return gradient

def main():
    """Create all test images"""
    print("Creating test grayscale images...")
    
    # Create test images
    images = {
        'horizontal_gradient.png': create_horizontal_gradient(),
        'vertical_gradient.png': create_vertical_gradient(),
        'step_pattern.png': create_step_pattern(),
        'circular_gradient.png': create_circular_gradient(),
        'test_stripes.png': create_step_pattern(width=400, height=200, steps=16)
    }
    
    # Save images
    for filename, image_array in images.items():
        image = Image.fromarray(image_array, mode='L')
        filepath = os.path.join('.', filename)
        image.save(filepath)
        print(f"Created: {filepath} ({image_array.shape[1]}x{image_array.shape[0]})")
    
    print(f"\nTest images created successfully!")
    print("You can now upload these to test the frequency mapping:")
    for filename in images.keys():
        print(f"  - {filename}")

if __name__ == "__main__":
    main()
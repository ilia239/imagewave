import numpy as np
from xml.dom import minidom

class SVGGenerator:
    def __init__(self, stroke_width=1, stroke_color="black"):
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
    
    def generate_svg(self, sine_waves, width, height):
        """Generate complete SVG from sine wave data"""
        # Create SVG document
        doc = minidom.Document()
        svg = doc.createElement('svg')
        svg.setAttribute('width', str(width))
        svg.setAttribute('height', str(height))
        svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
        doc.appendChild(svg)
        
        # Add each sine wave as a path
        for wave_data in sine_waves:
            path = self._create_path_element(doc, wave_data)
            svg.appendChild(path)
        
        return doc.toxml()
    
    def _create_path_element(self, doc, wave_data):
        """Create SVG path element from wave data"""
        path = doc.createElement('path')
        path.setAttribute('stroke', self.stroke_color)
        path.setAttribute('stroke-width', str(self.stroke_width))
        path.setAttribute('fill', 'none')
        
        # Generate path data
        path_data = self._generate_path_data(wave_data)
        path.setAttribute('d', path_data)
        
        return path
    
    def _generate_path_data(self, wave_data):
        """Generate SVG path data string from coordinates"""
        x_coords = wave_data['x_coords']
        y_coords = wave_data['y_coords']
        
        if len(x_coords) == 0:
            return ""
        
        # Start with moveTo command
        path_parts = [f"M{x_coords[0]:.2f},{y_coords[0]:.2f}"]
        
        # Use quadratic Bézier curves for smooth lines
        # Sample every few points to create control points
        step = max(1, len(x_coords) // 100)  # Reduce points for optimization
        
        i = step
        while i < len(x_coords):
            if i + step < len(x_coords):
                # Quadratic curve to next point
                cx = x_coords[i]
                cy = y_coords[i]
                x = x_coords[i + step]
                y = y_coords[i + step]
                path_parts.append(f"Q{cx:.2f},{cy:.2f} {x:.2f},{y:.2f}")
                i += step * 2
            else:
                # Line to final point
                path_parts.append(f"L{x_coords[i]:.2f},{y_coords[i]:.2f}")
                break
        
        return " ".join(path_parts)
    
    def _generate_smooth_path_data(self, wave_data):
        """Alternative method using cubic Bézier curves for extra smoothness"""
        x_coords = wave_data['x_coords']
        y_coords = wave_data['y_coords']
        
        if len(x_coords) < 4:
            return self._generate_path_data(wave_data)
        
        path_parts = [f"M{x_coords[0]:.2f},{y_coords[0]:.2f}"]
        
        # Use cubic Bézier curves
        for i in range(3, len(x_coords), 3):
            if i < len(x_coords):
                x1, y1 = x_coords[i-2], y_coords[i-2]
                x2, y2 = x_coords[i-1], y_coords[i-1]
                x, y = x_coords[i], y_coords[i]
                path_parts.append(f"C{x1:.2f},{y1:.2f} {x2:.2f},{y2:.2f} {x:.2f},{y:.2f}")
        
        return " ".join(path_parts)
    
    def save_svg(self, sine_waves, width, height, filename):
        """Save SVG to file"""
        svg_content = self.generate_svg(sine_waves, width, height)
        with open(filename, 'w') as f:
            f.write(svg_content)
    
    def generate_optimized_svg(self, sine_waves, width, height):
        """Generate SVG with optimized path data for smaller file size"""
        doc = minidom.Document()
        svg = doc.createElement('svg')
        svg.setAttribute('width', str(width))
        svg.setAttribute('height', str(height))
        svg.setAttribute('viewBox', f"0 0 {width} {height}")
        svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
        doc.appendChild(svg)
        
        # Create a single group for all paths
        group = doc.createElement('g')
        group.setAttribute('stroke', self.stroke_color)
        group.setAttribute('stroke-width', str(self.stroke_width))
        group.setAttribute('fill', 'none')
        svg.appendChild(group)
        
        # Add optimized paths
        for wave_data in sine_waves:
            path = doc.createElement('path')
            path_data = self._generate_optimized_path_data(wave_data)
            path.setAttribute('d', path_data)
            group.appendChild(path)
        
        return doc.toprettyxml(indent="  ")
    
    def _generate_optimized_path_data(self, wave_data):
        """Generate optimized path data with fewer points"""
        x_coords = wave_data['x_coords']
        y_coords = wave_data['y_coords']
        
        step = 1
        # Reduce points significantly for smaller file size
        # step = max(1, len(x_coords) // 50)
        # if step > 1:
        #     x_coords = x_coords[::step]
        #     y_coords = y_coords[::step]
        
        if len(x_coords) == 0:
            return ""
        
        path_parts = [f"M{x_coords[0]:.1f},{y_coords[0]:.1f}"]
        
        for i in range(1, len(x_coords)):
            path_parts.append(f"L{x_coords[i]:.1f},{y_coords[i]:.1f}")
        
        return " ".join(path_parts)
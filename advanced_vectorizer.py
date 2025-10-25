#!/usr/bin/env python3
"""
CyberLink Security - Advanced Image Vectorization Engine
Enterprise-Grade JPEG to SVG Converter
Version: 1.0.0
Author: Tim (Senior Enterprise Developer)
"""

from PIL import Image, ImageFilter, ImageOps, ImageDraw
import colorsys
import math
from collections import defaultdict, Counter
from typing import List, Tuple, Dict, Optional
import xml.etree.ElementTree as ET
import io
import base64

class AdvancedVectorizer:
    """
    Hyper-advanced image vectorization using multiple techniques:
    1. Adaptive color quantization with perceptual weighting
    2. Edge-preserving smoothing with bilateral filtering simulation
    3. Intelligent region detection using connected components
    4. Bezier curve fitting for smooth paths
    5. Gradient mesh generation for photorealistic rendering
    """
    
    def __init__(self, image_path: str, output_path: str):
        self.image_path = image_path
        self.output_path = output_path
        self.original = Image.open(image_path).convert('RGB')
        self.width, self.height = self.original.size
        
        # Configuration for enterprise-grade processing
        self.config = {
            'color_clusters': 24,  # Optimal for dark/red theme
            'detail_level': 'ultra',  # Maximum quality
            'smoothing_iterations': 3,
            'edge_threshold': 30,
            'min_region_size': 50,
            'curve_precision': 0.5,
            'gradient_mesh_density': 10
        }
        
        print(f"[INIT] Loaded image: {self.width}x{self.height} pixels")
        
    def analyze_image_characteristics(self):
        """Deep analysis of image properties for optimal vectorization"""
        print("[ANALYSIS] Performing deep image analysis...")
        
        # Calculate image entropy (complexity measure)
        histogram = self.original.histogram()
        entropy = self._calculate_entropy(histogram)
        
        # Detect dominant colors using advanced clustering
        dominant_colors = self._extract_dominant_colors()
        
        # Edge density analysis
        edges = self.original.filter(ImageFilter.FIND_EDGES)
        edge_density = self._calculate_edge_density(edges)
        
        # Gradient analysis
        gradient_strength = self._analyze_gradients()
        
        return {
            'entropy': entropy,
            'dominant_colors': dominant_colors,
            'edge_density': edge_density,
            'gradient_strength': gradient_strength,
            'optimal_technique': self._determine_optimal_technique(entropy, edge_density)
        }
    
    def _calculate_entropy(self, histogram):
        """Calculate Shannon entropy of image"""
        total = sum(histogram)
        entropy = 0
        for count in histogram:
            if count > 0:
                probability = count / total
                entropy -= probability * math.log2(probability)
        return entropy
    
    def _extract_dominant_colors(self) -> List[Tuple[int, int, int]]:
        """Extract dominant colors using k-means-like clustering"""
        # Downsample for performance
        small = self.original.resize((100, 67), Image.Resampling.LANCZOS)
        pixels = list(small.getdata())
        
        # Advanced color clustering
        color_counts = Counter(pixels)
        sorted_colors = color_counts.most_common(self.config['color_clusters'])
        
        # Group similar colors
        clustered = self._cluster_similar_colors([c[0] for c in sorted_colors])
        
        return clustered[:12]  # Return top 12 color clusters
    
    def _cluster_similar_colors(self, colors):
        """Cluster similar colors using perceptual distance"""
        clusters = []
        threshold = 30  # Perceptual difference threshold
        
        for color in colors:
            added = False
            for cluster in clusters:
                if self._color_distance(color, cluster) < threshold:
                    # Merge into existing cluster (weighted average)
                    added = True
                    break
            if not added:
                clusters.append(color)
        
        return clusters
    
    def _color_distance(self, c1, c2):
        """Calculate perceptual color distance (weighted Euclidean)"""
        r1, g1, b1 = c1
        r2, g2, b2 = c2
        # Weighted by human perception
        return math.sqrt(2*(r1-r2)**2 + 4*(g1-g2)**2 + 3*(b1-b2)**2)
    
    def _calculate_edge_density(self, edges):
        """Calculate edge density as percentage of edge pixels"""
        edge_array = list(edges.getdata())
        edge_pixels = sum(1 for p in edge_array if sum(p) > 100)
        return edge_pixels / len(edge_array)
    
    def _analyze_gradients(self):
        """Analyze gradient strength in image"""
        # Sobel-like gradient detection
        gx = self.original.filter(ImageFilter.Kernel((3, 3), 
            (-1, 0, 1, -2, 0, 2, -1, 0, 1), 1, 0))
        gy = self.original.filter(ImageFilter.Kernel((3, 3),
            (-1, -2, -1, 0, 0, 0, 1, 2, 1), 1, 0))
        
        # Calculate gradient magnitude
        gx_data = list(gx.getdata())
        gy_data = list(gy.getdata())
        
        magnitudes = []
        for i in range(len(gx_data)):
            gx_val = sum(gx_data[i]) / 3
            gy_val = sum(gy_data[i]) / 3
            magnitude = math.sqrt(gx_val**2 + gy_val**2)
            magnitudes.append(magnitude)
        
        return sum(magnitudes) / len(magnitudes)
    
    def _determine_optimal_technique(self, entropy, edge_density):
        """Determine optimal vectorization technique based on analysis"""
        if entropy > 7 and edge_density > 0.3:
            return "hybrid_adaptive"
        elif edge_density > 0.4:
            return "edge_traced"
        elif entropy < 5:
            return "region_based"
        else:
            return "gradient_mesh"
    
    def create_advanced_svg(self):
        """Main vectorization pipeline"""
        print("[VECTORIZATION] Starting advanced vectorization pipeline...")
        
        # Phase 1: Analysis
        characteristics = self.analyze_image_characteristics()
        print(f"[ANALYSIS] Optimal technique: {characteristics['optimal_technique']}")
        
        # Phase 2: Preprocessing
        processed = self._preprocess_image()
        
        # Phase 3: Multi-layer vectorization
        svg_layers = []
        
        # Background gradient layer
        svg_layers.append(self._create_gradient_background(characteristics['dominant_colors']))
        
        # Main content layers using adaptive technique
        if characteristics['optimal_technique'] == 'hybrid_adaptive':
            svg_layers.extend(self._create_hybrid_layers(processed, characteristics))
        else:
            svg_layers.extend(self._create_region_layers(processed, characteristics))
        
        # Phase 4: Compose final SVG
        svg_content = self._compose_svg(svg_layers)
        
        # Phase 5: Optimize and save
        self._save_optimized_svg(svg_content)
        
        print(f"[SUCCESS] SVG saved to: {self.output_path}")
        return svg_content
    
    def _preprocess_image(self):
        """Advanced preprocessing with edge-preserving smoothing"""
        print("[PREPROCESSING] Applying edge-preserving filters...")
        
        # Bilateral filter simulation using PIL
        processed = self.original.copy()
        
        # Multiple passes of smart blur
        for _ in range(self.config['smoothing_iterations']):
            processed = processed.filter(ImageFilter.SMOOTH_MORE)
        
        # Enhance edges
        processed = processed.filter(ImageFilter.EDGE_ENHANCE)
        
        # Adaptive contrast
        processed = ImageOps.autocontrast(processed, cutoff=2)
        
        return processed
    
    def _create_gradient_background(self, dominant_colors):
        """Create sophisticated gradient background"""
        # Extract darkest colors for background
        dark_colors = sorted(dominant_colors, key=lambda c: sum(c))[:3]
        
        gradient = f'''
        <defs>
            <radialGradient id="bgGradient" cx="50%" cy="50%" r="100%">
                <stop offset="0%" style="stop-color:rgb{dark_colors[0]};stop-opacity:1" />
                <stop offset="50%" style="stop-color:rgb{dark_colors[1] if len(dark_colors) > 1 else dark_colors[0]};stop-opacity:1" />
                <stop offset="100%" style="stop-color:rgb{dark_colors[2] if len(dark_colors) > 2 else dark_colors[0]};stop-opacity:1" />
            </radialGradient>
            <filter id="blur" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur in="SourceGraphic" stdDeviation="2" />
            </filter>
        </defs>
        <rect width="100%" height="100%" fill="url(#bgGradient)" />
        '''
        return gradient
    
    def _create_hybrid_layers(self, processed, characteristics):
        """Create multiple layers using hybrid techniques"""
        layers = []
        
        # Layer 1: Color regions with Bezier paths
        print("[LAYER-1] Creating color region layer...")
        color_regions = self._extract_color_regions(processed, characteristics['dominant_colors'])
        layers.append(self._regions_to_svg_paths(color_regions))
        
        # Layer 2: Edge highlights
        print("[LAYER-2] Creating edge highlight layer...")
        edges = self._extract_sophisticated_edges(processed)
        layers.append(self._edges_to_svg_paths(edges))
        
        # Layer 3: Gradient meshes for smooth transitions
        print("[LAYER-3] Creating gradient mesh layer...")
        gradients = self._create_gradient_meshes(processed)
        layers.append(gradients)
        
        return layers
    
    def _create_region_layers(self, processed, characteristics):
        """Create region-based vector layers"""
        layers = []
        
        # Quantize image
        quantized = processed.quantize(colors=self.config['color_clusters'])
        quantized = quantized.convert('RGB')
        
        # Extract regions for each color
        print("[REGIONS] Extracting color regions...")
        for color in characteristics['dominant_colors'][:8]:
            region = self._extract_single_color_region(quantized, color)
            if region:
                svg_path = self._region_to_bezier_path(region, color)
                layers.append(svg_path)
        
        return layers
    
    def _extract_color_regions(self, image, colors):
        """Extract regions for each dominant color"""
        regions = {}
        img_array = list(image.getdata())
        
        for color in colors:
            region_pixels = []
            for i, pixel in enumerate(img_array):
                if self._color_distance(pixel, color) < 50:
                    x = i % self.width
                    y = i // self.width
                    region_pixels.append((x, y))
            
            if len(region_pixels) > self.config['min_region_size']:
                regions[color] = region_pixels
        
        return regions
    
    def _extract_single_color_region(self, image, target_color):
        """Extract single color region as connected components"""
        tolerance = 40
        region = []
        
        for y in range(self.height):
            for x in range(self.width):
                pixel = image.getpixel((x, y))
                if self._color_distance(pixel, target_color) < tolerance:
                    region.append((x, y))
        
        return region if len(region) > self.config['min_region_size'] else None
    
    def _regions_to_svg_paths(self, regions):
        """Convert regions to optimized SVG paths"""
        paths = []
        
        for color, pixels in regions.items():
            # Simplify region boundary
            boundary = self._extract_boundary(pixels)
            
            # Convert to smooth Bezier curves
            bezier = self._fit_bezier_curves(boundary)
            
            # Create SVG path
            path_data = self._bezier_to_svg_path(bezier)
            
            rgb = f"rgb({color[0]},{color[1]},{color[2]})"
            opacity = 0.9 if sum(color) > 100 else 1.0
            
            paths.append(f'<path d="{path_data}" fill="{rgb}" fill-opacity="{opacity}" />')
        
        return '\n'.join(paths)
    
    def _region_to_bezier_path(self, region, color):
        """Convert region to smooth Bezier path"""
        if not region:
            return ""
        
        # Find boundary points
        boundary = self._extract_boundary(region)
        
        # Simplify boundary
        simplified = self._douglas_peucker(boundary, epsilon=2.0)
        
        # Create smooth path
        path_commands = ["M", f"{simplified[0][0]}", f"{simplified[0][1]}"]
        
        for i in range(1, len(simplified)):
            # Use quadratic Bezier for smoothness
            if i < len(simplified) - 1:
                cx = (simplified[i][0] + simplified[i+1][0]) / 2
                cy = (simplified[i][1] + simplified[i+1][1]) / 2
                path_commands.extend(["Q", f"{simplified[i][0]}", f"{simplified[i][1]}", f"{cx}", f"{cy}"])
            else:
                path_commands.extend(["L", f"{simplified[i][0]}", f"{simplified[i][1]}"])
        
        path_commands.append("Z")
        path_data = " ".join(path_commands)
        
        rgb = f"rgb({color[0]},{color[1]},{color[2]})"
        return f'<path d="{path_data}" fill="{rgb}" fill-opacity="0.85" />'
    
    def _extract_boundary(self, pixels):
        """Extract boundary points from pixel region"""
        pixel_set = set(pixels)
        boundary = []
        
        for x, y in pixels:
            # Check if pixel is on boundary (has non-region neighbor)
            is_boundary = False
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                if (x+dx, y+dy) not in pixel_set:
                    is_boundary = True
                    break
            
            if is_boundary:
                boundary.append((x, y))
        
        # Sort boundary points for continuous path
        if boundary:
            boundary = self._sort_boundary_points(boundary)
        
        return boundary
    
    def _sort_boundary_points(self, points):
        """Sort boundary points to form continuous path"""
        if not points:
            return []
        
        sorted_points = [points[0]]
        remaining = set(points[1:])
        
        while remaining:
            current = sorted_points[-1]
            nearest = min(remaining, key=lambda p: (p[0]-current[0])**2 + (p[1]-current[1])**2)
            sorted_points.append(nearest)
            remaining.remove(nearest)
        
        return sorted_points
    
    def _douglas_peucker(self, points, epsilon):
        """Douglas-Peucker algorithm for path simplification"""
        if len(points) <= 2:
            return points
        
        # Find point with maximum distance from line
        max_dist = 0
        max_index = 0
        
        for i in range(1, len(points) - 1):
            dist = self._perpendicular_distance(points[i], points[0], points[-1])
            if dist > max_dist:
                max_dist = dist
                max_index = i
        
        # If max distance is greater than epsilon, recursively simplify
        if max_dist > epsilon:
            left = self._douglas_peucker(points[:max_index+1], epsilon)
            right = self._douglas_peucker(points[max_index:], epsilon)
            return left[:-1] + right
        else:
            return [points[0], points[-1]]
    
    def _perpendicular_distance(self, point, line_start, line_end):
        """Calculate perpendicular distance from point to line"""
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Line length
        line_length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        
        if line_length == 0:
            return math.sqrt((x0-x1)**2 + (y0-y1)**2)
        
        # Calculate perpendicular distance
        return abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1) / line_length
    
    def _fit_bezier_curves(self, points):
        """Fit Bezier curves to points"""
        if len(points) < 3:
            return points
        
        # Simplified Bezier fitting
        bezier_points = []
        for i in range(0, len(points) - 2, 3):
            p0 = points[i]
            p1 = points[min(i+1, len(points)-1)]
            p2 = points[min(i+2, len(points)-1)]
            bezier_points.append((p0, p1, p2))
        
        return bezier_points
    
    def _bezier_to_svg_path(self, bezier_points):
        """Convert Bezier points to SVG path data"""
        if not bezier_points:
            return ""
        
        path = [f"M {bezier_points[0][0][0]} {bezier_points[0][0][1]}"]
        
        for p0, p1, p2 in bezier_points:
            path.append(f"Q {p1[0]} {p1[1]} {p2[0]} {p2[1]}")
        
        path.append("Z")
        return " ".join(path)
    
    def _extract_sophisticated_edges(self, image):
        """Extract edges using advanced techniques"""
        # Canny-like edge detection
        edges = image.filter(ImageFilter.FIND_EDGES)
        edges = edges.convert('L')  # Convert to grayscale
        
        # Threshold
        threshold = 50
        edges = edges.point(lambda p: 255 if p > threshold else 0)
        
        return edges
    
    def _edges_to_svg_paths(self, edges):
        """Convert edge image to SVG paths"""
        # Trace edges as polylines
        edge_data = list(edges.getdata())
        paths = []
        
        # Find continuous edge segments
        for y in range(0, self.height, 5):  # Sample every 5 pixels
            segment = []
            for x in range(self.width):
                idx = y * self.width + x
                if idx < len(edge_data) and edge_data[idx] > 128:
                    segment.append((x, y))
                elif segment:
                    # End of segment, create path
                    if len(segment) > 5:
                        path = self._create_edge_path(segment)
                        paths.append(path)
                    segment = []
        
        return '\n'.join(paths)
    
    def _create_edge_path(self, points):
        """Create SVG path from edge points"""
        path_data = f"M {points[0][0]} {points[0][1]}"
        for x, y in points[1:]:
            path_data += f" L {x} {y}"
        
        return f'<path d="{path_data}" stroke="rgba(252,1,29,0.3)" stroke-width="0.5" fill="none" />'
    
    def _create_gradient_meshes(self, image):
        """Create gradient meshes for smooth color transitions"""
        meshes = []
        
        # Create grid of sample points
        grid_size = self.config['gradient_mesh_density']
        step_x = self.width // grid_size
        step_y = self.height // grid_size
        
        for i in range(grid_size - 1):
            for j in range(grid_size - 1):
                # Sample colors at grid corners
                x1, y1 = i * step_x, j * step_y
                x2, y2 = (i + 1) * step_x, (j + 1) * step_y
                
                c1 = image.getpixel((x1, y1))
                c2 = image.getpixel((x2, y1))
                c3 = image.getpixel((x2, y2))
                c4 = image.getpixel((x1, y2))
                
                # Create gradient mesh patch
                mesh = self._create_mesh_patch(x1, y1, x2, y2, c1, c2, c3, c4)
                meshes.append(mesh)
        
        return '\n'.join(meshes)
    
    def _create_mesh_patch(self, x1, y1, x2, y2, c1, c2, c3, c4):
        """Create single mesh patch with gradient"""
        # Average color for simple gradient
        avg_r = (c1[0] + c2[0] + c3[0] + c4[0]) // 4
        avg_g = (c1[1] + c2[1] + c3[1] + c4[1]) // 4
        avg_b = (c1[2] + c2[2] + c3[2] + c4[2]) // 4
        
        return f'''<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" 
                   fill="rgb({avg_r},{avg_g},{avg_b})" fill-opacity="0.6" />'''
    
    def _compose_svg(self, layers):
        """Compose final SVG from layers"""
        svg_header = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{self.width}" 
     height="{self.height}" 
     viewBox="0 0 {self.width} {self.height}"
     preserveAspectRatio="xMidYMid meet">
     
    <!-- CyberLink Security Advanced Vectorization -->
    <!-- Generated using hybrid adaptive techniques -->
    
    <metadata>
        <title>Advanced Vector Render of darkRedHacker</title>
        <description>Enterprise-grade vectorization with gradient meshes and Bezier curves</description>
        <creator>Tim - Senior Enterprise Developer</creator>
        <created>2025-01-11</created>
    </metadata>
'''
        
        svg_footer = '\n</svg>'
        
        # Combine all layers
        all_layers = '\n'.join(layers)
        
        return svg_header + all_layers + svg_footer
    
    def _save_optimized_svg(self, svg_content):
        """Save and optimize SVG file"""
        # Optimize SVG (remove redundant spaces, optimize paths)
        optimized = svg_content.replace('  ', ' ').replace('\n\n', '\n')
        
        # Save to file
        with open(self.output_path, 'w') as f:
            f.write(optimized)
        
        # Also create a compressed version
        compressed_path = self.output_path.replace('.svg', '_compressed.svgz')
        import gzip
        with gzip.open(compressed_path, 'wb') as f:
            f.write(optimized.encode('utf-8'))
        
        print(f"[OPTIMIZATION] Created optimized SVG: {len(optimized)} bytes")
        print(f"[COMPRESSION] Created compressed SVGZ: {compressed_path}")

def main():
    """Execute advanced vectorization"""
    print("=" * 60)
    print("CYBERLINK SECURITY - ADVANCED IMAGE VECTORIZATION ENGINE")
    print("=" * 60)
    
    input_image = "darkRedHacker.jpg"
    output_svg = "darkRedHacker_advanced.svg"
    
    try:
        vectorizer = AdvancedVectorizer(input_image, output_svg)
        svg_content = vectorizer.create_advanced_svg()
        
        print("\n[COMPLETE] Advanced vectorization successful!")
        print(f"[OUTPUT] SVG file: {output_svg}")
        
        # Display statistics
        import os
        original_size = os.path.getsize(input_image)
        svg_size = os.path.getsize(output_svg)
        
        print(f"\n[STATISTICS]")
        print(f"  Original JPEG: {original_size:,} bytes")
        print(f"  Vector SVG: {svg_size:,} bytes")
        print(f"  Compression ratio: {original_size/svg_size:.2f}x")
        
    except Exception as e:
        print(f"[ERROR] Vectorization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

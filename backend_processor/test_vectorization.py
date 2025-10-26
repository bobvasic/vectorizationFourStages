#!/usr/bin/env python3
"""
CyberLink Security - Vectorization Test Suite
Comprehensive unit and integration tests
Version: 1.0.0
"""

import unittest
import os
import io
import tempfile
from PIL import Image

# Import modules to test
from intelligent_vectorizer import IntelligentVectorizer, vectorize_image
from semantic_vectorizer import SemanticVectorizer, vectorize_semantic

try:
    import rust_core
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False


class TestIntelligentVectorizer(unittest.TestCase):
    """Test suite for intelligent vectorizer"""
    
    @classmethod
    def setUpClass(cls):
        """Create test images"""
        cls.test_dir = tempfile.mkdtemp()
        
        # Create simple test image (100x100, red square)
        img = Image.new('RGB', (100, 100), color='white')
        for y in range(25, 75):
            for x in range(25, 75):
                img.putpixel((x, y), (255, 0, 0))
        
        cls.test_image_path = os.path.join(cls.test_dir, 'test_input.png')
        img.save(cls.test_image_path)
    
    def test_vectorizer_initialization(self):
        """Test vectorizer loads image correctly"""
        vectorizer = IntelligentVectorizer(self.test_image_path)
        self.assertEqual(vectorizer.width, 100)
        self.assertEqual(vectorizer.height, 100)
        self.assertIsNotNone(vectorizer.original)
    
    def test_quality_settings(self):
        """Test quality preset configurations"""
        vectorizer = IntelligentVectorizer(self.test_image_path)
        
        fast_settings = vectorizer._get_quality_settings('fast')
        self.assertEqual(fast_settings['colors'], 16)
        
        ultra_settings = vectorizer._get_quality_settings('ultra')
        self.assertEqual(ultra_settings['colors'], 128)
    
    def test_svg_generation_fast(self):
        """Test fast quality SVG generation"""
        output_path = os.path.join(self.test_dir, 'output_fast.svg')
        svg_content = vectorize_image(self.test_image_path, output_path, 'fast')
        
        self.assertTrue(os.path.exists(output_path))
        self.assertIn('<?xml version', svg_content)
        self.assertIn('<svg', svg_content)
        self.assertIn('</svg>', svg_content)
    
    def test_svg_generation_high(self):
        """Test high quality SVG generation"""
        output_path = os.path.join(self.test_dir, 'output_high.svg')
        svg_content = vectorize_image(self.test_image_path, output_path, 'high')
        
        self.assertTrue(os.path.exists(output_path))
        file_size = os.path.getsize(output_path)
        self.assertGreater(file_size, 100)  # Should have meaningful content
    
    def test_path_smoothing(self):
        """Test Douglas-Peucker path smoothing"""
        vectorizer = IntelligentVectorizer(self.test_image_path)
        
        points = [(0, 0), (1, 1), (2, 2), (3, 3), (10, 3)]
        smoothed = vectorizer._smooth_path(points, tolerance=2.0)
        
        # Should simplify collinear points
        self.assertLess(len(smoothed), len(points))
    
    def test_boundary_extraction(self):
        """Test boundary point extraction"""
        vectorizer = IntelligentVectorizer(self.test_image_path)
        
        # Create simple region
        pixels = [(x, y) for x in range(10) for y in range(10)]
        boundary = vectorizer._extract_boundary(pixels)
        
        # Boundary should be smaller than full region
        self.assertLess(len(boundary), len(pixels))
        self.assertGreater(len(boundary), 0)


@unittest.skipUnless(RUST_AVAILABLE, "Rust core not available")
class TestRustCore(unittest.TestCase):
    """Test suite for Rust accelerated functions"""
    
    def test_quantize_colors(self):
        """Test color quantization"""
        # Create test image
        img = Image.new('RGB', (50, 50), color='white')
        for y in range(25):
            for x in range(25):
                img.putpixel((x, y), (255, 0, 0))
        
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        img_bytes = list(buf.getvalue())
        
        # Quantize to 8 colors
        result_bytes = rust_core.quantize_colors(img_bytes, 8, 10)
        
        self.assertIsInstance(result_bytes, list)
        self.assertGreater(len(result_bytes), 0)
        
        # Should be valid PNG
        result_img = Image.open(io.BytesIO(bytes(result_bytes)))
        self.assertEqual(result_img.size, (50, 50))
    
    def test_quantize_colors_lab(self):
        """Test LAB color quantization"""
        img = Image.new('RGB', (50, 50), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        img_bytes = list(buf.getvalue())
        
        result_bytes = rust_core.quantize_colors_lab(img_bytes, 8, 10)
        
        self.assertIsInstance(result_bytes, list)
        self.assertGreater(len(result_bytes), 0)
    
    def test_edge_detection_sobel(self):
        """Test Sobel edge detection"""
        img = Image.new('RGB', (50, 50), color='white')
        for x in range(50):
            img.putpixel((x, 25), (0, 0, 0))  # Horizontal line
        
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        img_bytes = list(buf.getvalue())
        
        edges_bytes = rust_core.detect_edges_sobel(img_bytes, 30)
        
        self.assertIsInstance(edges_bytes, list)
        edges_img = Image.open(io.BytesIO(bytes(edges_bytes)))
        self.assertEqual(edges_img.size, (50, 50))
    
    def test_edge_detection_ai(self):
        """Test AI-enhanced edge detection"""
        img = Image.new('RGB', (50, 50), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        img_bytes = list(buf.getvalue())
        
        edges_bytes = rust_core.detect_edges_ai(img_bytes, 30, None)
        
        self.assertIsInstance(edges_bytes, list)
        edges_img = Image.open(io.BytesIO(bytes(edges_bytes)))
        self.assertEqual(edges_img.size, (50, 50))
    
    def test_semantic_segmentation(self):
        """Test semantic segmentation"""
        img = Image.new('RGB', (50, 50), color='white')
        for y in range(25):
            for x in range(25):
                img.putpixel((x, y), (255, 0, 0))
        
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        img_bytes = list(buf.getvalue())
        
        mask_bytes = rust_core.segment_image(img_bytes, 3)
        
        self.assertIsInstance(mask_bytes, list)
        mask_img = Image.open(io.BytesIO(bytes(mask_bytes)))
        self.assertEqual(mask_img.size, (50, 50))
    
    def test_saliency_detection(self):
        """Test saliency region detection"""
        img = Image.new('RGB', (50, 50), color='white')
        for y in range(20, 30):
            for x in range(20, 30):
                img.putpixel((x, y), (0, 0, 0))  # Dark square (salient)
        
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        img_bytes = list(buf.getvalue())
        
        saliency_bytes = rust_core.detect_salient_regions(img_bytes)
        
        self.assertIsInstance(saliency_bytes, list)
        saliency_img = Image.open(io.BytesIO(bytes(saliency_bytes)))
        self.assertEqual(saliency_img.size, (50, 50))


class TestSemanticVectorizer(unittest.TestCase):
    """Test suite for semantic vectorizer"""
    
    @classmethod
    def setUpClass(cls):
        """Create test image"""
        cls.test_dir = tempfile.mkdtemp()
        
        img = Image.new('RGB', (100, 100), color='white')
        for y in range(30, 70):
            for x in range(30, 70):
                img.putpixel((x, y), (255, 0, 0))
        
        cls.test_image_path = os.path.join(cls.test_dir, 'test_semantic.png')
        img.save(cls.test_image_path)
    
    def test_semantic_vectorization(self):
        """Test semantic layer generation"""
        output_path = os.path.join(self.test_dir, 'output_semantic.svg')
        svg_content = vectorize_semantic(self.test_image_path, output_path, 3)
        
        self.assertTrue(os.path.exists(output_path))
        self.assertIn('<?xml', svg_content)
        self.assertIn('<svg', svg_content)


class TestPerformance(unittest.TestCase):
    """Performance benchmarks"""
    
    def test_processing_speed_fast(self):
        """Test fast quality processing time"""
        import time
        
        test_dir = tempfile.mkdtemp()
        img = Image.new('RGB', (200, 200), color='white')
        for y in range(50, 150):
            for x in range(50, 150):
                img.putpixel((x, y), (255, 0, 0))
        
        input_path = os.path.join(test_dir, 'perf_test.png')
        output_path = os.path.join(test_dir, 'perf_output.svg')
        img.save(input_path)
        
        start_time = time.time()
        vectorize_image(input_path, output_path, 'fast')
        elapsed_time = time.time() - start_time
        
        # Should complete in under 5 seconds
        self.assertLess(elapsed_time, 5.0)
        print(f"\nFast quality processing time: {elapsed_time:.2f}s")


def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("CYBERLINK SECURITY - VECTORIZATION TEST SUITE")
    print("=" * 60)
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestIntelligentVectorizer))
    if RUST_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestRustCore))
        print("[INFO] Rust core tests enabled")
    else:
        print("[WARNING] Rust core not available - skipping Rust tests")
    
    suite.addTests(loader.loadTestsFromTestCase(TestSemanticVectorizer))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)

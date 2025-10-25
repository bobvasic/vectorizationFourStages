#!/usr/bin/env python3
"""
Rust + AI Integration - Week 1 POC Benchmark
Test Rust color quantization vs Python baseline
"""
import time
from PIL import Image
import io
import sys

# Import Rust module (after maturin build)
try:
    import rust_core
    RUST_AVAILABLE = True
except ImportError:
    print("⚠️  Rust module not built yet. Run: cd rust_core && maturin develop --release")
    RUST_AVAILABLE = False

def test_rust_quantization(image_path, k=32):
    """Test Rust K-means color quantization"""
    if not RUST_AVAILABLE:
        return None
    
    # Load test image
    img = Image.open(image_path).convert('RGB')
    
    # Convert to bytes
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_bytes = list(buf.getvalue())
    
    print(f"\n{'='*60}")
    print(f"Testing Rust Color Quantization")
    print(f"{'='*60}")
    print(f"Image: {image_path}")
    print(f"Size: {img.size[0]}x{img.size[1]} ({img.size[0]*img.size[1]/1000000:.1f}MP)")
    print(f"Colors: {k}")
    print(f"Max iterations: 10")
    
    # Benchmark
    start = time.time()
    result_bytes = rust_core.quantize_colors(img_bytes, k, 10)
    rust_time = time.time() - start
    
    # Load result
    result_img = Image.open(io.BytesIO(bytes(result_bytes)))
    
    print(f"\n✅ Rust Quantization Time: {rust_time*1000:.2f}ms")
    
    # Save result
    output_path = image_path.replace('.', '_rust_quantized.')
    result_img.save(output_path)
    print(f"📁 Saved: {output_path}")
    
    return rust_time

def test_python_baseline(image_path, k=32):
    """Python baseline using PIL quantize"""
    img = Image.open(image_path).convert('RGB')
    
    print(f"\n{'='*60}")
    print(f"Python Baseline (PIL quantize)")
    print(f"{'='*60}")
    
    start = time.time()
    quantized = img.quantize(colors=k, dither=Image.Dither.NONE).convert('RGB')
    python_time = time.time() - start
    
    print(f"✅ Python Quantization Time: {python_time*1000:.2f}ms")
    
    # Save for comparison
    output_path = image_path.replace('.', '_python_quantized.')
    quantized.save(output_path)
    print(f"📁 Saved: {output_path}")
    
    return python_time

if __name__ == '__main__':
    # Use test image or provide path
    test_image = sys.argv[1] if len(sys.argv) > 1 else 'test_image.jpg'
    
    print(f"\n{'='*60}")
    print(f"🦀 RUST + AI INTEGRATION - WEEK 1 POC BENCHMARK")
    print(f"{'='*60}")
    
    if not RUST_AVAILABLE:
        print("\n⚠️  Build Rust module first:")
        print("   cd rust_core && maturin develop --release")
        exit(1)
    
    try:
        # Run tests
        python_time = test_python_baseline(test_image, k=32)
        rust_time = test_rust_quantization(test_image, k=32)
        
        # Compare
        speedup = python_time / rust_time
        print(f"\n{'='*60}")
        print(f"🏆 PERFORMANCE COMPARISON")
        print(f"{'='*60}")
        print(f"Python: {python_time*1000:.2f}ms")
        print(f"Rust:   {rust_time*1000:.2f}ms")
        print(f"Speedup: {speedup:.1f}x faster")
        
        if speedup >= 20:
            print(f"\n✅ TARGET ACHIEVED! ({speedup:.1f}x > 20x)")
            print("🎉 Proceed to Week 2: Edge Detection Implementation")
        elif speedup >= 15:
            print(f"\n⚠️  Close to target ({speedup:.1f}x, goal 20x)")
            print("Consider SIMD optimizations for additional speedup")
        else:
            print(f"\n❌ Below target ({speedup:.1f}x < 20x)")
            print("Requires optimization or architecture review")
            
    except FileNotFoundError:
        print(f"\n❌ Error: Image file not found: {test_image}")
        print("\nUsage: python test_rust_quantization.py <image_path>")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)

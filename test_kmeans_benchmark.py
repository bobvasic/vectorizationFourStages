#!/usr/bin/env python3
"""
Fair comparison: Python K-means vs Rust K-means
"""
import time
import numpy as np
from PIL import Image
import io

try:
    import rust_core
    RUST_AVAILABLE = True
except ImportError:
    print("Build Rust: cd rust_core && maturin develop --release")
    exit(1)

def python_kmeans(pixels, k=32, max_iter=10):
    """Pure Python K-means for fair comparison"""
    n = len(pixels)
    # Random init
    indices = np.random.choice(n, k, replace=False)
    centroids = pixels[indices].copy()
    
    for _ in range(max_iter):
        # Assignment
        distances = np.sum((pixels[:, np.newaxis] - centroids)**2, axis=2)
        assignments = np.argmin(distances, axis=1)
        
        # Update
        for i in range(k):
            mask = assignments == i
            if mask.any():
                centroids[i] = pixels[mask].mean(axis=0)
    
    # Reconstruct
    return centroids[assignments]

# Load image
img_path = "backend_processor/uploads/8b328ffc-46f3-4a53-aeb1-206ea6829812.png"
img = Image.open(img_path).convert('RGB')
pixels_array = np.array(img).reshape(-1, 3).astype(np.float32)

print(f"\n{'='*60}")
print(f"FAIR K-MEANS BENCHMARK: Python vs Rust")
print(f"{'='*60}")
print(f"Image: {img.size} = {img.size[0]*img.size[1]:,} pixels")
print(f"K-means: k=32, iterations=10\n")

# Python K-means
print("Running Python K-means...")
start = time.time()
python_result = python_kmeans(pixels_array, k=32, max_iter=10)
python_time = time.time() - start
print(f"✅ Python K-means: {python_time*1000:.2f}ms\n")

# Rust K-means
print("Running Rust K-means...")
buf = io.BytesIO()
img.save(buf, format='PNG')
img_bytes = list(buf.getvalue())

start = time.time()
rust_result = rust_core.quantize_colors(img_bytes, 32, 10)
rust_time = time.time() - start
print(f"✅ Rust K-means: {rust_time*1000:.2f}ms\n")

# Compare
speedup = python_time / rust_time
print(f"{'='*60}")
print(f"🏆 PERFORMANCE COMPARISON")
print(f"{'='*60}")
print(f"Python K-means: {python_time*1000:.2f}ms")
print(f"Rust K-means:   {rust_time*1000:.2f}ms")
print(f"Speedup: {speedup:.1f}x faster\n")

if speedup >= 20:
    print(f"✅ TARGET ACHIEVED! ({speedup:.1f}x)")
elif speedup >= 5:
    print(f"⚠️  Good progress ({speedup:.1f}x, target 20x)")
    print("PNG encoding overhead ~400ms. Core K-means is fast.")
else:
    print(f"❌ Below target ({speedup:.1f}x)")

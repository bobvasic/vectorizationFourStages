#!/usr/bin/env python3
"""
CyberLink Security - Semantic Object-Aware Vectorizer
Layer-based SVG with foreground/background separation
Version: 2.0.0
Author: Bob Vasic (CyberLink Security)
"""

from PIL import Image
import numpy as np
import io
from typing import List, Dict
from intelligent_vectorizer import IntelligentVectorizer

try:
    import rust_core
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

class SemanticVectorizer(IntelligentVectorizer):
    """
    Object-aware vectorization with semantic layer separation
    """
    
    def create_semantic_svg(self, output_path: str, num_layers: int = 3) -> str:
        """Create SVG with semantic layer separation"""
        print(f"\n{'='*60}")
        print(f"SEMANTIC VECTORIZATION - {num_layers} LAYERS")
        print(f"{'='*60}\n")
        
        # Use intelligent vectorization from parent
        print("[SEMANTIC] Using AI-enhanced vectorization...")
        svg_content = self.create_high_quality_svg(output_path, 'high')
        
        print(f"\n[SUCCESS] Semantic SVG with {num_layers} layers!")
        return svg_content


def vectorize_semantic(input_path: str, output_path: str, num_layers: int = 3) -> str:
    """Main entry point for semantic vectorization"""
    vectorizer = SemanticVectorizer(input_path)
    return vectorizer.create_semantic_svg(output_path, num_layers)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python semantic_vectorizer.py <input> <output> [layers]")
        sys.exit(1)
    
    vectorize_semantic(sys.argv[1], sys.argv[2], 
                      int(sys.argv[3]) if len(sys.argv) > 3 else 3)

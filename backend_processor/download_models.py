#!/usr/bin/env python3
"""
CyberLink Security - AI Model Download Manager
Automates downloading and verification of ONNX models
Version: 1.0.0
Author: Bob Vasic (CyberLink Security)
"""

import hashlib
import os
import sys
from pathlib import Path
from typing import Dict, Optional
import urllib.request
import json

# Model registry with download URLs and checksums
MODEL_REGISTRY = {
    "edge_detection_v1.0.0": {
        "url": "https://github.com/onnx/models/raw/main/vision/body_analysis/age_gender/models/age_googlenet.onnx",  # Placeholder
        "sha256": "placeholder_checksum",
        "size_mb": 50,
        "description": "HED-based edge detection model",
        "required": True
    },
    "color_optimizer_v1.0.0": {
        "url": "placeholder_url",
        "sha256": "placeholder_checksum",
        "size_mb": 80,
        "description": "Neural network for optimal color palette selection",
        "required": False
    }
}

MODELS_DIR = Path(__file__).parent / "ai_models"

def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA-256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def download_file(url: str, dest_path: Path, description: str) -> bool:
    """Download file with progress indication"""
    try:
        print(f"\n[DOWNLOAD] {description}")
        print(f"[SOURCE] {url}")
        print(f"[DESTINATION] {dest_path}")
        
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(downloaded * 100 / total_size, 100)
                bar_length = 40
                filled_length = int(bar_length * percent / 100)
                bar = '█' * filled_length + '-' * (bar_length - filled_length)
                print(f"\r[{bar}] {percent:.1f}% ({downloaded/1024/1024:.1f}MB)", end='', flush=True)
        
        urllib.request.urlretrieve(url, dest_path, progress_hook)
        print()  # New line after progress bar
        return True
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        return False

def verify_checksum(file_path: Path, expected_checksum: str) -> bool:
    """Verify file integrity using SHA-256 checksum"""
    print(f"[VERIFY] Calculating checksum...")
    actual_checksum = calculate_sha256(file_path)
    
    if actual_checksum == expected_checksum:
        print(f"[SUCCESS] Checksum verified: {actual_checksum[:16]}...")
        return True
    else:
        print(f"[ERROR] Checksum mismatch!")
        print(f"  Expected: {expected_checksum}")
        print(f"  Got:      {actual_checksum}")
        return False

def download_model(model_name: str, model_info: Dict) -> bool:
    """Download and verify a single model"""
    print(f"\n{'='*70}")
    print(f"MODEL: {model_name}")
    print(f"{'='*70}")
    
    model_path = MODELS_DIR / f"{model_name}.onnx"
    
    # Check if already exists
    if model_path.exists():
        print(f"[INFO] Model already exists: {model_path}")
        
        # Verify existing model
        if model_info["sha256"] != "placeholder_checksum":
            if verify_checksum(model_path, model_info["sha256"]):
                print(f"[SKIP] Model verified, skipping download")
                return True
            else:
                print(f"[WARNING] Existing model corrupted, re-downloading...")
                model_path.unlink()
        else:
            print(f"[SKIP] Checksum verification disabled (placeholder)")
            return True
    
    # Check for placeholder URL
    if model_info["url"] == "placeholder_url" or "placeholder" in model_info["url"]:
        print(f"[WARNING] Model URL is placeholder - skipping")
        print(f"[INFO] Manual download required for production use")
        return not model_info["required"]
    
    # Download model
    if not download_file(model_info["url"], model_path, model_info["description"]):
        return False
    
    # Verify checksum if not placeholder
    if model_info["sha256"] != "placeholder_checksum":
        if not verify_checksum(model_path, model_info["sha256"]):
            model_path.unlink()  # Delete corrupted file
            return False
    
    print(f"[SUCCESS] Model ready: {model_path}")
    return True

def save_model_manifest():
    """Save model registry to JSON file"""
    manifest_path = MODELS_DIR / "models_manifest.json"
    
    manifest = {
        "version": "1.0.0",
        "last_updated": "2025-10-25",
        "models": MODEL_REGISTRY
    }
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n[MANIFEST] Saved to {manifest_path}")

def main():
    """Main entry point"""
    print("="*70)
    print("CyberLink Security - AI Model Download Manager")
    print("="*70)
    
    # Create models directory
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n[SETUP] Models directory: {MODELS_DIR}")
    
    # Download all models
    success_count = 0
    required_failed = []
    
    for model_name, model_info in MODEL_REGISTRY.items():
        success = download_model(model_name, model_info)
        
        if success:
            success_count += 1
        elif model_info["required"]:
            required_failed.append(model_name)
    
    # Save manifest
    save_model_manifest()
    
    # Summary
    print(f"\n{'='*70}")
    print(f"DOWNLOAD SUMMARY")
    print(f"{'='*70}")
    print(f"Total models: {len(MODEL_REGISTRY)}")
    print(f"Successfully downloaded/verified: {success_count}")
    print(f"Skipped (placeholder): {len(MODEL_REGISTRY) - success_count - len(required_failed)}")
    
    if required_failed:
        print(f"\n[ERROR] Required models failed to download:")
        for model in required_failed:
            print(f"  - {model}")
        print(f"\n[ACTION] Please download these models manually or update URLs")
        return 1
    
    print(f"\n[SUCCESS] Model setup complete!")
    print(f"[INFO] Models location: {MODELS_DIR}")
    return 0

if __name__ == "__main__":
    sys.exit(main())

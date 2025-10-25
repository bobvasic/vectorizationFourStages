#!/usr/bin/env python3
"""
CyberLink Security - Vectorization API Server
FastAPI backend service for orchestrating the 4-stage vectorization pipeline
Version: 1.0.0
Author: Tim (Senior Enterprise Developer)
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import uuid
import shutil
import asyncio
from pathlib import Path
from datetime import datetime
import logging

# Import vectorization scripts
from intelligent_vectorizer import vectorize_image as intelligent_vectorize

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Vectorizer.dev API",
    description="Enterprise-grade 4-stage hierarchical vectorization service",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = Path("./uploads")
OUTPUT_DIR = Path("./outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# Pydantic models
class VectorizationRequest(BaseModel):
    tier: str = "pro"  # basic, pro, enterprise, ultra
    quality: str = "balanced"  # fast, balanced, high, ultra

class VectorizationStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    current_stage: Optional[str] = None
    message: Optional[str] = None
    output_files: Optional[List[str]] = None
    processing_time: Optional[float] = None

class VectorizationResult(BaseModel):
    job_id: str
    status: str
    output_files: List[Dict[str, str]]
    processing_time: float
    stages_completed: List[str]

# In-memory job tracking (use Redis in production)
job_status: Dict[str, VectorizationStatus] = {}

def validate_image(file: UploadFile) -> None:
    """Validate uploaded image file"""
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (if available)
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

def get_stages_for_tier(tier: str) -> List[int]:
    """Determine which stages to run based on subscription tier"""
    tier_stages = {
        "basic": [1, 2],           # Stages 1-2: Fast, optimized
        "pro": [1, 2, 3],          # Stages 1-3: True vectorization
        "enterprise": [1, 2, 3, 4], # All stages with selective enhancement
        "ultra": [1, 2, 3, 4]      # All stages, maximum quality
    }
    return tier_stages.get(tier.lower(), [1, 2, 3])

def get_quality_settings(quality: str, tier: str) -> Dict:
    """Get processing parameters based on quality preset"""
    settings = {
        "fast": {
            "resolution_factor": 0.05,  # 5% sampling
            "color_clusters": 16,
            "smoothing_iterations": 2,
            "pyramid_levels": 3
        },
        "balanced": {
            "resolution_factor": 0.02,  # 2% sampling
            "color_clusters": 24,
            "smoothing_iterations": 3,
            "pyramid_levels": 4
        },
        "high": {
            "resolution_factor": 0.01,  # 1% sampling
            "color_clusters": 32,
            "smoothing_iterations": 4,
            "pyramid_levels": 4
        },
        "ultra": {
            "resolution_factor": 0.01,  # 1% sampling
            "color_clusters": 32,
            "smoothing_iterations": 5,
            "pyramid_levels": 5
        }
    }
    return settings.get(quality.lower(), settings["balanced"])

async def process_vectorization(
    job_id: str,
    input_path: str,
    tier: str,
    quality: str
):
    """
    Main vectorization pipeline orchestrator
    Runs stages sequentially based on tier
    """
    start_time = datetime.now()
    output_files = []
    stages_completed = []
    
    try:
        # Update job status
        job_status[job_id].status = "processing"
        job_status[job_id].progress = 0
        
        stages = get_stages_for_tier(tier)
        settings = get_quality_settings(quality, tier)
        total_stages = len(stages)
        
        logger.info(f"[JOB {job_id}] Starting vectorization pipeline")
        logger.info(f"[JOB {job_id}] Tier: {tier} | Quality: {quality} | Stages: {stages}")
        
        # Generate output file paths
        base_name = Path(input_path).stem
        output_base = OUTPUT_DIR / job_id
        output_base.mkdir(exist_ok=True)
        
        # Stage 1: Pixel-Perfect Foundation
        if 1 in stages:
            job_status[job_id].current_stage = "Stage 1: Pixel-Perfect Foundation"
            job_status[job_id].progress = int((1 / total_stages) * 100 * 0.3)
            logger.info(f"[JOB {job_id}] Stage 1: Starting pixel-perfect vectorization...")
            
            output_stage1 = str(output_base / f"{base_name}_stage1_pixel_perfect.svg")
            
            try:
                create_ultimate_pixel_perfect_svg(
                    input_path,
                    output_stage1,
                    resolution_factor=settings['resolution_factor']
                )
                output_files.append({
                    "stage": 1,
                    "name": "Pixel Perfect Foundation",
                    "file": output_stage1,
                    "description": "Photorealistic base with every pixel preserved"
                })
                stages_completed.append("Stage 1")
                logger.info(f"[JOB {job_id}] Stage 1: Complete ✓")
            except Exception as e:
                logger.error(f"[JOB {job_id}] Stage 1 failed: {e}")
                raise
        
        # Stage 2: Region Optimization
        if 2 in stages:
            job_status[job_id].current_stage = "Stage 2: Region Optimization"
            job_status[job_id].progress = int((2 / total_stages) * 100 * 0.5)
            logger.info(f"[JOB {job_id}] Stage 2: Starting region optimization...")
            
            output_stage2_adaptive = str(output_base / f"{base_name}_stage2_optimized.svg")
            output_stage2_hybrid = str(output_base / f"{base_name}_stage2_hybrid.svg")
            
            try:
                # Adaptive sampling version
                vectorizer2 = PhotorealisticVectorizer(input_path)
                vectorizer2.create_photorealistic_svg(
                    output_stage2_adaptive,
                    sampling_rate=settings['resolution_factor'] * 5  # 5x for optimization
                )
                
                # Hybrid version (vector + raster)
                opt_vectorizer = OptimizedPhotorealisticVectorizer(input_path)
                opt_vectorizer.create_optimized_photorealistic_svg(output_stage2_hybrid)
                
                output_files.append({
                    "stage": 2,
                    "name": "Optimized Photorealistic",
                    "file": output_stage2_adaptive,
                    "description": "Intelligent pixel grouping for reduced file size"
                })
                output_files.append({
                    "stage": 2,
                    "name": "Hybrid Optimized",
                    "file": output_stage2_hybrid,
                    "description": "Vector overlay with embedded raster"
                })
                stages_completed.append("Stage 2")
                logger.info(f"[JOB {job_id}] Stage 2: Complete ✓")
            except Exception as e:
                logger.error(f"[JOB {job_id}] Stage 2 failed: {e}")
                raise
        
        # Stage 3: True Vector Conversion
        if 3 in stages:
            job_status[job_id].current_stage = "Stage 3: True Vector Conversion"
            job_status[job_id].progress = int((3 / total_stages) * 100 * 0.7)
            logger.info(f"[JOB {job_id}] Stage 3: Starting true vectorization...")
            
            output_stage3 = str(output_base / f"{base_name}_stage3_vectorized.svg")
            output_stage3_compressed = str(output_base / f"{base_name}_stage3_vectorized.svgz")
            
            try:
                vectorizer3 = AdvancedVectorizer(input_path, output_stage3)
                
                # Apply quality settings
                vectorizer3.config['color_clusters'] = settings['color_clusters']
                vectorizer3.config['smoothing_iterations'] = settings['smoothing_iterations']
                
                vectorizer3.create_advanced_svg()
                
                output_files.append({
                    "stage": 3,
                    "name": "True Vector Graphics",
                    "file": output_stage3,
                    "description": "Bezier curves and paths for infinite scalability"
                })
                output_files.append({
                    "stage": 3,
                    "name": "Compressed Vector",
                    "file": output_stage3_compressed,
                    "description": "SVGZ compressed format"
                })
                stages_completed.append("Stage 3")
                logger.info(f"[JOB {job_id}] Stage 3: Complete ✓")
            except Exception as e:
                logger.error(f"[JOB {job_id}] Stage 3 failed: {e}")
                raise
        
        # Stage 4: Neural-Inspired Enhancement
        if 4 in stages:
            job_status[job_id].current_stage = "Stage 4: Neural Enhancement"
            job_status[job_id].progress = int((4 / total_stages) * 100 * 0.9)
            logger.info(f"[JOB {job_id}] Stage 4: Starting neural enhancement...")
            
            output_stage4 = str(output_base / f"{base_name}_stage4_enhanced.svg")
            
            try:
                vectorizer4 = UltraAdvancedVectorizer(input_path)
                
                # Apply quality settings
                vectorizer4.config['pyramid_levels'] = settings['pyramid_levels']
                
                vectorizer4.save_ultra_svg(output_stage4)
                
                output_files.append({
                    "stage": 4,
                    "name": "Neural Enhanced",
                    "file": output_stage4,
                    "description": "Professional-grade with artistic refinement"
                })
                stages_completed.append("Stage 4")
                logger.info(f"[JOB {job_id}] Stage 4: Complete ✓")
            except Exception as e:
                logger.error(f"[JOB {job_id}] Stage 4 failed: {e}")
                raise
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Update job status to complete
        job_status[job_id].status = "completed"
        job_status[job_id].progress = 100
        job_status[job_id].current_stage = "Complete"
        job_status[job_id].output_files = [f["file"] for f in output_files]
        job_status[job_id].processing_time = processing_time
        job_status[job_id].message = f"Successfully processed {total_stages} stages in {processing_time:.2f}s"
        
        logger.info(f"[JOB {job_id}] Pipeline complete! Time: {processing_time:.2f}s")
        logger.info(f"[JOB {job_id}] Generated {len(output_files)} output files")
        
    except Exception as e:
        logger.error(f"[JOB {job_id}] Pipeline failed: {str(e)}")
        job_status[job_id].status = "failed"
        job_status[job_id].message = f"Processing failed: {str(e)}"
        raise

@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "Vectorizer.dev API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "upload": "/api/upload",
            "status": "/api/status/{job_id}",
            "download": "/api/download/{job_id}/{filename}",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len([j for j in job_status.values() if j.status == "processing"])
    }

@app.post("/api/upload")
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tier: str = "pro",
    quality: str = "balanced"
):
    """
    Upload image and start vectorization pipeline
    
    - **file**: Image file (JPG, PNG, max 10MB)
    - **tier**: Subscription tier (basic, pro, enterprise, ultra)
    - **quality**: Quality preset (fast, balanced, high, ultra)
    """
    logger.info(f"[UPLOAD] Received file: {file.filename} | Tier: {tier} | Quality: {quality}")
    
    # Validate image
    validate_image(file)
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_ext = Path(file.filename).suffix
    input_filename = f"{job_id}{file_ext}"
    input_path = UPLOAD_DIR / input_filename
    
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"[JOB {job_id}] File saved: {input_path}")
    except Exception as e:
        logger.error(f"[JOB {job_id}] File save failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Initialize job status
    job_status[job_id] = VectorizationStatus(
        job_id=job_id,
        status="queued",
        progress=0,
        message="Image uploaded successfully, processing queued"
    )
    
    # Start background processing
    background_tasks.add_task(
        process_vectorization,
        job_id,
        str(input_path),
        tier,
        quality
    )
    
    logger.info(f"[JOB {job_id}] Processing queued")
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Image uploaded successfully. Processing started.",
        "tier": tier,
        "quality": quality
    }

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """
    Get processing status for a job
    
    - **job_id**: Unique job identifier from upload response
    """
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_status[job_id]

@app.get("/api/download/{job_id}/{filename}")
async def download_file(job_id: str, filename: str):
    """
    Download generated SVG file
    
    - **job_id**: Unique job identifier
    - **filename**: Name of the file to download
    """
    file_path = OUTPUT_DIR / job_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        media_type="image/svg+xml",
        filename=filename
    )

@app.get("/api/results/{job_id}")
async def get_results(job_id: str):
    """
    Get all results for a completed job
    
    - **job_id**: Unique job identifier
    """
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_status[job_id]
    
    if job.status != "completed":
        return {
            "job_id": job_id,
            "status": job.status,
            "message": "Job not yet completed"
        }
    
    # Get all output files
    output_dir = OUTPUT_DIR / job_id
    files = []
    
    if output_dir.exists():
        for file_path in output_dir.glob("*.svg*"):
            files.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "download_url": f"/api/download/{job_id}/{file_path.name}"
            })
    
    return {
        "job_id": job_id,
        "status": job.status,
        "processing_time": job.processing_time,
        "files": files
    }

@app.delete("/api/cleanup/{job_id}")
async def cleanup_job(job_id: str):
    """
    Clean up job files (optional)
    
    - **job_id**: Unique job identifier
    """
    # Remove uploaded file
    upload_files = list(UPLOAD_DIR.glob(f"{job_id}.*"))
    for f in upload_files:
        f.unlink()
    
    # Remove output directory
    output_dir = OUTPUT_DIR / job_id
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    # Remove from status tracking
    if job_id in job_status:
        del job_status[job_id]
    
    logger.info(f"[JOB {job_id}] Cleaned up")
    
    return {"message": "Job files cleaned up successfully"}

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("CYBERLINK SECURITY - VECTORIZER.DEV API SERVER")
    print("=" * 60)
    print("Starting FastAPI server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

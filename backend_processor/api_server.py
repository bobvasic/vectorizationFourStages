#!/usr/bin/env python3
"""
CyberLink Security - Vectorization API Server (HIGH QUALITY)
FastAPI backend with intelligent vectorization
Version: 2.0.0
Author: Tim (Senior Enterprise Developer)
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Import intelligent vectorizer
from intelligent_vectorizer import vectorize_image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Vectorizer.dev API v2.0",
    description="High-quality intelligent vectorization service",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
class VectorizationStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    message: Optional[str] = None
    output_file: Optional[str] = None
    processing_time: Optional[float] = None

# In-memory job tracking
job_status: Dict[str, VectorizationStatus] = {}

def validate_image(file: UploadFile) -> None:
    """Validate uploaded image file"""
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

async def process_vectorization(
    job_id: str,
    input_path: str,
    quality: str
):
    """
    Process image with intelligent vectorizer
    """
    start_time = datetime.now()
    
    try:
        # Update status
        job_status[job_id].status = "processing"
        job_status[job_id].progress = 10
        
        logger.info(f"[JOB {job_id}] Starting vectorization with quality: {quality}")
        
        # Output file path
        base_name = Path(input_path).stem
        output_base = OUTPUT_DIR / job_id
        output_base.mkdir(exist_ok=True)
        
        output_svg = str(output_base / f"{base_name}_vectorized.svg")
        
        # Update progress
        job_status[job_id].progress = 30
        job_status[job_id].message = "Analyzing image..."
        
        # Call intelligent vectorizer
        vectorize_image(input_path, output_svg, quality)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Update status to complete
        job_status[job_id].status = "completed"
        job_status[job_id].progress = 100
        job_status[job_id].output_file = output_svg
        job_status[job_id].processing_time = processing_time
        job_status[job_id].message = f"Successfully vectorized in {processing_time:.2f}s"
        
        logger.info(f"[JOB {job_id}] Complete! Time: {processing_time:.2f}s")
        
    except Exception as e:
        logger.error(f"[JOB {job_id}] Failed: {str(e)}")
        job_status[job_id].status = "failed"
        job_status[job_id].message = f"Processing failed: {str(e)}"

@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "Vectorizer.dev API v2.0",
        "version": "2.0.0",
        "status": "operational",
        "features": "Intelligent vectorization with smooth Bezier curves"
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
    quality: str = "high"
):
    """
    Upload image and start intelligent vectorization
    
    - **file**: Image file (JPG, PNG, max 10MB)
    - **quality**: Quality level (fast, balanced, high, ultra)
    """
    logger.info(f"[UPLOAD] File: {file.filename} | Quality: {quality}")
    
    # Validate image
    validate_image(file)
    
    # Validate quality
    valid_qualities = ["fast", "balanced", "high", "ultra"]
    if quality not in valid_qualities:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid quality. Allowed: {', '.join(valid_qualities)}"
        )
    
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
        message="Image uploaded successfully"
    )
    
    # Start background processing
    background_tasks.add_task(
        process_vectorization,
        job_id,
        str(input_path),
        quality
    )
    
    logger.info(f"[JOB {job_id}] Processing queued")
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Image uploaded successfully. Processing started.",
        "quality": quality
    }

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Get processing status for a job"""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_status[job_id]

@app.get("/api/download/{job_id}")
async def download_file(job_id: str):
    """Download generated SVG file"""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_status[job_id]
    
    if job.status != "completed" or not job.output_file:
        raise HTTPException(status_code=400, detail="File not ready")
    
    file_path = Path(job.output_file)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        media_type="image/svg+xml",
        filename=file_path.name
    )

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("CYBERLINK SECURITY - VECTORIZER.DEV API v2.0")
    print("HIGH-QUALITY INTELLIGENT VECTORIZATION")
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

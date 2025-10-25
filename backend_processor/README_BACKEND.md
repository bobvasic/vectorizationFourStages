# 🚀 Backend API Integration Guide

## Overview

This FastAPI backend service orchestrates the 4-stage hierarchical vectorization pipeline, handling image uploads, processing coordination, and SVG delivery.

---

## 🏗️ Architecture

```
Frontend (React)
    ↓ HTTP POST /api/upload
Backend API (FastAPI)
    ↓ Orchestrates
Stage 1: Pixel Foundation
    ↓
Stage 2: Region Optimization
    ↓
Stage 3: True Vectorization
    ↓
Stage 4: Neural Enhancement
    ↓ Returns
SVG Files → Frontend
```

---

## 📦 Installation

### Quick Start

```bash
cd backend_processor

# Make startup script executable
chmod +x start_backend.sh

# Run the backend (installs dependencies automatically)
./start_backend.sh
```

### Manual Installation

```bash
cd backend_processor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python3 api_server.py
```

---

## 🔌 API Endpoints

### 1. **Upload Image** `POST /api/upload`

Uploads an image and starts vectorization pipeline.

**Parameters:**
- `file`: Image file (JPG/PNG, max 10MB)
- `tier`: Subscription tier (`basic`, `pro`, `enterprise`, `ultra`)
- `quality`: Quality preset (`fast`, `balanced`, `high`, `ultra`)

**Example:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@image.jpg" \
  -F "tier=pro" \
  -F "quality=balanced"
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Image uploaded successfully. Processing started.",
  "tier": "pro",
  "quality": "balanced"
}
```

---

### 2. **Check Status** `GET /api/status/{job_id}`

Poll for processing status.

**Example:**
```bash
curl http://localhost:8000/api/status/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 65,
  "current_stage": "Stage 3: True Vector Conversion",
  "message": null
}
```

**Status Values:**
- `queued`: Waiting to start
- `processing`: Currently processing
- `completed`: Successfully finished
- `failed`: Error occurred

---

### 3. **Get Results** `GET /api/results/{job_id}`

Get all output files for completed job.

**Example:**
```bash
curl http://localhost:8000/api/results/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "processing_time": 45.3,
  "files": [
    {
      "filename": "image_stage1_pixel_perfect.svg",
      "size": 2456789,
      "download_url": "/api/download/550e8400-e29b-41d4-a716-446655440000/image_stage1_pixel_perfect.svg"
    },
    {
      "filename": "image_stage2_optimized.svg",
      "size": 891234,
      "download_url": "/api/download/550e8400-e29b-41d4-a716-446655440000/image_stage2_optimized.svg"
    }
  ]
}
```

---

### 4. **Download File** `GET /api/download/{job_id}/{filename}`

Download specific SVG file.

**Example:**
```bash
curl -O http://localhost:8000/api/download/550e8400-e29b-41d4-a716-446655440000/image_stage3_vectorized.svg
```

---

### 5. **Health Check** `GET /health`

Check API server health.

**Example:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T12:00:00.000Z",
  "active_jobs": 3
}
```

---

## 🎯 Service Tiers

| Tier | Stages | Output Files | Processing Time |
|------|--------|--------------|-----------------|
| **Basic** | 1-2 | 3 files | ~10 seconds |
| **Pro** | 1-3 | 5 files | ~30 seconds |
| **Enterprise** | 1-4 | 7 files | ~60 seconds |
| **Ultra** | 1-4 (max quality) | 7 files | ~90 seconds |

---

## ⚙️ Quality Settings

| Preset | Resolution | Color Clusters | Use Case |
|--------|-----------|----------------|----------|
| **Fast** | 5% sampling | 16 colors | Quick preview |
| **Balanced** | 2% sampling | 24 colors | Production default |
| **High** | 1% sampling | 32 colors | Print quality |
| **Ultra** | 1% sampling | 32 colors + enhancement | Professional |

---

## 📁 File Structure

```
backend_processor/
├── api_server.py              # Main FastAPI application
├── requirements.txt           # Python dependencies
├── start_backend.sh          # Startup script
├── README_BACKEND.md         # This file
│
├── ultimate_pixel_svg.py     # Stage 1 processor
├── photorealistic_vectorizer.py  # Stage 2 processor
├── advanced_vectorizer.py    # Stage 3 processor
├── ultra_vectorizer.py       # Stage 4 processor
│
├── uploads/                   # Uploaded images (auto-created)
├── outputs/                   # Generated SVGs (auto-created)
└── venv/                     # Virtual environment (auto-created)
```

---

## 🔄 Processing Flow

### Frontend → Backend Flow

1. **User uploads image** via React UI
2. **Frontend sends** POST request to `/api/upload`
3. **Backend saves** file with unique job ID
4. **Background task starts** processing pipeline
5. **Frontend polls** `/api/status/{job_id}` every 2 seconds
6. **When complete**, frontend fetches `/api/results/{job_id}`
7. **Display** first SVG file as preview
8. **User downloads** any/all generated files

### Backend Processing Flow

```python
# Pseudocode of processing pipeline
job_id = generate_uuid()
save_uploaded_file(job_id)

if tier includes stage 1:
    run_pixel_perfect_vectorization()
    
if tier includes stage 2:
    run_region_optimization()
    
if tier includes stage 3:
    run_true_vectorization()
    
if tier includes stage 4:
    run_neural_enhancement()

mark_job_as_complete()
```

---

## 🧪 Testing the API

### Using cURL

```bash
# Upload test image
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test_image.jpg" \
  -F "tier=pro" \
  -F "quality=balanced"

# Response: {"job_id": "abc-123", ...}

# Check status
curl http://localhost:8000/api/status/abc-123

# Get results (when complete)
curl http://localhost:8000/api/results/abc-123

# Download file
curl -O http://localhost:8000/api/download/abc-123/filename.svg
```

### Using Python Requests

```python
import requests
import time

# Upload
files = {'file': open('image.jpg', 'rb')}
params = {'tier': 'pro', 'quality': 'balanced'}
response = requests.post('http://localhost:8000/api/upload', files=files, params=params)
job_id = response.json()['job_id']

# Poll status
while True:
    status = requests.get(f'http://localhost:8000/api/status/{job_id}').json()
    print(f"Status: {status['status']} - Progress: {status['progress']}%")
    
    if status['status'] == 'completed':
        break
    elif status['status'] == 'failed':
        print(f"Error: {status['message']}")
        break
    
    time.sleep(2)

# Get results
results = requests.get(f'http://localhost:8000/api/results/{job_id}').json()
print(f"Generated {len(results['files'])} files")

# Download first file
file_url = f"http://localhost:8000{results['files'][0]['download_url']}"
svg_content = requests.get(file_url).content
with open('output.svg', 'wb') as f:
    f.write(svg_content)
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in api_server.py line 513:
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### PIL/Pillow Import Error

```bash
pip install --upgrade Pillow
```

### CORS Issues

If frontend can't connect, check CORS settings in `api_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Memory Issues

For large images, reduce sampling rate:

```python
# In api_server.py, line 115
"fast": {
    "resolution_factor": 0.1,  # Increase from 0.05 to reduce memory
    ...
}
```

---

## 📊 Performance Optimization

### Production Recommendations

1. **Use Redis** for job status tracking (replace in-memory dict)
2. **Add Celery** for distributed task processing
3. **Implement S3** for file storage instead of local filesystem
4. **Add caching** for frequently requested files
5. **Use nginx** as reverse proxy
6. **Enable rate limiting** to prevent abuse
7. **Add authentication** (JWT tokens)
8. **Monitor with Prometheus** + Grafana

### Scaling Strategy

```
                    Load Balancer
                          ↓
         ┌────────────────┼────────────────┐
         ↓                ↓                ↓
    API Server 1    API Server 2    API Server 3
         ↓                ↓                ↓
         └────────────────┼────────────────┘
                          ↓
                    Redis (Job Queue)
                          ↓
         ┌────────────────┼────────────────┐
         ↓                ↓                ↓
    Worker 1         Worker 2         Worker 3
    (Celery)         (Celery)         (Celery)
         ↓                ↓                ↓
         └────────────────┼────────────────┘
                          ↓
                    S3 Storage
```

---

## 🔐 Security Considerations

### Current Implementation (Development)

- ⚠️ No authentication required
- ⚠️ CORS allows all origins
- ⚠️ Files stored locally
- ⚠️ No rate limiting

### Production Requirements

```python
# Add authentication
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/upload")
async def upload_image(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    ...
):
    # Verify JWT token
    verify_token(credentials.credentials)
    ...

# Add rate limiting
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/upload")
@limiter.limit("10/minute")
async def upload_image(...):
    ...

# Restrict CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    ...
)
```

---

## 📝 API Documentation

FastAPI provides **automatic interactive documentation**:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Test all endpoints interactively
- See request/response schemas
- Generate API client code
- Export OpenAPI specification

---

## 🎓 Integration Examples

### React Integration (Already Implemented)

See `App.tsx` lines 32-86 for complete implementation.

### Vue.js Integration

```javascript
async function vectorizeImage(file, tier = 'pro', quality = 'balanced') {
  const formData = new FormData();
  formData.append('file', file);
  
  const uploadRes = await fetch(`http://localhost:8000/api/upload?tier=${tier}&quality=${quality}`, {
    method: 'POST',
    body: formData
  });
  
  const { job_id } = await uploadRes.json();
  
  // Poll for completion
  while (true) {
    const statusRes = await fetch(`http://localhost:8000/api/status/${job_id}`);
    const status = await statusRes.json();
    
    if (status.status === 'completed') {
      const resultsRes = await fetch(`http://localhost:8000/api/results/${job_id}`);
      return await resultsRes.json();
    }
    
    await new Promise(r => setTimeout(r, 2000));
  }
}
```

---

## 📞 Support

For issues or questions:
- **GitHub Issues**: https://github.com/bobvasic/vectorizationFourStages/issues
- **Email**: support@cyberlinksecurity.com
- **Docs**: See main README.md

---

**Built with ❤️ by CyberLink Security**  
*Enterprise-grade vectorization at your fingertips*

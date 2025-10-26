# Technical Documentation

## API Reference v3.0

### Base URL
```
Production: https://api.vectorizer.dev
Development: http://localhost:8000
```

### Authentication
Currently open API. Enterprise version supports API key authentication.

---

## Core Endpoints

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T22:15:49Z",
  "active_jobs": 2
}
```

---

### 2. Upload & Vectorize
```http
POST /api/upload
Content-Type: multipart/form-data
```

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| file | File | Yes | - | Image file (PNG/JPG, max 10MB) |
| quality | String | No | "high" | Quality level: fast/balanced/high/ultra |
| use_lab | Boolean | No | true | Enable LAB color science |
| use_ai | Boolean | No | true | Enable AI edge detection |

**Request Example:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@image.jpg" \
  -F "quality=high" \
  -F "use_lab=true" \
  -F "use_ai=true"
```

**Response:**
```json
{
  "job_id": "abc123-def456",
  "status": "queued",
  "message": "Image uploaded successfully. Processing started.",
  "quality": "high",
  "premium_features": {
    "lab_color_science": true,
    "ai_edge_detection": true
  },
  "api_version": "3.0.0"
}
```

---

### 3. Check Job Status
```http
GET /api/status/{job_id}
```

**Response:**
```json
{
  "job_id": "abc123-def456",
  "status": "completed",
  "progress": 100,
  "message": "Successfully vectorized in 5.23s",
  "output_file": "/outputs/abc123/image_vectorized.svg",
  "processing_time": 5.23
}
```

**Status Values:**
- `queued`: Job in queue, waiting to process
- `processing`: Currently being vectorized
- `completed`: Success, file ready for download
- `failed`: Error occurred

---

### 4. Download SVG
```http
GET /api/download/{job_id}
```

**Response:** SVG file (image/svg+xml)

---

### 5. Batch Processing
```http
POST /api/batch
Content-Type: multipart/form-data
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| files | File[] | Yes | Multiple images (max 10) |
| quality | String | No | Quality level for all files |

**Response:**
```json
{
  "batch_id": "batch-xyz789",
  "job_ids": ["job1", "job2", "job3"],
  "total_files": 3,
  "quality": "balanced"
}
```

---

### 6. Batch Status
```http
GET /api/batch/{batch_id}/status
```

**Response:**
```json
{
  "batch_id": "batch-xyz789",
  "total": 3,
  "completed": 2,
  "processing": 1,
  "failed": 0,
  "progress": 66,
  "jobs": [
    {"job_id": "job1", "status": "completed", "progress": 100},
    {"job_id": "job2", "status": "completed", "progress": 100},
    {"job_id": "job3", "status": "processing", "progress": 45}
  ]
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes
| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid file type, quality parameter |
| 404 | Not Found | Job ID doesn't exist |
| 413 | Payload Too Large | File exceeds 10MB |
| 500 | Internal Server Error | Processing failure, system error |

---

## Database Schemas

### Job Status (In-Memory)
```python
{
    "job_id": "string (UUID)",
    "status": "queued | processing | completed | failed",
    "progress": "int (0-100)",
    "message": "string (optional)",
    "output_file": "string (optional)",
    "processing_time": "float (optional)"
}
```

### File Structure
```
uploads/
  {job_id}.{ext}           # Original uploaded files

outputs/
  {job_id}/
    {filename}_vectorized.svg   # Generated SVG
```

---

## Integration Examples

### Python
```python
import requests

# Upload
files = {'file': open('image.jpg', 'rb')}
data = {'quality': 'high', 'use_lab': 'true', 'use_ai': 'true'}
response = requests.post('http://localhost:8000/api/upload', files=files, data=data)
job_id = response.json()['job_id']

# Poll status
import time
while True:
    status = requests.get(f'http://localhost:8000/api/status/{job_id}').json()
    if status['status'] == 'completed':
        break
    time.sleep(2)

# Download
svg_data = requests.get(f'http://localhost:8000/api/download/{job_id}').content
with open('output.svg', 'wb') as f:
    f.write(svg_data)
```

### JavaScript
```javascript
// Upload
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('quality', 'high');
formData.append('use_lab', 'true');
formData.append('use_ai', 'true');

const uploadResponse = await fetch('http://localhost:8000/api/upload', {
  method: 'POST',
  body: formData
});
const { job_id } = await uploadResponse.json();

// Poll status
let status;
do {
  await new Promise(r => setTimeout(r, 2000));
  const statusResponse = await fetch(`http://localhost:8000/api/status/${job_id}`);
  status = await statusResponse.json();
} while (status.status !== 'completed');

// Download
window.location.href = `http://localhost:8000/api/download/${job_id}`;
```

### cURL
```bash
# Upload
JOB_ID=$(curl -X POST http://localhost:8000/api/upload \
  -F "file=@image.jpg" \
  -F "quality=high" \
  | jq -r '.job_id')

# Poll until complete
while true; do
  STATUS=$(curl -s http://localhost:8000/api/status/$JOB_ID | jq -r '.status')
  [ "$STATUS" = "completed" ] && break
  sleep 2
done

# Download
curl -o output.svg http://localhost:8000/api/download/$JOB_ID
```

---

## Performance Metrics

### Processing Times (Intel Core i7, 16GB RAM)

| Image Size | Quality | Time (Rust) | Time (Python) | Speedup |
|------------|---------|-------------|---------------|---------|
| 512x512 | Fast | 0.8s | 5.2s | 6.5x |
| 512x512 | High | 2.1s | 18.4s | 8.8x |
| 1024x1024 | Fast | 2.3s | 15.8s | 6.9x |
| 1024x1024 | High | 5.4s | 58.2s | 10.8x |
| 2048x2048 | High | 12.7s | 186.3s | 14.7x |

### Resource Usage
- **Memory**: ~200MB base, +50MB per concurrent job
- **CPU**: Multi-threaded (uses Rayon), scales with cores
- **Disk**: Input + output ~2-5x image size

---

## Troubleshooting

### Common Issues

**1. Upload fails with 413 error**
- Solution: Resize image to < 10MB or contact admin for limit increase

**2. Job stuck in "processing"**
- Check logs: `docker logs vectorizer-api`
- Restart: `docker-compose restart vectorizer-api`

**3. Poor quality output**
- Try "ultra" quality mode
- Ensure input image has sufficient resolution (min 200x200)
- Enable LAB + AI features for best results

**4. Rust module not loading**
- Rebuild: `cd rust_core && maturin develop --release`
- Check Python can import: `python3 -c "import rust_core"`

**5. API returns 500 errors**
- Check system resources (RAM, disk space)
- Review error logs
- Verify Rust core is compiled correctly

---

## System Requirements

### Development
- **OS**: Linux/macOS/WSL2
- **Python**: 3.12+
- **Rust**: 1.75+
- **Node.js**: 20+
- **RAM**: 8GB minimum, 16GB recommended

### Production
- **OS**: Linux (Ubuntu 22.04+ recommended)
- **CPU**: 4+ cores
- **RAM**: 16GB minimum, 32GB for high concurrency
- **Disk**: 50GB+ SSD
- **Docker**: 24.0+
- **Docker Compose**: 2.20+

---

## Rate Limits

### Free Tier
- 10 uploads per day
- Max 3 concurrent jobs
- Max file size: 10MB

### Pro Tier
- Unlimited uploads
- Max 10 concurrent jobs
- Max file size: 50MB

### Enterprise
- Custom limits
- Dedicated infrastructure
- SLA guarantees

---

**Last Updated**: 2025-10-25  
**API Version**: 3.0.0  
**Author**: Bob Vasic (CyberLink Security)

# API Reference - Vectorizer.dev v3.0

**Last Updated:** 2025-10-26  
**Author:** Bob Vasic (CyberLink Security)  
**Base URL:** `http://localhost:8000` (development) | `https://api.vectorizer.dev` (production)

---

## Quick Start

```bash
# Upload image
curl -X POST http://localhost:8000/api/upload \
  -F "file=@image.jpg" \
  -F "quality=high" \
  -F "use_lab=true" \
  -F "use_ai=true"

# Response: {"job_id": "abc-123", ...}

# Check status
curl http://localhost:8000/api/status/abc-123

# Download result
curl http://localhost:8000/api/download/abc-123 -o output.svg
```

---

## Endpoints

### 1. Root - Service Info
```http
GET /
```

**Response:**
```json
{
  "service": "Vectorizer.dev API v3.0",
  "version": "3.0.0",
  "status": "operational",
  "features": {
    "lab_color_quantization": "Perceptually-optimized color reduction",
    "ai_edge_detection": "ML-enhanced hyper-realistic edges",
    "bezier_smoothing": "Douglas-Peucker + quadratic curves",
    "rust_acceleration": "30x performance boost"
  },
  "quality_levels": ["fast", "balanced", "high", "ultra"]
}
```

---

### 2. Health Check
```http
GET /health
```

Used by load balancers, Docker health checks, and monitoring systems.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-26T00:15:00.000Z",
  "active_jobs": 3
}
```

---

### 3. Upload Image
```http
POST /api/upload
```

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | File | ✅ Yes | - | Image file (PNG/JPG, max 10MB) |
| `quality` | String | No | `"high"` | Quality preset: `fast`, `balanced`, `high`, `ultra` |
| `use_lab` | Boolean | No | `true` | Enable LAB color science (+40% quality) |
| `use_ai` | Boolean | No | `true` | Enable AI edge detection (+20% sharper) |

**Example:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@photo.jpg" \
  -F "quality=ultra" \
  -F "use_lab=true" \
  -F "use_ai=true"
```

**Response (200 OK):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Image uploaded successfully. Processing started.",
  "quality": "ultra",
  "premium_features": {
    "lab_color_science": true,
    "ai_edge_detection": true
  },
  "api_version": "3.0.0"
}
```

**Errors:**
- `400 Bad Request` - Invalid file type or quality parameter
- `413 Payload Too Large` - File exceeds 10MB
- `500 Internal Server Error` - File save failure

---

### 4. Check Status
```http
GET /api/status/{job_id}
```

Poll this endpoint every 2-5 seconds to monitor progress.

**Example:**
```bash
curl http://localhost:8000/api/status/550e8400-e29b-41d4-a716-446655440000
```

**Response (200 OK):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 65,
  "message": "Analyzing image...",
  "output_file": null,
  "processing_time": null
}
```

**Status Values:**
- `queued` - Waiting in background task queue
- `processing` - Currently vectorizing (progress 0-100)
- `completed` - Successfully finished
- `failed` - Error occurred (see `message` field)

**When Completed:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "message": "Successfully vectorized in 5.23s",
  "output_file": "/path/to/outputs/550e8400.../filename_vectorized.svg",
  "processing_time": 5.23
}
```

**Errors:**
- `404 Not Found` - Job ID doesn't exist

---

### 5. Download SVG
```http
GET /api/download/{job_id}
```

Download the generated SVG file.

**Example:**
```bash
curl http://localhost:8000/api/download/550e8400-e29b-41d4-a716-446655440000 \
  -o vectorized.svg
```

**Response:**
- **200 OK** - SVG file (Content-Type: `image/svg+xml`)
- **404 Not Found** - Job ID doesn't exist or file missing
- **400 Bad Request** - Job not completed yet

---

### 6. Batch Upload
```http
POST /api/batch
```

Upload multiple images simultaneously (max 10 files).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `files` | File[] | ✅ Yes | - | Array of images (max 10) |
| `quality` | String | No | `"balanced"` | Quality applied to all files |

**Example:**
```bash
curl -X POST http://localhost:8000/api/batch \
  -F "files=@image1.jpg" \
  -F "files=@image2.png" \
  -F "files=@image3.jpg" \
  -F "quality=high"
```

**Response (200 OK):**
```json
{
  "batch_id": "batch-uuid-here",
  "job_ids": [
    "job-uuid-1",
    "job-uuid-2",
    "job-uuid-3"
  ],
  "total_files": 3,
  "quality": "high"
}
```

**Errors:**
- `400 Bad Request` - More than 10 files submitted

---

### 7. Batch Status
```http
GET /api/batch/{batch_id}/status
```

Get aggregated status for all jobs in a batch.

**Example:**
```bash
curl http://localhost:8000/api/batch/batch-uuid-here/status
```

**Response (200 OK):**
```json
{
  "batch_id": "batch-uuid-here",
  "total": 3,
  "completed": 2,
  "processing": 1,
  "failed": 0,
  "progress": 66,
  "jobs": [
    {
      "job_id": "job-uuid-1",
      "status": "completed",
      "progress": 100
    },
    {
      "job_id": "job-uuid-2",
      "status": "completed",
      "progress": 100
    },
    {
      "job_id": "job-uuid-3",
      "status": "processing",
      "progress": 45
    }
  ]
}
```

**Errors:**
- `404 Not Found` - Batch ID doesn't exist

---

## Integration Examples

### Python
```python
import requests
import time

# Upload
files = {'file': open('image.jpg', 'rb')}
data = {'quality': 'high', 'use_lab': 'true', 'use_ai': 'true'}
response = requests.post('http://localhost:8000/api/upload', 
                         files=files, data=data)
job_id = response.json()['job_id']

# Poll status
while True:
    status = requests.get(f'http://localhost:8000/api/status/{job_id}').json()
    if status['status'] == 'completed':
        break
    elif status['status'] == 'failed':
        raise Exception(status['message'])
    time.sleep(2)

# Download
svg_data = requests.get(f'http://localhost:8000/api/download/{job_id}').content
with open('output.svg', 'wb') as f:
    f.write(svg_data)
```

### JavaScript/TypeScript
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
} while (status.status !== 'completed' && status.status !== 'failed');

// Download
if (status.status === 'completed') {
  window.location.href = `http://localhost:8000/api/download/${job_id}`;
}
```

### Bash/cURL
```bash
#!/bin/bash

# Upload
JOB_ID=$(curl -sX POST http://localhost:8000/api/upload \
  -F "file=@image.jpg" \
  -F "quality=high" \
  | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# Poll until complete
while true; do
  STATUS=$(curl -s http://localhost:8000/api/status/$JOB_ID | jq -r '.status')
  echo "Status: $STATUS"
  
  [ "$STATUS" = "completed" ] && break
  [ "$STATUS" = "failed" ] && exit 1
  
  sleep 2
done

# Download
curl http://localhost:8000/api/download/$JOB_ID -o output.svg
echo "Downloaded: output.svg"
```

---

## Error Handling

### Standard Error Format
```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes
| Code | Meaning | Common Causes |
|------|---------|---------------|
| `200` | Success | Request completed successfully |
| `400` | Bad Request | Invalid file type, quality parameter, or >10 files in batch |
| `404` | Not Found | Job ID or batch ID doesn't exist |
| `413` | Payload Too Large | File exceeds 10MB limit |
| `500` | Internal Server Error | Processing failure, Rust core error, disk full |

---

## Rate Limits

### Free Tier
- **10 uploads/day**
- Max 3 concurrent jobs
- Max file size: 10MB

### Pro Tier ($29/month)
- **Unlimited uploads**
- Max 10 concurrent jobs
- Max file size: 50MB

### Enterprise ($299/month)
- **Custom limits**
- Dedicated infrastructure
- SLA guarantees

---

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI Spec:** `http://localhost:8000/openapi.json`

---

## Troubleshooting

### Upload fails with 413 error
**Solution:** Resize image to < 10MB or upgrade to Pro tier

### Job stuck in "processing"
**Check:** 
```bash
docker logs vectorizer-api
```
**Restart:** 
```bash
docker-compose restart vectorizer-api
```

### Poor quality output
**Try:**
- Use `quality=ultra`
- Ensure input image ≥ 200×200 pixels
- Enable both `use_lab=true` and `use_ai=true`

### Rust module error
**Check:**
```bash
python3 -c "import rust_core; print('OK')"
```
**Rebuild:**
```bash
cd rust_core
maturin develop --release
```

---

**For deployment setup, see:** [3_DEPLOYMENT_GUIDE.md](3_DEPLOYMENT_GUIDE.md)  
**For operational procedures, see:** [4_OPERATIONS_MANUAL.md](4_OPERATIONS_MANUAL.md)

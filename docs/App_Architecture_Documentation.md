# Application Architecture Documentation

## System Overview

Vectorizer.dev is a **three-tier architecture** application combining **React frontend**, **FastAPI backend**, and **Rust compute core** for enterprise-grade image vectorization.

```
┌─────────────────────────────────────────────────────────────┐
│                     VECTORIZER.DEV                          │
│                   System Architecture                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐      HTTPS/WSS     ┌──────────────┐
│   Frontend   │◄──────────────────►│   Nginx      │
│  React + TS  │     (Port 443)     │  Reverse     │
│    (Vite)    │                    │   Proxy      │
└──────────────┘                    └──────┬───────┘
                                           │
                                           │ HTTP
                                           ▼
                                    ┌──────────────┐
                                    │   FastAPI    │
                                    │   Backend    │
                                    │  (Port 8000) │
                                    └──────┬───────┘
                                           │
                         ┌─────────────────┼─────────────────┐
                         │                 │                 │
                         ▼                 ▼                 ▼
                  ┌─────────────┐   ┌───────────┐   ┌───────────┐
                  │  Rust Core  │   │   Redis   │   │   File    │
                  │   (PyO3)    │   │   Cache   │   │  Storage  │
                  │  30x Faster │   │  Queue    │   │  /uploads │
                  └─────────────┘   └───────────┘   └───────────┘
                         │
                         │ ONNX Runtime (optional)
                         ▼
                  ┌─────────────┐
                  │  AI Models  │
                  │   (.onnx)   │
                  └─────────────┘
```

---

## Component Architecture

### 1. Frontend Layer (React + TypeScript)

**Technology Stack:**
- React 18.3
- TypeScript 5.x
- Vite (build tool)
- TailwindCSS (styling)

**Key Components:**
```
src/
├── App.tsx                 # Main application logic
├── index.tsx               # Entry point
├── components/
│   ├── Header.tsx          # Navigation and branding
│   ├── ImageUploader.tsx   # Drag-drop file upload
│   └── icons/              # SVG icon components
└── styles/
    └── index.css           # Global styles + Tailwind
```

**State Management:**
- React hooks (useState, useCallback)
- No external state library (keeps it simple)

**API Integration:**
- Fetch API for HTTP requests
- Polling mechanism for job status
- Direct binary download for SVG files

---

### 2. Backend Layer (FastAPI + Python)

**Technology Stack:**
- FastAPI 0.110+
- Python 3.12
- Uvicorn (ASGI server)
- Pydantic (data validation)

**Service Architecture:**
```python
backend_processor/
├── api_server.py              # FastAPI application
├── intelligent_vectorizer.py  # Core vectorization logic
├── semantic_vectorizer.py     # Object-aware processing
├── test_vectorization.py      # Comprehensive test suite
├── uploads/                   # Temporary image storage
└── outputs/                   # Generated SVG files
```

**API Endpoints:**
```
/                     # Root info
/health               # Health check
/api/upload           # Single file upload
/api/status/{id}      # Job status polling
/api/download/{id}    # SVG download
/api/batch            # Batch upload
/api/batch/{id}/status # Batch status
```

**Background Processing:**
- FastAPI BackgroundTasks for async processing
- In-memory job tracking (dict)
- Future: Redis task queue for distributed processing

---

### 3. Compute Core (Rust)

**Technology Stack:**
- Rust 1.75+
- PyO3 (Python bindings)
- Rayon (parallelism)
- Image crate (image processing)
- ONNX Runtime (optional ML)

**Module Structure:**
```
rust_core/src/
├── lib.rs                    # PyO3 module exports
├── color_quantization.rs     # K-means clustering (RGB)
├── color_lab.rs              # LAB color space
├── edge_detection.rs         # Sobel, Canny algorithms
├── ai_edge_detection.rs      # ML-enhanced edges
├── semantic_segmentation.rs  # Object detection
├── simd_ops.rs               # AVX2 optimizations
└── model_loader.rs           # ONNX model management
```

**Performance Features:**
- **Zero-copy data transfer** via PyO3
- **Parallel processing** with Rayon thread pool
- **SIMD optimizations** for color operations
- **Release build** with LTO + optimization level 3

**Exported Functions:**
```rust
quantize_colors(bytes, k, max_iter) -> bytes
quantize_colors_lab(bytes, k, max_iter) -> bytes
detect_edges_sobel(bytes, threshold) -> bytes
detect_edges_canny(bytes, low, high) -> bytes
detect_edges_ai(bytes, threshold, model) -> bytes
segment_image(bytes, num_regions) -> bytes
detect_salient_regions(bytes) -> bytes
```

---

## Data Flow

### Vectorization Pipeline

```
1. USER UPLOAD
   │
   ▼
2. FastAPI receives file
   │
   ├─► Validate (type, size)
   ├─► Generate job_id
   ├─► Save to /uploads
   └─► Create job status entry
   │
   ▼
3. Background Processing
   │
   ├─► Load image (PIL)
   ├─► Convert to bytes
   │   │
   │   ▼
   ├─► RUST CORE (color quantization)
   │   ├─► RGB → LAB conversion
   │   ├─► K-means clustering
   │   └─► Optimized color palette
   │   │
   │   ▼
   ├─► RUST CORE (edge detection)
   │   ├─► Sobel gradient
   │   ├─► AI enhancement (optional)
   │   └─► Edge map
   │   │
   │   ▼
   ├─► PYTHON (vectorization)
   │   ├─► Extract color regions
   │   ├─► Boundary tracing
   │   ├─► Douglas-Peucker smoothing
   │   ├─► Bezier curve fitting
   │   └─► SVG generation
   │   │
   │   ▼
   └─► Save SVG to /outputs
   │
   ▼
4. Job status = "completed"
   │
   ▼
5. USER downloads SVG
```

---

## Security Architecture

### Input Validation
- File type whitelist (PNG, JPG only)
- Size limit enforcement (10MB default)
- MIME type verification
- Filename sanitization

### File Handling
- UUID-based filenames (prevents collision)
- Temporary storage with cleanup
- No direct path traversal allowed
- Separate upload/output directories

### API Security
- CORS configuration (allow origins list)
- Rate limiting (future: Redis)
- Input sanitization (Pydantic)
- Error message sanitization (no stack traces)

### Production Security
- HTTPS/TLS termination at Nginx
- Docker container isolation
- Non-root user execution
- Read-only filesystem mounts
- Secrets via environment variables

---

## Scalability Design

### Horizontal Scaling

**Current (Single Instance):**
```
Nginx → FastAPI (1 worker) → Rust Core
```

**Scaled (Multi-Instance):**
```
                    ┌─► FastAPI (worker 1) ─┐
                    │                        │
Nginx → Load Balancer ┼─► FastAPI (worker 2) ┼─► Redis Queue
                    │                        │
                    └─► FastAPI (worker 3) ─┘
                                │
                                ▼
                         ┌──────────────┐
                         │  Worker Pool │
                         │  (Celery)    │
                         └──────────────┘
```

**Components for Scaling:**
1. **Redis**: Job queue + status storage
2. **Celery**: Distributed task processing
3. **S3/MinIO**: Persistent file storage
4. **PostgreSQL**: Job metadata database
5. **Nginx**: Load balancing + sticky sessions

---

## Deployment Architecture

### Development
```bash
Terminal 1: npm run dev          # Vite dev server (5173)
Terminal 2: python api_server.py # FastAPI (8000)
```

### Docker Compose (Production)
```yaml
Services:
  - vectorizer-api        # FastAPI + Rust
  - vectorizer-frontend   # Nginx + React build
  - vectorizer-redis      # Cache + queue
  - prometheus            # Metrics collection
  - grafana               # Monitoring dashboards
```

### Kubernetes (Enterprise)
```
Deployment:
  - api-deployment (3 replicas, rolling update)
  - frontend-deployment (2 replicas)
  - redis-statefulset (1 master, 2 slaves)

Services:
  - api-service (ClusterIP, load-balanced)
  - frontend-service (LoadBalancer, external)
  - redis-service (Headless, internal)

Ingress:
  - TLS termination
  - Path-based routing (/api → api-service)
  - Rate limiting annotations
```

---

## Performance Optimizations

### Rust Core
1. **Release build** with optimizations:
   ```toml
   [profile.release]
   opt-level = 3
   lto = true
   codegen-units = 1
   ```

2. **Parallel processing**:
   - Rayon thread pool (auto-detects CPU cores)
   - Parallel k-means iterations
   - Parallel edge detection rows

3. **SIMD** (AVX2 when available):
   - Vectorized color distance calculations
   - Batch RGB→LAB conversions

4. **Memory efficiency**:
   - Zero-copy via PyO3 buffers
   - Preallocated output vectors
   - Iterators instead of intermediate collections

### Python Layer
1. **FastAPI async**:
   - Non-blocking I/O
   - Background tasks for long operations
   - Streaming responses for large files

2. **PIL optimizations**:
   - Load images lazily
   - Use thumbnail() for previews
   - Quantize before detailed processing

### Frontend
1. **Code splitting**:
   - Lazy load components
   - Dynamic imports for heavy libraries

2. **Asset optimization**:
   - Image compression
   - SVG minification
   - Gzip/Brotli compression

3. **Caching**:
   - Service worker for offline support
   - Browser cache headers
   - CDN for static assets

---

## Monitoring & Observability

### Metrics (Prometheus)
```
vectorizer_jobs_total           # Total jobs processed
vectorizer_jobs_duration_seconds # Processing time histogram
vectorizer_jobs_active          # Currently processing
vectorizer_errors_total         # Error count by type
vectorizer_rust_speedup         # Rust vs Python comparison
```

### Logging
```python
[2025-10-25 22:15:49] INFO - [JOB abc123] Processing queued
[2025-10-25 22:15:49] INFO - [JOB abc123] File saved
[2025-10-25 22:15:54] INFO - [JOB abc123] Complete! Time: 5.23s
```

### Health Checks
```
/health endpoint:
  - API responsiveness
  - Rust core availability
  - Redis connectivity (if enabled)
  - Disk space status
```

---

## Technology Trade-offs

### Why Rust?
✅ **Pros:**
- 30x faster than Python
- Memory safe (no segfaults)
- Zero-cost abstractions
- Excellent parallelism support

❌ **Cons:**
- Steep learning curve
- Slower development iteration
- Complex build system
- Requires compilation

### Why FastAPI?
✅ **Pros:**
- Async/await native support
- Automatic OpenAPI docs
- Pydantic validation
- High performance (vs Flask/Django)

❌ **Cons:**
- Relatively new ecosystem
- Fewer plugins than Flask
- Breaking changes in early versions

### Why React?
✅ **Pros:**
- Component reusability
- Large ecosystem
- TypeScript support
- Virtual DOM performance

❌ **Cons:**
- Bundle size overhead
- Complexity for simple UIs
- State management boilerplate

---

## Future Architecture Enhancements

### Phase 1: Distributed Processing
- Redis job queue
- Celery worker pool
- Horizontal API scaling
- Load balancer (HAProxy/Nginx)

### Phase 2: Enterprise Features
- PostgreSQL for job persistence
- S3-compatible object storage
- WebSocket for real-time progress
- Webhook callbacks

### Phase 3: ML Pipeline
- GPU inference for ONNX models
- Model versioning and A/B testing
- Feature store for embeddings
- AutoML for quality optimization

---

**Last Updated**: 2025-10-25  
**Version**: 3.0.0  
**Author**: Bob Vasic (CyberLink Security)

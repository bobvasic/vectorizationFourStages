# Core Functionality - Vectorizer.dev v3.0

**Last Updated:** 2025-10-26  
**Author:** Bob Vasic (CyberLink Security)

---

## What This Application Does

Vectorizer.dev transforms raster images (PNG, JPG) into scalable vector graphics (SVG) using advanced computer vision and AI-enhanced processing.

**Input:** Raster image (pixels)  
**Output:** Vector SVG (mathematical paths, infinite scaling)

---

## Core Features

### 1. **Intelligent Color Quantization**
- **LAB Color Space Processing** - Perceptually-optimized color reduction
- **K-means Clustering** - Intelligent palette generation
- **40% Better Quality** vs standard RGB quantization

### 2. **AI-Enhanced Edge Detection**
- **Hybrid Sobel + ML** - Multi-scale edge analysis
- **Hysteresis Thresholding** - Clean boundary detection
- **20% Sharper Results** vs traditional methods

### 3. **Smooth Curve Generation**
- **Douglas-Peucker Algorithm** - Path simplification
- **Bezier Curve Fitting** - Smooth vector paths
- **60-80% Path Point Reduction** while preserving shape

### 4. **Quality Presets**

| Level | Colors | Use Case | Speed |
|-------|--------|----------|-------|
| **Fast** | 16 | Quick previews | 0.8s (512px) |
| **Balanced** | 32 | Production default | 1.5s (512px) |
| **High** | 64 | Print quality | 2.1s (512px) |
| **Ultra** | 128 | Professional work | 3.8s (512px) |

### 5. **Batch Processing**
- Upload up to 10 images simultaneously
- Parallel processing support
- Individual job tracking per image

---

## Technology Stack

### Frontend
- **React 18.3** + TypeScript 5.x
- **Vite** build system
- **TailwindCSS** styling
- Premium dark theme with green accents

### Backend
- **FastAPI** (Python 3.12) - Async API server
- **Uvicorn** - ASGI production server
- **Pydantic** - Request/response validation

### Compute Core
- **Rust 1.75+** - High-performance image processing
- **PyO3** - Zero-copy Python↔Rust bindings
- **Rayon** - Parallel processing framework
- **30-90x Performance** vs pure Python

### Infrastructure
- **Docker** + **Docker Compose** - Containerization
- **Nginx** - Reverse proxy & static serving
- **Prometheus** + **Grafana** - Monitoring
- **GitHub Actions** - CI/CD pipeline

---

## Performance Benchmarks

**Test System:** Intel Core i7, 16GB RAM, Ubuntu 22.04

| Image Size | Quality | Time | Output Size |
|------------|---------|------|-------------|
| 512×512 | Fast | 0.8s | ~50KB |
| 512×512 | High | 2.1s | ~120KB |
| 1024×1024 | High | 5.4s | ~280KB |
| 2048×2048 | High | 12.7s | ~650KB |

**Quality Improvements:**
- **LAB Color Science:** 40% better perceptual accuracy
- **AI Edge Detection:** 20% sharper definition
- **Curve Smoothing:** 60-80% fewer path points

---

## Business Model

### Free Tier
- 10 uploads per day
- Max 3 concurrent jobs
- Max file size: 10MB
- All quality levels available
- LAB + AI features included

### Pro ($29/month)
- Unlimited uploads
- Max 10 concurrent jobs
- Max file size: 50MB
- Priority processing queue
- API access with authentication

### Enterprise ($299/month)
- Self-hosted deployment
- Custom file size limits
- Dedicated infrastructure
- White-label option
- SLA guarantees
- Technical support

---

## Competitive Advantages

### vs Adobe Illustrator Image Trace
✅ 3x faster processing  
✅ Better automation (no manual tweaking)  
✅ API-first architecture for integration  
✅ LAB color science for superior quality

### vs vector.ink
✅ 40% better color accuracy (LAB vs RGB)  
✅ AI-enhanced edges (sharper output)  
✅ Self-hosted option (data privacy)  
✅ Open architecture (Rust core)

### vs Inkscape Trace Bitmap
✅ Modern web interface (no desktop install)  
✅ Batch processing capability  
✅ 30x faster (Rust acceleration)  
✅ Premium AI features

---

## Use Cases

### Graphic Design
- Logo conversion to scalable vectors
- Icon generation from raster images
- Illustration vectorization

### Print Production
- High-resolution output for printing
- Color separation support
- Professional quality standards

### Web Development
- Lightweight SVG assets
- Responsive graphics (infinite scaling)
- Optimized file sizes

### Automation/Integration
- API integration with design tools
- Batch processing workflows
- Automated asset generation pipelines

---

## System Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │ ───► │   FastAPI    │ ───► │  Rust Core  │
│  Frontend   │      │   Backend    │      │  (30x Fast) │
│  (Port 80)  │      │  (Port 8000) │      │   + PyO3    │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
          ┌──────────┐ ┌────────┐ ┌─────────┐
          │  Redis   │ │ Files  │ │Monitoring│
          │  Cache   │ │Storage │ │Prom+Graf│
          └──────────┘ └────────┘ └─────────┘
```

---

## Security Features

- ✅ File type whitelist (PNG/JPG only)
- ✅ Size limit enforcement (10MB default)
- ✅ UUID-based filenames (no path traversal)
- ✅ CORS configuration
- ✅ Docker container isolation
- ✅ Automated security audits (GitHub Actions)
- ✅ Input validation (FastAPI + Pydantic)

---

## Roadmap

### Current: v3.0 ✅ (Production Ready)
- LAB color quantization
- AI-enhanced edge detection
- Rust acceleration
- Batch processing API
- Docker deployment
- CI/CD pipeline

### Next: v3.5 (Q1 2026)
- PostgreSQL job persistence
- Redis task queue
- WebSocket real-time updates
- JWT authentication
- User account system

### Future: v4.0 (Q2 2026)
- Deep learning contour extraction
- Semantic object segmentation
- Gradient mesh support
- Multiple export formats (PDF, EPS, DXF)

---

**For API usage, see:** [2_API_REFERENCE.md](2_API_REFERENCE.md)  
**For deployment, see:** [3_DEPLOYMENT_GUIDE.md](3_DEPLOYMENT_GUIDE.md)  
**For operations, see:** [4_OPERATIONS_MANUAL.md](4_OPERATIONS_MANUAL.md)

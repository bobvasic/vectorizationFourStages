# Vectorizer.dev - AI-Powered Image Vectorization

Transform raster images (PNG/JPG) into scalable vector graphics (SVG) using LAB color science, AI-enhanced edge detection, and Rust acceleration.

**Version:** 3.0.0 | **Status:** Production Ready | **License:** Proprietary | **Last Reviewed:** 2025-10-26

---

## 🎯 Key Features

- **30-90x Faster** - Rust-powered compute core
- **40% Better Colors** - LAB color space quantization  
- **20% Sharper Edges** - AI-enhanced detection
- **Smooth Curves** - Douglas-Peucker + Bezier fitting
- **Batch Processing** - Up to 10 files simultaneously
- **Production Ready** - Docker deployment, REST API

---

## 🚀 Quick Start

### Local Development

```bash
# Clone
git clone https://github.com/bobvasic/vectorizationFourStages.git
cd vectorizationFourStages

# Start with Docker (recommended)
docker-compose up -d

# Or manual setup
npm install
cd backend_processor && pip install -r requirements.txt
cd ../rust_core && cargo build --release && maturin develop --release
cd .. && ./start_fullstack.sh
```

**Access:**
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📦 Deploy to Render.com

**Cost:** $7/month (Backend) + Free (Frontend)

### 1. Backend API Setup

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub repo
4. Configure:
   ```
   Name: vectorizer-api
   Runtime: Docker
   Dockerfile Path: ./Dockerfile
   Instance Type: Starter ($7/mo)
   ```

5. **Add Persistent Disk** (CRITICAL):
   ```
   Name: vectorizer-storage
   Mount Path: /app/data
   Size: 10 GB
   ```

6. **Environment Variables:**
   ```bash
   PORT=10000
   PYTHONUNBUFFERED=1
   MAX_FILE_SIZE_MB=10
   ```

7. Click **Create Web Service**

**Build time:** ~15-20 minutes (first deploy)

### 2. Frontend Static Site

1. Click **New +** → **Static Site**
2. Connect same GitHub repo
3. Configure:
   ```
   Name: vectorizer-frontend
   Build Command: npm install && npm run build
   Publish Directory: dist
   ```

4. **Environment Variable:**
   ```bash
   VITE_API_URL=https://vectorizer-api.onrender.com
   ```
   *(Replace with your actual backend URL)*

5. Click **Create Static Site**

**Build time:** ~2-3 minutes

### 3. Update CORS

After backend deploys, update `backend_processor/api_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vectorizer-frontend.onrender.com",  # Your frontend URL
        "http://localhost:5173",  # Local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push to redeploy.

### 4. Verify Deployment

```bash
# Test backend
curl https://vectorizer-api.onrender.com/health

# Test frontend
open https://vectorizer-frontend.onrender.com
```

✅ Done! Your app is live.

---

## 🏗️ Architecture

```
┌──────────┐      ┌──────────┐      ┌──────────┐
│  React   │ ───► │ FastAPI  │ ───► │   Rust   │
│ Frontend │      │  Backend │      │   Core   │
└──────────┘      └──────────┘      └──────────┘
                       │
                  ┌────┴────┐
              Uploads    Outputs
```

**Stack:**
- **Frontend:** React 18 + TypeScript + Vite + TailwindCSS
- **Backend:** FastAPI (Python 3.12) + Uvicorn
- **Core:** Rust 1.75 + PyO3 + Rayon (parallelism)
- **ML:** ONNX Runtime (optional)

---

## 📡 API Usage

### Upload & Vectorize

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@image.jpg" \
  -F "quality=high" \
  -F "use_lab=true" \
  -F "use_ai=true"

# Response: {"job_id": "abc-123", ...}
```

### Check Status

```bash
curl http://localhost:8000/api/status/abc-123

# Response: {"status": "completed", "progress": 100, ...}
```

### Download Result

```bash
curl http://localhost:8000/api/download/abc-123 -o output.svg
```

**Full API Docs:** http://localhost:8000/docs (Swagger UI)

---

## ⚙️ Configuration

### Quality Levels

| Level | Colors | Speed | Use Case |
|-------|--------|-------|----------|
| `fast` | 16 | 0.8s | Quick previews |
| `balanced` | 32 | 1.5s | Production default |
| `high` | 64 | 2.1s | Print quality |
| `ultra` | 128 | 3.8s | Professional work |

*Benchmarked on 512×512 images, Intel i7, 16GB RAM*

### Environment Variables

```bash
# Backend
API_HOST=0.0.0.0
API_PORT=8000          # 10000 for Render
MAX_FILE_SIZE_MB=10
ALLOWED_ORIGINS=*       # Restrict in production

# Frontend
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Testing

```bash
cd backend_processor
python3 test_vectorization.py

# Expected: 14/14 tests passing
```

---

## 📚 Documentation

- **[Core Functionality](docs/1_CORE_FUNCTIONALITY.md)** - Features, business model
- **[API Reference](docs/2_API_REFERENCE.md)** - Complete API docs
- **[Deployment Guide](docs/3_DEPLOYMENT_GUIDE.md)** - Docker, production
- **[Operations Manual](docs/4_OPERATIONS_MANUAL.md)** - Monitoring, troubleshooting

---

## 🔒 Security

- File type whitelist (PNG/JPG only)
- Size limit enforcement (10MB default)
- UUID-based filenames (no path traversal)
- CORS configuration
- Docker container isolation
- Input validation (FastAPI + Pydantic)

---

## 💰 Pricing

### Free Tier
- 10 uploads/day
- Max 3 concurrent jobs
- All quality levels
- LAB + AI features included

### Pro ($29/month)
- Unlimited uploads
- Max 10 concurrent jobs
- 50MB file size limit
- API access

### Enterprise ($299/month)
- Self-hosted deployment
- Custom limits
- White-label option
- SLA + support

---

## 🛠️ Development

### Project Structure

```
vectorizer_four_stages/
├── backend_processor/       # Python API + processing
│   ├── api_server.py       # FastAPI application
│   ├── intelligent_vectorizer.py  # Core vectorizer
│   └── requirements.txt    # Python dependencies
├── rust_core/              # Rust acceleration
│   ├── src/lib.rs         # PyO3 bindings
│   └── Cargo.toml         # Rust dependencies
├── components/             # React UI components
├── docs/                   # Documentation (4 files)
├── Dockerfile              # Production build
├── docker-compose.yml      # Local development
└── README.md              # This file
```

### Commands

```bash
# Development
npm run dev                 # Start Vite dev server
python3 backend_processor/api_server.py  # Start API
./start_fullstack.sh       # Start both

# Production
docker-compose up -d       # Start containers
docker-compose logs -f     # View logs
docker-compose down        # Stop containers

# Testing
python3 backend_processor/test_vectorization.py
cargo test --manifest-path=rust_core/Cargo.toml
```

---

## 🐛 Troubleshooting

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Rust module not loading
```bash
cd rust_core
cargo clean
cargo build --release
maturin develop --release
```

### Docker build fails
```bash
docker system prune -a
docker-compose build --no-cache
```

### CORS errors
Update `allow_origins` in `backend_processor/api_server.py`

---

## 📈 Performance

| Image Size | Quality | Time | Output |
|------------|---------|------|--------|
| 512×512 | Fast | 0.8s | ~50KB |
| 512×512 | High | 2.1s | ~120KB |
| 1024×1024 | High | 5.4s | ~280KB |
| 2048×2048 | High | 12.7s | ~650KB |

**Improvements:**
- LAB color: +40% perceptual accuracy
- AI edges: +20% sharpness
- Bezier curves: -70% file size

---

## 🤝 Support

- **Documentation:** `/docs` directory
- **API Issues:** Check [API Reference](docs/2_API_REFERENCE.md)
- **Deployment Help:** See [Deployment Guide](docs/3_DEPLOYMENT_GUIDE.md)
- **Bug Reports:** GitHub Issues
- **Email:** support@cyberlinksecurity.com

---

## 📄 License

**Proprietary** - Commercial use requires Pro/Enterprise license.

- Free tier: Personal use only
- Pro/Enterprise: Commercial use permitted

---

## 🏆 Credits

**Created by:** Bob Vasic (CyberLink Security)  
**Version:** 3.0.0  
**Release Date:** 2025-10-25  
**Status:** ✅ Production Ready

---

Built with ❤️ and Rust 🦀

# Render.com Deployment Guide - Vectorizer.dev

**Last Updated:** 2025-10-26  
**Author:** Bob Vasic (CyberLink Security)

---

## Overview

Deploy Vectorizer.dev to Render.com using **two services**:
1. **Backend API** (Web Service with Docker) - $7/mo
2. **Frontend** (Static Site) - Free

**Total Cost:** $7/month + bandwidth usage

---

## Prerequisites

- GitHub account with your repository
- Render.com account (free signup at https://render.com)
- Your repo pushed to GitHub

---

## Part 1: Deploy Backend API

### Step 1: Create Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `vectorizationFourStages`
4. Configure the service:

**Basic Settings:**
```
Name: vectorizer-api
Region: Oregon (US West) or closest to your users
Branch: main
Runtime: Docker
```

**Build Settings:**
```
Dockerfile Path: ./Dockerfile
Docker Context: .
Docker Command: (leave empty - uses CMD from Dockerfile)
```

### Step 2: Configure Environment Variables

Add these environment variables:

```bash
PYTHON_VERSION=3.12
API_HOST=0.0.0.0
API_PORT=10000
MAX_FILE_SIZE_MB=10
ALLOWED_ORIGINS=*
```

**Note:** Render uses port `10000` by default for web services.

### Step 3: Add Persistent Disk

**CRITICAL:** Without this, uploaded files will be lost on restart.

1. Scroll to **"Disk"** section
2. Click **"Add Disk"**
3. Configure:
   ```
   Name: vectorizer-storage
   Mount Path: /app/data
   Size: 10 GB
   ```

### Step 4: Update Dockerfile for Render

We need to modify the Dockerfile to use Render's port and mount point:

---

## Part 2: Deploy Frontend Static Site

### Step 1: Create Static Site

1. Click **"New +"** → **"Static Site"**
2. Connect same GitHub repository
3. Configure:

**Basic Settings:**
```
Name: vectorizer-frontend
Branch: main
```

**Build Settings:**
```
Build Command: npm install && npm run build
Publish Directory: dist
```

### Step 2: Configure Environment Variables

```bash
VITE_API_URL=https://vectorizer-api.onrender.com
```

**Replace with your actual backend URL after it's deployed.**

### Step 3: Add Custom Domain (Optional)

1. Go to **"Settings"** → **"Custom Domain"**
2. Add your domain (e.g., `vectorizer.dev`)
3. Update DNS records as instructed

---

## Part 3: Required Code Changes

### 1. Update Dockerfile for Render

Create `Dockerfile.render` with Render-specific configuration:

```dockerfile
# Multi-stage Dockerfile for Render.com
FROM rust:1.75-slim as rust-builder

WORKDIR /build
RUN apt-get update && apt-get install -y python3-dev pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

COPY rust_core/ ./rust_core/
WORKDIR /build/rust_core
RUN cargo build --release

# Production stage
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY backend_processor/ ./backend_processor/
COPY --from=rust-builder /build/rust_core/target/release/*.so ./backend_processor/

# Create data directory for persistent disk
RUN mkdir -p /app/data/uploads /app/data/outputs

WORKDIR /app/backend_processor
RUN pip install --no-cache-dir -r requirements.txt

# Render uses PORT environment variable (default 10000)
EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

CMD ["python3", "api_server.py"]
```

### 2. Update api_server.py for Render

Modify `backend_processor/api_server.py` to use Render's PORT environment variable:

```python
import os

# Get port from environment (Render sets this)
PORT = int(os.getenv('PORT', 10000))

# Update directories to use persistent disk
UPLOAD_DIR = Path(os.getenv('UPLOAD_DIR', '/app/data/uploads'))
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', '/app/data/outputs'))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# At the bottom of the file, change:
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,  # Use PORT from environment
        log_level="info"
    )
```

### 3. Update Frontend API URL

Create `.env.production` in root directory:

```bash
VITE_API_URL=https://vectorizer-api.onrender.com
```

Update `App.tsx` to use environment variable:

```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Replace all fetch calls:
fetch(`${API_URL}/api/upload`, ...)
fetch(`${API_URL}/api/status/${jobId}`, ...)
fetch(`${API_URL}/api/download/${jobId}`, ...)
```

---

## Part 4: Deployment Steps

### Step 1: Push Code Changes

```bash
git add -A
git commit -m "Add Render.com deployment configuration"
git push origin main
```

### Step 2: Deploy Backend

1. In Render dashboard, create new Web Service
2. Connect GitHub repo
3. Set Dockerfile path to: `Dockerfile.render` (or use default if you replaced it)
4. Add environment variables (see Part 1, Step 2)
5. Add persistent disk at `/app/data` (10GB)
6. Click **"Create Web Service"**

**Build time:** ~15-20 minutes (Rust compilation is slow first time)

### Step 3: Deploy Frontend

1. Create new Static Site
2. Connect same GitHub repo
3. Set build command and publish directory
4. Add `VITE_API_URL` environment variable with your backend URL
5. Click **"Create Static Site"**

**Build time:** ~2-3 minutes

### Step 4: Update CORS

Once backend is deployed, update `api_server.py` CORS settings:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vectorizer-frontend.onrender.com",  # Your frontend URL
        "http://localhost:5173",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push to trigger redeploy.

---

## Part 5: Verify Deployment

### Test Backend

```bash
# Check health
curl https://vectorizer-api.onrender.com/health

# Expected response:
# {"status":"healthy","timestamp":"...","active_jobs":0}
```

### Test Frontend

1. Open `https://vectorizer-frontend.onrender.com`
2. Upload a test image
3. Verify vectorization works

### Check Logs

**Backend Logs:**
```
Dashboard → vectorizer-api → Logs
```

**Frontend Logs:**
```
Dashboard → vectorizer-frontend → Logs
```

---

## Part 6: Performance & Optimization

### Backend Optimization

**Instance Type:** Start with **Starter ($7/mo)**
- 512 MB RAM
- 0.5 CPU
- Should handle 10-20 concurrent users

**Upgrade to Standard ($25/mo) if:**
- Memory usage consistently > 400MB
- Response times > 5 seconds
- More than 50 concurrent users

### Disk Usage

Monitor disk usage:
```bash
# In Render shell
df -h /app/data
du -sh /app/data/uploads
du -sh /app/data/outputs
```

**Set up auto-cleanup:**
Add to `api_server.py`:
```python
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

def cleanup_old_files():
    """Delete files older than 7 days"""
    import time
    now = time.time()
    for folder in [UPLOAD_DIR, OUTPUT_DIR]:
        for file in folder.glob('**/*'):
            if file.is_file() and (now - file.stat().st_mtime) > 7*24*60*60:
                file.unlink()

scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup_old_files, trigger="interval", hours=24)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())
```

---

## Part 7: Custom Domain Setup

### Backend API Domain

1. Go to Settings → Custom Domain
2. Add `api.yourdomain.com`
3. Update DNS:
   ```
   Type: CNAME
   Name: api
   Value: vectorizer-api.onrender.com
   ```

### Frontend Domain

1. Go to Settings → Custom Domain
2. Add `yourdomain.com` and `www.yourdomain.com`
3. Update DNS:
   ```
   Type: A
   Name: @
   Value: [Render IP from dashboard]
   
   Type: CNAME
   Name: www
   Value: vectorizer-frontend.onrender.com
   ```

4. Update `.env.production`:
   ```bash
   VITE_API_URL=https://api.yourdomain.com
   ```

---

## Part 8: Monitoring & Maintenance

### Enable Notifications

1. Dashboard → Settings → Notifications
2. Add email for deploy failures
3. Add Slack webhook (optional)

### Monitor Usage

**Bandwidth:** Check monthly usage in Dashboard → Usage
**Disk:** Monitor in Dashboard → Disks → vectorizer-storage

### Automatic Deploys

Render auto-deploys on every `git push` to `main` branch.

**Disable auto-deploy:**
Settings → Auto-Deploy → Off

---

## Part 9: Cost Breakdown

### Monthly Costs

| Service | Plan | Cost |
|---------|------|------|
| Backend API | Starter | $7/mo |
| Frontend | Free | $0/mo |
| Disk (10GB) | Included | $0/mo |
| **Total** | | **$7/mo** |

**Additional costs:**
- Bandwidth: $0.10/GB after 100GB/mo
- Upgrade to Standard: +$18/mo ($25 total)

---

## Part 10: Troubleshooting

### Build Fails

**Error:** "Rust compilation timeout"
**Solution:** Use smaller instance or build locally and push binary

**Error:** "Out of memory"
**Solution:** Upgrade to Standard plan

### Runtime Issues

**Error:** "Port 10000 already in use"
**Solution:** Render handles this automatically - check logs

**Error:** "Disk full"
**Solution:** 
```bash
# SSH into instance (Render shell)
find /app/data/outputs -mtime +7 -delete
```

### CORS Errors

**Error:** "CORS policy blocked"
**Solution:** Add frontend URL to `allow_origins` in `api_server.py`

---

## Part 11: Rollback Procedure

### Quick Rollback

1. Dashboard → Deploys
2. Find last working deploy
3. Click **"Redeploy"**

### Manual Rollback

```bash
# Locally
git revert HEAD
git push origin main
# Render auto-deploys
```

---

## Summary

✅ **Backend:** Docker web service with persistent disk  
✅ **Frontend:** Static site with auto-deploy  
✅ **Cost:** $7/month  
✅ **Performance:** Handles 10-20 concurrent users  
✅ **Monitoring:** Built-in logs and metrics  
✅ **SSL:** Free automatic HTTPS  
✅ **Auto-deploy:** Every git push  

**Deployment time:** ~25 minutes first time, ~3 minutes for updates

---

**Questions?** Check Render docs: https://render.com/docs

**Support:** info@cyberlinksecurity.com

---

**Created by:** Bojan Vasic (CyberLink Security)  
**Date:** 2025-10-26

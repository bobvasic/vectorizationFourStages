# 🎨 Vectorizer.dev - Intelligent Image to Vector Converter

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

**Enterprise-Grade Raster to Vector Conversion System**

*Transforming raster images into smooth, infinitely scalable SVG graphics*

[Features](#-key-features) • [Quick Start](#-quick-start) • [Architecture](#-system-architecture) • [API](#-api-reference) • [Deployment](#-deployment)

---

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Quick Start](#-quick-start)
- [Quality Levels](#-quality-levels)
- [System Architecture](#-system-architecture)
- [API Reference](#-api-reference)
- [Frontend](#-frontend-application)
- [Deployment](#-deployment)
- [Performance](#-performance-benchmarks)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**Vectorizer.dev** is a full-stack web application that converts raster images (JPG, PNG) into high-quality, scalable SVG vector graphics using intelligent algorithms and smooth Bezier curve generation.

### Why Vectorizer.dev?

Traditional vectorization tools produce either:
- ❌ **Pixelated output** - Not true vectors, just rectangles
- ❌ **Oversimplified** - Loss of detail and color accuracy
- ❌ **Bloated files** - Massive file sizes with poor performance

**Vectorizer.dev solves this with:**
- ✅ **True vector curves** - Smooth Bezier paths, not pixels
- ✅ **Intelligent color reduction** - Preserves visual quality
- ✅ **Quality tiers** - Fast, Balanced, High, Ultra
- ✅ **Production-ready** - Full-stack with REST API
- ✅ **Modern UI** - Beautiful React frontend with real-time preview

---

## 🚀 Key Features

<table>
<tr>
<td width="50%">

### 🎯 **Technical Excellence**
- Intelligent color posterization (16-128 colors)
- Smooth Bezier curve generation
- Edge detection and contour tracing
- Multi-layer SVG composition
- Adaptive quality settings
- Background job processing

</td>
<td width="50%">

### 💼 **Production Features**
- Full-stack architecture (React + FastAPI)
- RESTful API with job tracking
- Real-time processing status
- Quality selector UI
- Side-by-side preview
- Download management

</td>
</tr>
</table>

---

## 🛠 Technology Stack

### Backend
- **Python 3.12+** - Modern Python with type hints
- **FastAPI 0.115** - High-performance async API framework
- **Pillow 11.0** - Advanced image processing
- **Uvicorn** - ASGI server with WebSockets support

### Frontend
- **React 18.3** - Modern UI framework with hooks
- **TypeScript 5.6** - Type-safe development
- **Vite 6.0** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling

### Deployment
- **Render.com** - Cloud hosting platform
- **Organization Plan** - Optimized for cost efficiency

---

## ⚡ Quick Start

### Prerequisites
```bash
Python 3.12+
Node.js 18+
npm or yarn
```

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/vectorizer-dev.git
cd vectorizer-dev
```

### 2. Start Full-Stack Application
```bash
# Single command to start everything
./start_fullstack.sh
```

This automatically:
- ✓ Installs frontend dependencies (npm)
- ✓ Creates Python virtual environment
- ✓ Installs backend dependencies (pip)
- ✓ Starts backend API (port 8000)
- ✓ Starts frontend dev server (port 5173)
- ✓ Opens browser automatically

### 3. Access Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Stop Servers
```bash
./stop_fullstack.sh
```

---

## 🎯 Quality Levels

Choose the optimal balance between speed and quality:

<table>
<tr>
<th width="20%">Quality</th>
<th width="20%">Colors</th>
<th width="20%">Processing Time</th>
<th width="20%">File Size</th>
<th width="20%">Best For</th>
</tr>
<tr>
<td><strong>Fast</strong></td>
<td>16 colors</td>
<td>~2-5 seconds</td>
<td>Small</td>
<td>Quick previews, icons</td>
</tr>
<tr>
<td><strong>Balanced</strong></td>
<td>32 colors</td>
<td>~5-10 seconds</td>
<td>Medium</td>
<td>Web graphics, logos</td>
</tr>
<tr>
<td><strong>High</strong> ⭐</td>
<td>64 colors</td>
<td>~10-20 seconds</td>
<td>Large</td>
<td>Print, professional use</td>
</tr>
<tr>
<td><strong>Ultra</strong></td>
<td>128 colors</td>
<td>~20-40 seconds</td>
<td>Very Large</td>
<td>Artistic, photorealistic</td>
</tr>
</table>

**Recommended:** Start with **High** quality for best results.

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     VECTORIZER.DEV                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │                  │         │                  │         │
│  │  React Frontend  │ ◄─────► │  FastAPI Backend │         │
│  │  (Port 5173)     │  HTTP   │  (Port 8000)     │         │
│  │                  │  REST   │                  │         │
│  └──────────────────┘         └──────────────────┘         │
│                                        │                     │
│                                        ▼                     │
│                              ┌──────────────────┐           │
│                              │ Intelligent      │           │
│                              │ Vectorizer       │           │
│                              │ Engine           │           │
│                              └──────────────────┘           │
│                                        │                     │
│                              ┌─────────┴─────────┐          │
│                              ▼                   ▼          │
│                    ┌──────────────┐   ┌──────────────┐     │
│                    │ Image        │   │ Vector Path  │     │
│                    │ Processing   │   │ Generation   │     │
│                    └──────────────┘   └──────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow
1. **Upload** - User uploads image via React UI
2. **API Call** - POST to `/api/upload` with quality parameter
3. **Job Creation** - Backend creates unique job ID
4. **Processing** - Background task runs intelligent vectorizer
5. **Polling** - Frontend polls `/api/status/{job_id}` every 2s
6. **Download** - Once complete, GET `/api/download/{job_id}`

---

## 📚 API Reference

### Base URL
```
Production: https://your-app.onrender.com
Development: http://localhost:8000
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T12:00:00",
  "active_jobs": 2
}
```

#### 2. Upload Image
```http
POST /api/upload?quality=high
Content-Type: multipart/form-data

Body: { file: <image_file> }
```

**Parameters:**
- `quality` (optional): `fast`, `balanced`, `high` (default), `ultra`

**Response:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "queued",
  "message": "Image uploaded successfully. Processing started.",
  "quality": "high"
}
```

#### 3. Check Status
```http
GET /api/status/{job_id}
```

**Response (Processing):**
```json
{
  "job_id": "a1b2c3d4-...",
  "status": "processing",
  "progress": 45,
  "message": "Analyzing image..."
}
```

**Response (Complete):**
```json
{
  "job_id": "a1b2c3d4-...",
  "status": "completed",
  "progress": 100,
  "message": "Successfully vectorized in 12.34s",
  "output_file": "/outputs/.../image_vectorized.svg",
  "processing_time": 12.34
}
```

#### 4. Download SVG
```http
GET /api/download/{job_id}
```

**Response:**
- Content-Type: `image/svg+xml`
- File: SVG vector graphic

---

## 🎨 Frontend Application

### Features
- **Drag & Drop Upload** - Intuitive file upload interface
- **Quality Selector** - Four buttons for quality selection
- **Real-time Preview** - Side-by-side original vs vectorized
- **Processing Status** - Live progress indicator
- **Download Button** - One-click SVG download
- **Responsive Design** - Works on desktop and tablet

### UI Components

#### Quality Selector
```tsx
<div className="quality-selector">
  <button className={selectedQuality === 'fast' ? 'active' : ''}>
    Fast
  </button>
  <button className={selectedQuality === 'balanced' ? 'active' : ''}>
    Balanced
  </button>
  <button className={selectedQuality === 'high' ? 'active' : ''}>
    High
  </button>
  <button className={selectedQuality === 'ultra' ? 'active' : ''}>
    Ultra
  </button>
</div>
```

### Customization

#### Colors
```css
/* Primary color (green) */
--color-primary: #16a34a;

/* Background */
--color-bg: #000000;

/* Text */
--color-text: #e5e7eb;
```

---

## 🚀 Deployment

### Render.com (Recommended)

#### 1. Backend Service
```yaml
# render.yaml
services:
  - type: web
    name: vectorizer-api
    env: python
    buildCommand: pip install -r backend_processor/requirements.txt
    startCommand: python backend_processor/api_server.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.3
```

#### 2. Frontend Static Site
```yaml
services:
  - type: web
    name: vectorizer-frontend
    env: static
    buildCommand: npm install && npm run build
    staticPublishPath: ./dist
    envVars:
      - key: VITE_API_URL
        value: https://vectorizer-api.onrender.com
```

### Environment Variables

#### Backend
```bash
PORT=8000
HOST=0.0.0.0
```

#### Frontend
```bash
VITE_API_URL=http://localhost:8000
```

### Docker (Optional)

#### Backend Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY backend_processor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend_processor/ .

CMD ["python", "api_server.py"]
```

---

## ⚡ Performance Benchmarks

### Processing Time (800x600px image)

| Quality | Colors | Processing Time | Output Size | Use Case |
|---------|--------|-----------------|-------------|----------|
| **Fast** | 16 | 2-5s | ~50KB | Quick previews |
| **Balanced** | 32 | 5-10s | ~120KB | Web graphics |
| **High** | 64 | 10-20s | ~250KB | Professional use |
| **Ultra** | 128 | 20-40s | ~500KB | Artistic work |

### Scalability

```
Image Resolution    Fast    Balanced    High    Ultra
────────────────────────────────────────────────────
800x600 (0.5MP)     3s      7s          12s     25s
1920x1080 (2MP)     8s      15s         30s     65s
3840x2160 (8MP)     28s     52s         120s    280s
```

### Concurrent Jobs
- **Development:** 3 concurrent jobs
- **Production:** 10+ concurrent jobs (with worker scaling)

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **Port Already in Use**
```bash
Error: Address already in use (port 8000/5173)
```

**Solution:**
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9

# Or use the stop script
./stop_fullstack.sh
```

#### 2. **Python Dependencies Failed**
```bash
ERROR: Failed to build 'numpy'
```

**Solution:**
```bash
# Update pip and setuptools
cd backend_processor
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### 3. **CORS Errors in Browser**
```
Access-Control-Allow-Origin error
```

**Solution:** Backend already configured for CORS. Ensure frontend is making requests to correct API URL.

#### 4. **SVG Not Displaying**
**Solution:** Verify the download URL includes the job_id and file exists in `backend_processor/outputs/{job_id}/`

#### 5. **Memory Error During Processing**
```bash
MemoryError: Unable to allocate array
```

**Solution:** Use lower quality setting or reduce image resolution before upload.

---

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- [ ] **GPU Acceleration** - CUDA/OpenCL for faster processing
- [ ] **Batch Processing** - Multiple images at once
- [ ] **Progress Streaming** - WebSocket for real-time updates
- [ ] **Advanced Filters** - Artistic effects and styles
- [ ] **Cloud Storage** - S3/R2 integration for outputs
- [ ] **User Accounts** - Save history and preferences
- [ ] **API Rate Limiting** - Protect against abuse
- [ ] **Docker Compose** - One-command deployment

### Development Setup
```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/vectorizer-dev.git
cd vectorizer-dev

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test
./start_fullstack.sh

# Commit with descriptive message
git commit -m "feat: add GPU acceleration"

# Push and create PR
git push origin feature/amazing-feature
```

### Code Style
- **Python:** PEP 8, type hints, docstrings
- **TypeScript:** ESLint, Prettier formatting
- **Commits:** Conventional Commits specification

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 CyberLink Security

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 🙏 Acknowledgments

- **FastAPI Team** - Outstanding async web framework
- **React Team** - Modern UI development
- **Pillow Team** - Comprehensive image processing
- **CyberLink Security** - Research and development
- **Open Source Community** - Inspiration and support

---

## 📞 Support & Contact

<div align="center">

**Technical Lead:** Tim - Senior Enterprise Developer  
**Organization:** CyberLink Security

[![GitHub Issues](https://img.shields.io/github/issues/yourusername/vectorizer-dev)](https://github.com/yourusername/vectorizer-dev/issues)
[![GitHub Stars](https://img.shields.io/github/stars/yourusername/vectorizer-dev)](https://github.com/yourusername/vectorizer-dev/stargazers)

**Report Issues:** [GitHub Issues](https://github.com/yourusername/vectorizer-dev/issues)  
**Documentation:** [Wiki](https://github.com/yourusername/vectorizer-dev/wiki)

---

### 🌟 If this project helped you, please star the repository!

**Built with ❤️ by CyberLink Security**  
*Transforming pixels into infinite scalability*

</div>

---

<div align="center">

**Last Updated:** 2025-10-25  
**Version:** 2.0.0  
**Status:** Production Ready ✅

</div>

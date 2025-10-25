# 🚀 Quick Start Guide

Get the complete vectorization application running in 3 minutes!

---

## ⚡ Super Quick Start

```bash
# Terminal 1: Start Backend
cd backend_processor
./start_backend.sh

# Terminal 2: Start Frontend  
npm install
npm run dev
```

Then open: **http://localhost:5173**

---

## 📋 Step-by-Step Guide

### Step 1: Start the Backend API (Terminal 1)

```bash
cd backend_processor

# Make script executable (first time only)
chmod +x start_backend.sh

# Start backend server (installs dependencies automatically)
./start_backend.sh
```

**You should see:**
```
╔════════════════════════════════════════════════════════════╗
║    CYBERLINK SECURITY - VECTORIZER.DEV BACKEND SERVER     ║
╚════════════════════════════════════════════════════════════╝

✓ Python 3 detected: Python 3.11.5
✓ Virtual environment created
✓ All dependencies installed

════════════════════════════════════════════════════════════
🚀 STARTING BACKEND SERVER
════════════════════════════════════════════════════════════

📍 API Server: http://localhost:8000
📖 API Documentation: http://localhost:8000/docs
💚 Health Check: http://localhost:8000/health
```

### Step 2: Start the Frontend (Terminal 2)

Open a **new terminal window** and run:

```bash
# Install frontend dependencies (first time only)
npm install

# Start Vite development server
npm run dev
```

**You should see:**
```
  VITE v6.2.0  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### Step 3: Open the Application

Open your browser and go to:
```
http://localhost:5173
```

---

## 🎯 How to Use

1. **Upload an Image**
   - Drag and drop JPG/PNG (max 10MB)
   - Or click to browse files

2. **Processing Starts Automatically**
   - Shows "Vectorizing..." with spinner
   - Processes through 3 stages (Pro tier)

3. **View Results**
   - SVG preview appears on right side
   - Download button becomes available

4. **Download SVG**
   - Click "Download SVG" to get your file
   - Or view all output files via API

---

## 🔧 Troubleshooting

### Backend Won't Start

**Problem:** Port 8000 already in use

**Solution:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in api_server.py line 513
```

### Frontend Won't Connect

**Problem:** CORS or connection refused

**Solution:**
1. Make sure backend is running (Terminal 1 should show logs)
2. Check backend URL in `App.tsx` line 44
3. Verify: http://localhost:8000/health

### Python Dependencies Error

**Problem:** PIL/Pillow not found

**Solution:**
```bash
cd backend_processor
source venv/bin/activate
pip install --upgrade Pillow
```

---

## 📊 Testing the Integration

### Test Backend API (cURL)

```bash
# Check health
curl http://localhost:8000/health

# Test upload (use your own image)
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test_image.jpg" \
  -F "tier=pro" \
  -F "quality=balanced"
```

### Interactive API Docs

Visit: **http://localhost:8000/docs**

Try uploading an image directly through Swagger UI!

---

## 🎨 Features to Test

- ✅ Drag and drop upload
- ✅ File type validation (try uploading .txt - should fail)
- ✅ Processing status updates
- ✅ SVG preview after completion
- ✅ Download functionality
- ✅ "Start Over" to reset

---

## 🏗️ Project Structure

```
vectorizer_four_stages/
├── backend_processor/          # Python backend
│   ├── api_server.py          # FastAPI server ⭐
│   ├── requirements.txt       # Dependencies
│   ├── start_backend.sh       # Startup script
│   └── [4 vectorizer scripts]
│
├── components/                 # React components
│   ├── ImageUploader.tsx
│   └── icons/
│
├── App.tsx                    # Main React app ⭐
├── index.tsx                  # React entry
├── package.json               # Frontend deps
└── README.md                  # Full documentation
```

---

## 🎓 What's Happening Behind the Scenes

```
1. Frontend (React)
   ↓ User uploads image.jpg
   
2. POST /api/upload
   ↓ Backend receives file
   
3. FastAPI Backend
   ↓ Saves to uploads/[uuid].jpg
   ↓ Starts background processing
   
4. Stage 1: ultimate_pixel_svg.py
   ↓ Creates pixel-perfect base
   
5. Stage 2: photorealistic_vectorizer.py
   ↓ Optimizes regions
   
6. Stage 3: advanced_vectorizer.py
   ↓ Converts to true vectors
   
7. SVG Files Generated
   ↓ Saved to outputs/[uuid]/
   
8. Frontend Polls Status
   ↓ Every 2 seconds via GET /api/status/{job_id}
   
9. When Complete
   ↓ GET /api/results/{job_id}
   ↓ Display first SVG in preview
   
10. User Downloads
    ↓ GET /api/download/{job_id}/{filename}
```

---

## 💡 Tips

### For Development

- **Backend logs**: Watch Terminal 1 for processing status
- **Frontend logs**: Open browser DevTools Console
- **API testing**: Use http://localhost:8000/docs

### For Testing Different Tiers

Edit `App.tsx` line 44:
```typescript
// Change tier parameter
`http://localhost:8000/api/upload?tier=ultra&quality=high`

// Options:
// tier: basic, pro, enterprise, ultra
// quality: fast, balanced, high, ultra
```

### For Production Deployment

1. **Backend**: Deploy to Render.com, Heroku, or AWS
2. **Frontend**: Deploy to Vercel, Netlify, or Cloudflare Pages
3. **Update**: Change API URL in `App.tsx` to production backend
4. **Add**: Authentication, rate limiting, monitoring

---

## 📞 Need Help?

- **Backend Issues**: See `backend_processor/README_BACKEND.md`
- **Full Documentation**: See `README.md`
- **GitHub Issues**: https://github.com/bobvasic/vectorizationFourStages/issues

---

## ✅ Success Checklist

- [ ] Backend starts without errors (Terminal 1)
- [ ] Frontend starts and opens browser (Terminal 2)
- [ ] Can drag and drop an image
- [ ] See "Vectorizing..." spinner
- [ ] SVG preview appears on right
- [ ] Can download the SVG file
- [ ] Backend logs show processing stages

If all checked, you're ready to vectorize! 🎉

---

**Built with ❤️ by CyberLink Security**  
*Full-stack vectorization made simple*

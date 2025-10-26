# Deployment Guide - Vectorizer.dev v3.0

**Last Updated:** 2025-10-26  
**Author:** Bob Vasic (CyberLink Security)

---

## Quick Deploy (Docker)

```bash
git clone https://github.com/cyberlink-security/vectorizer_four_stages.git
cd vectorizer_four_stages
docker-compose up -d
```

**Services will be available at:**
- Frontend: `http://localhost:80`
- API: `http://localhost:8000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

---

## Prerequisites

### Production Server
- **OS:** Ubuntu 22.04+ LTS (recommended) or any Linux distro
- **CPU:** 4+ cores
- **RAM:** 16GB minimum (32GB for high concurrency)
- **Disk:** 50GB+ SSD
- **Docker:** 24.0+
- **Docker Compose:** 2.20+

### Development Environment
- **Node.js:** 20+
- **Python:** 3.12+
- **Rust:** 1.75+
- **RAM:** 8GB minimum

---

## Option 1: Docker Deployment (Recommended)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/cyberlink-security/vectorizer_four_stages.git
cd vectorizer_four_stages

# Configure environment (optional)
cp .env.example .env
nano .env  # Edit if needed
```

### Build and Start

```bash
# Build all services
docker-compose build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f vectorizer-api
```

### Verify Health

```bash
# Check all containers
docker-compose ps

# Test API
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"...","active_jobs":0}
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## Option 2: Manual Deployment

### Backend Setup

```bash
cd backend_processor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Build Rust core
cd ../rust_core
cargo build --release
maturin develop --release

# Start API server
cd ../backend_processor
python3 api_server.py
```

**API runs on:** `http://localhost:8000`

### Frontend Setup

```bash
# Install dependencies
npm install

# Development mode
npm run dev  # http://localhost:5173

# Production build
npm run build
npm run preview  # http://localhost:4173
```

---

## Environment Variables

### Backend (.env or export)

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
MAX_FILE_SIZE_MB=10
ALLOWED_ORIGINS=*  # Production: https://vectorizer.dev

# Storage
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs

# Performance
MAX_CONCURRENT_JOBS=10
WORKER_THREADS=4

# Monitoring (optional)
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
```

### Frontend (.env)

```bash
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Vectorizer.dev
```

---

## Production Configuration

### 1. Domain & SSL Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d vectorizer.dev -d api.vectorizer.dev

# Auto-renewal (crontab)
sudo crontab -e
# Add: 0 3 * * * certbot renew --quiet
```

### 2. Nginx Configuration

Create `/etc/nginx/sites-available/vectorizer.conf`:

```nginx
# Frontend
server {
    listen 80;
    server_name vectorizer.dev;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name vectorizer.dev;

    ssl_certificate /etc/letsencrypt/live/vectorizer.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vectorizer.dev/privkey.pem;

    root /var/www/vectorizer/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    gzip on;
    gzip_types text/css application/javascript application/json;
}

# API
server {
    listen 80;
    server_name api.vectorizer.dev;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.vectorizer.dev;

    ssl_certificate /etc/letsencrypt/live/api.vectorizer.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.vectorizer.dev/privkey.pem;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/vectorizer.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Systemd Service (Non-Docker)

Create `/etc/systemd/system/vectorizer-api.service`:

```ini
[Unit]
Description=Vectorizer.dev API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/vectorizer_four_stages/backend_processor
Environment="PATH=/opt/vectorizer_four_stages/backend_processor/venv/bin"
ExecStart=/opt/vectorizer_four_stages/backend_processor/venv/bin/python3 api_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vectorizer-api
sudo systemctl start vectorizer-api
sudo systemctl status vectorizer-api
```

---

## Docker Compose Services

### Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| `vectorizer-frontend` | 80 | React UI (Nginx) |
| `vectorizer-api` | 8000 | FastAPI backend |
| `vectorizer-redis` | 6379 | Cache (future) |
| `prometheus` | 9090 | Metrics collection |
| `grafana` | 3000 | Monitoring dashboards |

### docker-compose.yml Structure

```yaml
version: '3.8'

services:
  vectorizer-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./backend_processor/uploads:/app/uploads
      - ./backend_processor/outputs:/app/outputs
    environment:
      - MAX_FILE_SIZE_MB=10
      - MAX_CONCURRENT_JOBS=10
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  vectorizer-frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./dist:/usr/share/nginx/html:ro
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    restart: unless-stopped
```

---

## CI/CD Pipeline (GitHub Actions)

### Workflow: `.github/workflows/ci-cd.yml`

Automatically runs on push to `main`:

1. **Test** - Run Python + Rust test suites
2. **Build** - Build Docker images
3. **Security Audit** - cargo audit, npm audit, safety
4. **Performance Benchmark** - Measure processing times
5. **Deploy** - Push to production (on main branch)

### Manual Deployment Trigger

```bash
# Trigger deployment manually
gh workflow run ci-cd.yml
```

---

## Monitoring Setup

### Prometheus Metrics

Automatically collected at `http://localhost:8000/metrics`:

```
vectorizer_jobs_total          # Total processed
vectorizer_jobs_active         # Currently processing  
vectorizer_jobs_duration       # Processing time histogram
vectorizer_errors_total        # Error count
```

### Grafana Dashboard

1. Open `http://localhost:3000`
2. Login: `admin` / `admin`
3. Add Prometheus data source: `http://prometheus:9090`
4. Import dashboard: `monitoring/grafana-dashboard.json`

---

## Backup & Disaster Recovery

### Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/vectorizer"
DATE=$(date +%Y%m%d_%H%M%S)

# Stop services
docker-compose down

# Backup uploads & outputs
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" \
    backend_processor/uploads \
    backend_processor/outputs

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    .env \
    docker-compose.yml \
    monitoring/

# Restart services
docker-compose up -d

# Keep only last 7 days
find "$BACKUP_DIR" -mtime +7 -delete
```

Schedule with cron:

```bash
crontab -e
# Add: 0 2 * * * /opt/vectorizer/backup.sh
```

### Restore Procedure

```bash
# Stop services
docker-compose down

# Restore files
tar -xzf /backups/vectorizer/files_YYYYMMDD_HHMMSS.tar.gz

# Restore config
tar -xzf /backups/vectorizer/config_YYYYMMDD_HHMMSS.tar.gz

# Restart
docker-compose up -d
```

---

## Security Hardening

### Firewall (UFW)

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### Fail2Ban (Brute-force protection)

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Docker Security

```bash
# Run containers as non-root
docker-compose exec vectorizer-api whoami
# Should output: www-data (not root)

# Enable Docker content trust
export DOCKER_CONTENT_TRUST=1
```

---

## Scaling Strategies

### Horizontal Scaling

```bash
# Scale API workers
docker-compose up -d --scale vectorizer-api=3

# Add load balancer (nginx upstream)
upstream vectorizer_api {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

### Vertical Scaling

```yaml
# docker-compose.yml
services:
  vectorizer-api:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
```

---

## Troubleshooting

### Container won't start
```bash
docker-compose logs vectorizer-api
docker-compose ps
docker inspect vectorizer-api
```

### Out of disk space
```bash
docker system prune -a  # Remove unused images
du -sh backend_processor/outputs  # Check output size
```

### High memory usage
```bash
docker stats
# Reduce MAX_CONCURRENT_JOBS in .env
```

### Rust build fails
```bash
docker-compose build --no-cache vectorizer-api
```

---

**For API usage, see:** [2_API_REFERENCE.md](2_API_REFERENCE.md)  
**For operations, see:** [4_OPERATIONS_MANUAL.md](4_OPERATIONS_MANUAL.md)

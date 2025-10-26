# Operations Manual - Vectorizer.dev v3.0

**Last Updated:** 2025-10-26  
**Author:** Bob Vasic (CyberLink Security)

---

## Daily Operations

### Health Monitoring

```bash
# Check all services
docker-compose ps

# Check API health
curl http://localhost:8000/health

# Check logs
docker-compose logs --tail=100 -f vectorizer-api
```

### Performance Monitoring

**Prometheus Metrics:** `http://localhost:9090`  
**Grafana Dashboards:** `http://localhost:3000`

**Key Metrics to Monitor:**
- `vectorizer_jobs_active` - Current processing jobs
- `vectorizer_jobs_total` - Total processed (counter)
- `vectorizer_jobs_duration` - Processing time histogram
- `vectorizer_errors_total` - Error count by type

---

## Log Management

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs vectorizer-api

# Follow logs (real-time)
docker-compose logs -f vectorizer-api

# Last 100 lines
docker-compose logs --tail=100 vectorizer-api

# Filter by time
docker-compose logs --since=1h vectorizer-api
```

### Log Format

```
[2025-10-26 00:15:49] INFO - [JOB abc-123] Processing queued
[2025-10-26 00:15:49] INFO - [JOB abc-123] File saved: ./uploads/abc-123.jpg
[2025-10-26 00:15:54] INFO - [JOB abc-123] Complete! Time: 5.23s
```

### Log Levels

- **INFO** - Normal operations (job start, completion)
- **WARNING** - Non-critical issues (slow processing, retry)
- **ERROR** - Failed jobs, exceptions
- **CRITICAL** - Service failures, system errors

---

## Common Issues & Solutions

### 1. Job Stuck in "processing"

**Symptoms:**
- Status endpoint shows `"processing"` for > 10 minutes
- Progress stops updating

**Diagnosis:**
```bash
# Check container resources
docker stats vectorizer-api

# Check logs for errors
docker-compose logs --tail=50 vectorizer-api

# Check disk space
df -h
```

**Solutions:**
```bash
# Solution 1: Restart API service
docker-compose restart vectorizer-api

# Solution 2: Kill specific process (if needed)
docker-compose exec vectorizer-api ps aux
docker-compose exec vectorizer-api kill -9 <PID>

# Solution 3: Full restart
docker-compose down && docker-compose up -d
```

---

### 2. High Memory Usage

**Symptoms:**
- Container uses > 4GB RAM
- System becomes slow
- OOM (Out of Memory) errors

**Diagnosis:**
```bash
docker stats  # Check memory usage
docker-compose exec vectorizer-api free -h
```

**Solutions:**
```bash
# Reduce concurrent jobs in docker-compose.yml
environment:
  - MAX_CONCURRENT_JOBS=5  # Default: 10

# Limit container memory
deploy:
  resources:
    limits:
      memory: 4G

# Restart to apply
docker-compose down && docker-compose up -d
```

---

### 3. Disk Space Full

**Symptoms:**
- Upload fails with 500 error
- Docker errors: "no space left on device"

**Diagnosis:**
```bash
df -h
du -sh backend_processor/uploads
du -sh backend_processor/outputs
```

**Solutions:**
```bash
# Clean old processed files (7+ days old)
find backend_processor/outputs -type f -mtime +7 -delete

# Clean Docker system
docker system prune -a

# Clean upload cache
rm -rf backend_processor/uploads/*
```

**Prevention:**
```bash
# Set up automatic cleanup (cron)
crontab -e
# Add: 0 3 * * * find /opt/vectorizer/backend_processor/outputs -mtime +7 -delete
```

---

### 4. API Returns 500 Errors

**Symptoms:**
- Upload or status endpoint returns 500
- Error message: "Internal Server Error"

**Diagnosis:**
```bash
# Check recent errors
docker-compose logs --tail=50 vectorizer-api | grep ERROR

# Check Python traceback
docker-compose logs vectorizer-api | grep Traceback -A 20
```

**Common Causes:**

**A. Rust Module Not Loaded**
```bash
# Verify Rust core
docker-compose exec vectorizer-api python3 -c "import rust_core; print('OK')"

# Rebuild if needed
docker-compose build --no-cache vectorizer-api
docker-compose up -d vectorizer-api
```

**B. File Permission Issues**
```bash
# Fix permissions
docker-compose exec vectorizer-api chown -R www-data:www-data /app/uploads /app/outputs
```

**C. Corrupted Input File**
```bash
# Check file
file backend_processor/uploads/<job_id>.jpg
# Should show: JPEG image data

# Remove if corrupted
rm backend_processor/uploads/<job_id>.*
```

---

### 5. Slow Processing Times

**Symptoms:**
- Jobs take > 20s for 512×512 images
- Progress updates slowly

**Diagnosis:**
```bash
# Check CPU usage
docker stats vectorizer-api

# Check if Rust acceleration active
docker-compose logs vectorizer-api | grep RUST
# Should see: [RUST] Premium AI modules loaded
```

**Solutions:**
```bash
# Ensure Rust module compiled with optimizations
cd rust_core
cargo build --release
maturin develop --release

# Restart API
docker-compose restart vectorizer-api

# Verify improvement
time curl -X POST http://localhost:8000/api/upload -F "file=@test.jpg"
```

---

### 6. CORS Errors (Frontend)

**Symptoms:**
- Browser console: "CORS policy blocked"
- Frontend can't connect to API

**Diagnosis:**
```bash
# Check CORS config in api_server.py
grep "allow_origins" backend_processor/api_server.py
```

**Solutions:**

**Development:**
```python
# api_server.py - Allow all origins
allow_origins=["*"]
```

**Production:**
```python
# api_server.py - Restrict to domain
allow_origins=["https://vectorizer.dev"]
```

Restart after changes:
```bash
docker-compose restart vectorizer-api
```

---

## Performance Tuning

### Optimize for Speed

```yaml
# docker-compose.yml
environment:
  - MAX_CONCURRENT_JOBS=15  # Increase if CPU has headroom
  - WORKER_THREADS=8        # Match CPU cores
```

### Optimize for Quality

```python
# Users should use quality="ultra" parameter
# No server-side config needed
```

### Optimize for Memory

```yaml
# docker-compose.yml
environment:
  - MAX_CONCURRENT_JOBS=3   # Reduce concurrent jobs
  
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G
```

---

## Maintenance Procedures

### Weekly Tasks

```bash
# 1. Check disk usage
df -h

# 2. Clean old outputs (7+ days)
find backend_processor/outputs -mtime +7 -delete

# 3. Review error logs
docker-compose logs --since=7d vectorizer-api | grep ERROR

# 4. Check metrics
curl http://localhost:9090/api/v1/query?query=vectorizer_errors_total
```

### Monthly Tasks

```bash
# 1. Update Docker images
docker-compose pull
docker-compose up -d

# 2. Rotate logs
docker-compose logs > logs/vectorizer-$(date +%Y%m).log
docker-compose down && docker-compose up -d

# 3. Backup configuration
tar -czf backups/config-$(date +%Y%m%d).tar.gz \
    docker-compose.yml \
    .env \
    monitoring/

# 4. Security updates
sudo apt update && sudo apt upgrade -y
```

### Quarterly Tasks

```bash
# 1. Performance audit
cd backend_processor
python3 test_vectorization.py

# 2. Security audit
docker scan vectorizer-api:latest
npm audit
pip-audit

# 3. Capacity planning review
# Review Grafana metrics for growth trends

# 4. Documentation update
# Ensure all operational docs are current
```

---

## Incident Response

### Critical Issues (Immediate Action)

**Definition:** Service unavailable, data loss risk, security breach

**Response Checklist:**

1. **Assess Impact**
   ```bash
   # Check if service is down
   curl -f http://localhost:8000/health || echo "SERVICE DOWN"
   
   # Check active jobs
   curl http://localhost:8000/health | jq '.active_jobs'
   ```

2. **Attempt Quick Fix**
   ```bash
   # Restart services
   docker-compose restart vectorizer-api
   
   # If still down, full restart
   docker-compose down && docker-compose up -d
   ```

3. **Collect Logs**
   ```bash
   # Save logs for analysis
   docker-compose logs --since=1h > incident-$(date +%Y%m%d-%H%M%S).log
   ```

4. **Notify Stakeholders**
   - Post status update
   - Estimate recovery time
   - Document incident

5. **Root Cause Analysis**
   - Review logs
   - Identify failure point
   - Document in `incidents/` directory

---

## Backup & Recovery

### Automated Backups

**Backup Script:** `/opt/vectorizer/backup.sh`

```bash
#!/bin/bash
BACKUP_DIR="/backups/vectorizer"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup files
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" \
    backend_processor/uploads \
    backend_processor/outputs

# Backup config
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    .env docker-compose.yml monitoring/

# Cleanup old backups (> 30 days)
find "$BACKUP_DIR" -mtime +30 -delete

echo "Backup complete: $DATE"
```

**Schedule (crontab):**
```
0 2 * * * /opt/vectorizer/backup.sh
```

### Recovery Procedure

```bash
# 1. Stop services
docker-compose down

# 2. Restore files
cd /opt/vectorizer_four_stages
tar -xzf /backups/vectorizer/files_YYYYMMDD_HHMMSS.tar.gz

# 3. Restore config
tar -xzf /backups/vectorizer/config_YYYYMMDD_HHMMSS.tar.gz

# 4. Restart services
docker-compose up -d

# 5. Verify
curl http://localhost:8000/health
```

---

## Monitoring & Alerts

### Prometheus Alerts

Create `monitoring/alert-rules.yml`:

```yaml
groups:
  - name: vectorizer_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(vectorizer_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"
          
      - alert: ServiceDown
        expr: up{job="vectorizer-api"} == 0
        for: 1m
        annotations:
          summary: "Vectorizer API is down"
          
      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes{name="vectorizer-api"} > 4e9
        for: 5m
        annotations:
          summary: "High memory usage (> 4GB)"
```

### Grafana Dashboards

**Key Panels:**
1. Jobs processed (counter)
2. Active jobs (gauge)
3. Processing time (histogram)
4. Error rate (graph)
5. Memory usage (graph)
6. CPU usage (graph)

**Import:** `monitoring/grafana-dashboard.json`

---

## Security Operations

### Access Control

```bash
# Change default Grafana password
docker-compose exec grafana grafana-cli admin reset-admin-password <new_password>

# Restrict API origins (production)
# Edit api_server.py: allow_origins=["https://vectorizer.dev"]
```

### Security Audits

```bash
# Docker image scan
docker scan vectorizer-api:latest

# Python dependencies
pip-audit

# NPM dependencies
npm audit

# Rust dependencies
cargo audit
```

### SSL Certificate Renewal

```bash
# Auto-renewal (certbot)
sudo certbot renew --quiet

# Manual renewal
sudo certbot renew

# Verify expiry
sudo certbot certificates
```

---

## Scaling Operations

### Horizontal Scaling

```bash
# Scale API replicas
docker-compose up -d --scale vectorizer-api=3

# Verify
docker-compose ps
```

**Load Balancer (Nginx):**
```nginx
upstream vectorizer_backend {
    least_conn;
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
          cpus: '8.0'
          memory: 16G
```

---

## Contact & Support

### Escalation Path

1. **Level 1:** Operations team (routine issues)
2. **Level 2:** DevOps engineer (infrastructure)
3. **Level 3:** Bob Vasic (critical/security)

### Emergency Contacts

- **On-call:** [Phone/Slack channel]
- **Security:** security@cyberlinksecurity.com
- **DevOps:** Bob Vasic

---

**For core functionality, see:** [1_CORE_FUNCTIONALITY.md](1_CORE_FUNCTIONALITY.md)  
**For API usage, see:** [2_API_REFERENCE.md](2_API_REFERENCE.md)  
**For deployment, see:** [3_DEPLOYMENT_GUIDE.md](3_DEPLOYMENT_GUIDE.md)

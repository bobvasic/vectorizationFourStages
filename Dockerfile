# Multi-stage Dockerfile for Vectorizer.dev
# Production-ready with Rust + Python + Node.js

# Stage 1: Build Rust modules
FROM rust:1.75-slim as rust-builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Rust source
COPY rust_core/ ./rust_core/

# Build Rust with release optimizations
WORKDIR /build/rust_core
RUN cargo build --release

# Stage 2: Build Frontend
FROM node:20-slim as frontend-builder

WORKDIR /build

# Copy frontend source
COPY package*.json ./
COPY *.tsx ./
COPY *.ts ./
COPY *.json ./
COPY *.html ./
COPY components/ ./components/

# Install and build
RUN npm install
RUN npm run build

# Stage 3: Production Image
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python backend
COPY backend_processor/ ./backend_processor/
COPY --from=rust-builder /build/rust_core/target/release/*.so ./backend_processor/

# Copy built frontend
COPY --from=frontend-builder /build/dist ./dist

# Install Python dependencies
WORKDIR /app/backend_processor
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python3", "api_server.py"]

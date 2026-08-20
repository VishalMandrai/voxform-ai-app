# ─────────────────────────────────────────────────────────────────────────────
# VoxForm AI – Dockerfile
# ─────────────────────────────────────────────────────────────────────────────

## -> To build docker image move to project root directory.
## -> Run this command: 
##                      docker build -t voxform:<version-tag> .

## This creates Docker Image for VoxForm App

# ============================================================
# STAGE 1 — Build Next.js frontend
# ============================================================

FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

# Install dependencies first for better Docker layer caching
# Copy package.json to /app/frontend
COPY frontend-next/package*.json ./

RUN npm ci

# Copy frontend source - to /app/frontend
COPY frontend-next/ .

# Build static Next.js application
RUN npm run build


# ============================================================
# Stage 2 — FastAPI backend + Compiled Static frontend
# ============================================================

FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY app/ ./app/

# Copy the static Next.js output from Stage 1
COPY --from=frontend-builder /app/frontend/out ./frontend/out/

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# ============================================================

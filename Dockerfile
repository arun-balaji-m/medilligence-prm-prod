#FROM python:3.11
#
## --------------------------------
## Python runtime settings
## --------------------------------
#ENV PYTHONDONTWRITEBYTECODE=1
#ENV PYTHONUNBUFFERED=1
#
#WORKDIR /app
#
## --------------------------------
## System libraries needed by:
## - av, livekit, pipecat (audio/video)
## - pdf2image, pypdfium2 (PDF)
## - pytesseract (OCR)
## --------------------------------
#RUN apt-get update && apt-get install -y \
#    build-essential \
#    ffmpeg \
#    libsndfile1 \
#    libglib2.0-0 \
#    libsm6 \
#    libxext6 \
#    libxrender1 \
#    poppler-utils \
#    tesseract-ocr \
#    git \
#    curl \
#    && rm -rf /var/lib/apt/lists/*
#
## --------------------------------
## Python deps
## --------------------------------
#COPY requirements.txt .
#
#RUN pip install --upgrade pip
#RUN pip install --no-cache-dir -r requirements.txt
#
## --------------------------------
## Copy app
## --------------------------------
#COPY . .
#
## --------------------------------
## Render port
## --------------------------------
#EXPOSE 10000
#
## --------------------------------
## Production server
## --------------------------------
#CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--workers", "1", "--threads", "8", "--bind", "0.0.0.0:10000"]



###Working version
## --------------------------------
## Base image (best compatibility for ML/AV/OCR libs)
## --------------------------------
#FROM python:3.11
#
## --------------------------------
## Python runtime settings
## --------------------------------
#ENV PYTHONDONTWRITEBYTECODE=1
#ENV PYTHONUNBUFFERED=1
#ENV PIP_NO_CACHE_DIR=1
#ENV PIP_DISABLE_PIP_VERSION_CHECK=1
#
#WORKDIR /app
#
## --------------------------------
## System libraries
## --------------------------------
#RUN apt-get update && apt-get install -y \
#    build-essential \
#    ffmpeg \
#    libsndfile1 \
#    libglib2.0-0 \
#    libsm6 \
#    libxext6 \
#    libxrender1 \
#    poppler-utils \
#    tesseract-ocr \
#    curl \
#    && rm -rf /var/lib/apt/lists/*
#
## --------------------------------
## Python tooling
## --------------------------------
#RUN pip install --upgrade pip setuptools wheel
#
## --------------------------------
## Python dependencies
## --------------------------------
#COPY requirements.txt .
#
#RUN pip install --prefer-binary -r requirements.txt
#
## --------------------------------
## Copy app
## --------------------------------
#COPY . .
#
## --------------------------------
## Render port
## --------------------------------
#EXPOSE 10000
#
## --------------------------------
## Production server
## --------------------------------
#CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--workers", "1", "--threads", "8", "--bind", "0.0.0.0:10000"]



# ----------------------------
# Build stage
# ----------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install only build tools temporarily
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ----------------------------
# Runtime stage
# ----------------------------
FROM python:3.11-slim

WORKDIR /app

# Only runtime libs (no build tools)
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    tesseract-ocr \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MALLOC_ARENA_MAX=2
ENV PYTHONMALLOC=malloc

# Copy installed packages from builder
COPY --from=builder /usr/local /usr/local

# Copy app
COPY . .

EXPOSE 10000

# Single worker, low threads = low memory
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--workers", "1", "--threads", "2", "--bind", "0.0.0.0:10000"]

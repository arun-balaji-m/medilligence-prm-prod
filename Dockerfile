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


# --------------------------------
# Base image (best compatibility for ML/AV/OCR libs)
# --------------------------------
FROM python:3.11

# --------------------------------
# Python runtime settings
# --------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# --------------------------------
# System libraries
# --------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsndfile1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    poppler-utils \
    tesseract-ocr \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------
# Python tooling
# --------------------------------
RUN pip install --upgrade pip setuptools wheel

# --------------------------------
# Python dependencies
# --------------------------------
COPY requirements.txt .

RUN pip install --prefer-binary -r requirements.txt

# --------------------------------
# Copy app
# --------------------------------
COPY . .

# --------------------------------
# Render port
# --------------------------------
EXPOSE 10000

# --------------------------------
# Production server
# --------------------------------
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--workers", "1", "--threads", "8", "--bind", "0.0.0.0:10000"]

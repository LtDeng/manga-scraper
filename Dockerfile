FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    docker.io \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium

COPY src ./src

ENV PYTHONPATH=/app/src
ENV LIBRARY_ROOT=/app/library
# HOST_LIBRARY_ROOT intentionally has no image default.
# It must be injected at runtime so nested `docker run -v` mounts use host paths.
ENV KCC_DOCKER_IMAGE=ghcr.io/ciromattia/kcc:latest
ENV KCC_EXECUTABLE=""
ENV KCC_DOCKER_PLATFORM=""
ENV KCC_FLAGS="--format EPUB --nokepub --manga-style"

RUN mkdir -p /app/library

CMD ["uvicorn", "image_scraper.api:app", "--host", "0.0.0.0", "--port", "8000"]

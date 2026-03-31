FROM mcr.microsoft.com/playwright/python:v1.41.0

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src ./src

# Ensure imports work
ENV PYTHONPATH=/app/src

# Optional: create output dir (avoids runtime issues)
RUN mkdir -p /app/output/images

CMD ["python", "-m", "image_scraper.main"]

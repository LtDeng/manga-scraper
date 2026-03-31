FROM mcr.microsoft.com/playwright/python:v1.41.0

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

ENV PYTHONPATH=/app/src

RUN mkdir -p /app/output/images

CMD ["uvicorn", "image_scraper.api:app", "--host", "0.0.0.0", "--port", "8000"]
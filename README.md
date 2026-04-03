# Manga Scraper to EPUB Service

Playwright-based manga scraper API that captures chapter images and converts each chapter to EPUB through a Dockerized KCC (`kcc-c2e`) invocation.

## What changed

- Primary output is now **EPUB** (PDF is no longer the main pipeline).
- Output is stored in a deterministic manga library layout under `LIBRARY_ROOT` (default `/app/library`).
- API now accepts rich series/chapter metadata and persists `series.json` and `chapter.json`.
- KCC runs in a **separate Docker container** from the API runtime.

## Library folder structure

```text
/app/library/
  series/
    <series_slug>/
      series.json
      cover/
        cover.jpg
      chapters/
        <chapter_sort_key>__<chapter_slug>/
          chapter.json
          images/
            00000.jpg
            00001.png
      epub/
        <series_slug>__<chapter_sort_key>__<chapter_slug>.epub
```

## API

### `GET /health`
Health check.

### `POST /scrape-and-convert`
Scrape a chapter and convert to EPUB.

Request fields:

- `target_url` (required)
- `series_name` (required)
- `series_sort_name` (optional)
- `series_id` (optional)
- `volume` (optional)
- `chapter_number` (required)
- `chapter_title` (optional)
- `chapter_id` (optional)
- `author` (optional)
- `publisher` (optional)
- `language` (optional)
- `description` (optional)
- `tags` (optional list)
- `cover_image_url` (optional)
- `output_root` (optional, default `LIBRARY_ROOT`)
- `overwrite` (optional, default `false`)
- `cleanup_images_after_epub` (optional, default `false`)
- `fetch_existing_only` (optional, default `false`)

Behavior:

- If EPUB already exists and `overwrite=false`, returns existing file metadata immediately.
- If `fetch_existing_only=true` and file does not exist, returns `404`.
- Scrapes images into chapter-specific `images/` only.
- Persists `series.json` and `chapter.json`.
- Invokes KCC through Docker and writes deterministic EPUB filename.

### `GET /files/epub/{filename}`
Serves only EPUB files from the managed library path and blocks path traversal.

### Optional metadata endpoints

- `GET /series/{series_slug}/chapters`
- `GET /series/{series_slug}/chapters/{chapter_key}`

## Example curl

```bash
curl -X POST http://localhost:8000/scrape-and-convert \
  -H 'Content-Type: application/json' \
  -d '{
    "target_url": "https://mangapill.com/chapters/2-11173000/one-piece-chapter-1173",
    "series_name": "One Piece",
    "series_sort_name": "one_piece",
    "chapter_number": "1173",
    "chapter_id": "ch-1173",
    "author": "Eiichiro Oda",
    "publisher": "Shueisha",
    "language": "en",
    "output_root": "./library",
    "cover_image_url": "https://cdn11.bigcommerce.com/s-zkx5lhzlf8/images/stencil/1500x1500/products/1524988/8643666/9781569319017__87729.1743235474.jpg?c=1?imbypass=on"
  }'
```

## Example response payload

```json
{
  "status": "ok",
  "series_slug": "demo-series",
  "chapter_slug": "a-new-dawn",
  "chapter_sort_key": "0012_5",
  "image_count": 42,
  "chapter_dir": "/app/library/series/demo-series/chapters/0012_5__a-new-dawn",
  "epub_path": "/app/library/series/demo-series/epub/demo-series__0012_5__a-new-dawn.epub",
  "epub_filename": "demo-series__0012_5__a-new-dawn.epub",
  "fetch_url": "/files/epub/demo-series__0012_5__a-new-dawn.epub"
}
```

## Running with Docker

Build:

```bash
docker build -t manga-scraper .
```

Run (host Docker socket required for nested KCC container execution):

```bash
docker run --rm -p 8000:8000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/library:/app/library \
  -e LIBRARY_ROOT=/app/library \
  -e KCC_DOCKER_IMAGE=ghcr.io/ciromattia/kcc:latest \
  -e KCC_EXECUTABLE='' \
  -e KCC_DOCKER_PLATFORM='' \
  -e KCC_FLAGS='--format EPUB --nokepub --manga-style' \
  manga-scraper
```

For ARM hosts (Raspberry Pi / Jetson), if KCC image architecture detection is problematic, set:

```bash
-e KCC_DOCKER_PLATFORM=linux/arm64
```

## Multi-arch build (recommended for server deploy)

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t your-registry/manga-scraper:latest \
  --push .
```

### Assumptions / host requirements

- Linux host is 64-bit (`linux/amd64` or `linux/arm64`).
- Docker daemon is running on the host and reachable from container via `/var/run/docker.sock`.
- Host can pull and run `ghcr.io/ciromattia/kcc:latest`.
- API container has permissions to access the mounted Docker socket.

## Development

```bash
set -a
source .env
set +a
pip install -r requirements.txt
PYTHONPATH=src uvicorn image_scraper.api:app --host 0.0.0.0 --port 8000 --reload
pytest
ruff check .
```

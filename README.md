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
    "target_url": "https://reader.example.com/series/demo/chapter-12-5",
    "series_name": "Demo Series",
    "series_sort_name": "Demo Series",
    "series_id": "ext-123",
    "volume": "3",
    "chapter_number": "12.5",
    "chapter_title": "A New Dawn",
    "chapter_id": "ch-12-5",
    "author": "Jane Doe",
    "publisher": "Manga House",
    "language": "en",
    "description": "Chapter description",
    "tags": ["action", "fantasy"],
    "cover_image_url": "https://example.com/cover.jpg",
    "overwrite": false,
    "cleanup_images_after_epub": false,
    "fetch_existing_only": false
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
  -e KCC_DOCKER_IMAGE=ciromattia/kcc:latest \
  -e KCC_EXECUTABLE=kcc-c2e \
  -e KCC_FLAGS='--profile=KPW --manga-style' \
  manga-scraper
```

### Assumptions / host requirements

- Docker CLI is available in the API container.
- Host Docker daemon is reachable (typically via `/var/run/docker.sock`).
- KCC image is pullable by the host daemon.

## Development

```bash
pip install -r requirements.txt
pytest
ruff check .
```

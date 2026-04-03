from __future__ import annotations

import json
import logging
import os
import shutil
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from image_scraper.library import compute_paths, ensure_layout, list_chapters, write_chapter_metadata, write_series_metadata
from image_scraper.models import ScrapeConvertRequest, ScrapeConvertResponse
from image_scraper.services.cover import fetch_cover
from image_scraper.services.kcc import KccError, convert_with_kcc
from image_scraper.services.scrape import scrape_chapter_images

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
LIBRARY_ROOT = Path(os.getenv("LIBRARY_ROOT", "/app/library")).resolve()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scrape-and-convert", response_model=ScrapeConvertResponse)
def scrape_and_convert(req: ScrapeConvertRequest):
    paths = compute_paths(req)
    ensure_layout(paths)

    if paths.epub_path.exists() and not req.overwrite:
        return ScrapeConvertResponse(
            status="ok",
            series_slug=paths.series_slug,
            chapter_slug=paths.chapter_slug,
            chapter_sort_key=paths.chapter_sort_key,
            image_count=len(list(paths.chapter_images_dir.glob("*"))),
            chapter_dir=str(paths.chapter_dir),
            epub_path=str(paths.epub_path),
            epub_filename=paths.epub_filename,
            fetch_url=f"/files/epub/{paths.epub_filename}",
        )

    if req.fetch_existing_only:
        raise HTTPException(status_code=404, detail="EPUB not found for requested chapter")

    if req.overwrite:
        for image in paths.chapter_images_dir.glob("*"):
            if image.is_file():
                image.unlink()

    cover_saved = False
    if req.cover_image_url:
        cover_saved = fetch_cover(str(req.cover_image_url), paths.cover_path)

    write_series_metadata(req, paths, cover_saved)

    image_count = scrape_chapter_images(str(req.target_url), paths.chapter_images_dir)
    if image_count == 0:
        raise HTTPException(status_code=422, detail="No images were captured for chapter")

    write_chapter_metadata(req, paths, image_count)

    try:
        convert_with_kcc(paths.chapter_images_dir, paths.epub_dir, paths.epub_filename)
    except KccError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if req.cleanup_images_after_epub:
        shutil.rmtree(paths.chapter_images_dir)
        paths.chapter_images_dir.mkdir(parents=True, exist_ok=True)

    write_chapter_metadata(req, paths, image_count)

    return ScrapeConvertResponse(
        status="ok",
        series_slug=paths.series_slug,
        chapter_slug=paths.chapter_slug,
        chapter_sort_key=paths.chapter_sort_key,
        image_count=image_count,
        chapter_dir=str(paths.chapter_dir),
        epub_path=str(paths.epub_path),
        epub_filename=paths.epub_filename,
        fetch_url=f"/files/epub/{paths.epub_filename}",
    )


@app.get("/files/epub/{filename}")
def get_epub_file(filename: str):
    clean_name = Path(filename).name
    if clean_name != filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    matches = list(LIBRARY_ROOT.glob(f"series/*/epub/{clean_name}"))
    if not matches:
        raise HTTPException(status_code=404, detail="EPUB not found")

    path = matches[0].resolve()
    if not str(path).endswith(".epub"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    return FileResponse(path, media_type="application/epub+zip", filename=clean_name)


@app.get("/series/{series_slug}/chapters")
def get_series_chapters(series_slug: str):
    series_dir = LIBRARY_ROOT / "series" / series_slug
    if not series_dir.exists():
        raise HTTPException(status_code=404, detail="Series not found")
    return {"series_slug": series_slug, "chapters": list_chapters(series_dir)}


@app.get("/series/{series_slug}/chapters/{chapter_key}")
def get_chapter(series_slug: str, chapter_key: str):
    chapter_json = LIBRARY_ROOT / "series" / series_slug / "chapters" / chapter_key / "chapter.json"
    if not chapter_json.exists():
        raise HTTPException(status_code=404, detail="Chapter not found")
    return json.loads(chapter_json.read_text(encoding="utf-8"))

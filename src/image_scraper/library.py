from __future__ import annotations

import json
from pathlib import Path

from image_scraper.models import ChapterMetadata, ComputedPaths, ScrapeConvertRequest, SeriesMetadata
from image_scraper.naming import chapter_slug, chapter_sort_key, slugify


def compute_paths(request: ScrapeConvertRequest) -> ComputedPaths:
    output_root = Path(request.output_root).resolve()
    series_slug = slugify(request.series_sort_name or request.series_name)
    ch_sort_key = chapter_sort_key(request.chapter_number)
    ch_slug = chapter_slug(request.chapter_title, request.chapter_number)
    ch_key = f"{ch_slug}"

    series_dir = output_root / "series" / series_slug
    epub_filename = f"{series_slug}-{ch_slug}.epub"

    return ComputedPaths(
        output_root=output_root,
        series_slug=series_slug,
        chapter_slug=ch_slug,
        chapter_sort_key=ch_sort_key,
        chapter_key=ch_key,
        series_dir=series_dir,
        series_json_path=series_dir / "series.json",
        cover_dir=series_dir / "cover",
        cover_path=series_dir / "cover" / "cover.jpg",
        chapters_dir=series_dir / "chapters",
        chapter_dir=series_dir / "chapters" / ch_key,
        chapter_json_path=series_dir / "chapters" / ch_key / "chapter.json",
        chapter_images_dir=series_dir / "chapters" / ch_key / "images",
        epub_dir=series_dir / "epub",
        epub_filename=epub_filename,
        epub_path=series_dir / "epub" / epub_filename,
    )


def ensure_layout(paths: ComputedPaths) -> None:
    paths.series_dir.mkdir(parents=True, exist_ok=True)
    paths.cover_dir.mkdir(parents=True, exist_ok=True)
    paths.chapters_dir.mkdir(parents=True, exist_ok=True)
    paths.chapter_dir.mkdir(parents=True, exist_ok=True)
    paths.chapter_images_dir.mkdir(parents=True, exist_ok=True)
    paths.epub_dir.mkdir(parents=True, exist_ok=True)


def write_series_metadata(request: ScrapeConvertRequest, paths: ComputedPaths, cover_exists: bool) -> None:
    metadata = SeriesMetadata(
        series_name=request.series_name,
        series_sort_name=request.series_sort_name,
        series_id=request.series_id,
        author=request.author,
        publisher=request.publisher,
        language=request.language,
        description=request.description,
        tags=request.tags,
        series_slug=paths.series_slug,
        cover_path=str(paths.cover_path) if cover_exists else None,
    )
    paths.series_json_path.write_text(json.dumps(metadata.model_dump(), indent=2), encoding="utf-8")


def write_chapter_metadata(request: ScrapeConvertRequest, paths: ComputedPaths, image_count: int) -> None:
    metadata = ChapterMetadata(
        chapter_number=str(request.chapter_number),
        chapter_title=request.chapter_title,
        chapter_id=request.chapter_id,
        volume=request.volume,
        target_url=str(request.target_url),
        chapter_slug=paths.chapter_slug,
        chapter_sort_key=paths.chapter_sort_key,
        chapter_key=paths.chapter_key,
        image_count=image_count,
        images_dir=str(paths.chapter_images_dir),
        epub_path=str(paths.epub_path),
    )
    paths.chapter_json_path.write_text(json.dumps(metadata.model_dump(), indent=2), encoding="utf-8")


def list_chapters(series_dir: Path) -> list[dict]:
    chapters = []
    chapters_dir = series_dir / "chapters"
    if not chapters_dir.exists():
        return chapters

    for chapter_dir in sorted(chapters_dir.iterdir()):
        chapter_json = chapter_dir / "chapter.json"
        if chapter_json.exists():
            chapters.append(json.loads(chapter_json.read_text(encoding="utf-8")))
    return chapters

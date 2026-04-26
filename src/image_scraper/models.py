from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ScrapeConvertRequest(BaseModel):
    target_url: HttpUrl
    series_name: str = Field(min_length=1)
    series_sort_name: str | None = None
    series_id: str | None = None
    volume: str | None = None
    chapter_number: str | float | int
    chapter_title: str | None = None
    chapter_id: str | None = None
    author: str | None = None
    publisher: str | None = None
    language: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    cover_image_url: HttpUrl | None = None
    output_root: str = Field(default_factory=lambda: os.getenv("LIBRARY_ROOT", "/app/library"))
    overwrite: bool = False
    cleanup_images_after_epub: bool = False
    fetch_existing_only: bool = False

    @field_validator("series_name")
    @classmethod
    def normalize_series_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("series_name must not be empty")
        return normalized


class ScrapeConvertResponse(BaseModel):
    status: str
    series_slug: str
    chapter_label: str
    chapter_slug: str
    chapter_sort_key: str
    image_count: int
    chapter_dir: str
    epub_path: str
    epub_filename: str
    fetch_url: str


class SeriesMetadata(BaseModel):
    series_name: str
    series_sort_name: str | None = None
    series_id: str | None = None
    author: str | None = None
    publisher: str | None = None
    language: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    series_slug: str
    cover_path: str | None = None


class ChapterMetadata(BaseModel):
    chapter_number: str
    chapter_label: str
    chapter_title: str | None = None
    chapter_id: str | None = None
    volume: str | None = None
    target_url: str
    chapter_slug: str
    chapter_sort_key: str
    chapter_key: str
    image_count: int = 0
    images_dir: str
    epub_path: str


class ComputedPaths(BaseModel):
    output_root: Path
    series_slug: str
    chapter_label: str
    chapter_slug: str
    chapter_sort_key: str
    chapter_key: str
    series_dir: Path
    series_json_path: Path
    cover_dir: Path
    cover_path: Path
    chapters_dir: Path
    chapter_dir: Path
    chapter_json_path: Path
    chapter_images_dir: Path
    epub_dir: Path
    epub_filename: str
    epub_path: Path

    model_config = {"arbitrary_types_allowed": True}

    def as_dict(self) -> dict[str, Any]:
        data = self.model_dump()
        for key, value in data.items():
            if isinstance(value, Path):
                data[key] = str(value)
        return data

from pathlib import Path

import pytest
from pydantic import ValidationError

import image_scraper.api as api_module
from image_scraper.api import scrape_and_convert
from image_scraper.models import ScrapeConvertRequest


def test_request_validation_for_required_fields():
    with pytest.raises(ValidationError):
        ScrapeConvertRequest(target_url="https://example.com")


def test_existing_file_short_circuit(tmp_path):
    series_dir = tmp_path / "series" / "demo-series" / "epub"
    series_dir.mkdir(parents=True)
    epub_file = series_dir / "demo-series_chapter_1.epub"
    epub_file.write_text("ok", encoding="utf-8")

    req = ScrapeConvertRequest(
        target_url="https://example.com/ch1",
        series_name="Demo Series",
        chapter_number="1",
        output_root=str(tmp_path),
    )

    response = scrape_and_convert(req)
    assert response.epub_filename == epub_file.name
    assert Path(response.epub_path) == epub_file
    assert response.image_count == 0
    assert response.chapter_label == "1"


def test_existing_file_short_circuit_rewrites_metadata(tmp_path):
    api_module.LIBRARY_ROOT = tmp_path
    series_root = tmp_path / "series" / "demo-series"
    chapter_dir = series_root / "chapters" / "1"
    images_dir = chapter_dir / "images"
    epub_file = series_root / "epub" / "demo-series_chapter_1.epub"
    cover_file = series_root / "cover" / "cover.jpg"

    images_dir.mkdir(parents=True)
    epub_file.parent.mkdir(parents=True)
    cover_file.parent.mkdir(parents=True)

    (images_dir / "00000.jpg").write_text("img", encoding="utf-8")
    epub_file.write_text("ok", encoding="utf-8")
    cover_file.write_text("cover", encoding="utf-8")

    req = ScrapeConvertRequest(
        target_url="https://example.com/ch1",
        series_name="Demo Series",
        series_sort_name="demo_series",
        chapter_number="1",
        chapter_id="ch-1",
        author="Author Name",
        output_root=str(tmp_path),
    )

    response = scrape_and_convert(req)

    assert response.image_count == 1
    assert (series_root / "series.json").exists()
    assert (chapter_dir / "chapter.json").exists()
    assert "cover.jpg" in (series_root / "series.json").read_text(encoding="utf-8")
    assert '"chapter_key": "1"' in (chapter_dir / "chapter.json").read_text(encoding="utf-8")


def test_scrape_and_convert_applies_epub_metadata_after_conversion(tmp_path, monkeypatch):
    api_module.LIBRARY_ROOT = tmp_path
    applied = {}

    def fake_fetch_cover(url: str, destination: Path) -> bool:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("cover", encoding="utf-8")
        return True

    def fake_scrape_chapter_images(url: str, destination: Path) -> int:
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "00000.jpg").write_text("img", encoding="utf-8")
        return 1

    def fake_convert_with_kcc(images_dir: Path, output_dir: Path, desired_filename: str) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        epub_path = output_dir / desired_filename
        epub_path.write_text("epub", encoding="utf-8")
        return epub_path

    def fake_apply_epub_metadata(epub_path: Path, request: ScrapeConvertRequest) -> None:
        applied["epub_path"] = epub_path
        applied["series_name"] = request.series_name
        applied["chapter_number"] = str(request.chapter_number)

    monkeypatch.setattr(api_module, "fetch_cover", fake_fetch_cover)
    monkeypatch.setattr(api_module, "scrape_chapter_images", fake_scrape_chapter_images)
    monkeypatch.setattr(api_module, "convert_with_kcc", fake_convert_with_kcc)
    monkeypatch.setattr(api_module, "apply_epub_metadata", fake_apply_epub_metadata)

    req = ScrapeConvertRequest(
        target_url="https://example.com/ch1",
        series_name="Demo Series",
        chapter_number="1",
        author="Author Name",
        publisher="Publisher Name",
        language="en",
        output_root=str(tmp_path),
        overwrite=True,
    )

    response = scrape_and_convert(req)

    assert response.epub_filename == "demo-series_chapter_1.epub"
    assert applied == {
        "epub_path": tmp_path / "series" / "demo-series" / "epub" / "demo-series_chapter_1.epub",
        "series_name": "Demo Series",
        "chapter_number": "1",
    }

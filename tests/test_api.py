from pathlib import Path

import pytest
from pydantic import ValidationError

from image_scraper.api import scrape_and_convert
from image_scraper.models import ScrapeConvertRequest


def test_request_validation_for_required_fields():
    with pytest.raises(ValidationError):
        ScrapeConvertRequest(target_url="https://example.com")


def test_existing_file_short_circuit(tmp_path):
    series_dir = tmp_path / "series" / "demo-series" / "epub"
    series_dir.mkdir(parents=True)
    epub_file = series_dir / "demo-series__0001__chapter-1.epub"
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

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

import image_scraper.api as api_module


def _client_with_library_root(tmp_path: Path) -> TestClient:
    api_module.LIBRARY_ROOT = tmp_path
    return TestClient(api_module.app)


def test_health_endpoint_returns_ok(tmp_path):
    client = _client_with_library_root(tmp_path)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_epub_file_returns_epub_from_library(tmp_path):
    client = _client_with_library_root(tmp_path)
    epub_file = tmp_path / "series" / "one-piece" / "epub" / "one-piece_chapter_1173.epub"
    epub_file.parent.mkdir(parents=True, exist_ok=True)
    epub_file.write_bytes(b"epub-bytes")

    response = client.get(f"/files/epub/{epub_file.name}")

    assert response.status_code == 200
    assert response.content == b"epub-bytes"
    assert response.headers["content-type"].startswith("application/epub+zip")


def test_get_epub_file_path_traversal_is_not_routable(tmp_path):
    client = _client_with_library_root(tmp_path)

    response = client.get("/files/epub/../secret.epub")

    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


def test_get_epub_file_not_found_returns_404(tmp_path):
    client = _client_with_library_root(tmp_path)

    response = client.get("/files/epub/missing.epub")

    assert response.status_code == 404
    assert response.json()["detail"] == "EPUB not found"


def test_get_series_chapters_returns_chapter_metadata_list(tmp_path):
    client = _client_with_library_root(tmp_path)
    chapter_dir = tmp_path / "series" / "one-piece" / "chapters" / "1173"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    chapter_payload = {"chapter_key": "1173", "chapter_number": "1173", "chapter_label": "1173"}
    (chapter_dir / "chapter.json").write_text(json.dumps(chapter_payload), encoding="utf-8")

    response = client.get("/series/one-piece/chapters")

    assert response.status_code == 200
    assert response.json() == {"series_slug": "one-piece", "chapters": [chapter_payload]}


def test_get_series_chapters_missing_series_returns_404(tmp_path):
    client = _client_with_library_root(tmp_path)

    response = client.get("/series/missing-series/chapters")

    assert response.status_code == 404
    assert response.json()["detail"] == "Series not found"


def test_get_chapter_returns_json_payload(tmp_path):
    client = _client_with_library_root(tmp_path)
    chapter_key = "1173"
    chapter_dir = tmp_path / "series" / "one-piece" / "chapters" / chapter_key
    chapter_dir.mkdir(parents=True, exist_ok=True)
    chapter_payload = {"chapter_key": chapter_key, "image_count": 16}
    (chapter_dir / "chapter.json").write_text(json.dumps(chapter_payload), encoding="utf-8")

    response = client.get(f"/series/one-piece/chapters/{chapter_key}")

    assert response.status_code == 200
    assert response.json() == chapter_payload


def test_get_chapter_missing_file_returns_404(tmp_path):
    client = _client_with_library_root(tmp_path)

    response = client.get("/series/one-piece/chapters/1173")

    assert response.status_code == 404
    assert response.json()["detail"] == "Chapter not found"

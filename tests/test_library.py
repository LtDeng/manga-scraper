from image_scraper.library import compute_paths
from image_scraper.models import ScrapeConvertRequest


def test_compute_paths_is_deterministic():
    req = ScrapeConvertRequest(
        target_url="https://example.com/ch1",
        series_name="One Piece",
        chapter_number="12.5",
        chapter_title="A New Dawn",
        output_root="/tmp/library",
    )

    first = compute_paths(req)
    second = compute_paths(req)

    assert first.chapter_dir == second.chapter_dir
    assert first.chapter_dir.name == "12.5"
    assert first.epub_filename == "one-piece_chapter_12.5.epub"

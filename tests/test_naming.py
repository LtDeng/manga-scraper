from image_scraper.naming import chapter_number_label, chapter_slug, chapter_sort_key, slugify


def test_slugify_basic():
    assert slugify("My Hero Academia!!") == "my-hero-academia"


def test_chapter_sort_key_numeric_and_decimal():
    assert chapter_sort_key("1") == "0001"
    assert chapter_sort_key("1.5") == "0001_5"
    assert chapter_sort_key("1173") == "1173"


def test_chapter_number_label_normalizes_numeric_values():
    assert chapter_number_label("001") == "1"
    assert chapter_number_label("12.50") == "12.5"
    assert chapter_number_label(1173) == "1173"


def test_chapter_slug_uses_number_when_title_missing():
    assert chapter_slug(None, "12") == "chapter-12"

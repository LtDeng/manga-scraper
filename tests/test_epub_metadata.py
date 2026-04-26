from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from image_scraper.models import ScrapeConvertRequest
from image_scraper.services.epub_metadata import apply_epub_metadata, build_epub_title


def test_build_epub_title_includes_series_chapter_and_optional_title():
    req_without_title = ScrapeConvertRequest(
        target_url="https://example.com/ch1",
        series_name="One Piece",
        chapter_number="1173",
    )
    req_with_title = ScrapeConvertRequest(
        target_url="https://example.com/ch1",
        series_name="One Piece",
        chapter_number="1173",
        chapter_title="A New Dawn",
    )

    assert build_epub_title(req_without_title) == "One Piece Chapter 1173"
    assert build_epub_title(req_with_title) == "One Piece Chapter 1173: A New Dawn"


def test_apply_epub_metadata_updates_package_document(tmp_path: Path):
    epub_path = tmp_path / "chapter.epub"
    _create_test_epub(epub_path)

    req = ScrapeConvertRequest(
        target_url="https://example.com/ch1",
        series_name="One Piece",
        chapter_number="1173",
        chapter_title="A New Dawn",
        author="Eiichiro Oda",
        publisher="Shueisha",
        language="en",
        description="Pirates and adventure.",
    )

    apply_epub_metadata(epub_path, req)

    with ZipFile(epub_path) as archive:
        assert archive.getinfo("mimetype").compress_type == ZIP_STORED
        opf = archive.read("OEBPS/content.opf").decode("utf-8")

    assert "<dc:title>One Piece Chapter 1173: A New Dawn</dc:title>" in opf
    assert "<dc:creator>Eiichiro Oda</dc:creator>" in opf
    assert "<dc:publisher>Shueisha</dc:publisher>" in opf
    assert "<dc:language>en</dc:language>" in opf
    assert "<dc:description>Pirates and adventure.</dc:description>" in opf
    assert 'property="belongs-to-collection">One Piece</' in opf
    assert 'property="collection-type">series</' in opf
    assert 'property="group-position">1173</' in opf
    assert "<dc:title>images</dc:title>" not in opf
    assert "<dc:creator>KCC</dc:creator>" not in opf


def _create_test_epub(epub_path: Path) -> None:
    container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
    opf = """<?xml version="1.0" encoding="UTF-8"?>
<package version="3.0" unique-identifier="BookID" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>images</dc:title>
    <dc:language>en-US</dc:language>
    <dc:identifier id="BookID">urn:uuid:test-id</dc:identifier>
    <dc:creator>KCC</dc:creator>
    <meta property="belongs-to-collection">Old Series</meta>
    <meta refines="#series-collection" property="collection-type">set</meta>
    <meta refines="#series-collection" property="group-position">1</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" properties="nav" media-type="application/xhtml+xml"/>
  </manifest>
  <spine/>
</package>
"""

    with ZipFile(epub_path, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=ZIP_STORED)
        archive.writestr("META-INF/container.xml", container_xml, compress_type=ZIP_DEFLATED)
        archive.writestr("OEBPS/content.opf", opf, compress_type=ZIP_DEFLATED)
        archive.writestr("OEBPS/nav.xhtml", "<html/>", compress_type=ZIP_DEFLATED)

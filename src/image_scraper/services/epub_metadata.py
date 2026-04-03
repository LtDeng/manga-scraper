from __future__ import annotations

import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

from image_scraper.models import ScrapeConvertRequest

CONTAINER_PATH = "META-INF/container.xml"
OPF_NS = "http://www.idpf.org/2007/opf"
DC_NS = "http://purl.org/dc/elements/1.1/"
CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"

ET.register_namespace("", OPF_NS)
ET.register_namespace("dc", DC_NS)


def apply_epub_metadata(epub_path: Path, request: ScrapeConvertRequest) -> None:
    with ZipFile(epub_path, "r") as source:
        opf_path = _find_opf_path(source)
        opf_bytes = source.read(opf_path)
        updated_opf = _update_opf_metadata(opf_bytes, request)
        entries = [(info, source.read(info.filename)) for info in source.infolist()]

    with tempfile.NamedTemporaryFile(dir=epub_path.parent, suffix=".epub", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)

    try:
        with ZipFile(tmp_path, "w") as target:
            for info, data in entries:
                if info.filename == opf_path:
                    data = updated_opf
                _write_entry(target, info, data)
        tmp_path.replace(epub_path)
    finally:
        tmp_path.unlink(missing_ok=True)


def _find_opf_path(archive: ZipFile) -> str:
    container_xml = archive.read(CONTAINER_PATH)
    root = ET.fromstring(container_xml)
    rootfile = root.find(f".//{{{CONTAINER_NS}}}rootfile")
    if rootfile is None:
        raise ValueError("EPUB container is missing the package document reference")

    full_path = rootfile.get("full-path")
    if not full_path:
        raise ValueError("EPUB container rootfile is missing full-path")
    return full_path


def _update_opf_metadata(opf_bytes: bytes, request: ScrapeConvertRequest) -> bytes:
    root = ET.fromstring(opf_bytes)
    metadata = root.find(f"{{{OPF_NS}}}metadata")
    if metadata is None:
        raise ValueError("EPUB package is missing metadata")

    _remove_children(metadata, f"{{{DC_NS}}}title")
    _remove_children(metadata, f"{{{DC_NS}}}creator")
    _remove_children(metadata, f"{{{DC_NS}}}publisher")
    _remove_children(metadata, f"{{{DC_NS}}}language")
    _remove_children(metadata, f"{{{DC_NS}}}description")
    _remove_meta(metadata, property_name="belongs-to-collection")
    _remove_meta(metadata, property_name="collection-type")
    _remove_meta(metadata, property_name="group-position")

    ET.SubElement(metadata, f"{{{DC_NS}}}title").text = build_epub_title(request)
    ET.SubElement(metadata, f"{{{DC_NS}}}language").text = request.language or "en"

    if request.author:
        ET.SubElement(metadata, f"{{{DC_NS}}}creator").text = request.author
    if request.publisher:
        ET.SubElement(metadata, f"{{{DC_NS}}}publisher").text = request.publisher
    if request.description:
        ET.SubElement(metadata, f"{{{DC_NS}}}description").text = request.description

    collection_meta = ET.SubElement(metadata, f"{{{OPF_NS}}}meta")
    collection_meta.set("id", "series-collection")
    collection_meta.set("property", "belongs-to-collection")
    collection_meta.text = request.series_name

    collection_type_meta = ET.SubElement(metadata, f"{{{OPF_NS}}}meta")
    collection_type_meta.set("refines", "#series-collection")
    collection_type_meta.set("property", "collection-type")
    collection_type_meta.text = "series"

    group_position_meta = ET.SubElement(metadata, f"{{{OPF_NS}}}meta")
    group_position_meta.set("refines", "#series-collection")
    group_position_meta.set("property", "group-position")
    group_position_meta.text = str(request.chapter_number).strip()

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def build_epub_title(request: ScrapeConvertRequest) -> str:
    chapter_number = str(request.chapter_number).strip()
    if request.chapter_title:
        return f"{request.series_name} Chapter {chapter_number}: {request.chapter_title.strip()}"
    return f"{request.series_name} Chapter {chapter_number}"


def _remove_children(parent: ET.Element, tag: str) -> None:
    for child in list(parent.findall(tag)):
        parent.remove(child)


def _remove_meta(parent: ET.Element, *, property_name: str) -> None:
    for child in list(parent.findall(f"{{{OPF_NS}}}meta")):
        if child.get("property") == property_name:
            parent.remove(child)


def _write_entry(target: ZipFile, source_info: ZipInfo, data: bytes) -> None:
    info = ZipInfo(source_info.filename)
    info.date_time = source_info.date_time
    info.comment = source_info.comment
    info.extra = source_info.extra
    info.create_system = source_info.create_system
    info.external_attr = source_info.external_attr
    info.internal_attr = source_info.internal_attr
    info.flag_bits = source_info.flag_bits
    info.volume = source_info.volume
    info.compress_type = ZIP_STORED if source_info.filename == "mimetype" else ZIP_DEFLATED
    target.writestr(info, data)

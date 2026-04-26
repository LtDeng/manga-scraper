from __future__ import annotations

import re
import unicodedata


def slugify(value: str, fallback: str = "item") -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    lowered = normalized.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or fallback


def chapter_sort_key(chapter_number: str | int | float) -> str:
    raw = str(chapter_number).strip()

    whole_match = re.fullmatch(r"(\d+)", raw)
    if whole_match:
        whole = whole_match.group(1)
        return whole.zfill(max(4, len(whole)))

    decimal_match = re.fullmatch(r"(\d+)\.(\d+)", raw)
    if decimal_match:
        whole = decimal_match.group(1).zfill(max(4, len(decimal_match.group(1))))
        fraction = decimal_match.group(2).rstrip("0") or "0"
        return f"{whole}_{fraction}"

    fallback = re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_") or "special"
    return f"9999_{fallback}"


def chapter_number_label(chapter_number: str | int | float) -> str:
    raw = str(chapter_number).strip()

    whole_match = re.fullmatch(r"(\d+)", raw)
    if whole_match:
        return str(int(whole_match.group(1)))

    decimal_match = re.fullmatch(r"(\d+)\.(\d+)", raw)
    if decimal_match:
        whole = str(int(decimal_match.group(1)))
        fraction = decimal_match.group(2).rstrip("0")
        return f"{whole}.{fraction}" if fraction else whole

    return raw or "special"


def chapter_slug(chapter_title: str | None, chapter_number: str | int | float) -> str:
    if chapter_title:
        return slugify(chapter_title, fallback=f"chapter-{chapter_number}")
    return slugify(f"chapter-{chapter_number}")

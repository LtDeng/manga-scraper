from __future__ import annotations

import logging
from pathlib import Path
from urllib.request import urlopen

logger = logging.getLogger(__name__)


def fetch_cover(cover_url: str, cover_path: Path) -> bool:
    try:
        logger.info("Downloading cover image from %s", cover_url)
        with urlopen(cover_url) as response:  # nosec - trusted input from API caller
            data = response.read()
        cover_path.write_bytes(data)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("Cover download failed: %s", exc)
        return False

from pathlib import Path
from typing import Set
from playwright.sync_api import Response
from image_scraper.config import ScraperConfig


class ImageInterceptor:
    def __init__(self, config: ScraperConfig, output_dir: Path):
        self.config = config
        self.output_dir = output_dir
        self._seen_urls: Set[str] = set()
        self._counter = 0

    def handle_response(self, response: Response) -> None:
        if response.url in self._seen_urls:
            return

        content_type = response.headers.get("content-type", "").split(";")[0]
        if content_type not in self.config.allowed_image_types:
            return

        body = response.body()
        if len(body) < self.config.min_image_size_bytes:
            return

        self._seen_urls.add(response.url)
        self._save_image(body, content_type)

    def _save_image(self, data: bytes, mime: str) -> None:
        ext = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp"
        }[mime]

        filename = f"{self._counter:05}.{ext}"
        self._counter += 1
        (self.output_dir / filename).write_bytes(data)

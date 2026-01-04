from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


@dataclass(frozen=True)
class ScraperConfig:
    target_url: str
    output_dir: Path
    pdf_name: str = "output.pdf"

    viewport: Tuple[int, int] = (1280, 900)
    scroll_step: int = 2000
    scroll_iterations: int = 25
    scroll_delay: float = 0.25

    allowed_image_types: Tuple[str, ...] = ("image/jpeg", "image/png", "image/webp")
    min_image_size_bytes: int = 20_000

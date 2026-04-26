from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


@dataclass(frozen=True)
class ScraperConfig:
    target_url: str
    output_dir: Path
    pdf_name: str = "output.pdf"

    viewport: Tuple[int, int] = (1280, 900)
    scroll_step: int = 800
    scroll_iterations: int = 40
    scroll_delay: float = 0.15

    allowed_image_types: Tuple[str, ...] = ("image/jpeg", "image/png")
    min_image_size_bytes: int = 20_000

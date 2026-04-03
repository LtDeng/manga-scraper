from __future__ import annotations

import logging
from pathlib import Path

from image_scraper.config import ScraperConfig
from image_scraper.core.scraper import ScraperBot

logger = logging.getLogger(__name__)


def scrape_chapter_images(target_url: str, image_dir: Path) -> int:
    logger.info("Starting scrape for %s into %s", target_url, image_dir)
    config = ScraperConfig(target_url=target_url, output_dir=image_dir)
    bot = ScraperBot(config)
    image_count = bot.run()
    logger.info("Scrape complete with %s images", image_count)
    return image_count

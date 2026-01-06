from pathlib import Path
from image_scraper.config import ScraperConfig
from image_scraper.core.scraper import ScraperBot


def main():
    config = ScraperConfig(
        target_url="https://mangapill.com/chapters/2-11170000/one-piece-chapter-1167",
        output_dir=Path("output/images"),
        pdf_name="result.pdf"
    )

    bot = ScraperBot(config)
    bot.run()


if __name__ == "__main__":
    main()

from pathlib import Path
import argparse

from image_scraper.config import ScraperConfig
from image_scraper.core.scraper import ScraperBot


def parse_args():
    parser = argparse.ArgumentParser(description="Image scraper with Playwright")

    parser.add_argument(
        "--target_url",
        required=True,
        help="Target URL to scrape"
    )

    parser.add_argument(
        "--output_dir",
        default="output/images",
        help="Directory to store images (default: output/images)"
    )

    parser.add_argument(
        "--pdf_name",
        default="output.pdf",
        help="Output PDF filename (default: output.pdf)"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    pdf_name = args.pdf_name
    if not pdf_name.lower().endswith(".pdf"):
        pdf_name += ".pdf"

    config = ScraperConfig(
        target_url=args.target_url,
        output_dir=Path(args.output_dir),
        pdf_name=pdf_name
    )

    bot = ScraperBot(config)
    bot.run()


if __name__ == "__main__":
    main()
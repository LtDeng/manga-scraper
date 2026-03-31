from pathlib import Path
import argparse

from image_scraper.config import ScraperConfig
from image_scraper.core.scraper import ScraperBot


def run_scraper(target_url: str, output_dir: str, pdf_name: str):
    if not pdf_name.lower().endswith(".pdf"):
        pdf_name += ".pdf"

    config = ScraperConfig(
        target_url=target_url,
        output_dir=Path(output_dir),
        pdf_name=pdf_name
    )

    bot = ScraperBot(config)
    bot.run()


def parse_args():
    parser = argparse.ArgumentParser(description="Image scraper with Playwright")

    parser.add_argument("--target_url", required=True)
    parser.add_argument("--output_dir", default="output/images")
    parser.add_argument("--pdf_name", default="output.pdf")

    return parser.parse_args()


def main():
    args = parse_args()
    run_scraper(args.target_url, args.output_dir, args.pdf_name)


if __name__ == "__main__":
    main()
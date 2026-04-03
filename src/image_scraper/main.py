import argparse
from pathlib import Path

from image_scraper.services.scrape import scrape_chapter_images


def run_scraper(target_url: str, output_dir: str) -> int:
    return scrape_chapter_images(target_url=target_url, image_dir=Path(output_dir))


def parse_args():
    parser = argparse.ArgumentParser(description="Image scraper with Playwright")

    parser.add_argument("--target_url", required=True)
    parser.add_argument("--output_dir", default="output/images")

    return parser.parse_args()


def main():
    args = parse_args()
    run_scraper(args.target_url, args.output_dir)


if __name__ == "__main__":
    main()

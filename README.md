# Image Scraper

Playwright-based image scraper that intercepts network requests, saves lazy-loaded images, and compiles them into a PDF.

## Setup

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

## Usage

python -m image_scraper.main

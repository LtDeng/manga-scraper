from playwright.sync_api import sync_playwright, Browser, Page
from image_scraper.config import ScraperConfig


class BrowserSession:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self._playwright = None
        self.browser: Browser | None = None
        self.page: Page | None = None

    def __enter__(self) -> Page:
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page(
            viewport={"width": self.config.viewport[0],
                      "height": self.config.viewport[1]}
        )
        return self.page

    def __exit__(self, exc_type, exc, tb):
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()

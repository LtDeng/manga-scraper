import time
from image_scraper.config import ScraperConfig
from image_scraper.core.browser import BrowserSession
from image_scraper.core.interceptor import ImageInterceptor
from image_scraper.services.storage import ImageStore
from image_scraper.services.pdf import PdfCompiler


class ScraperBot:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.store = ImageStore(config.output_dir / self.config.target_url.rpartition('/')[-1].replace("-", "_"))
        self.interceptor = ImageInterceptor(config, config.output_dir)
        self.pdf = PdfCompiler()

    def run(self) -> None:
        with BrowserSession(self.config) as page:
            page.on("response", self.interceptor.handle_response)
            page.goto(self.config.target_url, wait_until="networkidle")
            self._scroll(page)

        images = self.store.list_images()
        pdf_name = self.config.target_url.rpartition('/')[-1].replace("-", "_")+".pdf"
        self.pdf.compile(images, self.config.output_dir.parent / pdf_name)

    def _scroll(self, page) -> None:
        for _ in range(self.config.scroll_iterations):
            page.mouse.wheel(0, self.config.scroll_step)
            time.sleep(self.config.scroll_delay)

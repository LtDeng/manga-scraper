import time

from image_scraper.config import ScraperConfig
from image_scraper.core.browser import BrowserSession
from image_scraper.core.interceptor import ImageInterceptor
from image_scraper.services.storage import ImageStore
from urllib.parse import urlsplit

class ScraperBot:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.store = ImageStore(config.output_dir)
        self.interceptor = ImageInterceptor(config, config.output_dir)

    def run(self) -> int:
        allowed_urls = set()

        with BrowserSession(self.config) as page:
            handler = self._filtered_handler(allowed_urls)
            page.on("response", handler)

            page.goto(self.config.target_url, wait_until="domcontentloaded")

            allowed_urls.update(self._get_allowed_images(page))

            self._scroll(page)

            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)

            page.remove_listener("response", handler)

        images = self.store.list_images()
        return len(images)

    def _scroll(self, page) -> None:
        scroll_step = 1200
        scroll_delay = 0.2
        stable_rounds = 0
        last_y = -1
    
        while True:
            page.mouse.wheel(0, scroll_step)
            time.sleep(scroll_delay)
    
            y = page.evaluate("() => window.scrollY")
            inner_height = page.evaluate("() => window.innerHeight")
            scroll_height = page.evaluate("() => document.documentElement.scrollHeight")
    
            if y == last_y:
                stable_rounds += 1
            else:
                stable_rounds = 0
    
            last_y = y
    
            if y + inner_height >= scroll_height - 50:
                break
    
            if stable_rounds >= 5:
                break

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

    def _get_allowed_images(self, page) -> set[str]:
        return set(page.eval_on_selector_all(
            "chapter-page img.js-page",
            "imgs => imgs.map(img => img.dataset.src || img.src).filter(src => src && src.startsWith('https://cdn.readdetectiveconan.com'))"
        ))
    
    def _filtered_handler(self, allowed_urls):
        def handler(response):
            url = response.url
    
            # Early exit (fast path)
            if url not in allowed_urls:
                return
    
            # Pass through to your existing logic
            self.interceptor.handle_response(response)
    
        return handler

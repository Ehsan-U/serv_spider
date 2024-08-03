from typing import Any, Iterable
import scrapy
from scrapy.crawler import Crawler
from scrapy.http import Request, Response
from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
import html_text
from playwright.async_api import Page



class Web(Spider):
    name = "web"
    allowed_domains = []
    playwright_args = {
        "playwright": True,
        "playwright_include_page": True,
        "playwright_page_goto_kwargs": {"wait_until": "load"}
    }


    def __init__(self, url: str, *a, **kw):
        super().__init__(*a, **kw)
        self.job_id = kw.get("_job")
        self.url = url
        self.allowed_domains.append(urlparse(self.url).netloc)
        self.request_meta = self.playwright_args if self.render else {}


    def start_requests(self) -> Iterable[Request]:
        yield scrapy.Request(self.url, meta=self.request_meta, callback=self.parse, errback=self.close_context_on_error)


    async def parse(self, response: Response, **kwargs: Any) -> Any:
        page: Page = response.meta.get("playwright_page")
        if page and not page.is_closed():
            await page.close()
        item = {
            "source": response.url,
            "content": html_text.extract_text(response.text)
        }
        self.logger.info({"source": response.url})
        yield item

        linkextractor = LinkExtractor(canonicalize=True, allow_domains=self.allowed_domains)
        for req in response.follow_all(linkextractor.extract_links(response), meta=self.request_meta, callback=self.parse, errback=self.close_context_on_error):
            yield req
    

    async def close_context_on_error(self, failure):
        page: Page = failure.request.meta.get("playwright_page")
        if page and not page.is_closed():
            await page.close()


    @classmethod
    def from_crawler(cls, crawler: Crawler, *args: Any, **kwargs: Any):
        render = kwargs.get("render")
        if render:
            crawler.settings.setdict(dict(
                DOWNLOAD_HANDLERS = {
                    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                }
            ), priority='cmdline')
        spider = super().from_crawler(crawler, *args, **kwargs)
        return spider
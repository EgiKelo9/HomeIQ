import logging
import time
from scrapy import signals
from scrapy.http import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """
    Middleware sederhana untuk mencatat durasi setiap request
    dan menampilkan peringatan jika response lambat atau error.
    """

    @classmethod
    def from_crawler(cls, crawler):
        mw = cls()
        crawler.signals.connect(mw.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(mw.spider_closed, signal=signals.spider_closed)
        return mw

    def spider_opened(self, spider):
        self._start_time = time.time()
        logger.info("═══ Spider dimulai: [%s] ═══", spider.name)

    def spider_closed(self, spider):
        elapsed = time.time() - self._start_time
        logger.info(
            "═══ Spider selesai: [%s] | durasi: %.1f detik ═══",
            spider.name, elapsed,
        )

    def process_request(self, request, spider):
        request.meta["_req_start"] = time.time()
        return None  # Lanjutkan ke handler berikutnya

    def process_response(self, request, response: Response, spider):
        elapsed = time.time() - request.meta.get("_req_start", time.time())
        status = response.status

        if status != 200:
            logger.warning(
                "[%s] HTTP %d | %.2fs | %s",
                spider.name, status, elapsed, response.url,
            )
        elif elapsed > 10:
            logger.warning(
                "[%s] LAMBAT %.2fs | %s",
                spider.name, elapsed, response.url,
            )
        else:
            logger.debug(
                "[%s] OK %.2fs | %s",
                spider.name, elapsed, response.url,
            )

        return response

    def process_exception(self, request, exception, spider):
        logger.error(
            "[%s] Exception pada %s: %s",
            spider.name, request.url, exception,
        )
        return None  # Biarkan Scrapy menangani retry
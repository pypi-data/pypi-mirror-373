import asyncio
import logging

from time import time

from .. import bhf_signals
from contextlib import suppress
from inspect import isawaitable
from ipaddress import ip_address
from bhfutils.crawler.playwright.cursor.do_async import GhostCursor, create_cursor
from typing import Union, Awaitable, Literal, Callable, Generator, Optional, Tuple, Type, TypeVar

from playwright.async_api import (
    Page,
    PlaywrightContextManager,
    Request as PlaywrightRequest,
    Response as PlaywrightResponse,
    TimeoutError as PlaywrightTimeoutError,
    Route
)
from scrapy import Spider, signals
from scrapy.crawler import Crawler
from scrapy.http import Request, Response
from scrapy.http.headers import Headers
from scrapy.utils.misc import load_object
from scrapy.utils.python import to_unicode
from scrapy.responsetypes import responsetypes
from scrapy.utils.defer import deferred_from_coro
from scrapy.utils.reactor import verify_installed_reactor
from twisted.internet.defer import Deferred, inlineCallbacks
from bhfutils.crawler.playwright.stealth import stealth_async
from scrapy.core.downloader.handlers.http import HTTPDownloadHandler
from w3lib.encoding import html_body_declared_encoding, http_content_type_encoding

from .headers import use_scrapy_headers
from .page import CursorMethod, PageMethod

__all__ = ["ScrapyPlaywrightDownloadHandler"]

PlaywrightHandler = TypeVar("PlaywrightHandler", bound="ScrapyPlaywrightDownloadHandler")

logger = logging.getLogger("scrapy-playwright")


def _make_request_logger(context_name: str) -> Callable:
    def _log_request(request: PlaywrightRequest) -> None:
        logger.debug(
            f"[Context={context_name}] Request: <{request.method.upper()} {request.url}> "
            f"(resource type: {request.resource_type}, referrer: {request.headers.get('referer')})"
        )

    return _log_request


def _make_response_logger(context_name: str) -> Callable:
    def _log_request(response: PlaywrightResponse) -> None:
        logger.debug(
            f"[Context={context_name}] Response: <{response.status} {response.url}> "
            f"(referrer: {response.headers.get('referer')})"
        )

    return _log_request


def _get_cursor_method_result(cursor: GhostCursor, cm: CursorMethod):
    try:
        method = getattr(cursor, cm.method)
    except AttributeError:
        logger.warning(f"Ignoring {repr(cm)}: could not find method")
        return None
    else:
        return method(*cm.args, **cm.kwargs)


def _get_page_method_result(page: Page, pm: PageMethod):
    try:
        method = getattr(page, pm.method)
    except AttributeError:
        logger.warning(f"Ignoring {repr(pm)}: could not find method")
        return None
    else:
        return method(*pm.args, **pm.kwargs)


class ScrapyPlaywrightDownloadHandler(HTTPDownloadHandler):
    def __init__(self, crawler: Crawler) -> None:
        settings = crawler.settings
        super().__init__(settings=crawler.settings, crawler=crawler)
        verify_installed_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
        crawler.signals.connect(self._engine_started, signals.engine_started)
        self.stats = crawler.stats

        # browser
        self.browser_type: str = settings.get("PLAYWRIGHT_BROWSER_TYPE") or "chromium"
        self.launch_options: dict = settings.getdict("PLAYWRIGHT_LAUNCH_OPTIONS") or {}

        # contexts
        self.static_context_kwargs: dict = settings.getdict("PLAYWRIGHT_STATIC_CONTEXT")
        self.dynamic_contexts_kwargs: [dict] = settings.getlist("PLAYWRIGHT_DYNAMIC_CONTEXTS") or []
        self.context_semaphore: asyncio.Semaphore = asyncio.Semaphore(value=1)

        self.default_navigation_timeout: Optional[float] = None
        if "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT" in settings:
            with suppress(TypeError, ValueError):
                self.default_navigation_timeout = float(
                    settings.get("PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT")
                )

        # headers
        if "PLAYWRIGHT_PROCESS_REQUEST_HEADERS" in settings:
            if settings["PLAYWRIGHT_PROCESS_REQUEST_HEADERS"] is None:
                self.process_request_headers = None
            else:
                self.process_request_headers = load_object(
                    settings["PLAYWRIGHT_PROCESS_REQUEST_HEADERS"]
                )
        else:
            self.process_request_headers = use_scrapy_headers

        self.abort_request: Optional[Callable[[PlaywrightRequest], Union[Awaitable, bool]]] = None
        if settings.get("PLAYWRIGHT_ABORT_REQUEST"):
            self.abort_request = load_object(settings["PLAYWRIGHT_ABORT_REQUEST"])

        self.context_rotation_idx = 0
        self.max_timeouts_before_rotation: int = settings.getint("PLAYWRIGHT_TIMEOUTS_FOR_ROTATION") or 2
        self.timeout_errors_in_row = 0
        self.page_load_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = settings.get(
            "PLAYWRIGHT_PAGE_LOAD_UNTIL") or "load"
        crawler.signals.connect(self._ip_changed, bhf_signals.ip_changed)

    @classmethod
    def from_crawler(cls: Type[PlaywrightHandler], crawler: Crawler) -> PlaywrightHandler:
        return cls(crawler)

    def _engine_started(self) -> Deferred:
        """Launch the browser. Use the engine_started signal as it supports returning deferreds."""
        return deferred_from_coro(self._launch_browser())

    def _ip_changed(self) -> Deferred:
        """Plan User-Agent rotation"""
        return deferred_from_coro(self._plan_context_rotation())

    async def _launch_browser(self) -> None:
        self.playwright_context_manager = PlaywrightContextManager()
        self.playwright = await self.playwright_context_manager.start()
        logger.info("Launching browser")
        browser_launcher = getattr(self.playwright, self.browser_type).launch
        self.browser = await browser_launcher(**self.launch_options)
        logger.info(f"Browser {self.browser_type} launched")

    async def _plan_context_rotation(self) -> None:
        logger.info("Re create browser: Before acquire")
        await self.context_semaphore.acquire()
        logger.info("Re create browser: After acquire")

        await self._close()
        await self._launch_browser()
        self.context_rotation_idx = self.context_rotation_idx + 1
        if self.context_rotation_idx >= len(self.dynamic_contexts_kwargs):
            self.context_rotation_idx = 0

        if self.context_semaphore.locked():
            self.context_semaphore.release()
        logger.warning(f"Re create browser: Completed with new context index {self.context_rotation_idx}")

    async def _create_page(self) -> Page:
        """Create a new page in a context, also creating a new context if necessary."""
        page_context_kwargs = self.static_context_kwargs
        additional_page_context_kwargs = self.dynamic_contexts_kwargs[self.context_rotation_idx]
        for key in additional_page_context_kwargs:
            page_context_kwargs[key] = additional_page_context_kwargs[key]
        page = await self.browser.new_page(**page_context_kwargs)
        await stealth_async(page)
        self.stats.inc_value("playwright/page_count")
        logger.debug(
            "[Context=%s] New page created, page count is %i (%i for all contexts)",
            "default",
            1,
            self._get_total_page_count(),
        )
        if self.default_navigation_timeout is not None:
            page.set_default_timeout(self.default_navigation_timeout)
            page.set_default_navigation_timeout(self.default_navigation_timeout)

        page.on("request", _make_request_logger("default"))
        page.on("response", _make_response_logger("default"))
        page.on("request", self._increment_request_stats)
        page.on("response", self._increment_response_stats)

        return page

    def _get_total_page_count(self):
        count = 1
        current_max_count = self.stats.get_value("playwright/page_count/max_concurrent")
        if current_max_count is None or count > current_max_count:
            self.stats.set_value("playwright/page_count/max_concurrent", count)
        return count

    @inlineCallbacks
    def close(self) -> Deferred:
        yield super().close()
        yield deferred_from_coro(self._close())
        self.context_semaphore = None

    async def _close(self) -> None:
        if getattr(self, "browser", None):
            logger.info("Closing browser")
            await self.browser.close()
        await self.playwright_context_manager.__aexit__()

    def download_request(self, request: Request, spider: Spider) -> Deferred:
        if request.meta.get("playwright"):
            return deferred_from_coro(self._download_request(request, spider))
        return super().download_request(request, spider)

    async def _download_request(self, request: Request, spider: Spider) -> Response:
        page = None
        try:
            logger.info(f"[{request.url}] Before acquire")
            await self.context_semaphore.acquire()
            logger.info(f"[{request.url}] After acquire")
            page = await self._create_page()

            # attach event handlers
            event_handlers = request.meta.get("playwright_page_event_handlers") or {}
            for event, handler in event_handlers.items():
                if callable(handler):
                    page.on(event, handler)
                elif isinstance(handler, str):
                    try:
                        page.on(event, getattr(spider, handler))
                    except AttributeError:
                        logger.warning(
                            f"Spider '{spider.name}' does not have a '{handler}' attribute,"
                            f" ignoring handler for event '{event}'"
                        )
            # overwrite request handler
            await page.unroute("**")
            await page.route(
                "**",
                self._make_request_handler(
                    method=request.method,
                    scrapy_headers=request.headers,
                    body=request.body,
                    encoding=getattr(request, "encoding", None),
                ),
            )

            result = await self._download_request_with_page(request, page)
        except PlaywrightTimeoutError:
            self.timeout_errors_in_row = self.timeout_errors_in_row + 1
            logger.error(f"[{request.url}] Request timeout while downloading request")
            return Response('', status=504)
        except:
            logger.exception(f"[{request.url}] Error while downloading request")
            return Response('', status=504)
        else:
            if result.status == 429:
                self.timeout_errors_in_row = self.max_timeouts_before_rotation + 1
                return Response('', status=504)
            else:
                self.timeout_errors_in_row = 0
                return result
        finally:
            try:
                if page is not None and not page.is_closed():
                    try:
                        await asyncio.wait_for(page.close(), timeout=10)
                    except asyncio.TimeoutError:
                        if self.context_semaphore.locked():
                            self.context_semaphore.release()
                        await self._plan_context_rotation()
                    else:
                        if self.context_semaphore.locked():
                            self.context_semaphore.release()
                else:
                    if self.context_semaphore.locked():
                        self.context_semaphore.release()
                if self.timeout_errors_in_row > self.max_timeouts_before_rotation:
                    self.timeout_errors_in_row = 0
                    await self._plan_context_rotation()
            except:
                logger.exception(f"[{request.url}] Error on page close")
                raise

    async def _download_request_with_page(self, request: Request, page: Page) -> Response:
        start_time = time()
        response: PlaywrightResponse = await page.goto(request.url, wait_until=self.page_load_until)

        logger.info(f"[{request.url}] After goto")
        await self._apply_page_methods(page, request)

        logger.info(f"[{request.url}] After apply page methods")
        body_str = await page.content()
        request.meta["download_latency"] = time() - start_time

        server_ip_address = None
        with suppress(AttributeError, KeyError, ValueError):
            server_addr = await response.server_addr()
            if server_addr is not None:
                server_ip_address = ip_address(server_addr["ipAddress"])

        with suppress(AttributeError):
            request.meta["playwright_security_details"] = await response.security_details()

        headers = Headers(response.headers)
        headers.pop("Content-Encoding", None)
        body, encoding = _encode_body(headers=headers, text=body_str)
        respcls = responsetypes.from_args(headers=headers, url=page.url, body=body)
        return respcls(
            url=page.url,
            status=response.status,
            headers=headers,
            body=body,
            request=request,
            flags=["playwright"],
            encoding=encoding,
            ip_address=server_ip_address,
        )

    async def _apply_page_methods(self, page: Page, request: Request) -> None:
        page_methods = request.meta.get("playwright_page_methods") or ()

        if isinstance(page_methods, dict):
            page_methods = page_methods.values()
        for pm in page_methods:
            if isinstance(pm, dict):
                pm_group = pm.popitem()
                pm_group_name = pm_group[0]
                pm_group_items = pm_group[1]
                if pm_group_name == 'wait_for_any':
                    timeouts = 0
                    group_length = len(pm_group_items)
                    for pgi in pm_group_items:
                        result = _get_page_method_result(page, pgi)
                        if result is not None:
                            try:
                                pgi.result = await result if isawaitable(result) else result
                                await page.wait_for_load_state(timeout=self.default_navigation_timeout)
                                return
                            except Exception:
                                timeouts += 1
                                if timeouts == group_length:
                                    raise
                                else:
                                    logger.warning(f"Ignoring TimeoutError {timeouts} time")
            elif isinstance(pm, PageMethod):
                result = _get_page_method_result(page, pm)
                if result is not None:
                    pm.result = await result if isawaitable(result) else result
                    await page.wait_for_load_state(timeout=self.default_navigation_timeout)
            elif isinstance(pm, CursorMethod):
                cursor = create_cursor(page)
                result = _get_cursor_method_result(cursor, pm)
                if result is not None:
                    pm.result = await result if isawaitable(result) else result
            else:
                logger.warning(f"Ignoring {repr(pm)}: expected PageMethod or CursorMethod, got {repr(type(pm))}")

    def _increment_request_stats(self, request: PlaywrightRequest) -> None:
        stats_prefix = "playwright/request_count"
        self.stats.inc_value(stats_prefix)
        self.stats.inc_value(f"{stats_prefix}/resource_type/{request.resource_type}")
        self.stats.inc_value(f"{stats_prefix}/method/{request.method}")
        if request.is_navigation_request():
            self.stats.inc_value(f"{stats_prefix}/navigation")

    def _increment_response_stats(self, response: PlaywrightResponse) -> None:
        stats_prefix = "playwright/response_count"
        self.stats.inc_value(stats_prefix)
        self.stats.inc_value(f"{stats_prefix}/resource_type/{response.request.resource_type}")
        self.stats.inc_value(f"{stats_prefix}/method/{response.request.method}")

    def _make_request_handler(
            self, method: str, scrapy_headers: Headers, body: Optional[bytes], encoding: str = "utf8"
    ) -> Callable:
        async def _request_handler(route: Route, playwright_request: PlaywrightRequest) -> None:
            """Override request headers, method and body."""
            if self.abort_request and self.abort_request(playwright_request):
                await route.abort()
                self.stats.inc_value("playwright/request_count/aborted")
                return None

            processed_headers = await self.process_request_headers(
                self.browser_type, playwright_request, scrapy_headers
            )

            # the request that reaches the callback should contain the headers that were sent
            scrapy_headers.clear()
            scrapy_headers.update(processed_headers)

            overrides: dict = {"headers": processed_headers}
            if playwright_request.is_navigation_request():
                overrides["method"] = method
                if body is not None:
                    overrides["post_data"] = body.decode(encoding)

            await route.continue_(**overrides)

        return _request_handler


def _possible_encodings(headers: Headers, text: str) -> Generator[str, None, None]:
    if headers.get("content-type"):
        content_type = to_unicode(headers["content-type"])
        yield http_content_type_encoding(content_type)
    yield html_body_declared_encoding(text)


def _encode_body(headers: Headers, text: str) -> Tuple[bytes, str]:
    for encoding in filter(None, _possible_encodings(headers, text)):
        try:
            body = text.encode(encoding)
        except UnicodeEncodeError:
            pass
        else:
            return body, encoding
    return text.encode("utf-8"), "utf-8"  # fallback

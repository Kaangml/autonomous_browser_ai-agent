"""High-level actions exposed to the agent layer."""

from __future__ import annotations

from typing import Optional

from playwright.async_api import Page

from browser.browser import BrowserManager
from browser.utils import BrowserUtils


class BrowserActions:
    """Collection of reusable async browser actions."""

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager

    async def go_to_url(self, url: str) -> Page:
        """Open a fresh page at the provided URL."""

        normalized_url = BrowserUtils.normalize_url(url)
        page = await self.browser_manager.new_page()
        timeout_ms = self._timeout_ms

        async def _navigate() -> None:
            await page.goto(normalized_url, wait_until="load", timeout=timeout_ms)

        await BrowserUtils.retry(_navigate)
        return page

    async def click(self, page: Page, selector: str) -> None:
        """Click an element after ensuring it exists."""

        await BrowserUtils.ensure_selector_exists(page, selector, self._timeout_ms)
        await BrowserUtils.retry(lambda: page.click(selector, timeout=self._timeout_ms))

    async def fill(self, page: Page, selector: str, text: str) -> None:
        """Fill the input field with provided text."""

        await BrowserUtils.ensure_selector_exists(page, selector, self._timeout_ms)
        await BrowserUtils.retry(lambda: page.fill(selector, text, timeout=self._timeout_ms))

    async def extract_text(self, page: Page, selector: str) -> str:
        """Return trimmed text content from the element."""

        await BrowserUtils.ensure_selector_exists(page, selector, self._timeout_ms)
        text = await BrowserUtils.retry(lambda: page.inner_text(selector, timeout=self._timeout_ms))
        return text.strip()

    async def scroll(self, page: Page, selector: Optional[str] = None) -> None:
        """Scroll either the whole page or a targeted element into view."""

        if selector:
            await BrowserUtils.ensure_selector_exists(page, selector, self._timeout_ms)
            await BrowserUtils.retry(
                lambda: page.eval_on_selector(
                    selector,
                    "el => el.scrollIntoView({behavior: 'smooth', block: 'center'})",
                )
            )
            return

        await BrowserUtils.retry(
            lambda: page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        )

    async def wait_for(self, page: Page, selector: str, timeout: Optional[int] = None) -> None:
        """Wait for element to appear with optional custom timeout in seconds."""

        timeout_ms = int((timeout or self.config_timeout) * 1000)
        await BrowserUtils.ensure_selector_exists(page, selector, timeout_ms)

    @property
    def config_timeout(self) -> int:
        """Return configured timeout in seconds."""

        return self.browser_manager.config_manager.config.timeout

    @property
    def _timeout_ms(self) -> int:
        return self.config_timeout * 1000

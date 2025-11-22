"""Playwright-based browser manager abstraction."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from playwright.async_api import (
    Browser as PlaywrightBrowser,
    BrowserContext,
    Page,
    async_playwright,
)

from browser.browser_config import BrowserConfigManager


class BrowserManager:
    """Controls the Playwright browser lifecycle with safe defaults."""

    def __init__(
        self,
        config_manager: BrowserConfigManager,
        browser_type: str = "chromium",
        playwright_factory: Callable[[], Any] = async_playwright,
    ) -> None:
        self.config_manager = config_manager
        self.browser_type = browser_type
        self._playwright_factory = playwright_factory

        self._playwright_context_manager = None
        self._playwright = None
        self._browser: Optional[PlaywrightBrowser] = None
        self._context: Optional[BrowserContext] = None

    async def start(self) -> PlaywrightBrowser:
        """Launch the configured browser if not already running."""

        if self._browser:
            return self._browser

        options = self.config_manager.to_playwright_options()
        self._playwright_context_manager = self._playwright_factory()
        self._playwright = await self._playwright_context_manager.start()
        engine = getattr(self._playwright, self.browser_type)
        self._browser = await engine.launch(**options["launch"])
        self._context = await self._browser.new_context(**options["context"])
        self._apply_config(options)
        return self._browser

    async def new_page(self) -> Page:
        """Create a new page within the active context."""

        if not self._browser:
            await self.start()
        if not self._context:
            raise RuntimeError("Browser context is not initialized")
        return await self._context.new_page()

    async def close(self) -> None:
        """Gracefully close page, context and browser resources."""

        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        self._playwright_context_manager = None

    async def restart(self) -> PlaywrightBrowser:
        """Restart browser by closing and launching a new instance."""

        await self.close()
        return await self.start()

    def _apply_config(self, options: Dict[str, Any]) -> None:
        """Apply timeouts and other context-level settings."""

        if self._context:
            timeout_ms = options.get("timeout", self.config_manager.config.timeout * 1000)
            self._context.set_default_timeout(timeout_ms)

    @property
    def is_running(self) -> bool:
        """Return True when browser/context are active."""

        return self._browser is not None and self._context is not None

import pytest

from browser.browser import BrowserManager
from browser.browser_config import BrowserConfig, BrowserConfigManager


class FakePage:
    async def close(self):
        pass


class FakeContext:
    def __init__(self):
        self.pages = []
        self.timeout = None
        self.closed = False

    def set_default_timeout(self, timeout):
        self.timeout = timeout

    async def new_page(self):
        page = FakePage()
        self.pages.append(page)
        return page

    async def close(self):
        self.closed = True


class FakeBrowser:
    def __init__(self):
        self.contexts = []
        self.closed = False

    async def new_context(self, **_):
        context = FakeContext()
        self.contexts.append(context)
        return context

    async def close(self):
        self.closed = True


class FakeEngine:
    def __init__(self):
        self.launch_kwargs = None
        self.browser = FakeBrowser()

    async def launch(self, **kwargs):
        self.launch_kwargs = kwargs
        return self.browser


class FakePlaywright:
    def __init__(self):
        self.chromium = FakeEngine()
        self.stopped = False

    async def stop(self):
        self.stopped = True


class FakeAsyncPlaywright:
    def __init__(self, playwright):
        self.playwright = playwright

    async def start(self):
        return self.playwright


@pytest.mark.asyncio
async def test_browser_manager_start_creates_context_and_page():
    config = BrowserConfig(True, {"width": 1200, "height": 800}, 15, "UA", False)
    manager = BrowserConfigManager(config)
    fake_playwright = FakePlaywright()
    browser_manager = BrowserManager(
        config_manager=manager,
        playwright_factory=lambda: FakeAsyncPlaywright(fake_playwright),
    )

    browser = await browser_manager.start()

    assert browser is fake_playwright.chromium.browser
    assert fake_playwright.chromium.launch_kwargs["headless"] is True
    assert browser_manager.is_running

    page = await browser_manager.new_page()
    assert isinstance(page, FakePage)


@pytest.mark.asyncio
async def test_browser_manager_close_terminates_resources():
    config = BrowserConfig(True, {"width": 1200, "height": 800}, 15, "UA", False)
    manager = BrowserConfigManager(config)
    fake_playwright = FakePlaywright()
    browser_manager = BrowserManager(
        config_manager=manager,
        playwright_factory=lambda: FakeAsyncPlaywright(fake_playwright),
    )

    await browser_manager.start()
    await browser_manager.close()

    assert fake_playwright.chromium.browser.closed is True
    assert fake_playwright.chromium.browser.contexts[0].closed is True
    assert fake_playwright.stopped is True
    assert browser_manager.is_running is False

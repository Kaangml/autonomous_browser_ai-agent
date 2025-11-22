import pytest

from browser.actions import BrowserActions
from browser.browser_config import BrowserConfig, BrowserConfigManager


class DummyPage:
    def __init__(self):
        self.goto_url = None
        self.goto_kwargs = None
        self.clicked = []
        self.filled = []
        self.inner_text_values = {"#title": "  Hello World  "}
        self.waited = []
        self.scrolled_selector = None
        self.scrolled_page = False

    async def goto(self, url, **kwargs):
        self.goto_url = url
        self.goto_kwargs = kwargs

    async def click(self, selector, **kwargs):
        self.clicked.append((selector, kwargs))

    async def fill(self, selector, text, **kwargs):
        self.filled.append((selector, text, kwargs))

    async def inner_text(self, selector, **kwargs):
        return self.inner_text_values[selector]

    async def eval_on_selector(self, selector, callback):
        self.scrolled_selector = selector

    async def evaluate(self, script):
        self.scrolled_page = script == "window.scrollTo(0, document.body.scrollHeight)"

    async def wait_for_selector(self, selector, **kwargs):
        self.waited.append((selector, kwargs))
        return True


class DummyBrowserManager:
    def __init__(self):
        config = BrowserConfig(True, {"width": 1200, "height": 800}, 5, "UA", False)
        self.config_manager = BrowserConfigManager(config)
        self._page = DummyPage()

    async def new_page(self):
        return self._page


@pytest.mark.asyncio
async def test_go_to_url_opens_normalized_page():
    manager = DummyBrowserManager()
    actions = BrowserActions(manager)

    page = await actions.go_to_url("example.com")

    assert page.goto_url.startswith("https://")
    assert page.goto_kwargs["wait_until"] == "load"


@pytest.mark.asyncio
async def test_click_and_fill_require_selector():
    manager = DummyBrowserManager()
    actions = BrowserActions(manager)
    page = await manager.new_page()

    await actions.click(page, "#btn")
    await actions.fill(page, "#input", "value")

    assert page.waited[0][0] == "#btn"
    assert page.clicked[0][0] == "#btn"
    assert page.filled[0][0] == "#input"


@pytest.mark.asyncio
async def test_extract_text_trims_whitespace():
    manager = DummyBrowserManager()
    actions = BrowserActions(manager)
    page = await manager.new_page()

    text = await actions.extract_text(page, "#title")

    assert text == "Hello World"


@pytest.mark.asyncio
async def test_scroll_handles_selector_and_page():
    manager = DummyBrowserManager()
    actions = BrowserActions(manager)
    page = await manager.new_page()

    await actions.scroll(page, "#section")
    assert page.scrolled_selector == "#section"

    await actions.scroll(page)
    assert page.scrolled_page is True


@pytest.mark.asyncio
async def test_wait_for_uses_config_timeout():
    manager = DummyBrowserManager()
    actions = BrowserActions(manager)
    page = await manager.new_page()

    await actions.wait_for(page, "#item", timeout=2)

    selector, kwargs = page.waited[-1]
    assert selector == "#item"
    assert kwargs["timeout"] == 2000
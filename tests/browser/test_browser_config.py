from browser.browser_config import BrowserConfigManager
from config.settings import Settings


def test_load_from_settings_uses_global_defaults():
    manager = BrowserConfigManager.load_from_settings(Settings())

    assert manager.config.headless == Settings.BROWSER_HEADLESS
    assert manager.config.viewport == Settings.BROWSER_VIEWPORT
    assert manager.config.timeout == Settings.BROWSER_TIMEOUT
    assert manager.config.user_agent == Settings.BROWSER_USER_AGENT


def test_validate_rejects_invalid_timeout():
    data = {
        "headless": True,
        "viewport": {"width": 1280, "height": 720},
        "timeout": 0,
        "user_agent": "agent",
        "stealth": False,
    }

    try:
        BrowserConfigManager.validate(data)
    except ValueError as exc:
        assert "timeout" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("ValueError expected for non-positive timeout")


def test_to_playwright_options_contains_launch_and_context():
    manager = BrowserConfigManager.load_from_settings(Settings())
    options = manager.to_playwright_options()

    assert "launch" in options
    assert "context" in options
    assert options["context"]["viewport"] == Settings.BROWSER_VIEWPORT
    assert options["timeout"] == Settings.BROWSER_TIMEOUT * 1000

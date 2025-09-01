import logging
from abc import abstractmethod

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from zapp.driver.selenium.browser.base import BROWSER_AWARE_MESSAGE, Browser
from zapp.driver import REMOTE_EXECUTOR

log = logging.getLogger(__name__)


class InternetExplorerBrowser(Browser):
    is_bidi_supported: bool = False

    def _options(self):
        log.warning(BROWSER_AWARE_MESSAGE.format("Internet Explorer"))
        options = webdriver.IeOptions()
        options.ignore_protected_mode_settings = True
        options.ignore_zoom_level = True
        options.require_window_focus = False
        options.ensure_clean_session = True
        options.native_events = True
        options.persistent_hover = False
        options.capabilities.update({"requireWindowFocus": False})
        return options

    @abstractmethod
    def _init_driver(self, options) -> WebDriver:
        pass


class LocalInternetExplorerBrowser(InternetExplorerBrowser):
    def __repr__(self):
        return "IE-local"

    def _init_driver(self, options) -> WebDriver:
        return webdriver.Ie(options=options)


class RemoteInternetExplorerBrowser(InternetExplorerBrowser):
    is_remote = True

    def __repr__(self):
        return "IE-remote"

    def _init_driver(self, options) -> WebDriver:
        return webdriver.Remote(command_executor=REMOTE_EXECUTOR, options=options)

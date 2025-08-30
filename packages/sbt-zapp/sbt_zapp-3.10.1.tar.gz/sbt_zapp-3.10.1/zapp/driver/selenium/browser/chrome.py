from typing import Type

from selenium.webdriver import ChromeOptions, Chrome, Remote
from selenium.webdriver.remote.webdriver import WebDriver

from zapp.driver.selenium.browser.chromium import ChromiumBrowser
from zapp.driver import (
    REMOTE_EXECUTOR,
)


class LocalChromeBrowser(ChromiumBrowser):
    def __repr__(self):
        return "Chrome-local"

    def _options_cls(self) -> Type[ChromeOptions]:
        return ChromeOptions

    def _local_driver_cls(self) -> Type[Chrome]:
        return Chrome

    def _init_driver(self, options) -> WebDriver:
        return self._local_driver_cls()(options=options)


class RemoteChromeBrowser(ChromiumBrowser):
    is_remote = True

    def __repr__(self):
        return "Chrome-remote"

    def _options_cls(self) -> Type[ChromeOptions]:
        return ChromeOptions

    def _init_driver(self, options) -> WebDriver:
        return Remote(command_executor=REMOTE_EXECUTOR, options=options)

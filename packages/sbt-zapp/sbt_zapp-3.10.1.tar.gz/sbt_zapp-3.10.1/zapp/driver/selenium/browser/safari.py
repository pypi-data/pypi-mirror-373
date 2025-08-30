import logging
from abc import abstractmethod

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from zapp.driver.selenium.browser.base import BROWSER_AWARE_MESSAGE, Browser
from zapp.driver import BROWSER_USERAGENT, REMOTE_EXECUTOR

log = logging.getLogger(__name__)


class SafariBrowser(Browser):
    is_bidi_supported: bool = False

    def _options(self):
        log.warning(BROWSER_AWARE_MESSAGE.format("Safari"))
        options = webdriver.SafariOptions()
        options.use_technology_preview = False

        if BROWSER_USERAGENT is not None:
            options.add_argument(f'--user-agent="{BROWSER_USERAGENT}"')

        return options

    @abstractmethod
    def _init_driver(self, options) -> WebDriver:
        pass


class LocalSafariBrowser(SafariBrowser):
    def __repr__(self):
        return "Safari-local"

    def _init_driver(self, options) -> WebDriver:
        return webdriver.Safari(options=options)


class RemoteSafariBrowser(SafariBrowser):
    is_remote = True

    def __repr__(self):
        return "Safari-remote"

    def _init_driver(self, options) -> WebDriver:
        return webdriver.Remote(command_executor=REMOTE_EXECUTOR, options=options)

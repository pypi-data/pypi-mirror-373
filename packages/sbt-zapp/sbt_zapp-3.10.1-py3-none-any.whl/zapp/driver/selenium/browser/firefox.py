from abc import abstractmethod
from typing import Type

from selenium.webdriver import FirefoxOptions, FirefoxProfile, Firefox, Remote
from selenium.webdriver.remote.webdriver import WebDriver

from zapp.driver.selenium.browser.base import Browser
from zapp.driver import (
    BROWSER_HEADLESS,
    BROWSER_USERAGENT,
    REMOTE_EXECUTOR,
)


class FirefoxBrowser(Browser):
    def _options_cls(self) -> Type[FirefoxOptions]:
        return FirefoxOptions

    def _options(self):
        profile = FirefoxProfile()
        # Список всех параметров можно найти по адресу: about:config
        # Часть параметров задокументирована https://kb.mozillazine.org/About:config_entries
        preferences = {
            "browser.download.dir": self._tempdir,
            "browser.download.folderList": 2,
            "browser.download.manager.showWhenStarting": False,
            "browser.helperApps.neverAsk.saveToDisk": "application/pdf,application/x-pdf,application/octet-stream,application/zip,text/html,text/plain",
            "browser.safebrowsing.downloads.enabled": False,
            "browser.tabs.warnOnCloseOtherTabs": False,
            "dom.event.clipboardevents.enabled": True,
            "dom.event.contextmenu.enabled": True,
            "dom.event.clipboardeventlistener.enabled": True,
            "dom.allow_cut_copy": True,
            "dom.disable_beforeunload": True,
            "pdfjs.disabled": True,
            "security.mixed_content.block_active_content": False,  # Pref to block mixed scripts (fonts, plugin content, scripts, stylesheets, iframes, websockets, XHR)
            "security.mixed_content.block_display_content": True,  # Pref for mixed display content blocking (images, audio, video).
        }

        if BROWSER_USERAGENT is not None:
            preferences["general.useragent.override"] = BROWSER_USERAGENT

        for key, value in preferences.items():
            profile.set_preference(key, value)

        options = self._options_cls()()
        options.profile = profile

        if BROWSER_HEADLESS:
            options.add_argument("--headless")

        return options

    @abstractmethod
    def _init_driver(self, options) -> WebDriver:
        pass


class LocalFirefoxBrowser(FirefoxBrowser):
    def __repr__(self):
        return "Firefox-local"

    def _init_driver(self, options) -> WebDriver:
        return Firefox(options=options)


class RemoteFirefoxBrowser(FirefoxBrowser):
    is_remote = True

    def __repr__(self):
        return "Firefox-remote"

    def _init_driver(self, options) -> WebDriver:
        return Remote(command_executor=REMOTE_EXECUTOR, options=options)

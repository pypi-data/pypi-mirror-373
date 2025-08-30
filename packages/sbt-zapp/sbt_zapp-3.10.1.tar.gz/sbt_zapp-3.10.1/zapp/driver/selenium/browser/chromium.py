from abc import abstractmethod
from typing import Type

from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.chromium.webdriver import ChromiumDriver

from zapp.driver.selenium.browser.base import Browser
from zapp.driver import (
    BROWSER_HEADLESS,
    BROWSER_LOGGING,
    BROWSER_USERAGENT,
    CHROMIUM_DEFAULT_ARGS,
)


class ChromiumBrowser(Browser):

    def _options(self) -> ChromiumOptions:
        # @see https://peter.sh/experiments/chromium-command-line-switches/
        arguments = CHROMIUM_DEFAULT_ARGS.copy()

        if BROWSER_USERAGENT is not None:
            arguments.append(f'--user-agent="{BROWSER_USERAGENT}"')

        if BROWSER_HEADLESS:
            arguments.append("--headless=new")

        options = self._options_cls()()

        for arg in set(arguments):
            options.add_argument(arg)

        if BROWSER_LOGGING:
            options.add_argument("--enable-logging")
            options.add_experimental_option(
                "perfLoggingPrefs",
                {
                    "traceCategories": "browser,devtools.timeline,devtools",
                    "enableNetwork": True,
                },
            )
            options.set_capability(
                f"{self.options_prefix}:loggingPrefs",
                dict(browser="ALL", driver="ALL", performance="ALL"),
            )

        # @see https://chromium.googlesource.com/chromium/src/+/refs/heads/main/chrome/common/pref_names.h
        # @see https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/content_settings/core/common/pref_names.h
        # @see https://developer.chrome.com/docs/extensions/reference/api/contentSettings
        # 0 - Default, 1 - Allow, 2 - Block
        options.add_experimental_option(
            "prefs",
            {
                "profile": {
                    "managed_default_content_settings": {
                        "notifications": 2,
                        "popups": 2,
                        "clipboard": 1,
                        "automatic_downloads": 1,
                        "geolocation": 1,
                    }
                },
                "download": {
                    "prompt_for_download": False,
                    "directory_upgrade": True,
                    "default_directory": self._tempdir,
                },
            },
        )

        return options

    @abstractmethod
    def _options_cls(self) -> Type[ChromiumOptions]:
        pass

    @abstractmethod
    def _init_driver(self, options) -> ChromiumDriver:
        pass

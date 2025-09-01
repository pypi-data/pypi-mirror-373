from abc import ABC, abstractmethod
from datetime import datetime
from logging import getLogger
from typing import Type

from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.remote.webdriver import WebDriver

from zapp.driver import (
    BROWSER_ARGUMENTS,
    BROWSER_LOCALE,
    BROWSER_TIMEZONE,
    SELENOID_VIDEO_ENABLED,
    SELENOID_SESSION_TIMEOUT,
    SELENOID_BROWSER_VERSION,
    BROWSER,
)

from zapp.features.core.settings import (
    PROJECT_KEY,
    ENV,
)

log = getLogger(__name__)

BROWSER_AWARE_MESSAGE = "ZAPP поддерживает работу с браузером {} лишь частично, некоторые шаги могут быть не выполнены"


# @see https://github.com/aerokube/selenoid/blob/master/docs/special-capabilities.adoc
BASIC_REMOTE_CAPS = {
    "selenoid:options": dict(
        name=f"PROJECT={PROJECT_KEY}, ENV={ENV}",
        version=SELENOID_BROWSER_VERSION,
        enableVNC=True,
        enableVideo=bool(SELENOID_VIDEO_ENABLED),
        sessionTimeout=SELENOID_SESSION_TIMEOUT,
        timeZone=BROWSER_TIMEZONE,
        env=[f"LANG={BROWSER_LOCALE}.UTF-8", f"LC_ALL={BROWSER_LOCALE}.UTF-8"],
    )
}


class Browser(ABC):
    is_bidi_supported: bool = True
    is_remote: bool = False

    __video_name: str

    def __init__(self, tempdir=""):
        self._tempdir = tempdir
        self._driver = self._init_driver(self.__apply_common_set_up(self._options()))

    def __apply_common_set_up(self, options: ArgOptions) -> ArgOptions:
        options.accept_insecure_certs = True
        options.unhandled_prompt_behavior = "accept"
        options.enable_downloads = True
        options.enable_bidi = self.is_bidi_supported and not self.is_remote
        if not options.enable_bidi:
            options.capabilities.pop("webSocketUrl", None)

        if self.is_remote:
            self.__video_name = f'{PROJECT_KEY}_{ENV}_{BROWSER.upper()}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.mp4'
            remote_caps = BASIC_REMOTE_CAPS.copy()
            selenoid_options = remote_caps["selenoid:options"]
            if selenoid_options.get("enableVideo"):
                selenoid_options["videoName"] = self.video_name
            options.capabilities.update(remote_caps)
        else:
            if BROWSER_TIMEZONE:
                log.warning(
                    "Selenium: настройка таймзоны локально не поддерживается. Будет использовано значение ОС"
                )

        for argument in (arg for arg in BROWSER_ARGUMENTS.split(" ") if arg):
            options.add_argument(argument)

        return options

    @abstractmethod
    def _options(self) -> ArgOptions:
        pass

    @abstractmethod
    def _init_driver(self, options) -> WebDriver:
        pass

    @abstractmethod
    def _options_cls(self) -> Type[ArgOptions]:
        pass

    @property
    def options_prefix(self) -> str:
        cls = self._options_cls()
        field_name = "KEY"
        if hasattr(cls, field_name):
            return getattr(cls, field_name).split(":")[0]
        return ""

    @property
    def driver(self):
        return self._driver

    @property
    def name(self):
        return self.driver.capabilities.get("browserName")

    @property
    def version(self):
        return self.driver.capabilities.get("browserVersion", "неизвестна")

    @property
    def type(self):
        return "remote" if self.is_remote else "local"

    @property
    def video_name(self):
        return self.__video_name

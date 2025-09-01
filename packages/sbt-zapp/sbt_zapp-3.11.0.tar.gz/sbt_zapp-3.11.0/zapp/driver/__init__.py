from enum import Enum
import platform
import re

import validators
import logging
from envparse import env
from datetime import timedelta

log = logging.getLogger(__name__)


DRIVER_IMPL = env.str("DRIVER_IMPL", default="selenium").upper()

BROWSER = env.str("BROWSER", default="chrome")
BROWSER_HEADLESS = env.bool("BROWSER_HEADLESS", default=False)
BROWSER_ARGUMENTS = env.str("BROWSER_ARGUMENTS", default="")
BROWSER_USERAGENT = env.str("BROWSER_USERAGENT", default=None)
BROWSER_LOCALE = env.str("BROWSER_LOCALE", default="ru_RU")
BROWSER_TIMEZONE = env.str("BROWSER_TIMEZONE", default="Europe/Moscow")
BROWSER_ENABLE_DARK_COLOR_SCHEME = env.bool(
    "BROWSER_ENABLE_DARK_COLOR_SCHEME", default=False
)
BROWSER_WIDTH = env.int("BROWSER_WIDTH", default=1920)
BROWSER_HEIGHT = env.int("BROWSER_HEIGHT", default=1080)

BROWSER_GO_TO_HOST_ON_START = env.bool("BROWSER_GO_TO_HOST_ON_START", default=False)
BROWSER_DISABLE_FOR_TAGS = env.str("BROWSER_DISABLE_FOR_TAGS", default="")
BROWSER_LIFECYCLE = env.str("BROWSER_LIFECYCLE", default="ONE_INSTANCE")
if not re.match(r"^(ONE_INSTANCE|EACH_SCENARIO|EACH_FEATURE)$", BROWSER_LIFECYCLE):
    raise Exception(
        "Параметр BROWSER_LIFECYCLE может принимать значения ONE_INSTANCE, EACH_FEATURE или EACH_SCENARIO"
    )

if not re.match(r"^(PLAYWRIGHT|SELENIUM)$", DRIVER_IMPL):
    raise Exception(
        "Параметр DRIVER_IMPL может принимать значения PLAYWRIGHT или SELENIUM"
    )

# Есть долгие действия со стороны API перед обращением к UI, чтобы сессия Selenoid не валилась, пингуем периодически
REMOTE_BROWSER_PING_ENABLED = env.bool("REMOTE_BROWSER_PING_ENABLED", default=False)
REMOTE_BROWSER_PING_TIMEOUT_IN_SEC = timedelta(
    seconds=env.int("REMOTE_BROWSER_PING_TIMEOUT_IN_SEC", default=45)
)

REMOTE_EXECUTOR = env.str("REMOTE_EXECUTOR", default="")
if REMOTE_EXECUTOR and not validators.url(REMOTE_EXECUTOR):
    raise Exception("Параметр REMOTE_EXECUTOR должен содержать валидный URL")

SELENOID_UI_URL = env.str("SELENOID_UI_URL", default="https://zapp-vnc.example.com/")
if not validators.url(SELENOID_UI_URL):
    raise Exception("Параметр SELENOID_UI_URL должен содержать валидный URL")

SELENOID_BROWSER_VERSION = env.str(
    "SELENOID_BROWSER_VERSION", default=env.str("BROWSER_VERSION", default="")
)
SELENOID_VIDEO_ENABLED = env.bool(
    "SELENOID_VIDEO_ENABLED", default=env.bool("VIDEO", default=False)
)
SELENOID_SESSION_TIMEOUT = env.str("SELENOID_SESSION_TIMEOUT", default="1m")

RETRY_DELAY = timedelta(milliseconds=env.int("RETRY_DELAY", default=15_000))
ELEMENT_TIMEOUT = timedelta(
    seconds=env.float(
        "ELEMENT_TIMEOUT", default=env.float("SMARTWAIT_DELAY", default=7)
    )
)

CHROMIUM_DEFAULT_ARGS = [
    "--force-device-scale-factor=1",
    "--disable-gpu",
    "--ignore-certificate-errors",
    "--disable-web-security",
    "--disable-blink-features=AutomationControlled",
    "--disable-popup-blocking",
    "--no-sandbox",
]


class Platform(Enum):
    LINUX = "Linux"
    MAC = "Darwin"
    WIN = "Windows"

    @staticmethod
    def get() -> str:
        return platform.system()

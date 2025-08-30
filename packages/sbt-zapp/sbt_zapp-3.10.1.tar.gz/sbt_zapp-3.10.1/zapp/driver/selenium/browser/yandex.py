import os

from zapp.driver import Platform
from zapp.driver.selenium.browser.chrome import LocalChromeBrowser, RemoteChromeBrowser


class LocalYandexBrowser(LocalChromeBrowser):
    def __repr__(self):
        return "Yandex-local"

    def _options(self):
        options = super()._options()
        if Platform.get() == Platform.MAC.value:
            options.binary_location = "/Applications/Yandex.app/Contents/MacOS/Yandex"

        elif Platform.get() == Platform.WIN.value:
            options.binary_location = os.path.join(
                os.environ["USERPROFILE"],
                "AppData\\Local\\Yandex\\YandexBrowser\\Application\\browser.exe",
            )
        elif Platform.get() == Platform.LINUX.value:
            options.binary_location = "/usr/bin/yandex-browser-beta"
        return options


class RemoteYandexBrowser(RemoteChromeBrowser):

    def __repr__(self):
        return "Yandex-remote"

    def _options(self):
        options = super()._options()
        options.binary_location = "/usr/bin/yandex-browser-beta"
        options.capabilities.update({"browserName": "yandex"})
        return options

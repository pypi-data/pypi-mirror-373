import os

from zapp.driver import Platform
from zapp.driver.selenium.browser.chrome import LocalChromeBrowser, RemoteChromeBrowser


class LocalSberBrowser(LocalChromeBrowser):
    def __repr__(self):
        return "Sber-local"

    def _options(self):
        options = super()._options()
        if Platform.get() == Platform.MAC.value:
            options.binary_location = "/Applications/SberBrowser.app"

        elif Platform.get() == Platform.WIN.value:
            options.binary_location = os.path.join(
                os.environ["USERPROFILE"],
                "AppData\\Local\\Sber\\SberBrowser\\Application\\browser.exe",
            )
        elif Platform.get() == Platform.LINUX.value:
            options.binary_location = "/usr/bin/sberbrowser-browser"
        return options


class RemoteSberBrowser(RemoteChromeBrowser):

    def __repr__(self):
        return "Sber-remote"

    def _options(self):
        options = super()._options()
        options.binary_location = "/usr/bin/sberbrowser-browser"
        options.capabilities.update({"browserName": "sber"})
        return options

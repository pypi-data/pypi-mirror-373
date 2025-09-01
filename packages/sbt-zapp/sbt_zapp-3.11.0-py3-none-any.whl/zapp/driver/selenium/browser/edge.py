import os
from typing import Type

from selenium.webdriver import EdgeOptions, Edge

from zapp.driver.selenium.browser.chrome import LocalChromeBrowser, RemoteChromeBrowser

from selenium.webdriver import EdgeOptions


class LocalEdgeBrowser(LocalChromeBrowser):
    def __repr__(self):
        return "Edge-local"

    def _options_cls(self) -> EdgeOptions:
        return EdgeOptions

    def _local_driver_cls(self) -> Type[Edge]:
        return Edge


class RemoteEdgeBrowser(RemoteChromeBrowser):

    def __repr__(self):
        return "Egde-remote"

    def _options_cls(self) -> EdgeOptions:
        return EdgeOptions

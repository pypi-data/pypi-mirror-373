from abc import ABCMeta
from collections import namedtuple
from time import sleep
from typing import Sequence, Optional
import logging
from datetime import timedelta
from urllib.parse import urlparse
import requests
from selenium.webdriver import ActionChains
from selene import browser
from selene.core._browser import Browser
from selene.core.entity import (
    Element as SeleneOriginalElement,
    Collection as SeleneOriginalElementCollection,
    Locator,
)
from selene.core.match import *
from selene.support.conditions import have, be
import selenium.common.exceptions as se_exc


from tenacity import retry_if_exception, retry, stop_after_delay, wait_fixed
from zapp.driver import (
    REMOTE_EXECUTOR,
    SELENOID_UI_URL,
    RETRY_DELAY,
)
from zapp.driver.selenium.js import (
    DRAG_AND_DROP_TO_BY_STEPS,
    DRAG_AND_HOVER_ON_BY_STEPS,
    HOVER_ON_AND_DROP_TO_BY_STEPS,
    OUTLINE,
    GET_TEXT,
    CLICK,
    DOCUMENT_READY_STATE,
    SCROLL_BY,
    WINDOW_SCROLL_BY,
    WINDOW_SCROLL_TO,
    CLEAR,
    SCROLL_INTO_VIEW,
)
from zapp.driver.models import BrowserWrapper, Element, ElementCollection
from zapp.driver.selenium.browser.chrome import LocalChromeBrowser, RemoteChromeBrowser
from zapp.driver.selenium.browser.firefox import (
    LocalFirefoxBrowser,
    RemoteFirefoxBrowser,
)
from zapp.driver.selenium.browser.ie import (
    LocalInternetExplorerBrowser,
    RemoteInternetExplorerBrowser,
)
from zapp.driver.selenium.browser.safari import LocalSafariBrowser, RemoteSafariBrowser
from zapp.driver.selenium.browser.sber import LocalSberBrowser, RemoteSberBrowser
from zapp.driver.selenium.browser.edge import LocalEdgeBrowser, RemoteEdgeBrowser
from zapp.driver.selenium.browser.yandex import LocalYandexBrowser, RemoteYandexBrowser
from zapp.features.core.utils import bytes_to_file

log = logging.getLogger(__name__)


EXCEPTIONS_TO_RETRY = (
    se_exc.StaleElementReferenceException,
    se_exc.ElementNotInteractableException,
    se_exc.ElementClickInterceptedException,
    se_exc.InvalidElementStateException,
)


BrowserPair = namedtuple("BrowserPair", "local remote")
BROWSERS = {
    "chrome": BrowserPair(local=LocalChromeBrowser, remote=RemoteChromeBrowser),
    "firefox": BrowserPair(local=LocalFirefoxBrowser, remote=RemoteFirefoxBrowser),
    "safari": BrowserPair(local=LocalSafariBrowser, remote=RemoteSafariBrowser),
    "yandex": BrowserPair(local=LocalYandexBrowser, remote=RemoteYandexBrowser),
    "ie": BrowserPair(
        local=LocalInternetExplorerBrowser, remote=RemoteInternetExplorerBrowser
    ),
    "sber": BrowserPair(local=LocalSberBrowser, remote=RemoteSberBrowser),
    "edge": BrowserPair(local=LocalEdgeBrowser, remote=RemoteEdgeBrowser),
}


def _get_browser(context, name: str) -> BrowserWrapper:
    browser_type = BROWSERS[name]
    browser_wrapper = (browser_type.remote if REMOTE_EXECUTOR else browser_type.local)(
        context.tempdir
    )
    log.info(
        f"Версия {browser_wrapper.name}: {browser_wrapper.version} /{browser_wrapper.type}"
    )

    if REMOTE_EXECUTOR:
        log.info(
            f"Просмотр выполнения сценария на удалённой машине: {SELENOID_UI_URL}#/sessions/{browser_wrapper.driver.session_id}"
        )

    context.browser_wrapper = browser_wrapper
    browser.config.driver = browser_wrapper.driver
    return SeleneBrowserWrapper(browser)


def escaping_exceptions(exception: BaseException) -> bool:
    if isinstance(exception, EXCEPTIONS_TO_RETRY):
        log.debug(f"Catching {exception.__class__.__name__}, retrying...")
        return True
    return False


def decorated_selenium_retry():
    return retry(
        retry=retry_if_exception(escaping_exceptions),
        stop=stop_after_delay(RETRY_DELAY),
        wait=wait_fixed(timedelta(milliseconds=250)),
        reraise=True,
    )


class DecoratedSeleniumMeta(ABCMeta):
    """
    Метакласс, который автоматически применяет декоратор с tenacity ко всем методам,
    кроме специальных методов (__init__, __new__, ...) и методов класса/статических методов.
    """

    def __new__(cls, name, bases, namespace):
        for key, value in namespace.items():
            if callable(value) and not key.startswith("__"):
                # Оборачиваем методы декоратором tenacity
                namespace[key] = decorated_selenium_retry()(value)
        return super().__new__(cls, name, bases, namespace)


class SeleneElement(Element[SeleneOriginalElement], metaclass=DecoratedSeleniumMeta):

    def shadow_root(self) -> "Element":
        return SeleneElement(
            SeleneOriginalElement(
                Locator(
                    f"Shadow Root {self}",
                    lambda: self.evaluate("return self.shadowRoot"),
                ),
                self.wrapped.config,
            )
        )

    def element(self, locator) -> Element:
        return SeleneElement(self.wrapped.element(locator))

    def elements(self, locator) -> ElementCollection:
        return SeleneElementCollection(self.wrapped.all(locator))

    def click(self, using_js: bool = False) -> "Element":
        if using_js:
            self.evaluate(CLICK)
        else:
            self.wrapped.click()
        return self

    def click_by_offset(self, x: float, y: float) -> "Element":
        self.wrapped.click(xoffset=x, yoffset=y)
        return self

    def double_click(self) -> "Element":
        self.wrapped.double_click()
        return self

    def context_click(self) -> "Element":
        self.wrapped.context_click()
        return self

    def hover(self) -> "Element":
        self.wrapped.hover()
        return self

    def type(self, text: str, delay: Optional[float] = None) -> "Element":
        delay = timedelta(milliseconds=delay).total_seconds() if delay else None
        if delay:
            for char in text:
                self.wrapped.type(char)
                sleep(delay)
        else:
            self.wrapped.type(text)
        return self

    def clear(self, using_js: bool = False) -> "Element":
        if using_js:
            self.evaluate(CLEAR)
        else:
            self.wrapped.clear()
        return self

    def fill(self, value: str) -> "Element":
        self.wrapped.send_keys(value)
        return self

    def drag_and_drop(self, x: float, y: float) -> "Element":
        self.should_be_visible()
        (
            ActionChains(self.wrapped.config.driver)
            .move_to_element(self.wrapped())
            .drag_and_drop_by_offset(self.wrapped(), x, y)
            .perform()
        )
        return self

    def drag_and_drop_to(self, target: "SeleneElement") -> "Element":
        self.should_be_visible()
        target.should_be_visible()
        (
            ActionChains(self.wrapped.config.driver)
            .move_to_element(self.wrapped())
            .drag_and_drop(self.wrapped(), target.wrapped())
            .perform()
        )
        return self

    def drag_and_drop_to_by_steps(
        self, target: "Element", steps_count: str, step_delay: int
    ) -> "Element":
        return self._custom_drag_and_drop_to_by_steps(
            DRAG_AND_DROP_TO_BY_STEPS, target, steps_count, step_delay
        )

    def drag_and_hover_on_by_steps(
        self, target: "Element", steps_count: str, step_delay: int
    ) -> "Element":
        return self._custom_drag_and_drop_to_by_steps(
            DRAG_AND_HOVER_ON_BY_STEPS, target, steps_count, step_delay
        )

    def hover_on_and_drop_to_by_steps(
        self, target: "Element", steps_count: str, step_delay: int
    ) -> "Element":
        return self._custom_drag_and_drop_to_by_steps(
            HOVER_ON_AND_DROP_TO_BY_STEPS, target, steps_count, step_delay
        )

    def _custom_drag_and_drop_to_by_steps(
        self, script: str, target: "Element", steps_count: str, step_delay: int
    ):
        self.should_be_visible()
        target.should_be_visible()
        self.wrapped.config.driver.execute_async_script(
            script, self.wrapped(), target.wrapped(), steps_count, step_delay
        )
        return self

    def scroll_into_view(self) -> "Element":
        self.evaluate(SCROLL_INTO_VIEW)
        return self

    def attribute(self, name: str) -> str | None:
        return self.should_be_attached().wrapped().get_attribute(name)

    def text(self) -> str | None:
        return self.evaluate(GET_TEXT)

    def is_visible(self) -> bool:
        return self.wrapped.matching(be.visible)

    def is_hidden(self) -> bool:
        return self.wrapped.matching(be.hidden)

    def is_checked(self) -> bool:
        return self.wrapped.matching(be.selected)

    def is_enabled(self) -> bool:
        return self.wrapped.matching(be.enabled)

    def is_disabled(self) -> bool:
        return self.wrapped.matching(be.disabled)

    def evaluate(self, script: str, *args) -> Any | None:
        self.should_be_attached()
        return self.wrapped.config.driver.execute_script(
            f"""
                const [self, ...args] = [...arguments];
                return (function() {{
                    {script}
                }})(...args)
            """,
            self.wrapped(),
            *args,
        )

    def highlight(self) -> "Element":
        self.evaluate(OUTLINE)
        return self

    def scroll_by(self, x: float, y: float) -> "Element":
        self.evaluate(SCROLL_BY, x, y)
        return self

    def should_be_attached(self) -> "Element":
        self.wrapped.should(be.present)
        return self

    def should_be_checked(self) -> "Element":
        self.wrapped.should(be.selected)
        return self

    def should_be_disabled(self) -> "Element":
        self.wrapped.should(be.disabled)
        return self

    def should_be_empty(self) -> "Element":
        self.wrapped.should(be.empty)
        return self

    def should_be_enabled(self) -> "Element":
        self.wrapped.should(be.enabled)
        return self

    def should_be_hidden(self) -> "Element":
        self.wrapped.should(be.hidden)
        return self

    def should_be_visible(self) -> "Element":
        self.wrapped.should(be.visible)
        return self

    def should_have_text(self, text) -> "Element":
        self.should_be_attached().wrapped.should(have.exact_text(text))
        return self

    def should_contain_text(self, text) -> "Element":
        self.should_be_attached().wrapped.should(have.text(text))
        return self

    def should_have_value(self, value) -> "Element":
        self.should_be_attached().wrapped.should(have.value(value))
        return self

    def should_have_class(self, value) -> "Element":
        self.should_be_attached().wrapped.should(have.css_class(value))
        return self

    def should_have_attribute(self, name, value) -> "Element":
        self.should_be_attached().wrapped.should(have.attribute(name).value(value))
        return self

    def should_have_css_property(self, name, value) -> "Element":
        self.should_be_attached().wrapped.should(have.css_property(name).value(value))
        return self

    def should_not_be_attached(self) -> "Element":
        self.wrapped.should(be.not_.present)
        return self

    def should_not_be_checked(self) -> "Element":
        self.wrapped.should(be.not_.selected)
        return self

    def should_not_be_disable(self) -> "Element":
        self.wrapped.should(be.not_.disabled)
        return self

    def should_not_be_empty(self) -> "Element":
        self.wrapped.should(be.not_.blank)
        return self

    def should_not_be_enabled(self) -> "Element":
        self.wrapped.should(be.not_.enabled)
        return self

    def should_not_be_hidden(self) -> "Element":
        self.wrapped.should(be.not_.hidden)
        return self

    def should_not_be_visible(self) -> "Element":
        self.wrapped.should(be.not_.visible)
        return self

    def should_not_have_text(self, text) -> "Element":
        self.should_be_attached().wrapped.should(have.no.exact_text(text))
        return self

    def should_not_contain_text(self, text) -> "Element":
        self.should_be_attached().wrapped.should(have.no.text(text))
        return self

    def should_not_have_value(self, value) -> "Element":
        self.should_be_attached().wrapped.should(have.no.value(value))
        return self

    def should_not_have_class(self, value) -> "Element":
        self.should_be_attached().wrapped.should(have.no.css_class(value))
        return self

    def should_not_have_attribute(self, name, value) -> "Element":
        self.should_be_attached().wrapped.should(have.attribute(name).value(value).not_)
        return self

    def should_not_have_css_property(self, name, value) -> "Element":
        self.should_be_attached().wrapped.should(
            have.css_property(name).value(value).not_
        )
        return self


class SeleneElementCollection(
    ElementCollection[SeleneOriginalElementCollection], metaclass=DecoratedSeleniumMeta
):

    def __len__(self) -> int:
        return self.wrapped.__len__()

    def __iter__(self):
        for index in range(len(self)):
            yield self.nth(index)

    def first(self) -> Element:
        return SeleneElement(self.wrapped.first)

    def last(self) -> Element:
        return SeleneElement(self.nth(len(self) - 1))

    def nth(self, index) -> Element:
        return SeleneElement(self.wrapped.element(index))

    def texts(self) -> list[str]:
        return [
            element.text() for element in self if element.wrapped.matching(be.present)
        ]

    def attribute_values(self, attribute) -> list[str]:
        return [
            element.attribute(attribute)
            for element in self
            if element.wrapped.matching(be.present)
        ]

    def elements(self, locator) -> "ElementCollection":
        return SeleneElementCollection(self.wrapped.all(locator))

    def filter_by_text(self, text) -> "ElementCollection":
        return self._filter_by_condition(have.exact_text(text))

    def filter_by_partial_text(self, text) -> "ElementCollection":
        return self._filter_by_condition(have.text(text))

    def filter_by_attribute_value(self, attribute, value) -> "ElementCollection":
        return self._filter_by_condition(have.attribute(attribute).value(value))

    def filter_by_partial_attribute_value(
        self, attribute, value
    ) -> "ElementCollection":
        return self._filter_by_condition(
            have.attribute(attribute).value_containing(value)
        )

    def _filter_by_condition(self, condition) -> "ElementCollection":
        return SeleneElementCollection(self.wrapped.by(condition))

    def should_have_texts(self, texts: Sequence[str]) -> "ElementCollection":
        self.wrapped.should(have.exact_texts(texts))
        return self

    def should_contain_texts(self, texts: Sequence[str]) -> "ElementCollection":
        self.wrapped.should(have.texts(texts))
        return self

    def should_have_values(self, values: Sequence[str]) -> "ElementCollection":
        self.wrapped.should(have.values(values))
        return self

    def should_have_count(self, count: int) -> "ElementCollection":
        self.wrapped.should(have.size(count))
        return self

    def should_not_have_texts(self, texts: Sequence[str]) -> "ElementCollection":
        self.wrapped.should(have.no.exact_texts(texts))
        return self

    def should_not_contain_texts(self, texts: Sequence[str]) -> "ElementCollection":
        self.wrapped.should(have.no.texts(texts))
        return self

    def should_not_have_values(self, values: Sequence[str]) -> "ElementCollection":
        self.wrapped.should(have.no.values(values))
        return self

    def should_not_have_count(self, count: int) -> "ElementCollection":
        self.wrapped.should(have.no.size(count))
        return self


class SeleneBrowserWrapper(BrowserWrapper[Browser]):

    @property
    def timeout(self) -> timedelta:
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: timedelta):
        self._timeout = timeout
        self.wrapped.config.timeout = timeout.total_seconds()

    def name(self) -> str:
        return self.wrapped.driver.name

    def page_source(self) -> str:
        return self.wrapped.driver.page_source

    def title(self) -> str:
        return self.wrapped.driver.title

    def url(self) -> str:
        return self.wrapped.driver.current_url

    def wait_for_loading(self) -> bool:
        return self.wrapped.wait_until(
            lambda _: str(self.evaluate(DOCUMENT_READY_STATE)) == "complete"
        )

    def open(self, url):
        self.wrapped.open(url)

    def refresh(self):
        self.wrapped.driver.refresh()

    def quit(self):
        self.wrapped.quit()

    def close(self):
        self.wrapped.close()

    def scroll_to(self, x: float, y: float):
        self.evaluate(WINDOW_SCROLL_TO, x, y)

    def scroll_by(self, x: float, y: float):
        self.evaluate(WINDOW_SCROLL_BY, x, y)

    def element(self, locator) -> Element:
        return SeleneElement(self.wrapped.element(locator))

    def elements(self, locator) -> ElementCollection:
        return SeleneElementCollection(self.wrapped.all(locator))

    def close_other_tabs(self):
        tabs = self.wrapped.driver.window_handles
        current_tab = self.wrapped.driver.current_window_handle
        for tab in tabs:
            if tab != current_tab:
                self.wrapped.driver.switch_to.window(tab)
                self.close()
        self.wrapped.driver.switch_to.window(current_tab)

    def switch_to_last_tab(self):
        tabs = len(self.wrapped.driver.window_handles)
        self.wrapped.switch_to_tab(tabs - 1)

    def switch_to_next_tab(self):
        self.wrapped.switch_to_next_tab()

    def switch_to_previous_tab(self):
        self.wrapped.switch_to_previous_tab()

    def switch_to_tab(self, index_or_name):
        self.wrapped.switch_to_tab(index_or_name)

    def screenshot(self) -> bytes:
        return self.wrapped.driver.get_screenshot_as_png()

    def clear_local_storage(self):
        self.wrapped.clear_local_storage()

    def clear_session_storage(self):
        self.wrapped.clear_session_storage()

    def clear_cookies(self):
        self.wrapped.driver.delete_all_cookies()

    def add_cookies(self, cookies: Sequence[dict]):
        for cookie in cookies:
            self.wrapped.driver.add_cookie(cookie)

    def switch_to_frame(self, selector: str):
        element = self.element(selector).should_be_attached().wrapped()
        self.wrapped.switch_to.frame(element)

    def switch_to_default_content(self):
        self.wrapped.switch_to.default_content()

    def set_window_size(self, width: int, height: int):
        self.wrapped.driver.set_window_size(width, height)

    def get_window_size(self) -> dict:
        return self.wrapped.driver.get_window_size()

    def evaluate(self, script: str, *args):
        return self.wrapped.driver.execute_script(script, *args)

    def press(
        self, *keys: Sequence[str], delay: Optional[float] = None
    ) -> BrowserWrapper:
        delay = timedelta(milliseconds=delay).total_seconds() if delay else None
        actions = ActionChains(self.wrapped.driver)
        for key in keys:
            actions.send_keys(key)
            if delay:
                actions.pause(delay)
        actions.perform()
        return self

    def up(self, *keys: Sequence[str]) -> BrowserWrapper:
        actions = ActionChains(self.wrapped.driver)
        for key in keys:
            actions.key_up(key)
        actions.perform()
        return self

    def down(self, *keys: Sequence[str]) -> BrowserWrapper:
        actions = ActionChains(self.wrapped.driver)
        for key in keys:
            actions.key_down(key)
        actions.perform()
        return self

    def type(self, text: str, delay: Optional[float] = None) -> BrowserWrapper:
        return self.press(*text, delay=delay)

    def get_clipboard_value(self):
        if REMOTE_EXECUTOR:
            """@see https://github.com/aerokube/selenoid/blob/master/docs/clipboard.adoc"""
            selenoid_url = urlparse(REMOTE_EXECUTOR)
            response = requests.get(
                f"{selenoid_url.scheme}://{selenoid_url.netloc}/clipboard/{self.wrapped.driver.session_id}"
            )
            response.raise_for_status()
            return response.text
        else:
            return super().get_clipboard_value()

    def pdf(
        self,
        output: str,
        landscape: bool = True,
        print_background: bool = False,
        prefer_css_page_size: bool = False,
        display_header_footer: bool = True,
    ) -> "BrowserWrapper":
        pdf_data = self.wrapped.driver.execute_cdp_cmd(
            "Page.printToPDF",
            {
                "landscape": landscape,
                "printBackground": print_background,
                "preferCSSPageSize": prefer_css_page_size,
                "displayHeaderFooter": display_header_footer,
            },
        )

        bytes_to_file(pdf_data["data"], output, decode=True)
        return self

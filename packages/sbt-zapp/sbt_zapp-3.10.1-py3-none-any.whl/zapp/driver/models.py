from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, Sequence, Optional
from datetime import timedelta

import pyperclip

from zapp.driver import ELEMENT_TIMEOUT
from zapp.features.core.utils import bytes_to_file


WrappedType = TypeVar("WrappedType")


class Wrapper(ABC, Generic[WrappedType]):

    _wrapped: WrappedType

    def __init__(self, wrapped: WrappedType):
        self._wrapped = wrapped

    @property
    def wrapped(self) -> WrappedType:
        return self._wrapped


class Element(Wrapper[WrappedType]):

    @abstractmethod
    def shadow_root(self) -> "Element":
        pass

    @abstractmethod
    def element(self, locator) -> "Element":
        pass

    @abstractmethod
    def elements(self, locator) -> "ElementCollection":
        pass

    @abstractmethod
    def click(self, using_js: bool = False) -> "Element":
        pass

    @abstractmethod
    def click_by_offset(self, x: float, y: float) -> "Element":
        pass

    @abstractmethod
    def double_click(self) -> "Element":
        pass

    @abstractmethod
    def context_click(self) -> "Element":
        pass

    @abstractmethod
    def hover(self) -> "Element":
        pass

    @abstractmethod
    def type(self, text: str, delay: Optional[float] = None) -> "Element":
        pass

    @abstractmethod
    def clear(self, using_js: bool = False) -> "Element":
        pass

    @abstractmethod
    def fill(self, value: str) -> "Element":
        pass

    @abstractmethod
    def drag_and_drop(self, x: float, y: float) -> "Element":
        pass

    @abstractmethod
    def drag_and_drop_to(self, target: "Element") -> "Element":
        pass

    @abstractmethod
    def drag_and_drop_to_by_steps(
        self, target: "Element", steps_count: str, step_delay: int
    ) -> "Element":
        pass

    @abstractmethod
    def drag_and_hover_on_by_steps(
        self, target: "Element", steps_count: str, step_delay: int
    ) -> "Element":
        pass

    @abstractmethod
    def hover_on_and_drop_to_by_steps(
        self, target: "Element", steps_count: str, step_delay: int
    ) -> "Element":
        pass

    @abstractmethod
    def scroll_into_view(self) -> "Element":
        pass

    @abstractmethod
    def attribute(self, name: str) -> str | None:
        pass

    @abstractmethod
    def text(self) -> str | None:
        pass

    @abstractmethod
    def is_visible(self) -> bool:
        pass

    @abstractmethod
    def is_hidden(self) -> bool:
        pass

    @abstractmethod
    def is_checked(self) -> bool:
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        pass

    @abstractmethod
    def is_disabled(self) -> bool:
        pass

    @abstractmethod
    def evaluate(self, script: str, *args) -> Any | None:
        pass

    @abstractmethod
    def highlight(self) -> "Element":
        pass

    @abstractmethod
    def scroll_by(self, x: float, y: float) -> "Element":
        pass

    @abstractmethod
    def should_be_attached(self) -> "Element":
        pass

    @abstractmethod
    def should_be_checked(self) -> "Element":
        pass

    @abstractmethod
    def should_be_disabled(self) -> "Element":
        pass

    @abstractmethod
    def should_be_empty(self) -> "Element":
        pass

    @abstractmethod
    def should_be_enabled(self) -> "Element":
        pass

    @abstractmethod
    def should_be_hidden(self) -> "Element":
        pass

    @abstractmethod
    def should_be_visible(self) -> "Element":
        pass

    @abstractmethod
    def should_have_text(self, text) -> "Element":
        pass

    @abstractmethod
    def should_contain_text(self, text) -> "Element":
        pass

    @abstractmethod
    def should_have_value(self, value) -> "Element":
        pass

    @abstractmethod
    def should_have_class(self, value) -> "Element":
        pass

    @abstractmethod
    def should_have_attribute(self, name, value) -> "Element":
        pass

    @abstractmethod
    def should_have_css_property(self, name, value) -> "Element":
        pass

    @abstractmethod
    def should_not_be_attached(self) -> "Element":
        pass

    @abstractmethod
    def should_not_be_checked(self) -> "Element":
        pass

    @abstractmethod
    def should_not_be_disable(self) -> "Element":
        pass

    @abstractmethod
    def should_not_be_empty(self) -> "Element":
        pass

    @abstractmethod
    def should_not_be_enabled(self) -> "Element":
        pass

    @abstractmethod
    def should_not_be_hidden(self) -> "Element":
        pass

    @abstractmethod
    def should_not_be_visible(self) -> "Element":
        pass

    @abstractmethod
    def should_not_have_text(self, text) -> "Element":
        pass

    @abstractmethod
    def should_not_contain_text(self, text) -> "Element":
        pass

    @abstractmethod
    def should_not_have_value(self, value) -> "Element":
        pass

    @abstractmethod
    def should_not_have_class(self, value) -> "Element":
        pass

    @abstractmethod
    def should_not_have_attribute(self, name, value) -> "Element":
        pass

    @abstractmethod
    def should_not_have_css_property(self, name, value) -> "Element":
        pass


class ElementCollection(Wrapper[WrappedType]):

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def __iter__(self):
        pass

    def __getitem__(self, index) -> Element:
        return self.nth(index)

    def highlight(self) -> "ElementCollection":
        for element in self:
            element.highlight()
        return self

    @abstractmethod
    def first(self) -> Element:
        pass

    @abstractmethod
    def last(self) -> Element:
        pass

    @abstractmethod
    def nth(self, index) -> Element:
        pass

    @abstractmethod
    def texts(self) -> list[str]:
        pass

    @abstractmethod
    def attribute_values(self, attribute) -> list[str]:
        pass

    @abstractmethod
    def elements(self, locator) -> "ElementCollection":
        pass

    @abstractmethod
    def filter_by_text(self, text) -> "ElementCollection":
        pass

    @abstractmethod
    def filter_by_partial_text(self, text) -> "ElementCollection":
        pass

    @abstractmethod
    def filter_by_attribute_value(self, attribute, value) -> "ElementCollection":
        pass

    @abstractmethod
    def filter_by_partial_attribute_value(
        self, attribute, value
    ) -> "ElementCollection":
        pass

    @abstractmethod
    def should_have_texts(self, texts: Sequence[str]) -> "ElementCollection":
        pass

    @abstractmethod
    def should_contain_texts(self, texts: Sequence[str]) -> "ElementCollection":
        pass

    @abstractmethod
    def should_have_values(self, values: Sequence[str]) -> "ElementCollection":
        pass

    @abstractmethod
    def should_have_count(self, count: int) -> "ElementCollection":
        pass

    @abstractmethod
    def should_not_have_texts(self, texts: Sequence[str]) -> "ElementCollection":
        pass

    @abstractmethod
    def should_not_contain_texts(self, texts: Sequence[str]) -> "ElementCollection":
        pass

    @abstractmethod
    def should_not_have_values(self, values: Sequence[str]) -> "ElementCollection":
        pass

    @abstractmethod
    def should_not_have_count(self, count: int) -> "ElementCollection":
        pass


class BrowserWrapper(Wrapper[WrappedType]):

    _timeout: timedelta

    def __init__(self, wrapped: WrappedType):
        super().__init__(wrapped)
        self.timeout = ELEMENT_TIMEOUT

    @property
    def timeout(self) -> timedelta:
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: timedelta):
        self._timeout = timeout

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def page_source(self) -> str:
        pass

    @abstractmethod
    def title(self) -> str:
        pass

    @abstractmethod
    def url(self) -> str:
        pass

    @abstractmethod
    def wait_for_loading(self) -> bool:
        pass

    @abstractmethod
    def open(self, url):
        pass

    @abstractmethod
    def refresh(self):
        pass

    @abstractmethod
    def quit(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def scroll_to(self, x: float, y: float):
        pass

    @abstractmethod
    def scroll_by(self, x: float, y: float):
        pass

    @abstractmethod
    def element(self, locator) -> Element:
        pass

    @abstractmethod
    def elements(self, locator) -> ElementCollection:
        pass

    @abstractmethod
    def switch_to_last_tab(self):
        pass

    @abstractmethod
    def switch_to_next_tab(self):
        pass

    @abstractmethod
    def switch_to_previous_tab(self):
        pass

    @abstractmethod
    def switch_to_tab(self, index_or_name):
        pass

    @abstractmethod
    def close_other_tabs(self):
        pass

    @abstractmethod
    def clear_local_storage(self):
        pass

    @abstractmethod
    def clear_session_storage(self):
        pass

    @abstractmethod
    def clear_cookies(self):
        pass

    @abstractmethod
    def add_cookies(self, cookies: Sequence[dict]):
        pass

    @abstractmethod
    def switch_to_frame(self, selector: str):
        pass

    @abstractmethod
    def switch_to_default_content(self):
        pass

    @abstractmethod
    def set_window_size(self, width: int, height: int):
        pass

    @abstractmethod
    def get_window_size(self) -> dict:
        pass

    @abstractmethod
    def evaluate(self, script: str, *args) -> Any | None:
        pass

    @abstractmethod
    def press(
        self, *keys: Sequence[str], delay: Optional[float] = None
    ) -> "BrowserWrapper":
        pass

    @abstractmethod
    def up(self, *keys: Sequence[str]) -> "BrowserWrapper":
        pass

    @abstractmethod
    def down(self, *keys: Sequence[str]) -> "BrowserWrapper":
        pass

    @abstractmethod
    def type(self, text: str, delay: Optional[float] = None):
        pass

    def get_clipboard_value(self) -> str:
        return pyperclip.paste()

    @abstractmethod
    def screenshot(self) -> bytes:
        pass

    def screenshot_as_file(self, output: str) -> str:
        screenshot_bytes = self.screenshot()
        bytes_to_file(screenshot_bytes, output)
        return output

    @abstractmethod
    def pdf(
        self,
        output: str,
        landscape: bool = True,
        print_background: bool = False,
        prefer_css_page_size: bool = False,
        display_header_footer: bool = True,
    ) -> "BrowserWrapper":
        pass

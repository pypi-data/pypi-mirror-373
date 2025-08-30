from datetime import timedelta
import re
from playwright.sync_api import (
    sync_playwright,
    Page,
    Browser,
    BrowserContext,
    Locator,
    FrameLocator,
    expect,
)
from typing import Any, Sequence, Optional

from zapp.driver.playwright.js import (
    CLEAR_LOCAL_STORAGE,
    CLEAR_SESSION_STORAGE,
    CLICK,
    OUTLINE,
    WINDOW_SCROLL_TO,
    CLEAR,
    DRAG_AND_DROP_TO_BY_STEPS,
    DRAG_AND_HOVER_ON_BY_STEPS,
    HOVER_ON_AND_DROP_TO_BY_STEPS,
    SCROLL_INTO_VIEW
)
from zapp.driver.models import BrowserWrapper, Element, ElementCollection
from zapp.driver import BROWSER_HEADLESS, BROWSER_USERAGENT, CHROMIUM_DEFAULT_ARGS
from zapp.driver.playwright.key_mappings import (
    get_keyboard_event,
)

BROWSERS = {
    "chrome": lambda pw, **kwargs: pw.chromium.launch(
        channel="chrome", args=CHROMIUM_DEFAULT_ARGS, **kwargs
    ),
    "firefox": lambda pw, **kwargs: pw.firefox.launch(**kwargs),
    "safari": lambda pw, **kwargs: pw.webkit.launch(**kwargs),
    "edge": lambda pw, **kwargs: pw.chromium.launch(
        channel="msedge", args=CHROMIUM_DEFAULT_ARGS, **kwargs
    ),
}


def _get_browser(context, name: str) -> BrowserWrapper:
    pw = sync_playwright().start()
    context.add_cleanup(lambda _: pw.stop(), context)
    return PlaywrightBrowserWrapper(
        BROWSERS[name](pw, headless=BROWSER_HEADLESS, downloads_path=context.tempdir)
    )


class PlaywrightElement(Element[Locator]):

    def shadow_root(self) -> "Element":
        return self

    def element(self, locator) -> Element:
        return PlaywrightElement(self.wrapped.locator(locator).first)

    def elements(self, locator) -> ElementCollection:
        return PlaywrightElementCollection(self.wrapped.locator(locator))

    def click(self, using_js: bool = False) -> "Element":
        if using_js:
            self.evaluate(CLICK)
        else:
            self.wrapped.click()
        return self

    def click_by_offset(self, x: float, y: float) -> "Element":
        self.wrapped.click(position={"x": x, "y": y})
        return self

    def double_click(self) -> "Element":
        self.wrapped.dblclick()
        return self

    def context_click(self) -> "Element":
        self.wrapped.click(button="right")
        return self

    def hover(self) -> "Element":
        self.wrapped.hover()
        return self

    def type(self, text: str, delay: Optional[float] = None) -> "Element":
        self.wrapped.type(text, delay=delay)
        return self

    def clear(self, using_js: bool = False) -> "Element":
        if using_js:
            self.evaluate(CLEAR)
        else:
            self.wrapped.clear()
        return self

    def fill(self, value: str) -> "Element":
        self.wrapped.fill(value)
        return self

    def drag_and_drop(self, x: float, y: float) -> "Element":
        box = self.wrapped.bounding_box()
        original_x = box["x"] + box["width"] / 2
        original_y = box["y"] + box["height"] / 2
        self.wrapped.page.mouse.move(original_x, original_y)
        self.wrapped.page.mouse.down()
        self.wrapped.page.mouse.move(original_x + x, original_y + y)
        self.wrapped.page.mouse.up()
        return self

    def drag_and_drop_to(self, target: "PlaywrightElement") -> "Element":
        self.wrapped.drag_to(target=target.wrapped)
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
        self.evaluate(script, target.wrapped.element_handle(), steps_count, step_delay)
        return self

    def scroll_into_view(self) -> "Element":
        self.evaluate(SCROLL_INTO_VIEW)
        return self

    def attribute(self, name: str) -> str | None:
        return self.wrapped.get_attribute(name)

    def text(self) -> str | None:
        return self.wrapped.text_content()

    def is_visible(self) -> bool:
        return self.wrapped.is_visible()

    def is_hidden(self) -> bool:
        return self.wrapped.is_hidden()

    def is_checked(self) -> bool:
        return self.wrapped.is_checked()

    def is_enabled(self) -> bool:
        return self.wrapped.is_enabled()

    def is_disabled(self) -> bool:
        return self.wrapped.is_disabled()

    def evaluate(self, script: str, *args) -> Any | None:
        return self.wrapped.evaluate(script, list(args))

    def highlight(self) -> "Element":
        self.evaluate(OUTLINE)
        return self

    def scroll_by(self, x: float, y: float) -> "Element":
        self.hover().wrapped.page.mouse.wheel(x, y)
        return self

    def should_be_attached(self) -> "Element":
        expect(self.wrapped).to_be_attached()
        return self

    def should_be_checked(self) -> "Element":
        expect(self.wrapped).to_be_checked()
        return self

    def should_be_disabled(self) -> "Element":
        expect(self.wrapped).to_be_disabled()
        return self

    def should_be_empty(self) -> "Element":
        expect(self.wrapped).to_be_empty()
        return self

    def should_be_enabled(self) -> "Element":
        expect(self.wrapped).to_be_enabled()
        return self

    def should_be_hidden(self) -> "Element":
        expect(self.wrapped).to_be_hidden()
        return self

    def should_be_visible(self) -> "Element":
        expect(self.wrapped).to_be_visible()
        return self

    def should_have_text(self, text) -> "Element":
        expect(self.wrapped).to_have_text(text)
        return self

    def should_contain_text(self, text) -> "Element":
        expect(self.wrapped).to_contain_text(text)
        return self

    def should_have_value(self, value) -> "Element":
        expect(self.wrapped).to_have_value(value)
        return self

    def should_have_class(self, value) -> "Element":
        expect(self.wrapped).to_have_class(re.compile(rf"(^|\s){value}(\s|$)"))
        return self

    def should_have_attribute(self, name, value) -> "Element":
        expect(self.wrapped).to_have_attribute(name, value)
        return self

    def should_have_css_property(self, name, value) -> "Element":
        expect(self.wrapped).to_have_css(name, value)
        return self

    def should_not_be_attached(self) -> "Element":
        expect(self.wrapped).not_to_be_attached()
        return self

    def should_not_be_checked(self) -> "Element":
        expect(self.wrapped).not_to_be_checked()
        return self

    def should_not_be_disable(self) -> "Element":
        expect(self.wrapped).not_to_be_disabled()
        return self

    def should_not_be_empty(self) -> "Element":
        expect(self.wrapped).not_to_be_empty()
        return self

    def should_not_be_enabled(self) -> "Element":
        expect(self.wrapped).not_to_be_enabled()
        return self

    def should_not_be_hidden(self) -> "Element":
        expect(self.wrapped).not_to_be_hidden()
        return self

    def should_not_be_visible(self) -> "Element":
        expect(self.wrapped).not_to_be_visible()
        return self

    def should_not_have_text(self, text) -> "Element":
        expect(self.wrapped).not_to_have_text(text)
        return self

    def should_not_contain_text(self, text) -> "Element":
        expect(self.wrapped).not_to_contain_text(text)
        return self

    def should_not_have_value(self, value) -> "Element":
        expect(self.wrapped).not_to_have_value(value)
        return self

    def should_not_have_class(self, value) -> "Element":
        expect(self.wrapped).not_to_have_class(re.compile(rf"(^|\s){value}(\s|$)"))
        return self

    def should_not_have_attribute(self, name, value) -> "Element":
        expect(self.wrapped).not_to_have_attribute(name, value)
        return self

    def should_not_have_css_property(self, name, value) -> "Element":
        expect(self.wrapped).not_to_have_css(name, value)
        return self


class PlaywrightElementCollection(ElementCollection[Locator]):

    def __len__(self) -> int:
        return self.wrapped.count()

    def __iter__(self):
        for index in range(len(self)):
            yield self.nth(index)

    def first(self) -> Element:
        return PlaywrightElement(self.wrapped.first)

    def last(self) -> Element:
        return PlaywrightElement(self.wrapped.last)

    def nth(self, index) -> Element:
        return PlaywrightElement(self.wrapped.nth(index))

    def texts(self) -> list[str]:
        return self.wrapped.all_text_contents()

    def attribute_values(self, attribute) -> list[str]:
        return [element.attribute(attribute) for element in self]

    def elements(self, locator) -> "ElementCollection":
        return PlaywrightElementCollection(self.wrapped.locator(locator))

    def filter_by_text(self, text) -> "ElementCollection":
        return PlaywrightElementCollection(
            # Использование :text-is("{text}") аналогично text()=, то есть не учитывает innerText
            self.wrapped.and_(self.wrapped.page.locator(f'//*[.="{text}"]'))
        )

    def filter_by_partial_text(self, text) -> "ElementCollection":
        return PlaywrightElementCollection(
            self.wrapped.and_(self.wrapped.page.locator(f':has-text("{text}")'))
        )

    def filter_by_attribute_value(self, attribute, value) -> "ElementCollection":
        locator = f'[{attribute}="{value}"]'
        return PlaywrightElementCollection(
            self.wrapped.and_(self.wrapped.page.locator(locator))
        )

    def filter_by_partial_attribute_value(
        self, attribute, value
    ) -> "ElementCollection":
        locator = f'[{attribute}*="{value}"]'
        return PlaywrightElementCollection(
            self.wrapped.and_(self.wrapped.page.locator(locator))
        )

    def should_have_texts(self, texts: Sequence[str]) -> "ElementCollection":
        expect(self.wrapped).to_have_text(texts)
        return self

    def should_contain_texts(self, texts: Sequence[str]) -> "ElementCollection":
        expect(self.wrapped).to_contain_text(texts)
        return self

    def should_have_values(self, values: Sequence[str]) -> "ElementCollection":
        expect(self.wrapped).to_have_values(values)
        return self

    def should_have_count(self, count: int) -> "ElementCollection":
        expect(self.wrapped).to_have_count(count)
        return self

    def should_not_have_texts(self, texts: Sequence[str]) -> "ElementCollection":
        expect(self.wrapped).not_to_have_text(texts)
        return self

    def should_not_contain_texts(self, texts: Sequence[str]) -> "ElementCollection":
        expect(self.wrapped).not_to_contain_text(texts)
        return self

    def should_not_have_values(self, values: Sequence[str]) -> "ElementCollection":
        expect(self.wrapped).not_to_have_values(values)
        return self

    def should_not_have_count(self, count: int) -> "ElementCollection":
        expect(self.wrapped).not_to_have_count(count)
        return self


class PlaywrightBrowserWrapper(BrowserWrapper[Browser]):

    _context: BrowserContext
    _current_page: Page | None = None
    _current_iframe: Locator | None = None

    def __init__(self, browser: Browser):
        super().__init__(browser)
        self._context = browser.new_context(user_agent=BROWSER_USERAGENT)
        self._current_page = self.context.new_page()

    @property
    def timeout(self) -> timedelta:
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: timedelta):
        self._timeout = timeout
        milliseconds = timeout.total_seconds() * 1000
        expect.set_options(timeout=milliseconds)
        if self.page is not None:
            self.page.set_default_timeout(milliseconds)

    @property
    def page(self):
        return self._current_page

    @page.setter
    def page(self, page: Page):
        page.bring_to_front()
        page.set_default_timeout(self.timeout.total_seconds() * 1000)
        self._current_page = page

    @property
    def context(self):
        return self._context

    def name(self) -> str:
        return self.wrapped.browser_type.name

    def page_source(self) -> str:
        return self.page.content()

    def title(self) -> str:
        return self.page.title()

    def url(self) -> str:
        return self.page.url

    def wait_for_loading(self) -> bool:
        try:
            self.page.wait_for_load_state("domcontentloaded")
            return True
        except:
            return False

    def open(self, url):
        self.page.goto(url)

    def refresh(self):
        self.page.reload()

    def quit(self):
        self.wrapped.close()

    def close(self):
        self.page.close()

    def scroll_to(self, x: float, y: float):
        self.evaluate(WINDOW_SCROLL_TO, x, y)

    def scroll_by(self, x: float, y: float):
        self.page.mouse.wheel(x, y)

    def _root_to_locate(self) -> Page | FrameLocator:
        if self._current_iframe:
            return self._current_iframe
        return self.page

    def element(self, locator) -> Element:
        return PlaywrightElement(self._root_to_locate().locator(locator).first)

    def elements(self, locator) -> ElementCollection:
        return PlaywrightElementCollection(self._root_to_locate().locator(locator))

    def close_other_tabs(self):
        tabs = self.context.pages
        for tab in tabs:
            if tab != self.page:
                tab.close()

    def switch_to_last_tab(self):
        self.page = self.context.pages[-1]

    def switch_to_next_tab(self):
        tabs = self.context.pages
        current_index = tabs.index(self.page)
        self.page = (
            tabs[0] if current_index >= len(tabs) - 1 else tabs[current_index + 1]
        )

    def switch_to_previous_tab(self):
        tabs = self.context.pages
        current_index = tabs.index(self.page)
        self.page = tabs[-1] if current_index == 0 else tabs[current_index - 1]

    def switch_to_tab(self, index_or_name):
        tabs = self.context.pages
        if isinstance(index_or_name, int) and index_or_name < len(tabs):
            self.page = tabs[index_or_name]
        else:
            for tab in tabs:
                if tab.title() == index_or_name:
                    self.page = tab
                    return
        raise NameError(f"Tab with name/index {index_or_name} not found")

    def screenshot(self) -> bytes:
        return self.page.screenshot()

    def clear_local_storage(self):
        self.evaluate(CLEAR_LOCAL_STORAGE)

    def clear_session_storage(self):
        self.evaluate(CLEAR_SESSION_STORAGE)

    def clear_cookies(self):
        self.context.clear_cookies()

    def add_cookies(self, cookies: Sequence[dict]):
        self.context.add_cookies(cookies)

    def switch_to_frame(self, selector: str):
        self._current_iframe = self._root_to_locate().frame_locator(selector)

    def switch_to_default_content(self):
        self._current_iframe = None

    def set_window_size(self, width: int, height: int):
        self.page.set_viewport_size({"width": width, "height": height})

    def get_window_size(self) -> dict:
        return self.page.viewport_size

    def evaluate(self, script: str, *args):
        return self.page.evaluate(script, list(args))

    def press(
        self, *keys: Sequence[str], delay: Optional[float] = None
    ) -> BrowserWrapper:
        self.page.keyboard.press(
            "+".join([get_keyboard_event(key) for key in keys]),
            delay=delay,
        )
        return self

    def up(self, *keys: Sequence[str]) -> BrowserWrapper:
        for key in keys:
            self.page.keyboard.up(get_keyboard_event(key))
        return self

    def down(self, *keys: Sequence[str]) -> BrowserWrapper:
        for key in keys:
            self.page.keyboard.down(get_keyboard_event(key))
        return self

    def type(self, text: str, delay: Optional[float] = None) -> BrowserWrapper:
        self.page.keyboard.type(text, delay=delay)
        return self

    def pdf(
        self,
        output: str,
        landscape: bool = True,
        print_background: bool = False,
        prefer_css_page_size: bool = False,
        display_header_footer: bool = True,
    ) -> "BrowserWrapper":
        self.page.emulate_media(media="print")
        self.page.pdf(
            path=output,
            landscape=landscape,
            print_background=print_background,
            prefer_css_page_size=prefer_css_page_size,
            display_header_footer=display_header_footer,
            format="A4",
            margin={
                "top": "10mm",
                "right": "10mm",
                "bottom": "10mm",
                "left": "10mm",
            },
        )
        self.page.emulate_media(media=None)
        return self

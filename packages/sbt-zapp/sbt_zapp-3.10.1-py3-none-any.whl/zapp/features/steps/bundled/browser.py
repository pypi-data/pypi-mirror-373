import allure
import logging
from behave import step
from zapp.features.steps.bundled.ui import go_to_url, assert_page_load

from envparse import env

from zapp.driver import DRIVER_IMPL

log = logging.getLogger(__name__)

COOKIE_SET_MAX_ATTEMPTS = env.int("COOKIE_SET_MAX_ATTEMPTS", default=3)

_browser_cookie_fields = {
    # Проставляются все поля, кроме домена, так как мы выставляем только для определенного домена значения (по умолчанию его и берет) +
    # Автоматом криво ставит точку сам клиент перед доменом: https://stackoverflow.com/questions/1062963/how-do-browser-cookie-domains-work/1063760#1063760
    "name": lambda cookie: cookie.name,
    "value": lambda cookie: cookie.value,
    "path": lambda cookie: cookie.path,
    "secure": lambda cookie: cookie.secure,
    "httpOnly": lambda cookie: cookie._rest.get("HttpOnly"),
    "sameSite": lambda cookie: cookie._rest.get("SameSite"),
    "expiry": lambda cookie: cookie.expires,
}

if DRIVER_IMPL == "PLAYWRIGHT":
    _browser_cookie_fields["domain"] = (
        lambda cookie: cookie.domain
    )  # необходим для Playwright, но наоборот не нужен для Selenium


class MaxAttemptsExceededException(AssertionError):
    pass


@step("Я открыл главную страницу авторизованным")
def open_main_page_by_authorized_user(context):
    host = context.host

    if not hasattr(context, "keycloak_session"):
        raise AssertionError(
            "Не выполнена авторизация по API. Шаг: 'API: Я авторизовался через KeyCloak...'"
        )

    session = context.keycloak_session

    go_to_url(context, host)
    context.browser.wait_for_loading()

    add_cookies_and_refresh(context, session)

    go_to_url(context, host)
    assert_page_load(context)


@allure.step("Установка cookies в браузере")
def add_cookies_and_refresh(context, session):
    previous = None
    try_count = 0

    while True:
        if try_count > COOKIE_SET_MAX_ATTEMPTS:
            raise MaxAttemptsExceededException(
                "Превышено количество попыток установить куки"
            )

        try_count = try_count + 1

        # Устанавливаем куки только для открытого в данный момент домена
        domain, cookies = session.domain_cookies(context.browser.url())
        if previous == domain:
            return
        previous = domain

        with allure.step(f"Установка cookie для домена {domain}"):
            log.info(f"Домен: {domain}")
            for cookie in cookies:
                log.info(f"Добавляем cookie: {cookie.name}")
                browser_cookie = {}
                for key, value in _browser_cookie_fields.items():
                    field_value = value(cookie)
                    if field_value is not None:
                        browser_cookie[key] = field_value
                # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#cookie_prefixes
                if cookie.name.startswith("__Host-"):
                    browser_cookie["sameSite"] = "Strict"
                context.browser.add_cookies([browser_cookie])
            context.browser.refresh()
            context.browser.wait_for_loading()

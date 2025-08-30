import logging

import requests
from tenacity import Retrying, retry_if_result, stop_after_attempt, wait_fixed
from zapp.features.core.utils import resolve_variables

RETRY_DEFAULT_VALUES = (2, 5)

log = logging.getLogger(__name__)


def is_bad_response(response) -> bool:
    log.debug(
        f"REQUEST: {response.request.method} {response.url}, "
        f"RESPONSE: {response.status_code}, "
        f"SUCCESS: {response.ok}"
    )
    return response.ok is False


def return_response(retry_state):
    return retry_state.outcome.result()


class Api:
    session = requests.Session()

    def __init__(self, browser_cookies=None):
        self.session.verify = False
        browser_cookies = browser_cookies or []
        for c in browser_cookies:
            self.session.cookies.set(c["name"], c["value"])

    @classmethod
    def request(cls, method, url, browser_cookies=None, **kwargs):
        attempts, wait_fix = kwargs.pop("retry", RETRY_DEFAULT_VALUES)
        retry = Retrying(
            retry=retry_if_result(is_bad_response),
            stop=stop_after_attempt(attempts),
            wait=wait_fixed(wait_fix),
            retry_error_callback=return_response,
        )

        # Добавляем поддержку переменных в URL
        resolved_url = resolve_variables(url)
        resolved_kwargs = {
            k: resolve_variables(v) if isinstance(v, str) else v
            for k, v in kwargs.items()
        }

        return retry(
            cls(browser_cookies).session.request,
            method.upper(),
            resolved_url,
            **resolved_kwargs
        )

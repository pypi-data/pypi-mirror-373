from abc import abstractmethod, ABC

import logging
from functools import wraps
from typing import Callable, Any, TypeVar, ParamSpec
from urllib.parse import urljoin, urlparse

from envparse import env
from requests import Response, HTTPError, Session
from bs4 import BeautifulSoup

METHOD_CALL_LOGGING_ENABLED = env.bool("METHOD_CALL_LOGGING_ENABLED", default=True)

log = logging.getLogger(__name__)

_MAX_BODY_LENGTH = 1024
_ERROR_MESSAGE = "{code} {type} Error for url: {method} {url}\nResponse: {text}"


class ApiWrapper(ABC):
    """Класс-обретка для работы с API"""

    def __init__(self, base_url: str, path: str = None, session: Session = None):
        self._session: Session = session or new_session()
        self._base_url: str = base_url
        if path:
            self._base_url: str = self._build_url(path)

    def _build_url(self, endpoint: str = None) -> str:
        """
        Важно обращать внимание на наличие /, для более ожидаемого поведения всегда добавляем / в конце базового пути.
        >>> urljoin('https://example.com/path1/path2', 'path3/path4')
        'https://example.com/path1/path3/path4'
        >>> urljoin('https://example.com/path1/path2/', 'path3/path4')
        'https://example.com/path1/path2/path3/path4'
        >>> urljoin('https://example.com/path1/path2/', '/path3/path4')
        'https://example.com/path3/path4'
        >>> urljoin('https://example.com/path1/path2//', 'path3/path4')
        'https://example.com/path1/path2/path3/path4'
        """
        if not endpoint:
            return self.base_url
        return urljoin(self.base_url + "/", endpoint)

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return "self[%s]" % self.__class__.__name__

    @property
    def session(self) -> Session:
        return self._session

    @property
    def base_url(self) -> str:
        return self._base_url


def new_session() -> Session:
    session = Session()
    session.verify = False
    return session


def soup(html_content: str) -> BeautifulSoup:
    return BeautifulSoup(html_content, "html.parser")


class ServerHttpError(HTTPError):
    pass


class ClientHttpError(HTTPError):
    pass


class WrongHttpStatusError(HTTPError, AssertionError):
    pass


def body_to_str(response: Response) -> str:
    return response.text[:_MAX_BODY_LENGTH].strip()


def assert_http_status(response: Response, expected: list = []) -> Response:
    error_type = None

    if expected and response.status_code in expected:
        pass
    elif expected and response.status_code not in expected:
        error_type = "Wrong Status Code"
        err_cls = WrongHttpStatusError
    elif 400 <= response.status_code < 500:
        error_type = "Client"
        err_cls = ClientHttpError
    elif 500 <= response.status_code < 600:
        error_type = "Server"
        err_cls = ServerHttpError

    if error_type:
        http_error_msg = _ERROR_MESSAGE.format(
            type=error_type,
            code=response.status_code,
            method=response.request.method,
            url=response.url,
            text=body_to_str(response),
        )
        raise err_cls(http_error_msg, response=response)

    return response


T = TypeVar("T")
P = ParamSpec("P")


def info(func: Callable[P, T]) -> Callable[P, T]:
    return log_call(log.info)(func)


def debug(func: Callable[P, T]) -> Callable[P, T]:
    return log_call(log.debug)(func)


def log_call(log_func: Callable[[Any], None]):
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if METHOD_CALL_LOGGING_ENABLED:
                log_func(f"Вызов {func.__name__}() с {args}, {kwargs}")
            result = None
            try:
                result = func(*args, **kwargs)
            except Exception as ex:
                result = f"Error: {ex}"
                raise ex
            finally:
                if METHOD_CALL_LOGGING_ENABLED:
                    log_func(f"Результат вызова {func.__name__}() = {result}")
            return result

        return wrapper

    return decorator


class AuthSession(ABC):
    _auth_url: str
    __session: Session
    __username: str

    def __init__(self, auth_url: str):
        self._auth_url: str = auth_url

    def open(self, username: str, password: str):
        log.info(f"Сессия: {self.__class__.__name__}. Пользователь: {username}")
        self.__session = new_session()
        self.__username = username

        login_page_html_content = self._get_login_page_content()
        self._login(login_page_html_content, username, password)

        log.debug(f"Пользователь: {username}. Авторизация прошла успешно")
        log.debug(f"Куки сессии: {self.session.cookies}")
        return self

    def _get_login_page_content(self) -> str:
        """Получает страницу авторизации с отрисованными формами авторизации/токенами + для получения промежуточных кук"""
        headers = {"Accept": "text/html"}
        response = self.session.get(self._auth_url, headers=headers)
        assert_http_status(response)

        return response.text

    @abstractmethod
    def _login(self, login_page_html_content: str, username: str, password: str):
        pass

    def domain_cookies(self, url) -> tuple[str, list]:
        domain = urlparse(url).netloc
        if self.session is not None:
            return domain, [
                cookie for cookie in self.session.cookies if cookie.domain == domain
            ]
        return domain, []

    @property
    def session(self) -> Session | None:
        return self.__session

    @property
    def username(self) -> str | None:
        return self.__username

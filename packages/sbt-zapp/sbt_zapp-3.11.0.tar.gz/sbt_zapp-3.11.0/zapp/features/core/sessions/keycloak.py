import logging

import requests

from zapp.features.core.sessions import AuthSession, assert_http_status, soup

log = logging.getLogger(__name__)


class KeyCloakFrontSession(AuthSession):
    """Сессия для работы с API UI при авторизации через KeyCloak"""

    def _parse_login_url(self, login_page_html_content: str) -> str:
        bs = soup(login_page_html_content)
        kc_login_form = bs.select_one("#kc-form-login")
        if not kc_login_form:
            raise AttributeError(
                "Форма логина KeyCloak должна присутствовать на странице"
            )
        return kc_login_form.attrs["action"]

    def _login(
        self, login_page_html_content: str, username: str, password: str
    ) -> requests.Session:
        login_url = self._parse_login_url(login_page_html_content)
        login_data = {
            "username": username,
            "password": password,
            "credentialId": "",
        }
        login_response = self.session.post(login_url, data=login_data)
        assert_http_status(login_response)

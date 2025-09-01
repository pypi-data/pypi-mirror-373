from behave import step

from zapp.features.core.sessions.keycloak import KeyCloakFrontSession
from zapp.features.core.utils import get_from_variables


@step(
    'API: Я авторизовался через KeyCloak используя УЗ "{username}" и пароль "{password}"'
)
def login_in_keycloak_by_creds(context, username, password):
    context.keycloak_session = KeyCloakFrontSession(context.host).open(
        username, password
    )


@step(
    'API: Я авторизовался через KeyCloak используя значения переменных для УЗ "{username_var}" и пароля "{password_var}"'
)
def login_in_keycloak_by_cred_vars(context, username_var, password_var):
    context.keycloak_session = KeyCloakFrontSession(context.host).open(
        get_from_variables(username_var), get_from_variables(password_var)
    )

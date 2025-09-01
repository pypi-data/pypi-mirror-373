import re
import zoneinfo

from envparse import env

TIME_ZONE = zoneinfo.ZoneInfo(env.str("TIME_ZONE", default="Europe/Moscow"))
DATE_FORMAT = env.str("DATE_FORMAT", default="%Y.%m.%d %X")

ZEPHYR_USE = env.bool("ZEPHYR_USE", default=env.bool("USE_ZEPHYR", default=False))

ZEPHYR_RELEASE_REGEX = env.str("ZEPHYR_RELEASE_REGEX", default="([0-9.]*)")

JIRA_HOST = env.str("JIRA_HOST", default="https://sberworks.ru/jira")
JIRA_USER = env.str("JIRA_USER", default=None)
JIRA_PASSWORD = env.str("JIRA_PASSWORD", default=None)
JIRA_TOKEN = env.str("JIRA_TOKEN", default=None)

ZEPHYR_TEST_RUN = env.str("ZEPHYR_TEST_RUN", default=None)

ZEPHYR_TEST_CASE_SEARCH_TYPE = env.str(
    "ZEPHYR_TEST_CASE_SEARCH_TYPE", default="CUSTOM_FIELD"
)

ZEPHYR_TEST_CASE_FOLDER = env.str("ZEPHYR_TEST_CASE_FOLDER", default=None)
ZEPHYR_TEST_CASE_CUSTOM_FIELD_NAME = env.str(
    "ZEPHYR_TEST_CASE_CUSTOM_FIELD_NAME", default="ZephyrLabel"
)

ZEPHYR_TEST_CASE_RELEASE_UPDATE = env.bool(
    "ZEPHYR_TEST_CASE_RELEASE_UPDATE", default=False
)

ZEPHYR_RELEASE_CHECK_TYPE = env.str("ZEPHYR_RELEASE_CHECK_TYPE", default="CUSTOM_FIELD")
ZEPHYR_RELEASE_CUSTOM_FIELD_NAME = env.str(
    "ZEPHYR_RELEASE_CUSTOM_FIELD_NAME", default="Релиз"
)
ZEPHYR_RELEASE_VERSION = env.str("ZEPHYR_RELEASE_VERSION", default=None)

if ZEPHYR_USE:
    if JIRA_TOKEN is None and (JIRA_USER is None or not re.match(r"^[A-Za-z0-9_]*$", JIRA_USER)):
        raise Exception(
            "Параметр JIRA_USER должен содержать только строку логина (не email, без спецсимволов)"
        )

    if not re.match(r"^(CUSTOM_FIELD|KEY)$", ZEPHYR_TEST_CASE_SEARCH_TYPE):
        raise ValueError(
            "Параметр ZEPHYR_TEST_CASE_SEARCH_TYPE может принимать значения: CUSTOM_FIELD, KEY"
        )

    if ZEPHYR_TEST_CASE_RELEASE_UPDATE:
        if not re.match(r"^(CUSTOM_FIELD|LABEL)$", ZEPHYR_RELEASE_CHECK_TYPE):
            raise ValueError(
                "Параметр ZEPHYR_RELEASE_CHECK_TYPE может принимать значения: CUSTOM_FIELD, LABEL"
            )

        if not ZEPHYR_RELEASE_VERSION:
            raise ValueError(
                "Параметр ZEPHYR_RELEASE_VERSION должен содержать версию релиза"
            )

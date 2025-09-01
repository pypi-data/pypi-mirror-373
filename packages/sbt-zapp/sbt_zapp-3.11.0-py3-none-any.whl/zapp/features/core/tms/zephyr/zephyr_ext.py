"""Модуль с Zephyr Server API, который используется при работе через UI (расширяет возможности Server API)"""

import logging
import re
from abc import ABC, abstractmethod

from pyrate_limiter import Limiter, Rate, Duration
from zephyr import ZephyrScale
from zephyr.scale.server.endpoints.paths import ServerPaths
from zephyr.scale.server.server_api import ServerApiWrapper

from zapp.features.core.tms.zephyr import (
    ZEPHYR_RELEASE_VERSION,
    ZEPHYR_RELEASE_CUSTOM_FIELD_NAME,
    ZEPHYR_RELEASE_CHECK_TYPE,
    ZEPHYR_RELEASE_REGEX,
    ZEPHYR_TEST_CASE_RELEASE_UPDATE,
    ZEPHYR_USE,
)

log = logging.getLogger("zephyr_ext")


if ZEPHYR_USE and ZEPHYR_TEST_CASE_RELEASE_UPDATE:
    rate_limiter = Limiter(
        Rate(1, Duration.SECOND * 1), raise_when_fail=False, max_delay=1500
    )


class TestCaseReleaseType(ABC):
    """Класс, задающий способ определения релиза в Test Case"""

    @abstractmethod
    def is_release_match(self, test_case_fields: dict):
        pass

    @abstractmethod
    def update_release_version(self, test_case_fields: dict):
        pass


class CustomFieldReleaseType(TestCaseReleaseType):
    __custom_field_option: dict

    def is_release_match(self, test_case_fields: dict) -> bool:
        for custom_field_value in test_case_fields["customFieldValues"]:
            custom_field = custom_field_value["customField"]
            if custom_field["name"] == ZEPHYR_RELEASE_CUSTOM_FIELD_NAME:
                self.__custom_field_option = self.__get_custom_field_option(
                    custom_field, ZEPHYR_RELEASE_VERSION
                )
                return (
                    self.__custom_field_option["id"] == custom_field_value["intValue"]
                )
        raise ValueError(f"Zephyr: Не найдено поле {ZEPHYR_RELEASE_CUSTOM_FIELD_NAME}")

    def update_release_version(self, test_case_fields: dict) -> dict:
        for custom_field_value in test_case_fields["customFieldValues"]:
            custom_field = custom_field_value["customField"]
            if custom_field["name"] == ZEPHYR_RELEASE_CUSTOM_FIELD_NAME:
                custom_field_value["intValue"] = self.__custom_field_option["id"]
                return test_case_fields
        return test_case_fields

    @staticmethod
    def __get_custom_field_option(custom_field: dict, option_name: str) -> dict:
        for option in custom_field["options"]:
            if option["name"] == option_name:
                return option
        raise ValueError(
            f'Zephyr: Не найдено значение "{option_name}" в поле {custom_field["name"]}'
        )


class LabelReleaseType(TestCaseReleaseType):

    def is_release_match(self, test_case_fields: dict) -> bool:
        return ZEPHYR_RELEASE_VERSION in self.__fetch_labels(test_case_fields)

    def update_release_version(self, test_case_fields: dict) -> dict:
        labels = [
            label
            for label in self.__fetch_labels(test_case_fields)
            if not re.match(rf"^{ZEPHYR_RELEASE_REGEX}$", label)
        ]
        labels.append(ZEPHYR_RELEASE_VERSION)
        test_case_fields["labels"] = labels
        return test_case_fields

    def __fetch_labels(self, test_case_fields) -> list:
        return test_case_fields.get("labels", [])


class ZephyrFrontApi:
    __api: ServerApiWrapper
    __release_type: TestCaseReleaseType = {
        "CUSTOM_FIELD": CustomFieldReleaseType,
        "LABEL": LabelReleaseType,
    }[ZEPHYR_RELEASE_CHECK_TYPE]()

    def __init__(self, jira_url: str, auth: dict) -> None:
        self.__api = ZephyrScale.server_api(
            f"{jira_url}/rest/tests/1.0/", session_attrs={"verify": False}, **auth
        ).api

    def create_new_version_if_needed(self, key: str):
        last_version = sorted(
            self.get_test_case_versions(key), key=lambda x: x["majorVersion"]
        )[-1]
        log.info(f"Последняя версия {key}: {last_version}")
        test_case_fields = self.get_test_case_fields_values(
            last_version["id"], ["labels", "customFieldValues"]
        )
        if self.__release_type.is_release_match(test_case_fields):
            log.info(
                f'Версия {key} ({last_version["majorVersion"]}.0) '
                f"уже содержит релиз {ZEPHYR_RELEASE_VERSION}. Создание новой версии не требуется"
            )
        else:
            log.info(
                f'Версия {key} ({last_version["majorVersion"]}.0) '
                f"не содержит релиз {ZEPHYR_RELEASE_VERSION}. Будет создана новая версия"
            )
            new_version_id = self.create_new_version(last_version["id"])
            self.update_release_version(new_version_id)

    def update_release_version(self, version_id: str):
        new_test_case_fields = self.get_test_case_fields_values(
            version_id, ["labels", "projectId", "id", "customFieldValues"]
        )
        updated_fields = self.__release_type.update_release_version(
            new_test_case_fields
        )
        self.update_test_case(version_id, updated_fields)

    def set_release_version(self, key: str):
        last_version_id = sorted(
            self.get_test_case_versions(key), key=lambda x: x["majorVersion"]
        )[-1]["id"]
        self.update_release_version(last_version_id)

    def get_test_case_versions(self, key: str) -> list[dict]:
        if rate_limiter:
            rate_limiter.try_acquire("get_test_case_versions")
        return self.__api.test_cases.get_test_case(
            f"{key}/allVersions?fields=id,majorVersion"
        )

    def get_test_case_fields_values(self, version_id: str, fields: list[str]) -> dict:
        if rate_limiter:
            rate_limiter.try_acquire("get_test_case")
        return self.__api.test_cases.get_test_case(
            f'{version_id}?fields={",".join(fields)}'
        )

    def update_test_case(self, identifier: str, fields: dict) -> None:
        if rate_limiter:
            rate_limiter.try_acquire("update_test_case")
        self.__api.test_cases.update_test_case(identifier, **fields)

    # Передается последняя версия
    def create_new_version(self, identifier: str) -> str:
        if rate_limiter:
            rate_limiter.try_acquire("create_new_version")
        return self.__api.session.post(
            f"{ServerPaths.CASE_KEY.format(identifier)}/newversion",
            json={"id": identifier},
        )["id"]

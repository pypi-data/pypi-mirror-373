import logging
import traceback
from typing import Optional
from test_culture_client.client import TestCultureClient
from test_culture_client.models.tql import TqlRequest

from behave.model import Scenario, ScenarioOutline

from zapp.features.core.sessions.keycloak import KeyCloakFrontSession
from zapp.features.core.tms.test_culture import (
    TEST_CULTURE_DEFAULT_FOLDER_CODE,
    TEST_CULTURE_INTEGRATION_ENABLED,
    TEST_CULTURE_UPDATE_TEST_CASE,
    TEST_CULTURE_PASSWORD,
    TEST_CULTURE_SPACE,
    TEST_CULTURE_TOKEN,
    TEST_CULTURE_URL,
    TEST_CULTURE_USERNAME,
    TEST_CULTURE_ATTRIBUTE_PRODUCT_CODE,
    TEST_CULTURE_ATTRIBUTE_COMPONENT_CODE,
)
from zapp.features.core.tms.test_culture.context import TestCaseContext, TestDataContext
from zapp.features.core.tms.test_culture.utils import (
    TQL_LABEL_TEMPLATE,
    TQL_UNIT_TEMPLATE,
    TQL_OLD_JIRA_KEY_TEMPLATE,
    ScenarioTag,
    AC21_API_COOKIES,
    NoLabelProvidedException,
    TooManyTestCasesException,
)

log = logging.getLogger(__name__)


class TestCultureReporter:
    client: TestCultureClient
    space: str
    default_folder: str
    already_reported: list[str]  # Для корректной работы с ScenarioOutline
    update_test_case: bool
    product_code: str
    component_code: str

    def __init__(
        self,
        client: TestCultureClient,
        space: str,
        default_folder: str,
        update_test_case: bool,
        product_code: str,
        component_code: str,
    ):
        self.client = client
        self.space = space
        self.default_folder = default_folder
        self.already_reported = []
        self.update_test_case = update_test_case
        self.product_code = product_code
        self.component_code = component_code

        log.info("Включена интеграция с TestCulture")
        log.info(f"Обновлять тест-кейсы: {update_test_case}")

    def before_scenario(self, context, scenario):
        if not self.update_test_case:
            return

        try:
            tms_code, label = self._extract_attributes(scenario)

            if not tms_code and not label:
                log.error(
                    f"Сценарий '{scenario.name}' не содержит теги "
                    f"'{ScenarioTag.TMS.value}' или '{ScenarioTag.LABEL.value}'"
                )
                return

            code, folder = self._find(tms_code, label)

            if code in self.already_reported:
                self._log_test_case_action(code, "Актуализирован ранее")
                return

            if code:
                code = self._update(context, code, folder)
            elif label:
                code = self._create(context, label)
            else:
                raise NoLabelProvidedException(
                    f"Не найден ТК по коду {tms_code} и "
                    f"не задана метка для создания нового '@{ScenarioTag.LABEL.value}:'"
                )

            self.already_reported.append(code)
        except Exception as ex:
            log.error(
                f"Произошла ошибка при актуализации сценария '{scenario.name}':\n{ex}"
            )
            traceback.print_exception(ex)

    def _extract_attributes(
        self, scenario: Scenario | ScenarioOutline
    ) -> tuple[str, str]:
        """Поиск/извлечение атрибутов сценария: кода, метки. Данные атрибуты могут отсутствовать"""
        tags = scenario.effective_tags

        tms_code = ScenarioTag.TMS.find(tags)
        label = ScenarioTag.LABEL.find(tags)

        return tms_code, label

    def _find(self, tms_code: str, label: str) -> tuple[Optional[str], Optional[str]]:
        """Поиск ТК по коду юнита и по выставленной метке (при наличии). В случае успеха возвращает code юнита и его папку"""
        log.info(f"Атрибуты ТК для поиска: код '{tms_code}' и метка '{label}'")

        code = None
        folder = None
        if tms_code:
            code, folder = self._find_by_tql(
                TQL_UNIT_TEMPLATE.format(code=tms_code, space=self.space)
            )
            if not code:
                # Поиск ТК по номеру до миграции
                code, folder = self._find_by_tql(
                    TQL_OLD_JIRA_KEY_TEMPLATE.format(code=tms_code, space=self.space)
                )

        if not code and label:
            code, folder = self._find_by_tql(
                TQL_LABEL_TEMPLATE.format(label=label, space=self.space)
            )
        return code, folder

    def _find_by_tql(self, tql: str) -> tuple[Optional[str], Optional[str]]:
        """Поиск по TQL-запросу. Дополнительно запрашивается атрибут Папка"""
        search_results = self.client.units.find_by_tql(
            TqlRequest(query=tql, attributes=["folder"])
        )
        count = search_results["totalElements"]

        if count > 1:
            raise TooManyTestCasesException(
                f"Найдено более одного элемента по запросу: {tql}"
            )

        if count == 1:
            entry = search_results["content"][0]
            code = entry["unit"]["code"]
            folder = entry["attributes"][0]["value"]["code"]

            log.info(f"Найден ТК {code} по TQL: {tql}")
            return code, folder

        return None, None

    def _create(self, context, label: str) -> str:
        test_case_context = TestCaseContext.parse(context)
        test_case_request = test_case_context.to_create_request()
        test_case_request.space = self.space
        test_case_request.attributes.label = [label]
        test_case_request.attributes.folder = self.default_folder
        test_case_request.attributes.product_code = self.product_code
        test_case_request.attributes.component_code = self.component_code

        code = self.client.test_cases.create(test_case_request)["id"]
        self._log_test_case_action(code, "Создан")

        self._update_test_data(code, test_case_context.test_data)
        return code

    def _update(self, context, code: str, folder: str) -> str:
        test_case_context = TestCaseContext.parse(context)
        test_case_request = test_case_context.to_update_request()
        test_case_request.attributes.folder = folder
        test_case_request.attributes.product_code = self.product_code
        test_case_request.attributes.component_code = self.component_code

        # Обновление только выставленных полей без сброса оставшихся
        only_updated_fields = test_case_request.model_dump(exclude_unset=True)
        code = self.client.test_cases.update(code, only_updated_fields)["id"]
        self._log_test_case_action(code, "Обновлен")

        self._update_test_data(code, test_case_context.test_data)
        return code

    def _update_test_data(self, code: str, test_data_context: TestDataContext):
        if test_data_context is not None:
            self.client.test_cases.update_test_data(
                code, test_data_context.to_request()
            )
            self._log_test_case_action(code, "Обновлены тестовые данные")

    def _log_test_case_action(self, code: str, action: str):
        log.info(f"ТК {code}: {action}")


class StubTestCultureReporter:
    def __init__(self):
        log.info("Отключена интеграция с TestCulture")

    def before_scenario(self, context, scenario):
        pass


def _init_test_culture_reporter():
    try:
        ow_session_cookies = None
        if not TEST_CULTURE_TOKEN:
            ow_session_cookies = (
                KeyCloakFrontSession(TEST_CULTURE_URL)
                .open(TEST_CULTURE_USERNAME, TEST_CULTURE_PASSWORD)
                .session.cookies
            )
        else:
            ow_session_cookies = AC21_API_COOKIES

        client = TestCultureClient(
            url=TEST_CULTURE_URL,
            token=TEST_CULTURE_TOKEN,
            cookies=ow_session_cookies,
            verify=False,
        )
        return TestCultureReporter(
            client,
            space=TEST_CULTURE_SPACE,
            default_folder=TEST_CULTURE_DEFAULT_FOLDER_CODE,
            update_test_case=TEST_CULTURE_UPDATE_TEST_CASE,
            product_code=TEST_CULTURE_ATTRIBUTE_PRODUCT_CODE,
            component_code=TEST_CULTURE_ATTRIBUTE_COMPONENT_CODE,
        )
    except Exception as ex:
        log.error("Не удалось создать интеграцию с TestCulture")
        traceback.print_exception(ex)
        return StubTestCultureReporter()


test_culture_reporter = (
    _init_test_culture_reporter()
    if TEST_CULTURE_INTEGRATION_ENABLED
    else StubTestCultureReporter()
)

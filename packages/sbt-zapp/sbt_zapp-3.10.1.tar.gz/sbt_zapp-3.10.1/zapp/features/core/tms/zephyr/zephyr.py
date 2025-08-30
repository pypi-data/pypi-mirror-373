import logging
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from operator import itemgetter
from pydoc import html
import uuid

from behave.model import Table, Row
from requests import HTTPError
from zephyr import ZephyrScale

from zapp.features.core.settings import FILE_ENCODING, PROJECT_KEY, ENV
from zapp.features.core.tms.zephyr import (
    TIME_ZONE,
    DATE_FORMAT,
    ZEPHYR_TEST_RUN,
    JIRA_TOKEN,
    JIRA_PASSWORD,
    JIRA_USER,
    ZEPHYR_USE,
    JIRA_HOST,
    ZEPHYR_TEST_CASE_RELEASE_UPDATE,
    ZEPHYR_TEST_CASE_CUSTOM_FIELD_NAME,
    ZEPHYR_TEST_CASE_SEARCH_TYPE,
    ZEPHYR_TEST_CASE_FOLDER,
)
from zapp.features.core.tms.zephyr.allure_integration import (
    AllureTag,
    get_tms_key,
    get_issue_links,
)
from zapp.features.core.tms.zephyr.zephyr_ext import ZephyrFrontApi

log = logging.getLogger("zephyr")


class ZephyrStatus(Enum):
    NOT_EXECUTED = "Not Executed"
    PASS = "Pass"
    FAIL = "Fail"


class TestCaseDefinitionType(ABC):

    @abstractmethod
    def prepare(self, zapi):
        pass

    @abstractmethod
    def get_behave_tag_template(self):
        pass

    @abstractmethod
    def get_behave_tag_value(self, tags):
        pass

    @abstractmethod
    def get_test_case(self, zapi, tag_value):
        pass


class KeyTestCaseDefinitionType(TestCaseDefinitionType):

    def prepare(self, zapi):
        pass

    def get_behave_tag_template(self):
        return f"{AllureTag.TMS.value}:%s"

    def get_behave_tag_value(self, tags):
        return get_tms_key(tags)

    def get_test_case(self, zapi, tag_value):
        try:
            return zapi.api.test_cases.get_test_case(tag_value)
        except HTTPError as e:
            raise_not_found_if_needed(e, tag_value)


class CustomFieldTestCaseDefinitionType(TestCaseDefinitionType):

    def prepare(self, zapi):
        zapi.create_custom_field()

    def get_behave_tag_template(self):
        return f"{ZEPHYR_TEST_CASE_CUSTOM_FIELD_NAME}/{PROJECT_KEY}/%s"

    def get_behave_tag_value(self, tags):
        search = self.get_behave_tag_template() % ""
        for tag in tags:
            if search in tag:
                return tag.split("/")[-1]

    def get_test_case(self, zapi, tag_value):
        query = f'projectKey = "{PROJECT_KEY}" AND "{ZEPHYR_TEST_CASE_CUSTOM_FIELD_NAME}" = "{tag_value}"'
        log.info(f"Поиск ТК по запросу: {query}")
        test_cases = zapi.api.test_cases.search_cases(query, fields="key")

        if test_cases:
            return test_cases[0]
        else:
            log.info(f"ТК не найден. Будет создан новый")
            attributes = {
                "name": f"Создан с помощью ZAPP для {tag_value}",
                "customFields": {ZEPHYR_TEST_CASE_CUSTOM_FIELD_NAME: tag_value},
            }
            test_case = zapi.api.test_cases.create_test_case(PROJECT_KEY, **attributes)
            key = test_case["key"]
            log.info(f"Создан новый ТК: {key}")
            if ZEPHYR_TEST_CASE_RELEASE_UPDATE:
                zapi.front_api.set_release_version(key)
            return test_case


def to_zephyr_str(step: str) -> str:
    step = step.replace("{", "[").replace("}", "]").replace("<", "{").replace(">", "}")

    return html.escape(step)


def parameters_to_zephyr_table(data) -> str:
    if data:
        if isinstance(data, Table):
            values = [row_to_html_cells(row) for row in data]
        elif isinstance(data, Row):
            values = [row_to_html_cells(data)]
        else:
            raise ValueError(f"Неизвестный тип данных {type(data)}")
        headers = "\n".join([f"<th>{header}</th>" for header in data.headings])
        return f'<table><tr>{headers}</tr><tr>{"</tr><tr>".join(values)}</tr></table>'
    else:
        return ""


def multiline_text_to_zephyr_step(data) -> str:
    if data:
        return f"<table><td><pre>{to_zephyr_str(data)}</pre></td></table>"
    else:
        return ""


def row_to_html_cells(row) -> str:
    return "\n".join([f"<td>{to_zephyr_str(value)}</td>" for value in row.cells])


class NoSuchTestCase(Exception):
    pass


def raise_not_found_if_needed(exception, key):
    if "Error 404" in str(exception):
        raise NoSuchTestCase(f"Test case with key {key} not found", exception)
    else:
        raise exception


class ZephyrStep:
    def __init__(self):
        self.when = ""
        self.then = ""
        self.last_line = None
        self.comment = None
        self.status = ZephyrStatus.NOT_EXECUTED.value

    def add_when(self, message, line):
        self.when += f"{message}<br/>"
        self.last_line = line

    def add_then(self, message, line):
        self.then += f"{message}<br/>"
        self.last_line = line

    @classmethod
    def build_steps_from_scenario(cls, scenario):
        steps = []
        current_step = ZephyrStep()
        was_last_scenario_step_then = False

        for scenario_step in scenario.steps:
            # message = f"<b>{scenario_step.keyword}</b> {scenario_step.name}"
            message = (
                to_zephyr_str(scenario_step.name)
                + parameters_to_zephyr_table(scenario_step.table)
                + multiline_text_to_zephyr_step(scenario_step.text)
            )

            if scenario_step.step_type == "when":
                if was_last_scenario_step_then:
                    was_last_scenario_step_then = False
                    steps.append(current_step)
                    current_step = ZephyrStep()
                current_step.add_when(message, scenario_step.line)

            elif scenario_step.step_type == "then":
                current_step.add_then(message, scenario_step.line)
                was_last_scenario_step_then = True

            else:
                log.error(
                    f"Шаг с типом {scenario_step.step_type} в сценарии не поддерживается, пропускаю"
                )

        steps.append(current_step)
        return steps


class ZephyrTestCase:
    def __init__(self, key, steps, parameter):
        self.key = key
        self.steps = steps
        self.status = ZephyrStatus.NOT_EXECUTED.value
        self.parameter = parameter
        self.comment = ""
        self.screenshot_file = None
        self.trace_file = None

    def failed(self, exception_message):
        self.status = ZephyrStatus.FAIL.value
        self.comment = html.escape(exception_message)

    def passed(self):
        self.status = ZephyrStatus.PASS.value

    def pass_step_line(self, step_line):
        for i, step in enumerate(self.steps):
            if step.last_line == step_line:
                step.status = ZephyrStatus.PASS.value
                if i == len(self.steps) - 1:
                    self.passed()
                break

    def fail_step_line(self, exception_message):
        for step in self.steps:
            if step.status == ZephyrStatus.NOT_EXECUTED.value:
                step.status = ZephyrStatus.FAIL.value
                step.comment = exception_message
                self.failed("")
                break


class ZAPI:
    test_case_definition: TestCaseDefinitionType = {
        "CUSTOM_FIELD": CustomFieldTestCaseDefinitionType,
        "KEY": KeyTestCaseDefinitionType,
    }[ZEPHYR_TEST_CASE_SEARCH_TYPE]()

    def __init__(self, jira_url: str, auth: dict) -> None:
        self.api = ZephyrScale.server_api(
            f"{jira_url}/rest/atm/1.0/", session_attrs={"verify": False}, **auth
        ).api
        self.front_api = ZephyrFrontApi(jira_url, auth)

    def get_test_case(self, key) -> dict:
        try:
            log.info(f"Получение ТК по ключу: {key}")
            return self.api.test_cases.get_test_case(key)
        except HTTPError as e:
            raise_not_found_if_needed(e, key)

    def create_custom_field(self):
        try:
            log.debug(f"Создание custom field: {ZEPHYR_TEST_CASE_CUSTOM_FIELD_NAME}")
            self.api.custom_field.create_custom_field(
                PROJECT_KEY,
                ZEPHYR_TEST_CASE_CUSTOM_FIELD_NAME,
                "SINGLE_LINE_TEXT",
                "TEST_CASE",
            )
        except HTTPError as e:
            log.debug(e)
            if not ("Custom field name is duplicated" in str(e)):
                raise e

    def get_scenario_by_tms_tag(self, context, tag_value):
        if context.active_outline:
            for scenario in context.feature.scenarios:
                if (
                    self.test_case_definition.get_behave_tag_template() % tag_value
                    in scenario.tags
                ):
                    return scenario
        else:
            return context.scenario

    def update_test_case(self, context, tag_value, precondition, zephyr_steps) -> str:
        test_case = self.test_case_definition.get_test_case(self, tag_value)
        key = test_case["key"]

        if ZEPHYR_TEST_CASE_RELEASE_UPDATE:
            self.front_api.create_new_version_if_needed(key)

        scenario = self.get_scenario_by_tms_tag(context, tag_value)

        issue_links = set(test_case.get("issueLinks", []))
        issue_links.update(get_issue_links(scenario.tags))

        attributes = {
            "name": scenario.name,
            "precondition": precondition,
            "testScript": {
                "type": "STEP_BY_STEP",
                "steps": list(
                    map(
                        lambda step: {
                            "description": step.when,
                            "expectedResult": step.then,
                        },
                        zephyr_steps,
                    )
                ),
            },
            "issueLinks": list(issue_links),
        }
        if ZEPHYR_TEST_CASE_FOLDER:
            log.info(f"ТК будет расположен по пути: {ZEPHYR_TEST_CASE_FOLDER}")
            attributes["folder"] = ZEPHYR_TEST_CASE_FOLDER

        if scenario.type == "scenario_outline":
            entries = []
            for row in scenario.examples[0].table:
                entry = {}
                for header in row.headings:
                    entry[header] = row[header]
                entries.append(entry)
            attributes["paramType"] = "TEST_DATA"
            attributes["parameters"] = {
                "variables": [
                    {"name": header, "type": "FREE_TEXT"}
                    for header in scenario.examples[0].table.headings
                ],
                "entries": entries,
            }
        try:
            log.info("Обновление ТК в Zephyr...")
            self.api.test_cases.update_test_case(key, **attributes)
            return key
        except HTTPError as e:
            raise_not_found_if_needed(e, key)

    def create_test_run(self) -> dict:
        log.info("Создание тестового цикла в Zephyr...")
        attributes = {
            "name": f"[{ENV}][ZAPP] Регресс в {datetime.now(TIME_ZONE).strftime(DATE_FORMAT)}",
            "description": "Тестовый цикл был создан автоматически с помощью ZAPP",
        }
        test_run = self.api.test_runs.create_test_run(PROJECT_KEY, **attributes)
        log.info(f'Тестовый цикл был создан: {test_run["key"]}')
        return test_run

    def build_test_result(self, test_case: ZephyrTestCase):
        attributes = ZAPI.__build_test_result_attributes(test_case)
        test_result = self.api.test_results.create_test_result(
            PROJECT_KEY, test_case.key, **attributes
        )
        self.__upload_test_result_attachments(test_result["id"], test_case)

    def build_test_result_for_run(
        self, test_run_key, test_case: ZephyrTestCase, create_new_test_result: bool
    ):
        attributes = ZAPI.__build_test_result_attributes(test_case)

        if create_new_test_result:
            test_result = self.api.test_runs.create_test_result(
                test_run_key, test_case.key, **attributes
            )
        else:
            desired_result = self.__get_last_run_result(test_run_key, test_case.key)
            if desired_result["status"] == ZephyrStatus.FAIL.value:
                attributes["status"] = ZephyrStatus.FAIL.value
            test_result = self.api.test_runs.update_test_result(
                test_run_key, test_case.key, **attributes
            )
        self.__upload_test_result_attachments(test_result["id"], test_case)

    def __get_last_run_result(
        self, test_run_key: str, test_case_key: str
    ) -> dict | None:
        test_results = self.api.test_runs.get_test_results(test_run_key)
        desired_results = [
            result
            for result in test_results
            if result["testCaseKey"] == test_case_key and result["automated"]
        ]
        if desired_results:
            return sorted(desired_results, key=itemgetter("executionDate"))[-1]

    def __upload_test_result_attachments(
        self, test_result_id, test_case: ZephyrTestCase
    ):
        if test_case.trace_file is not None:
            self.api.test_results.create_attachment(
                test_result_id, test_case.trace_file
            )
        if test_case.screenshot_file is not None:
            self.api.test_results.create_attachment(
                test_result_id, test_case.screenshot_file
            )

    @staticmethod
    def __build_test_result_attributes(test_case: ZephyrTestCase):
        parameter_string = f"{test_case.parameter}\n" if test_case.parameter else ""
        results = [
            {
                "status": step.status,
                "comment": f'{parameter_string}{step.comment if step.comment else ""}',
                "index": i,
            }
            for i, step in enumerate(test_case.steps)
        ]
        return {
            "status": test_case.status,
            "comment": test_case.comment,
            "scriptResults": results,
        }


class ZephyrSync:
    api: ZAPI = None
    already_in_test_run: list = []

    @staticmethod
    def before_all(context, _):
        ZephyrSync.api = ZAPI(JIRA_HOST, ZephyrSync.__build_auth())

        ZephyrSync.api.test_case_definition.prepare(ZephyrSync.api)

        if ZEPHYR_TEST_RUN:
            if ZEPHYR_TEST_RUN.lower() == "new":
                context.zephyr_test_run_key = ZephyrSync.api.create_test_run()["key"]
            else:
                context.zephyr_test_run_key = ZEPHYR_TEST_RUN

    @staticmethod
    def before_scenario(context, current_scenario):
        tag_value = ZephyrSync.api.test_case_definition.get_behave_tag_value(
            context.tags
        )
        if tag_value is None:
            log.error(
                f"У теста '{context.scenario.name}' нет тега @{ZephyrSync.api.test_case_definition.get_behave_tag_template()},"
                f"интеграция с Zephyr Scale пропускается"
            )
            return

        scenario = ZephyrSync.api.get_scenario_by_tms_tag(context, tag_value)
        key = ZephyrSync.api.update_test_case(
            context,
            tag_value,
            ZephyrSync.__build_preconditions(context.feature),
            ZephyrStep.build_steps_from_scenario(scenario),
        )

        context.zephyr_test_case = ZephyrTestCase(
            key,
            ZephyrStep.build_steps_from_scenario(current_scenario),
            parameters_to_zephyr_table(context.active_outline),
        )

    @staticmethod
    def before_step(context, step):
        pass

    @staticmethod
    def after_step(context, step):
        if hasattr(context, "zephyr_test_case"):
            test_case = context.zephyr_test_case

            if step.filename == context.scenario.filename:
                if step.has_failed():
                    test_case.fail_step_line(
                        ZephyrSync.__format_step_error_message(step)
                    )
                    test_case.trace_file = ZephyrSync.__write_trace_to_file(step)
                    if hasattr(context, "browser"):
                        test_case.screenshot_file = (
                            ZephyrSync.__write_screenshot_to_file(context.browser)
                        )
                else:
                    test_case.pass_step_line(step.line)

            elif step.has_failed():
                test_case.failed(ZephyrSync.__format_step_error_message(step))

    @staticmethod
    def after_scenario(context, _):
        if hasattr(context, "zephyr_test_case"):
            test_case = context.zephyr_test_case

            if hasattr(context, "zephyr_test_run_key"):
                ZephyrSync.api.build_test_result_for_run(
                    context.zephyr_test_run_key,
                    test_case,
                    test_case.key not in ZephyrSync.already_in_test_run,
                )
                ZephyrSync.already_in_test_run.append(test_case.key)
            else:
                ZephyrSync.api.build_test_result(test_case)

    @staticmethod
    def after_all(context):
        pass

    @staticmethod
    def __format_step_error_message(step):
        return (
            f"<i>{step.filename}:{step.line}<br/>{step.keyword} {step.name}</i>:<br/>"
            f"<b>{html.escape(str(step.exception.__class__))}</b><pre>{html.escape(str(step.exception))}</pre>"
        )

    @staticmethod
    def __build_preconditions(feature):
        return (
            "<br />".join(map(lambda step: f"{step.name}", feature.background.steps))
            if feature.background
            else ""
        )

    @staticmethod
    def __write_trace_to_file(step):
        with open("traceback.txt", "w", encoding=FILE_ENCODING) as output:
            traceback.print_tb(step.exc_traceback, file=output)
            return "traceback.txt"

    @staticmethod
    def __write_screenshot_to_file(browser):
        return browser.screenshot_as_file(f"screenshot-{str(uuid.UUID())}.png")

    @staticmethod
    def __build_auth():
        if JIRA_TOKEN is not None:
            log.info("Для авторизации в Jira используется JIRA_TOKEN")
            return {"token": JIRA_TOKEN}
        elif JIRA_USER is not None and JIRA_PASSWORD is not None:
            log.info("Для авторизации в Jira используются JIRA_USER и JIRA_PASSWORD")
            return {"username": JIRA_USER, "password": JIRA_PASSWORD}
        elif ZEPHYR_USE:
            raise Exception(
                "Для интеграции с Zephyr Scale требуется задать либо JIRA_TOKEN, "
                "либо JIRA_USER и JIRA_PASSWORD"
            )

import re
from enum import Enum
from requests.cookies import cookiejar_from_dict

from behave.model import Scenario, ScenarioOutline, Table
from behave.runner import Context

from zapp.features.core.tms.test_culture import TEST_CULTURE_DEFAULT_LABEL_NAME

TQL_LABEL_TEMPLATE = 'space = "{space}" AND suit = "test_case" AND label IN ("{label}")'
# TQL_UNIT_TEMPLATE = 'space = "{space}" AND suit = "test_case" AND (unit = "{code}" OR old_jira_key ~ "{code}")'
TQL_UNIT_TEMPLATE = 'space = "{space}" AND suit = "test_case" AND unit = "{code}"'
TQL_OLD_JIRA_KEY_TEMPLATE = (
    'space = "{space}" AND suit = "test_case" AND old_jira_key ~ "{code}"'
)

TAG_SEARCH_PATTERN = r"%s:[^:]+"
FONT_SIZE = 12

AC21_API_COOKIES = cookiejar_from_dict({"api_swtr_as21": "true"})

# Приоритет
allure_priority_mapping = {
    "blocker": "blocker",
    "critical": "critical",
    "normal": "major",
    "minor": "minor",
    "trivial": "trivial",
}

# Вид теста
test_type_mapping = {
    "usability": "usability_type",
    "security": "security_type",
    "integration": "integration_type",
    "e2e": "e2e_type",
    "mt": "mt_type",
    "lt": "lt_type",
    "et": "et_type",
    "other": "other_type",
    None: None,
}

# Уровень теста
test_level_mapping = {
    "ui": "ui_level",
    "api": "api_level",
    "api+ui": "api_ui_level",
    "db": "db_level",
    "config": "config_level",
    "doc": "doc_level",
    "ift": "ift_level",
    "install": "install_level",
    "other": "other_level",
    None: None,
}


class TooManyTestCasesException(Exception):
    pass


class TooManyTagsException(Exception):
    pass


class NoLabelProvidedException(Exception):
    pass


class ScenarioTag(Enum):
    TMS = "allure.link.tms"
    OWNER = "allure.label.owner"
    LABEL = TEST_CULTURE_DEFAULT_LABEL_NAME
    PRODUCT_VERSION = "product_version"  # Версия продукта
    COMPONENT_VERSION = "component_version"  # Версия компонента
    STATUS = "status"  # Статус ТК (В процессе и проч)
    TYPE = "type"  # Вид теста (Е2Е и проч)
    SCOPE = "scope"  # Вид тестирования (Регресс, НФ и проч)
    LEVEL = "level"  # Уровень теста (UI и проч)

    def find(self, tags) -> str | None:
        matches = [
            tag for tag in tags if re.match(TAG_SEARCH_PATTERN % self.value, tag)
        ]
        match = _get_one_match(matches)
        if match:
            return match.split(":")[-1]


def get_scenario_tag_attributes(tags: list[str]) -> dict:
    return {
        "priority": get_priority(tags),
        "owner": get_tag_value(tags, ScenarioTag.OWNER, to_lower=False),
        "test_case_status": get_tag_value(tags, ScenarioTag.STATUS, "relevant"),
        "test_type": test_type_mapping[get_tag_value(tags, ScenarioTag.TYPE, "e2e")],
        "type_of_testing": get_tag_value(tags, ScenarioTag.SCOPE, "regress"),
        "test_level": test_level_mapping[get_tag_value(tags, ScenarioTag.LEVEL)],
        "product_version": get_tag_value(tags, ScenarioTag.PRODUCT_VERSION),
        "component_version": get_tag_value(tags, ScenarioTag.COMPONENT_VERSION),
    }


def get_tag_value(
    tags: list[str], tag: ScenarioTag, default: str = None, to_lower: bool = True
) -> str | None:
    value = tag.find(tags)
    if value and to_lower:
        return value.lower()
    return value or default


def get_priority(tags) -> str:
    matches = [tag for tag in tags if tag in allure_priority_mapping]

    match = _get_one_match(matches) or "normal"  # Значение по умолчанию
    return allure_priority_mapping[match]


def _get_one_match(matches: list[str]) -> str | None:
    if len(matches) > 1:
        raise TooManyTagsException(f"Найдено несколько тегов: {matches}")

    if len(matches) == 1:
        return matches[0]


def get_scenario(context: Context) -> Scenario | ScenarioOutline:
    if context.active_outline:
        tags_to_find = context.scenario.tags
        for scenario in context.feature.scenarios:
            if hasattr(scenario, "scenarios"):
                for examples in scenario.scenarios:
                    if examples.tags == tags_to_find:
                        return scenario
        raise RuntimeError(
            f"Не найден исходный сценарий в feature-файле. Теги для поиска: {tags_to_find}"
        )
    else:
        return context.scenario


def get_column_widths(table: Table) -> list[int]:
    """Подсчет максимальной длины столбца таблицы"""
    rows = [table.headings] + [row.cells for row in table.rows]
    widths = [[len(str(cell)) for cell in row] for row in rows]
    return [max(column) * FONT_SIZE for column in zip(*widths)]

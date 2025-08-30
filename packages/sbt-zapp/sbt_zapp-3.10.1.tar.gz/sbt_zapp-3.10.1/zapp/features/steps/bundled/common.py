import importlib
import logging
from behave import *
from hamcrest import *
from time import sleep

from zapp.features.core.utils import format_delay
from hamcrest import (
    assert_that,
    contains_string,
    empty,
    equal_to,
    matches_regexp,
    not_,
)
from zapp.features.core.utils import variables

log = logging.getLogger(__name__)


@step("Я подождал {} секунд")
@step("Я подождал {} секунды")
@step("Я подождал {} секунду")
def silly_wait(_, value):
    """
    Остановить выполнение теста на указанное количество секунд.
    В Firefox возможно выпадение с ошибкой connection reset by peer при ожидании 5 и больше секунд.
    В фреймворке для всех действий реализовано автоматическое ожидание загрузки элементов.
    Использовать форсированную паузу в большинстве случаев нет необходимости.
    Если тест падает по таймауту, можно в настройках изменить таймаут на значение больше чем 7 секунд по-умолчанию.
    """
    sleep(format_delay(value))


@given("Я установил функцию cleanup {path_to_func}")
@when("Я установил функцию cleanup {path_to_func}")
def set_cleanup(context, path_to_func):
    """
    Устанавливает функцию cleanup, которая будет вызываться вне зависимости от того, провалился ли сценарий или нет.

    Если использовать @given (в блоке Background), cleanup будет вызываться после каждого сценария;
    Если использовать @when (в блоке Scenario), cleanup будет вызываться только после текущего сценария;

    path_to_func - путь до функции (<название_файла_с кастомными шагами_без_.py>.<название_функции_уборки>),
    которая будет вызываться в качестве cleanup.

    Пример: Я установил функцию cleanup zapp_steps.clean_fields
    """
    module_name, func = f"features.steps.{path_to_func}".rsplit(".", 1)
    module = importlib.import_module(module_name)
    try:
        cleanup = getattr(module, func)
    except AttributeError:
        log.error(f"Не найдена {func} в {module}")
        raise

    context.add_cleanup(cleanup, context)
    log.debug(f"CLEANUP: Set. Will be executed after scenario: {func}")


@then('Я убедился что значение переменной "{variable}" непустое')
def assert_variable_value_is_not_empty(context, variable):
    value = variables[variable]
    assert_that(value, not_(empty))


@then('Я убедился что значение переменной "{variable}" пустая строка')
def assert_variable_value_is_empty(context, variable):
    value = variables[variable]
    assert_that(value, empty)


@then('Я убедился что значение переменной "{variable}" равно "{expected}"')
def assert_variable_value_equal_to(context, variable, expected):
    value = variables[variable]
    assert_that(value, equal_to(expected))


@then('Я убедился что значение переменной "{variable}" содержит подстроку "{expected}"')
def assert_variable_value_contains_string(context, variable, expected):
    value = variables[variable]
    assert_that(value, contains_string(expected))


@then(
    'Я убедился что значение переменной "{variable}" удовлетворяет регулярному выражению "{expected}"'
)
def assert_variable_value_matches_regexp(context, variable, expected):
    value = variables[variable]
    assert_that(value, matches_regexp(expected))


@step('Я сохранил результат выражения {expression} в переменную "{variable}"')
def eval_expression_and_store_in_variable(context, expression, variable):
    variables[variable] = eval(expression)

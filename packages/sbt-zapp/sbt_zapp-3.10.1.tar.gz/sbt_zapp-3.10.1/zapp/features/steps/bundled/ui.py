import datetime
import decimal
import logging
import random

import validators
from datetime import timedelta
from behave import then, when, step, given
from hamcrest import assert_that, contains_string, equal_to, less_than, greater_than
from mimesis import Generic
from mimesis.builtins import RussiaSpecProvider
from mimesis.enums import Gender, Locale
from selenium.webdriver.common.keys import Keys
import allure

from zapp.driver import ELEMENT_TIMEOUT, Platform
from zapp.features.core.locators import get_locator as locator
from zapp.features.core.utils import (
    generate_tranzact_number,
    generate_phone_code,
    generate_valid_snils,
    variables,
    totp,
    get_from_variables,
    get_absolute_url,
    format_delay,
)
from zapp.features.core.waits import wait_for

ELEMENT_CHECK_POLLING_INTERVAL = 0.25

log = logging.getLogger(__name__)

generic = Generic(Locale.RU)
RussiaSpecProvider.Meta.name = "ru"
generic.add_provider(RussiaSpecProvider)
gender = Gender.MALE if random.choice(["male", "female"]) == "male" else Gender.FEMALE

ctrl_key = Keys.COMMAND if Platform.get() == Platform.MAC.value else Keys.CONTROL

comparators = {
    "ровно": lambda a, b: a == b,
    "больше": lambda a, b: a > b,
    "не более": lambda a, b: a <= b,
    "меньше": lambda a, b: a < b,
    "не менее": lambda a, b: a >= b,
}


@step('Я установил задержку ожидания загрузки элементов "{delay}" секунд')
@step('Я установил задержку ожидания загрузки элементов "{delay}" секунды')
@step('Я установил задержку ожидания загрузки элементов "{delay}" секунду')
def change_element_timeout(context, delay):
    """Изменить задержку ожидания перед заведомо длительными действиями."""
    if delay:
        context.browser.timeout = timedelta(seconds=format_delay(delay))
        log.info(
            f"Задержка ожидания загрузки элементов: {context.browser.timeout.seconds} сек."
        )


@step("Я вернул задержку ожидания загрузки элементов на изначальную")
def restore_element_timeout(context):
    """Восстановить задержку ожидания на указанную при запуске тестов."""
    context.browser.timeout = ELEMENT_TIMEOUT
    log.info(
        f"Задержка ожидания загрузки элементов: {context.browser.timeout.seconds} сек."
    )


@step("Я установил посимвольный ввод")
@step('Я установил посимвольный ввод с задержкой "{delay}" секунд')
@step('Я установил посимвольный ввод с задержкой "{delay}" секунды')
@step('Я установил посимвольный ввод с задержкой "{delay}" секунду')
def change_send_keys_type(context, delay="0.1"):
    """Изменить ввод на посимвольный с указанной задержкой или по умолчанию - 0,1 сек."""
    context.type_delay = format_delay(delay) * 1000
    log.info(f"Ввод значений: посимвольный с задержкой {context.type_delay} сек.")


@step("Я вернул ввод элементов на изначальный")
def restore_send_keys_type(context):
    """Восстановить обычный ввод."""
    if hasattr(context, "type_delay"):
        del context.type_delay
    log.info("Ввод значений: обычный без задержки")


@given("Я перешел на главную страницу")
@when("Я перешел на главную страницу")
@then("Я вернулся на главную страницу")
def go_to_main(context):
    """
    Открыть страницу, указанную при запуске в параметре TEST_STAND.
    Удобно использовать для возможности запуска одного теста на разных стендах.
    """
    go_to_url(context, context.host)


@given('Я переключился на фрейм "{target}"')
@when('Я переключился на фрейм "{target}"')
def switch_to_frame(context, target):
    """
    Перейти в управление элементами внутри указанного фрейма.
    Для возврата использовать шаг "Я переключился на основную страницу"
    """
    context.browser.switch_to_frame(locator(target))


@given("Я переключился на основную страницу")
@when("Я переключился на основную страницу")
def return_to_default_content(context):
    """
    Вернуться в контекст основной страницы после перехода на управление внутри фрейма.
    """
    context.browser.switch_to_default_content()


@given(
    'Я сохранил значение свойства "{property_name}" элемента "{target}" в переменную "{variable_name}"'
)
@when(
    'Я сохранил значение свойства "{property_name}" элемента "{target}" в переменную "{variable_name}"'
)
def save_element_property(context, property_name, target, variable_name):
    """Сохранить значение свойства  элемента (или атрибута, если свойство не найдено) в указанную переменную"""
    element_property = (
        context.browser.element(locator(target)).highlight().attribute(property_name)
    )

    if element_property:
        variables[variable_name] = element_property
        log.debug(f'VALUE "{element_property}" saved to variable "{variable_name}"')
    else:
        log.warning(f'Не найдено свойство "{property_name}" у элемента "{target}"')


@given('Я сохранил значение элемента "{target}" в переменную "{name}"')
@when('Я сохранил значение элемента "{target}" в переменную "{name}"')
def save_test_variable(context, target, name):
    """Сохранить значение HTML-элемента в указанную переменную. Важно: регистр букв не учитывается."""
    value_from_element = context.browser.element(locator(target)).highlight().text()

    if value_from_element:
        variables[name] = value_from_element
        log.debug(f'VALUE "{value_from_element}" saved to variable "{name}"')
    else:
        log.warning(f'Не найден текст на элементе "{target}"')


@given('Я ввел в поле "{target}" значение переменной "{variable}"')
@when('Я ввел в поле "{target}" значение переменной "{variable}"')
@when('Я ввел в поле "{target}" значение переменной "{variable}"')
def fill_with_test_variable(context, target, variable):
    """
    Подставить в поле ввода значение переменной.

    target - название локатора,
    variable - название переменной или путь до неё, если в переменной лежит json

    Примеры:
    Я ввел в поле "Логин" значение переменной "color"
    Я ввел в поле "Логин" значение переменной "fruits > banana > color"
    """
    value = get_from_variables(variable)
    send_keys(context, target, value)


@given('Я перешел на страницу "{target}"')
@when('Я перешел на страницу "{target}"')
def go_to_page(context, target):
    """Открыть указанную страницу по имени из списка локаторов."""
    go_to_url(context, locator(target))


@step('Я перешел по ссылке из переменной "{variable}"')
def go_to_url_from_variable(context, variable):
    """
    Открыть страницу, указанную в переменной.

    variable - название переменной или путь до неё, если в переменной лежит json

    Примеры:
    Я перешел по ссылке из переменной "test_link"
    Я перешел по ссылке из переменной "site > links > main"
    """
    go_to_url(context, get_from_variables(variable))


@step('Я перешел по ссылке "{link}" относительно тестового стенда')
@step('Я перешел по ссылке "{link}" относительно стенда из переменной "{stand_var}"')
@step(
    'Я перешел по ссылке "{link}" с параметром "{link_appendix_var}" относительно тестового стенда'
)
@step(
    'Я перешел по ссылке "{link}" с параметром "{link_appendix_var}" относительно стенда из переменной "{stand_var}"'
)
def go_to_relative_link(context, link, **kwargs):
    """
    Перейти по ссылке относительно стенда TEST_STAND или указанного в переменной stand_var.
    Для того, чтобы использовать ссылку с параметром (например, '/deals/89', где '89' - номер сделки,
    который генерится сам в процессе прогона тестов) нужно передать параметр через переменную окружения или
    использовать шаг для сохранения в переменную, а затем указать его вместо 'link_appendix_var'.
    Например, 'Я перешел по ссылке "/deals/" с параметром "deal_id"

    В ссылках допустим любой вариант использования слэшей: '/changelog', 'changelog', 'changelog/', '/changelog/'
    """
    go_to_url(context, get_absolute_url(link, **kwargs))


@step('Я перешел по ссылке "{url}"')
def go_to_url(context, url):
    """Открыть указанный в шаге адрес."""
    if url is not None and validators.url(url):
        log.debug(f"GOING TO URL: {url}")
        context.browser.open(url)
    else:
        log.error(f'Невозможно перейти по URL "{url}"')


@then('Я убедился что URL текущей страницы содержит строку "{value}"')
@then('Я убедился что URL текущей страницы содержит значение переменной "{variable}"')
def assert_url_contains(context, **kwargs):
    """Проверить, что в текущем url содержится указанное значение."""
    value = kwargs.get("value")
    if value is None:
        variable_name = kwargs.get("variable")
        value = get_from_variables(variable_name)

    current_url = context.browser.url()
    assert_that(current_url, contains_string(value))


@step("Я перешел в только что открывшееся окно")
def switch_window(context):
    """Сделать активной новую вкладку."""
    context.browser.switch_to_last_tab()


@step("Я закрыл вкладку и вернулся на последнюю открытую")
def close_tab_return_to_last(context):
    """Закрыть текущую вкладку и перейти на последнюю открытую в сессии."""
    context.browser.close()
    context.browser.switch_to_last_tab()


@step("Я закрыл все вкладки кроме текущей")
def close_tabs(context):
    """Закрыть все вкладки браузера кроме текущей"""
    context.browser.close_other_tabs()


@step("Я очистил cookies")
def clear_cookies(context):
    """Удалить все куки выставленные на текущем открытом домене."""
    context.browser.clear_cookies()


@step('Я выставил cookie с именем "{cookie_name}" и значением "{cookie_value}"')
@step(
    'Я выставил cookie с именем из переменной "{cookie_name_var}" и значением из переменной "{cookie_value_var}"'
)
def set_cookie(context, **kwargs):
    """Выставить cookie с именем и значением. Выставлять нужно после открытия домена, для которого она ставится."""
    cookie_name_var = kwargs.get("cookie_name_var")
    cookie_value_var = kwargs.get("cookie_value_var")

    if cookie_name_var is not None and cookie_value_var is not None:
        cookie_name = get_from_variables(cookie_name_var)
        cookie_value = get_from_variables(cookie_value_var)
    else:
        cookie_name = kwargs.get("cookie_name")
        cookie_value = kwargs.get("cookie_value")

    if cookie_name is not None and cookie_value is not None:
        cookie = {"name": cookie_name, "value": cookie_value}
        context.browser.add_cookies([cookie])
        log.debug(
            f'На текущий открытый домен добавлена cookie с именем "{cookie_name}" и значением "{cookie_value}"'
        )
    else:
        log.critical("При попытке выставить cookie переданы пустые значения")


@step("Я очистил localStorage")
def clear_local_storage(context):
    """Очистить local storage. Рекомендуется использовать вместе с очисткой куки в предусловиях теста."""
    context.browser.clear_local_storage()


@step("Я очистил sessionStorage")
def clear_session_storage(context):
    """Очистить session storage."""
    context.browser.clear_session_storage()


@given("Я выбрал десктопную версию")
@when("Я выбрал десктопную версию")
def select_desktop_version(context):
    """Установить размер окна под ноутбучное разрешение 1366х768."""
    setup_window_size(context, 1366, 768)


@given("Я выбрал мобильную версию")
@when("Я выбрал мобильную версию")
def select_mobile_version(context):
    """Установить размер окна 400х600 для имитации мобильного."""
    setup_window_size(context, 400, 600)


@given('Я установил размер окна "{width:d}x{height:d}"')
@when('Я установил размер окна "{width:d}x{height:d}"')
def setup_window_size(context, width: int, height: int):
    """Установить произвольный размер окна."""
    context.browser.set_window_size(width, height)


@step("Я обновил страницу")
def refresh_page(context):
    """Обновить страницу в браузере."""
    context.browser.refresh()


@when('Я ввел в поле "{target}" значение "{value}"')
@when('Я ввел в "{target}" значение "{value}"')
def send_keys(context, target, value):
    """
    Передать нажатия клавиш строки, указанной в параметре "value" в поле, указанное в словаре локаторов.
    При возникновении проблем, попробуйте переключится на посимвольный ввод.
    """
    if not value:
        log.error("Передано пустое значение на ввод")
        return

    context.browser.element(locator(target)).highlight().type(
        value, delay=getattr(context, "type_delay", None)
    )


@when('Я ввел посимвольно в поле "{target}" значение "{value}"')
@when('Я ввел посимвольно в поле "{target}" значение переменной "{variable}"')
@when('Я ввел посимвольно в "{target}" значение "{value}"')
@when('Я ввел посимвольно в "{target}" значение переменной "{variable}"')
def send_keys_as_granny(context, target, **kwargs):
    """
    Посимвольно, с задержкой в 0,1 сек передать нажатия клавиш строки, указанной в параметре "value" в поле,
    указанное в словаре локаторов.
    """
    change_send_keys_type(context)
    value = kwargs.get("value")
    if not value:
        variable_name = kwargs.get("variable")
        value = get_from_variables(variable_name)
    send_keys(context, target, value)
    restore_send_keys_type(context)


@when('Я очистил поле "{target}"')
@then('Я очистил поле "{target}"')
def clear(context, target):
    """
    Очистить содержимое поля ввода. Может не сработать в случае, если поле по умолчанию не пустое.
    В таком случае, стоит использовать посимвольный метод
    """
    context.browser.element(locator(target)).highlight().clear()


@when('Я посимвольно очистил поле "{target}"')
@then('Я посимвольно очистил поле "{target}"')
def clear_by_symbols(context, target):
    """Очистить содержимое поля ввода посимвольно с помощью клавиши Backspace"""
    element = context.browser.element(locator(target)).highlight()
    length = len(element.text())
    element.type(length * Keys.BACKSPACE).clear()


@when('Я очистил поле "{target}" с помощью JavaScript')
@then('Я очистил поле "{target}" с помощью JavaScript')
def js_clear(context, target):
    """Очистить содержимое поля ввода c помощью команды JavaScript"""
    context.browser.element(locator(target)).highlight().clear(using_js=True)


@when('Я нажал на "{target}" с помощью JavaScript')
def js_click(context, target):
    context.browser.element(locator(target)).highlight().click(using_js=True)


@when('Я нажал "{target}" содержащий текст "{text}"')
def click_visible_in_scope_with_contains_text(context, target, text):
    (
        context.browser.elements(locator(target))
        .filter_by_partial_text(text)
        .should_not_have_count(0)
        .first()
        .should_be_visible()
        .highlight()
        .click()
    )


@when('Я нажал на "{target}"')
@when('Я нажал на кнопку "{target}"')
def click(context, target):
    """
    Выполнить нажатие на элемент с именем из списка локаторов.
    У Selenium есть принципиальное ограничение, клики выполняются только на ближайший к пользователю слой.
    Если элемент невидимый или перекрыт другим, тест упадет и выдаст соответствущее сообщение об ошибке.
    """
    context.browser.element(locator(target)).highlight().hover().click()


@when('Я нажал правой кнопкой на "{target}"')
def context_click(context, target):
    """
    Выполнить нажатие правой кнопкой на элемент с именем из списка локаторов.
    """
    context.browser.element(locator(target)).highlight().hover().context_click()


@when('Я сделал двойной клик на "{target}"')
def double_click(context, target):
    """
    Выполнить двойное нажатие на элемент с именем из списка локаторов.
    У Selenium есть принципиальное ограничение – клики выполняются только на ближайший к пользователю слой.
    Если элемент невидимый или перекрыт другим, тест упадет и выдаст соответствущее сообщение об ошибке.
    """
    context.browser.element(locator(target)).highlight().hover().double_click()


@when('Я сделал ctrl-клик на "{target}"')
def ctrl_click(context, target):
    """
    Выполнить нажатие с зажатой ctrl/cmd на элемент с именем из списка локаторов.
    У Selenium есть принципиальное ограничение – клики выполняются только на ближайший к пользователю слой.
    Если элемент невидимый или перекрыт другим, тест упадет и выдаст соответствущее сообщение об ошибке.
    """
    context.browser.down(ctrl_key)
    context.browser.element(locator(target)).highlight().hover().click()
    context.browser.up(ctrl_key)


@when('Я сделал shift-клик на "{target}"')
def shift_click(context, target):
    """
    Выполнить нажатие с зажатой shift на элемент с именем из списка локаторов.
    У Selenium есть принципиальное ограничение – клики выполняются только на ближайший к пользователю слой.
    Если элемент невидимый или перекрыт другим, тест упадет и выдаст соответствущее сообщение об ошибке.
    """
    mod_key = Keys.SHIFT
    context.browser.down(mod_key)
    context.browser.element(locator(target)).highlight().hover().click()
    context.browser.up(mod_key)


@when("Я нажал на клавишу {key_const}")
def press_key(context, key_const):
    """
    Выполнить нажатие клавиши на клавиатуре без фокуса на элементе.
    Чтобы сфокусироваться на элементе используйте шаг 'Я нажал на ...' или 'Я навел курсор на элемент ...'
    В параметре {key_const} указывается константа с названием клавиши, например: ENTER, TAB, ESCAPE.
    Полный список доступных клавиш:
    https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.common.keys
    """
    context.browser.press(vars(Keys)[key_const])


@when("Я зажал модификатор {mod_key} и нажал на клавишу {key_const}")
def hold_and_press_key(context, mod_key, key_const):
    """
    Выполнить нажатие клавиши на клавиатуре без фокуса на элементе.
    Чтобы сфокусироваться на элементе используйте шаг 'Я нажал на ...' или 'Я навел курсор на элемент ...'
    В параметрах {key_const}, {mod_key} указываются константы с названием клавиши, например: ENTER, CONTROL, ALT, SHIFT.
    Полный список доступных клавиш:
    https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.common.keys
    """
    keys_dict = vars(Keys)
    context.browser.down(keys_dict[mod_key]).press(keys_dict[key_const]).up(
        keys_dict[mod_key]
    )


@when('Я нажал на первый элемент в списке "{target}"')
@when('Я нажал на первое значение в списке "{target}"')
def click_first(context, target):
    """
    Нажать на первый элемент в списке элементов, найденных по общему локатору в словаре.
    В качестве локатора надо выбирать класс или атрибут, общий для всех элементов списка.
    """
    click_certain(context, 1, target)


@when('Я нажал на последний элемент в списке "{target}"')
@when('Я нажал на последнее значение в списке "{target}"')
def click_last(context, target):
    """
    Нажать на последний элемент в списке элементов, найденных по общему локатору в словаре.
    В качестве локатора надо выбирать класс или атрибут, общий для всех элементов списка.
    """
    click_certain(context, 0, target)


@when('Я нажал на {index}-й элемент в списке "{target}"')
@when('Я нажал на {index}-е значение в списке "{target}"')
def click_certain(context, index, target, **kwargs):
    """
    Нажать на соответствующий по номеру элемент в списке элементов, найденных по общему локатору в словаре.
    В качестве локатора надо выбирать класс или атрибут, общий для всех элементов списка.
    """
    elements = context.browser.elements(locator(target))
    desired_index = (
        random.randint(0, len(elements) - 1)
        if kwargs.get("random") is True
        else int(index) - 1
    )
    elements.nth(desired_index).highlight().hover().click()


@when('Я нажал на случайный элемент в списке "{target}"')
@when('Я нажал на случайное значение в списке "{target}"')
def click_random(context, target):
    """
    Нажать на соответствующий по номеру элемент в списке элементов, найденных по общему локатору в словаре.
    В качестве локатора надо выбирать класс или атрибут, общий для всех элементов списка.
    """
    click_certain(context, -42, target, random=True)


@when('Я нажал на точку со смещением "{x},{y}" от элемента "{target}"')
@then('Я нажал на точку со смещением "{x},{y}" от элемента "{target}"')
def click_coordinates(context, x, y, target):
    """
    Шаг для работы с элементами, которые нельзя найти обычными локаторами (например, яндекс карты)
    или для имитации произвольных кликов пользователя.
    Цепляемся локатором к известному элементу, в пикселях указываем смещение от левого верхнего угла
    до требуемой точки клика.
    """
    context.browser.element(locator(target)).highlight().click_by_offset(
        float(x), float(y)
    )


@when('Я перетащил элемент "{target}" на "{x},{y}" пикселей')
def drag_element_by_offset(context, target, x, y):
    """
    Попытаться протащить элемент на указанное количество пикселей по двум осям.
    """
    context.browser.element(locator(target)).highlight().drag_and_drop(
        float(x), float(y)
    )


@when('Я перетащил элемент "{target}" к "{other_element}"')
def drag_element_to_other(context, target, other_element):
    """
    Попытаться протащить элемент к другому элементу
    """
    drag = context.browser.element(locator(target))
    drop = context.browser.element(locator(other_element))
    drag.highlight().drag_and_drop_to(drop)


@when('Я перетащил элемент "{target}" на элемент "{other_element}"')
@when(
    'Я перетащил элемент "{target}" на элемент "{other_element}" за {steps_count:d} шагов'
)
@when(
    'Я перетащил элемент "{target}" на элемент "{other_element}" за {steps_count:d} шагов '
    "с задержкой в {step_delys_in_millis:d} мс между ними"
)
def drag_element_to_other_by_steps(
    context,
    target,
    other_element,
    steps_count: int = 1,
    step_delys_in_millis: int = 100,
):
    """
    Взять элемент, поместить его над другим и отпустить. Выполняется несколькими шагами с ожиданием
    """
    drop = context.browser.element(locator(other_element)).highlight()
    (
        context.browser.element(locator(target))
        .highlight()
        .drag_and_drop_to_by_steps(drop, steps_count, step_delys_in_millis)
    )


@when('Я взял элемент "{target}" и поместил над элементом "{other_element}"')
@when(
    'Я взял элемент "{target}" и поместил над элементом "{other_element}" за {steps_count:d} шагов'
)
@when(
    'Я взял элемент "{target}" и поместил над элементом "{other_element}" за {steps_count:d} шагов '
    "с задержкой в {step_delys_in_millis:d} мс между ними"
)
def drag_and_hover_on_other_by_steps(
    context,
    target,
    other_element,
    steps_count: int = 1,
    step_delys_in_millis: int = 100,
):
    """
    Взять элемент и поместить его над другим. Выполняется несколькими шагами с ожиданием
    """
    drop = context.browser.element(locator(other_element)).highlight()
    (
        context.browser.element(locator(target))
        .highlight()
        .drag_and_hover_on_by_steps(drop, steps_count, step_delys_in_millis)
    )


@when(
    'Я переместил курсор с элементом "{target}" на элемент "{other_element}" и отпустил'
)
@when(
    'Я переместил курсор с элементом "{target}" на элемент "{other_element}" и отпустил за {steps_count:d} шагов'
)
@when(
    'Я переместил курсор с элементом "{target}" на элемент "{other_element}" и отпустил за {steps_count:d} шагов '
    "с задержкой в {step_delys_in_millis:d} мс между ними"
)
def hover_on_and_drop_to_other_by_steps(
    context,
    target,
    other_element,
    steps_count: int = 1,
    step_delys_in_millis: int = 100,
):
    """
    Поместить элемент (который был ранее нажат и перенесен курсором) над другим и отпустить.
    Выполняется несколькими шагами с ожиданием
    """
    drop = context.browser.element(locator(other_element)).highlight()
    (
        context.browser.element(locator(target))
        .highlight()
        .hover_on_and_drop_to_by_steps(drop, steps_count, step_delys_in_millis)
    )


@given('Я навел курсор на элемент "{target}"')
@when('Я навел курсор на элемент "{target}"')
def hover_on_element(context, target):
    """Наводит курсор на элемент для срабатывания события hover (например, раскрытие выпадающих списков)."""
    context.browser.element(locator(target)).highlight().hover()


@when('Я выбрал "{text}" в выпадающем меню "{target}"')
def select_dropdown(context, text, target):
    """Выбрать элемент из списка по тексту. В качестве локатора - css селектор, общий для всех элементов списка."""
    (
        context.browser.elements(locator(target))
        .filter_by_text(text)
        .should_not_have_count(0)
        .first()
        .highlight()
        .click()
    )


@given('Я пролистал страницу до позиции "{x}","{y}" пикселей')
@when('Я пролистал страницу до позиции "{x}","{y}" пикселей')
def scroll_to_coord(context, x, y):
    """Устанавливает заданную позицию скролла."""
    context.browser.scroll_to(float(x), float(y))


@when('Я пролистал страницу на "{x}","{y}" пикселей')
def scroll_by(context, x, y):
    """Пролистывает страницу на указанное расстояние."""
    context.browser.scroll_by(float(x), float(y))


@when('Я пролистал контейнер "{target}" на "{x}","{y}" пикселей')
def scroll_container_by_coord(context, target, x, y):
    """Пролистывает элемент, которому доступна прокрутка на указанное расстояние."""
    if context.browser.name == "internet explorer":
        log.warning(
            f"Шаг {context.current_step['name']} не может быть выполнен браузером Internet Explorer"
        )
        return
    context.browser.element(locator(target)).highlight().scroll_by(float(x), float(y))


@when('Я прокрутил страницу до полного отображения элемента "{target}"')
def scroll_bscroll_into_view(context, target):
    context.browser.element(locator(target)).scroll_into_view()


@when('Я нажал на один из элементов "{target}" с текстом "{text}"')
@when('Я нажал "{target}" с текстом "{text}"')
def click_element_with_text_multiline(context, target, text):
    """
    Нажать на первый элемент, который найден по содержащемуся в нём тексту среди всех элементов по данному
    селектору. Для уточнения расположения элемента можно указать родство с контейнером в локаторе,
    например ".my-options button" (в этом случае поиск по тексту будет произведён во всех потомках
    .my-options с тегом button). Рекомендуется использовать шаг только для прототипирования тестов
    или если невозможно создать css-локатор.
    """
    (
        context.browser.elements(locator(target))
        .filter_by_text(text)
        .should_not_have_count(0)
        .first()
        .highlight()
        .hover()
        .click()
    )


@when('Я нажал на элемент с текстом "{text}"')
@when('Я нажал на ссылку с текстом "{text}"')
def click_link_with_text(context, text):
    """
    Нажать на первый элемент, который найден по содержащемуся в нём тексту.
    Работа тестов без локаторов принципиально нестабильна.
    Есть проблема с multiline текстом, в большинстве случаев он не находится этим шагом.
    Возможно нахождение скрытых элементов из невидимой, но подгруженной мобильной верстки.
    Рекомендуется использовать шаг только для прототипирования тестов или если невозможно создать css-локатор.
    """
    locator = f"//*[contains(text(),'{text}')]"
    context.browser.element(locator).highlight().hover().click()


@then('Я убедился что я нахожусь на странице с названием "{value}"')
def assert_page_name(context, value):
    """Проверить, что заголовок текущей страницы совпадает с указанной строкой."""
    assert_that(context.browser.title(), equal_to(value))


@then(
    'Я убедился что среди элементов "{target}" отображается элемент с текстом "{text}"'
)
def assert_visible_in_scope_with_text(context, target, text):
    """
    Проверить наличие элемента с заданным текстом среди всех элементов по данному
    селектору. Для уточнения расположения элемента можно указать родство с контейнером в локаторе,
    например ".my-options button" (в этом случае поиск по тексту будет произведён во всех потомках
    .my-options с тегом button). Рекомендуется использовать шаг только для прототипирования тестов
    или если невозможно создать css-локатор.
    """
    (
        context.browser.elements(locator(target))
        .filter_by_text(text)
        .should_not_have_count(0)
        .first()
        .should_be_visible()
    )


@then(
    'Я убедился что среди элементов "{target}" отображается элемент содержащий текст "{text}"'
)
def assert_visible_in_scope_with_text_contains(context, target, text):
    (
        context.browser.elements(locator(target))
        .filter_by_partial_text(text)
        .should_not_have_count(0)
        .first()
        .should_be_visible()
    )


@then(
    'Я убедился что среди элементов "{target}" не отображается элемент с текстом "{text}"'
)
def assert_invisible_in_scope_with_text(context, target, text):
    """
    Проверить отсутствие элемента (нет в DOM либо не виден пользователю) с заданным текстом среди всех элементов
    по данному селектору. Для уточнения расположения элемента можно указать родство с контейнером в локаторе,
    например ".my-options button" (в этом случае поиск по тексту будет произведён во всех потомках
    .my-options с тегом button). Рекомендуется использовать шаг только для прототипирования тестов
    или если невозможно создать css-локатор.
    """
    (
        context.browser.elements(locator(target))
        .filter_by_text(text)
        .first()
        .should_be_hidden()
    )


@then(
    'Я убедился что среди элементов "{target}" не отображается элемент содержащий текст "{text}"'
)
def assert_invisible_in_scope_contains_text(context, target, text):

    (
        context.browser.elements(locator(target))
        .filter_by_partial_text(text)
        .first()
        .should_be_hidden()
    )


@then('Я убедился что "{target}" отображается')
@then('Я убедился что поле "{target}" отображается')
def assert_visible(context, target):
    """Проверить, что указанный элемент виден для пользователя."""
    context.browser.element(locator(target)).should_be_visible().highlight()


@then('Я убедился что "{target}" не отображается')
@then('Я убедился что поле "{target}" не отображается')
def assert_not_visible(context, target):
    """Проверить, что указанный элемент невиден для пользователя."""
    context.browser.element(locator(target)).should_be_hidden()


@then('Я убедился что элемент с текстом "{text}" отображается')
def assert_visible_with_text(context, text):
    """Проверить, что первый найденный по содержащемуся в нем тексту элемент виден для пользователя."""
    locator = f"//*[contains(text(),'{text}')]"
    context.browser.element(locator).should_be_visible().highlight()


@then('Я убедился что элемент с текстом "{text}" не отображается')
def assert_not_visible_with_text(context, text):
    """Проверить, что первый найденный по содержащемуся в нем тексту элемент не виден для пользователя."""
    locator = f"//*[contains(text(),'{text}')]"
    context.browser.element(locator).should_be_hidden()


@given("Я убедился что страница прогрузилась")
@then("Я убедился что страница прогрузилась")
def assert_page_load(context):
    """Проверить, что страница полностью загрузилась"""
    assert_that(
        context.browser.wait_for_loading(),
        equal_to(True),
        "Страница должна была загрузиться",
    )


@then('Я убедился что поле "{target}" пустое')
def assert_field_is_empty(context, target):
    """Проверить, что указанное поле ввода не содержит значения."""
    context.browser.element(locator(target)).highlight().should_be_empty()


@then('Я убедился что поле "{target}" не пустое')
def assert_field_is_not_empty(context, target):
    """Проверить, что указанное поле ввода содержит значение."""
    context.browser.element(locator(target)).highlight().should_not_be_empty()


@then('Я убедился что "{target}" доступен для нажатия')
@then('Я убедился что "{target}" доступна для нажатия')
@then('Я убедился что "{target}" доступно для нажатия')
def assert_clickable(context, target):
    """Проверить, что указанный элемент кликабелен (виден и активен)."""
    element = context.browser.element(locator(target))
    element.should_be_visible().should_be_enabled().highlight()


@then('Я убедился что "{target}" не доступен для нажатия')
@then('Я убедился что "{target}" не доступна для нажатия')
@then('Я убедился что "{target}" не доступно для нажатия')
def assert_not_clickable(context, target):
    """Проверить, что указанный элемент некликабелен (виден, но не активен)."""
    element = context.browser.element(locator(target))
    element.should_be_visible().should_be_disabled().highlight()


@then('Я убедился что в списке "{target}" {count:d} значение')
@then('Я убедился что в списке "{target}" {count:d} значения')
@then('Я убедился что в списке "{target}" {count:d} значений')
@then('Я убедился что отображается {comparator} {count:d} элемент "{target}"')
@then('Я убедился что отображается {comparator} {count:d} элемента "{target}"')
@then('Я убедился что отображается {comparator} {count:d} элементов "{target}"')
@then('Я убедился что отображается {comparator} {count:d} элемент в списке "{target}"')
@then('Я убедился что отображается {comparator} {count:d} элемента в списке "{target}"')
@then(
    'Я убедился что отображается {comparator} {count:d} элементов в списке "{target}"'
)
def assert_element_count_comparison(context, count, target, comparator="ровно"):
    elements = context.browser.elements(locator(target))

    def action(_):
        actual = len(elements)
        return comparators[comparator](actual, count), actual

    elements.highlight()
    is_successful, result = wait_for(
        action_name=f"Проверка количество элементов '{target}'",
        func=action,
        delay=context.browser.timeout,
        wait=ELEMENT_CHECK_POLLING_INTERVAL,
    )

    assert_that(
        is_successful,
        equal_to(True),
        f'Количество элементов "{target}" должен быть {comparator} "{count}". Фактическое: {result}',
    )


@then(
    'Я убедился что численное значение из переменной "{name}" {comparator} чем на элементе "{target}"'
)
@then(
    'Я убедился что численное значение параметра "{name}" {comparator} чем на элементе "{target}"'
)
def variable_greater_or_less_than_element(context, name, comparator, target):
    """
    Сравнить значение указанного элемента со значением переменной окружения
    или ранее сохранённой переменной через шаг "Я сохранил значение элемента"

    Элемент и переменная должны содержать только числа
    comparator - 'больше' ИЛИ 'меньше'
    """
    text_to_compare = context.browser.element(locator(target)).highlight().text()
    text_value = get_from_variables(name)

    if comparator.lower() == "больше":
        assert_that(
            decimal.Decimal(text_value), greater_than(decimal.Decimal(text_to_compare))
        )
    elif comparator.lower() == "меньше":
        assert_that(
            decimal.Decimal(text_value), less_than(decimal.Decimal(text_to_compare))
        )


@then(
    'Я убедился что значение свойства "{property}" элемента "{target}" имеет значение "{value}"'
)
@then(
    'Я убедился что значение свойства "{property}" элемента "{target}" совпадает со значением переменной "{var}"'
)
def check_element_property(context, property, target, value=None, var=None):
    """
    Сравнить значение свойства  элемента (или атрибута, если свойство не найдено)
    с указаным значением на предмет совпадения.
    """
    expected = get_from_variables(var) if var else value
    context.browser.element(locator(target)).highlight().should_have_attribute(
        property, expected
    )


@then(
    'Я убедился что значение свойства "{property}" элемента "{target}" не имеет значение "{value}"'
)
@then(
    'Я убедился что значение свойства "{property}" элемента "{target}" не совпадает со значением переменной "{var}"'
)
def check_element_property_negative(context, property, target, value=None, var=None):
    """
    Сравнить значение свойства  элемента (или атрибута, если свойство не найдено)
    с указаным значением на предмет НЕ совпадения.
    """
    expected = get_from_variables(var) if var else value
    context.browser.element(locator(target)).highlight().should_not_have_attribute(
        property, expected
    )


@when('Я ввел в поле "{target}" сгенерированное случайно имя')
@when('Я ввел в "{target}" сгенерированное случайно имя')
def random_first_name(context, target):
    """Подставить в поле ввода сгенерированное случайно имя."""
    random_value = generic.person.name(gender=gender)
    send_keys(context, target, random_value)


@when('Я ввел в поле "{target}" сгенерированное случайно отчество')
@when('Я ввел в "{target}" сгенерированное случайно отчество')
def random_middle_name(context, target):
    """Подставить в поле ввода сгенерированное случайно отчество."""
    random_value = generic.ru.patronymic(gender=gender)
    send_keys(context, target, random_value)


@when('Я ввел в поле "{target}" сгенерированную случайно фамилию')
@when('Я ввел в "{target}" сгенерированную случайно фамилию')
def random_last_name(context, target):
    """Подставить в поле ввода сгенерированную случайно фамилию."""
    random_value = generic.person.last_name(gender=gender)
    send_keys(context, target, random_value)


@when('Я ввел в поле "{target}" сгенерированный случайно номер телефона')
@when('Я ввел в "{target}" сгенерированный случайно номер телефона')
def random_telephone(context, **kwargs):
    """
    Подставить в поле ввода случайный номер телефона из недоступного для звонка диапазона.
    Сгенерируется неотформатированный номер вида "XXXXXXXXXX". Например, "5167874562".
    """
    random_value = generic.person.telephone(mask=f"{generate_phone_code()}#######")
    send_keys(context, kwargs.get("target"), random_value)


@when('Я ввел в поле "{target}" сгенерированный случайно адрес')
@when('Я ввел в "{target}" сгенерированный случайно адрес')
def random_address(context, target):
    """Подставить в поле ввода случайный физический адрес (улицу и номер дома)."""
    random_value = generic.address.address()
    send_keys(context, target, random_value)


@when('Я ввел в поле "{target}" сгенерированный случайно e-mail')
@when('Я ввел в "{target}" сгенерированный случайно e-mail')
def random_email(context, target):
    """
    Подставить в поле ввода сгенерированный случайно e-mail вида xxxxx@diroms.ru
    Доступ к почтовому ящику по запросу.
    """
    random_value = generic.person.email(domains=["@diroms.ru"])
    send_keys(context, target, random_value)


@when('Я ввел в поле "{target}" сгенерированную случайно дату рождения')
@when('Я ввел в "{target}" сгенерированную случайно дату рождения')
def random_birthdate(context, target):
    """Подставить в поле ввода дату из диапазона 1930-2000г. в формате dd/mm/yyyy."""
    random_value = generic.datetime.formatted_date(fmt="%d/%m/%Y", start=1930, end=2000)
    send_keys(context, target, random_value)


@when(
    'Я ввел в поле "{target}" сгенерированную случайно дату в формате "{fmt}" и диапазоне от {start} до {end} года'
)
@when(
    'Я ввел в "{target}" сгенерированную случайно дату в формате "{fmt}" и диапазоне от {start} до {end} года'
)
def random_date(context, target, fmt, start, end):
    """Подставить в поле ввода случайную дату из заданного диапазона в указанном формате. Пример формата: %d.%m.%Y."""
    random_value = generic.datetime.formatted_date(
        fmt=fmt, start=int(start), end=int(end)
    )
    send_keys(context, target, random_value)


@when('Я ввел в поле "{target}" сгенерированный случайно СНИЛС')
@when('Я ввел в "{target}" сгенерированный случайно СНИЛС')
def random_snils(context, target):
    """Подставить в поле ввода случайный валидный номер СНИЛС."""
    send_keys(context, target, generate_valid_snils())


@when('Я ввел в поле "{target}" сгенерированный случайно ИНН')
@when('Я ввел в "{target}" сгенерированный случайно ИНН')
def random_inn(context, target):
    """Подставить в поле ввода случайный валидный номер ИНН."""
    random_value = generic.ru.inn()
    send_keys(context, target, random_value)


@when('Я ввел в поле "{target}" сгенерированный случайно номер транзакт')
@when('Я ввел в "{target}" сгенерированный случайно номер транзакт')
def random_tranzact_number(context, target):
    """Подставить в поле ввода сгенерированный случайно номер транзакт."""
    random_value = generate_tranzact_number()
    send_keys(context, target, random_value)


@when('Я ввел в поле "{target}" сгенерированную случайно серию паспорта')
@when('Я ввел в "{target}" сгенерированную случайно серию паспорта')
def random_passport_series(context, target):
    """Подставить в поле ввода две пары случайных цифр, разделённых пробелом."""
    random_value = generic.ru.passport_series()
    send_keys(context, target, random_value)


@when('Я ввел в поле "{target}" сгенерированный случайно номер паспорта')
@when('Я ввел в "{target}" сгенерированный случайно номер паспорта')
def random_passport_number(context, target):
    """Подставить в поле ввода случайные 6 цифр."""
    random_value = generic.ru.passport_number()
    send_keys(context, target, random_value)


@when('Я ввел в поле "{target}" сгенерированный случайно код подразделения')
@when('Я ввел в "{target}" сгенерированный случайно код подразделения')
def random_passport_unit_code(context, target):
    """Подставить в поле ввода случайные 6 цифр."""
    random_value = generic.ru.passport_number()
    send_keys(context, target, random_value)


@when('Я ввел в поле "{target}" сгенерированные случайно серию и номер паспорта')
@when('Я ввел в "{target}" сгенерированные случайно серию и номер паспорта')
def random_passport_series_number(context, target):
    """Подставить в поле ввода случайные 10 цифр в формате XX XX XXXXXX."""
    random_value = generic.ru.series_and_number()
    send_keys(context, target, random_value)


@when('Я ввел в поле "{target}" {digit} случайно сгенерированных цифр')
@when('Я ввел в поле "{target}" {digit} случайно сгенерированные цифры')
@when('Я ввел в поле "{target}" {digit} случайно сгенерированную цифру')
@when('Я ввел в "{target}" {digit} случайно сгенерированных цифр')
@when('Я ввел в "{target}" {digit} случайно сгенерированные цифры')
@when('Я ввел в "{target}" {digit} случайно сгенерированную цифру')
def random_digits(context, target, digit):
    """Подставить в поле ввода n случайных цифр."""
    random_values = generic.numeric.integers(start=0, end=10, n=int(digit))
    send_keys(context, target, "".join(map(str, random_values)))


@when('Я ввел в поле "{target}" случайно сгенерированное число от {start} до {end}')
@when('Я ввел в "{target}" случайно сгенерированное число от {start} до {end}')
def random_number(context, target, start, end):
    """Подставить в поле ввода случайно сгенерированное число в указанном интервале."""
    random_value = random.randint(int(start), int(end))
    send_keys(context, target, random_value)


@when(
    'Я ввел в поле "{target}" одноразовый код для секрета из переменной "{otp_secret_variable}"'
)
def send_otp_code(context, target, otp_secret_variable):
    """
    Ввести в указанное поле временный код аутентификации, сгенерированный из указанного в переменной ключа секрета.

    otp_secret_variable - название переменной, в которой лежит значение секретного ключа,
    полученное при регистрации.
    Пример кода: DT7QA5745F7DI5FIELC5ECYEPYAUFDQT
    """
    secret_code = get_from_variables(otp_secret_variable)
    otp_password = str(totp(secret_code))
    log.debug("Сгенерирован OTP-код: %s", otp_password)
    send_keys(context, target, otp_password)


@when('Я ввел в поле "{target}" сегодняшнюю дату')
@when('Я ввел в "{target}" сегодняшнюю дату')
@when('Я ввел в поле "{target}" сегодняшнюю дату в формате "{fmt}"')
@when('Я ввел в "{target}" сегодняшнюю дату в формате "{fmt}"')
def date_today(context, **kwargs):
    """Подставить в поле ввода сегодняшнюю дату в указанном формате или по умолчанию в формате dd/mm/yyyy."""
    dt = datetime.date.today()
    send_keys(context, kwargs.get("target"), dt.strftime(kwargs.get("fmt", "%d/%m/%Y")))


@when('Я ввел в поле "{target}" вчерашнюю дату')
@when('Я ввел в "{target}" вчерашнюю дату')
@when('Я ввел в поле "{target}" вчерашнюю дату в формате "{fmt}"')
@when('Я ввел в "{target}" вчерашнюю дату в формате "{fmt}"')
def date_yesterday(context, **kwargs):
    """Подставить в поле ввода вчерашнюю дату в указанном формате или по умолчанию в формате dd/mm/yyyy."""
    dt = datetime.date.today() - datetime.timedelta(days=1)
    send_keys(context, kwargs.get("target"), dt.strftime(kwargs.get("fmt", "%d/%m/%Y")))


@when('Я ввел в поле "{target}" завтрашнюю дату')
@when('Я ввел в "{target}" завтрашнюю дату')
@when('Я ввел в поле "{target}" завтрашнюю дату в формате "{fmt}"')
@when('Я ввел в "{target}" завтрашнюю дату в формате "{fmt}"')
def date_tomorrow(context, **kwargs):
    """Подставить в поле ввода завтрашнюю дату в указанном формате или по умолчанию в формате dd/mm/yyyy."""
    dt = datetime.date.today() + datetime.timedelta(days=1)
    send_keys(context, kwargs.get("target"), dt.strftime(kwargs.get("fmt", "%d/%m/%Y")))


@when('Я ввел в поле "{target}" дату на {n} дней позже текущей')
@when('Я ввел в "{target}" дату на {n} дней позже текущей')
@when('Я ввел в поле "{target}" дату на {n} дней позже текущей в формате "{fmt}"')
@when('Я ввел в "{target}" дату на {n} дней позже текущей в формате "{fmt}"')
def date_later_then_now(context, **kwargs):
    """Подставить в поле ввода дату позже на n дней в указанном формате или по умолчанию в формате dd/mm/yyyy."""
    dt = datetime.date.today() + datetime.timedelta(days=int(kwargs["n"]))
    send_keys(context, kwargs.get("target"), dt.strftime(kwargs.get("fmt", "%d/%m/%Y")))


@when('Я вставил в поле "{target}" значение из буфера обмена')
@when('Я вставил в "{target}" значение из буфера обмена')
def paste_from_clipboard(context, target):
    """Вставить в указанное поле скопированное ранее значение."""
    context.browser.element(locator(target)).highlight().type(Keys.SHIFT + Keys.INSERT)


@when('Я ввел в поле "{target}" дату на {n} дней раньше текущей')
@when('Я ввел в "{target}" дату на {n} дней раньше текущей')
@when('Я ввел в поле "{target}" дату на {n} дней раньше текущей в формате "{fmt}"')
@when('Я ввел в "{target}" дату на {n} дней раньше текущей в формате "{fmt}"')
def date_earlier_then_now(context, **kwargs):
    """Подставить в поле ввода дату позже на n дней в указанном формате или по умолчанию в формате dd/mm/yyyy."""
    dt = datetime.date.today() - datetime.timedelta(days=int(kwargs["n"]))
    send_keys(context, kwargs.get("target"), dt.strftime(kwargs.get("fmt", "%d/%m/%Y")))


@step('Я сохранил значение из буфера обмена в переменную "{variable_name}"')
def get_clipboard_value_and_store(context, variable_name):
    variables[variable_name] = context.browser.get_clipboard_value()


@when("Я напечатал")
@when('Я напечатал "{text}"')
def type_text(context, text=None):
    text = text or context.text  # Многострочный текст через """
    context.browser.type(text)


@then(
    'Я убедился что среди "{target}" элемент с атрибутом "{attribute_name}"="{attribute_value}" отображается'
)
def assert_element_with_attribute_is_visible(
    context, target, attribute_name, attribute_value
):
    (
        context.browser.elements(locator(target))
        .filter_by_attribute_value(attribute_name, attribute_value)
        .should_not_have_count(0)
        .first()
        .should_be_visible()
    )


@then(
    'Я убедился что среди "{target}" элемент с атрибутом "{attribute_name}"="{attribute_value}" не отображается'
)
def assert_element_with_attribute_is_hidden(
    context, target, attribute_name, attribute_value
):
    (
        context.browser.elements(locator(target))
        .filter_by_attribute_value(attribute_name, attribute_value)
        .first()
        .should_be_hidden()
    )


@then('Я убедился что текст элемента "{target}" равен "{expected}"')
def assert_element_text_equal_to(context, target, expected):
    (
        context.browser.element(locator(target))
        .should_be_visible()
        .highlight()
        .should_have_text(expected)
    )


@then('Я убедился что элемент "{target}" содержит текст "{expected}"')
def assert_element_contains_text(context, target, expected):
    (
        context.browser.element(locator(target))
        .should_be_visible()
        .highlight()
        .should_contain_text(expected)
    )


@then('Я убедился что текст элемента "{target}" не равен "{expected}"')
def assert_element_text_not_equal_to(context, target, expected):
    (
        context.browser.element(locator(target))
        .should_be_visible()
        .highlight()
        .should_not_have_text(expected)
    )


@then(
    'Я убедился что значение переменной "{name}" совпадает со значением элемента "{target}"'
)
@then(
    'Я убедился что текст элемента "{target}" совпадает со значением переменной "{name}"'
)
def variable_equals_element(context, name, target):
    """
    Сравнить значение указанного элемента на совпадение со значением переменной окружения
    или ранее сохранённой переменной через шаг "Я сохранил значение элемента"
    """
    expected = get_from_variables(name)
    assert_element_text_equal_to(context, target, expected)


@then('Я убедился что значение переменной "{name}" не совпадает с элементом "{target}"')
@then(
    'Я убедился что текст элемента "{target}" не совпадает со значением переменной "{name}"'
)
def variable_not_equals_element(context, name, target):
    """
    Сравнить значение указанного элемента на НЕ совпадение со значением переменной окружения
    или ранее сохранённой переменной через шаг "Я сохранил значение элемента"
    """
    expected = get_from_variables(name)
    assert_element_text_not_equal_to(context, target, expected)


@then('Я убедился что значение поля "{target}" равно "{expected}"')
def assert_element_value_equal_to(context, target, expected):
    """Проверка значения свойства value для input и textarea"""
    (
        context.browser.element(locator(target))
        .should_be_visible()
        .highlight()
        .should_have_value(expected)
    )


@then('Я убедился что значение поля "{target}" равно значению переменной "{variable}"')
def assert_element_value_equal_to_variable(context, target, variable):
    """Проверка значения свойства value для input и textarea"""
    expected = get_from_variables(variable)
    assert_element_value_equal_to(context, target, expected)


@then('Я убедился что значение поля "{target}" не равно "{expected}"')
def assert_element_value_not_equal_to(context, target, expected):
    """Проверка значения свойства value для input и textarea"""
    (
        context.browser.element(locator(target))
        .should_be_visible()
        .highlight()
        .should_not_have_value(expected)
    )


@then(
    'Я убедился что значение поля "{target}" не равно значению переменной "{variable}"'
)
def assert_element_value_not_equal_to_variable(context, target, variable):
    """Проверка значения свойства value для input и textarea"""
    expected = get_from_variables(variable)
    assert_element_value_not_equal_to(context, target, expected)


@step('Я навел курсор на "{target}" с текстом "{text}"')
def hover_on_visible_in_scope_with_text(context, target, text):
    (
        context.browser.elements(locator(target))
        .filter_by_text(text)
        .should_not_have_count(0)
        .first()
        .highlight()
        .hover()
    )


@step('Я навел курсор на "{target}" содержащий текст "{text}"')
def hover_on_visible_in_scope_with_contains_text(context, target, text):
    (
        context.browser.elements(locator(target))
        .filter_by_partial_text(text)
        .should_not_have_count(0)
        .first()
        .highlight()
        .hover()
    )


@then(
    'Я убедился что среди "{target}" элемент с текстом "{text}" имеет атрибут "{attribute_name}"="{attribute_value}"'
)
def assert_element_with_text_has_attibute_value(
    context, target, text, attribute_name, attribute_value
):
    (
        context.browser.elements(locator(target))
        .filter_by_text(text)
        .filter_by_attribute_value(attribute_name, attribute_value)
        .should_not_have_count(0)
    )


@then(
    'Я убедился что среди "{target}" элемент содержащий текст "{text}" '
    'имеет атрибут "{attribute_name}"="{attribute_value}"'
)
def assert_element_with_partial_text_has_attibute_value(
    context, target, text, attribute_name, attribute_value
):
    (
        context.browser.elements(locator(target))
        .filter_by_partial_text(text)
        .filter_by_attribute_value(attribute_name, attribute_value)
        .should_not_have_count(0)
    )


@then(
    'Я убедился что среди "{target}" элемент с текстом "{text}" '
    'имеет атрибут "{attribute_name}" содержащий "{attribute_value}"'
)
def assert_element_with_text_has_partial_attibute_value(
    context, target, text, attribute_name, attribute_value
):
    (
        context.browser.elements(locator(target))
        .filter_by_text(text)
        .filter_by_partial_attribute_value(attribute_name, attribute_value)
        .should_not_have_count(0)
    )


@then(
    'Я убедился что среди "{target}" элемент содержащий текст "{text}" '
    'имеет атрибут "{attribute_name}" содержащий "{attribute_value}"'
)
def assert_element_with_partial_text_has_partial_attibute_value(
    context, target, text, attribute_name, attribute_value
):
    (
        context.browser.elements(locator(target))
        .filter_by_partial_text(text)
        .filter_by_partial_attribute_value(attribute_name, attribute_value)
        .should_not_have_count(0)
    )


@then(
    'Я убедился что среди "{target}" элемент с текстом "{text}" не доступен для нажатия'
)
def assert_target_with_text_is_not_clickable(context, target, text):
    """Проверить, что указанный элемент некликабелен (виден, но не активен)."""
    (
        context.browser.elements(locator(target))
        .filter_by_text(text)
        .should_not_have_count(0)
        .first()
        .should_be_visible()
        .should_be_disabled()
        .highlight()
    )


@then('Я убедился что среди "{target}" элемент с текстом "{text}" доступен для нажатия')
def assert_target_with_text_is_clickable(context, target, text):
    """Проверить, что указанный элемент некликабелен (виден, но не активен)."""
    (
        context.browser.elements(locator(target))
        .filter_by_text(text)
        .should_not_have_count(0)
        .first()
        .should_be_visible()
        .should_be_enabled()
        .highlight()
    )


@then(
    'Я убедился что среди "{target}" элемент содержащий текст "{text}" доступен для нажатия'
)
def assert_target_with_partial_text_is_clickable(context, target, text):
    """Проверить, что указанный элемент некликабелен (виден, но не активен)."""
    (
        context.browser.elements(locator(target))
        .filter_by_partial_text(text)
        .should_not_have_count(0)
        .first()
        .should_be_visible()
        .should_be_enabled()
        .highlight()
    )


@then(
    'Я убедился что среди "{target}" элемент содержащий текст "{text}" не доступен для нажатия'
)
def assert_target_with_partial_text_is_not_clickable(context, target, text):
    """Проверить, что указанный элемент некликабелен (виден, но не активен)."""
    (
        context.browser.elements(locator(target))
        .filter_by_partial_text(text)
        .should_not_have_count(0)
        .first()
        .should_be_visible()
        .should_be_disabled()
        .highlight()
    )


@step('Я сохранил страницу как PDF в файл "{file_name}"')
def save_page_as_pdf(context, file_name):
    context.browser.pdf(file_name)
    allure.attach.file(
        file_name, name=file_name, attachment_type=allure.attachment_type.PDF
    )


@step('Я сохранил скриншот окна в файл "{file_name}"')
def save_screenshot_as_file(context, file_name):
    context.browser.screenshot_as_file(file_name)
    allure.attach.file(
        file_name,
        name=file_name,
        attachment_type=allure.attachment_type.PNG,
    )

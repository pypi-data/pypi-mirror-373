import requests
from behave import *
from hamcrest import *

from zapp.features.core.api import Api

from jsonschema import validate, ValidationError
from zapp.features.core.utils import *

log = logging.getLogger(__name__)

EM_API_REQUEST_NOT_FOUND = "Не удалось найти результат выполнения запроса, убедитесь что шаг с запросом к api выполнен"


@when('Я выполнил {r_type} запрос к "{url}"')
@when('Я выполнил {r_type} запрос к "{url}" c аргументами {arguments}')
@when('Я выполнил {r_type} запрос к "{url}" c аргументами {arguments} и JSON из "{json_file}"')
def perform_api_request(context, r_type, url, **kwargs):
    """
    Выполнить запрос к API.

    Обязательные параметры:
    r_type - тип запроса (GET, POST, PUT, PATCH, DELETE);
    url - путь к запрашиваемому документу; можно использовать относительный (в том числе с параметром) -
    аналогично шагу для перехода по относительной ссылке.
    В этом случае в arguments (о нем ниже) нужно добавить переменные stand_var и/или link_appendix_var.
    Для того чтобы принудительно добавить статическую часть в конец url, используйте параметр
    link_postfix. Например, link_postfix = '/' добавит слэш в конец адреса. Будьте аккуратны, валидность
    url в этом случае не проверяется и не гарантируется. Используйте режим debug и проверяйте отправляемый запрос.

    Также прям в url можно прописывать свои переменные через {{имя_переменной}}. Например:
    And Я сохранил значение поля "id" из ответа с сервера в переменную "order_id"
    When Я выполнил GET запрос к "https://petstore.swagger.io/v2/store/order/{{order_id}}"

    Опционально:
    json_file - имя файла с JSON, который будет отправлен в теле запроса. По умолчанию - None.
    arguments - словарь из параметров, которые будут переданы в запрос (headers, params, data и другие,
    подробнее в документации к requests: https://requests.readthedocs.io/en/master).

    По умолчанию, если запрос вернулся с status_code = 4XX или 5XX, то он будет выполнен повторно через 5 секунд.
    Чтобы изменить это поведение, добавьте в передаваемый словарь arguments параметр "retry" со значениями
    количества попыток и задержкой между запросами. Например, {"retry":[3, 10]} означает что на запрос будет
    отведено 3 попытки с интервалом 10 секунд. Чтобы не использовать retry, передайте значение {"retry":[1, 0]}.

    Примеры:
    Я выполнил GET запрос к "https://echo.com/cookies/set?foo1=bar1&foo2=bar2"
    Я выполнил GET запрос к "https://echo.com/get" c аргументами {"params":{"foo1":"bar1"}, "retry":[3, 10]}
    Я выполнил GET запрос к "/get/" c аргументами {"stand_var": "api_host", "link_appendix_var": "parameter_id"}

    Примеры вызова из кастомных шагов:
    arguments = {"headers": {"Content-Type": "application/json"}, "json": {"fb": {"foo1": "bar1","foo2": "bar2"}}}
    context.execute_steps(f'''When Я выполнил POST запрос к "https://echo.com/get" c аргументами {arguments}''')

    with open('my_file.xml') as my_file:
        my_file_data = my_file.read()
    arguments = {"headers": {"Content-Type": "application/xml"}, "data": my_file_data}
    context.execute_steps(f'''When Я выполнил POST запрос к "https://echo.com/post" c аргументами {arguments}''')

    arguments = {"files": [('file', ('my_file.xml', open('my_file.xml', 'rb').read(), 'multipart/form-data'))]}
    context.execute_steps(f'''When Я выполнил POST запрос к "https://echo.com/post" c аргументами {arguments}''')

    Ответ записывается во внутреннюю переменную context.api_resp, чтобы работать с ним дальше, используйте шаг
    'Я сохранил ответ с сервера в переменную "{variable_name}"' или другие, указанные в документации в разделе
    "Работа с API"
    """
    # Инициализация аргументов
    arguments_str = kwargs.get("arguments", "{}")
    json_file = kwargs.get("json_file")

    # Парсинг базовых аргументов
    arguments = parse_arguments(arguments_str)
    # Подстановка значений переменных в заголовки
    if arguments.get("headers") is not None:
        arguments["headers"] = resolve_variables_in_arguments(arguments.get("headers"))

    # Добавление JSON из файла
    if json_file:
        json_data = load_json_from_file(context, json_file)
        arguments.setdefault('json', {}).update(json_data)

    # Обработка URL
    url = build_url(url, arguments)
    # Выполнение запроса
    context.api_resp = Api.request(r_type, url, **arguments)
    log.debug(f"RESPONSE HEADERS: {context.api_resp.headers}")
    try:
        log.debug(f"RESPONSE JSON: {context.api_resp.json()}")
    except json.JSONDecodeError as e:
        log.debug(f"RESPONSE JSON: None")
        pass


@then("Я убедился что с сервера пришел ответ без ошибки")
def check_api_status_code_is_ok(context):
    """Проверить, что после запроса вернулся ответ с кодом HTTP отличным от 4XX и 5XX."""
    try:
        assert_that(context.api_resp.ok, is_(True))

    except AttributeError as e:
        log.error("%s. %s", EM_API_REQUEST_NOT_FOUND, e)


@then("Я убедился что с сервера пришел ответ {status_codes_string}")
def check_api_status_code(context, status_codes_string):
    """
    Проверить, что после запроса вернулся один из ожидаемых кодов состояния HTTP.
    Примеры:
    Я убедился что с сервера пришел ответ 200
    Я убедился что с сервера пришел ответ 200 или 201
    Я убедился что с сервера пришел ответ 200, 201 или 204
    """
    try:
        assert_that(
            str(context.api_resp.status_code),
            is_in(re.findall(r"\d{3}", status_codes_string)),
        )

    except AttributeError as e:
        log.error("%s. %s", EM_API_REQUEST_NOT_FOUND, e)


@then('Я убедился что в ответе с сервера заголовок "{header_name}" имеет значение "{header_value}"')
@then('Я убедился что в ответе с сервера заголовок "{header_name}" имеет значение переменной "{variable_name}"')
def check_api_resp_header(context, **kwargs):
    """
    Сравнить значение заголовка из ответа на api запрос с указанным значением

    header_name - название заголовка
    header_value - значение, с которым сравниваем
    """
    header_value = kwargs.get("header_value") or get_from_variables(kwargs.get("variable_name"))

    try:
        found_header = get_from_headers(context.api_resp.headers, kwargs["header_name"])
        assert_that(str(found_header), equal_to(str(header_value)))

    except AttributeError as e:
        log.error("%s. %s", EM_API_REQUEST_NOT_FOUND, e)


@then('Я убедился что в ответе с сервера заголовки соответствуют значениям в таблице:')
def check_api_resp_headers_table(context):
    """
    Сравнить заголовки ответа с сервера со значениями, переданными в таблице.
    Таблица должна содержать 2 колонки:
    - заголовок ответа
    - ожидаемое значение
    Заголовки колонок обязательны, но могут быть любыми.
    """
    for row in context.table:
        check_api_resp_header(context, header_name=row[0], header_value=row[1])


@then('Я убедился что в ответе с сервера заголовки соответствуют переменным в таблице:')
def check_api_resp_headers_table_variables(context):
    """
    Сравнить заголовки ответа с сервера с переменными, переданными в таблице.
    Таблица должна содержать 2 колонки:
    - заголовок ответа
    - ожидаемое значение в переменной
    Заголовки колонок обязательны, но могут быть любыми.
    """
    for row in context.table:
        check_api_resp_header(context, header_name=row[0], variable_name=row[1])


@step('Я сохранил все заголовки ответа с сервера в переменную "{variable_name}"')
def save_api_resp(context, variable_name):
    """
    Сохранить все заголовки ответа с сервера в переменную для дальнейшего использования

    variable_name - название переменной, в которую хотим сохранить значение
    """
    save_header_from_api_resp(context, None, variable_name)


@step('Я сохранил значение заголовка "{header_name}" ответа с сервера в переменную "{variable_name}"')
def save_header_from_api_resp(context, header_name, variable_name):
    """Сохранить значение заголовка ответа с сервера в переменную"""
    try:
        resp_headers = context.api_resp.headers
        value = (
            resp_headers if header_name is None else get_from_headers(resp_headers, header_name)
        )

        if value is not None:
            variables[variable_name] = value
            log.debug('Value "%s" saved to variable "%s"', value, variable_name)

    except AttributeError as e:
        log.error(f"{EM_API_REQUEST_NOT_FOUND}. {e}")


@step('Я сохранил значения заголовков ответа с сервера в переменные по таблице:')
def save_table_fields_from_api_resp(context):
    """
    Сохранить заголовки ответа с сервера в переменные, переданными в таблице.
    Таблица должна содержать 2 колонки:
    - заголовок ответа
    - переменная для сохранения
    Заголовки колонок обязательны, но могут быть любыми.
    """
    for row in context.table:
        save_header_from_api_resp(context, header_name=row[0], variable_name=row[1])


@then('Я убедился что в ответе с сервера поле "{field_name}" имеет значение "{field_value}"')
@then('Я убедился что в ответе с сервера поле "{field_name}" имеет значение переменной "{variable_name}"')
def check_api_resp(context, **kwargs):
    """
    Сравнить значение поля из ответа на api запрос с указанным значением или переменной

    field_name - путь до поля из json: "fruits > banana > color".
    Если указано только название поля, то будет взято значение корня.
    field_value - значение, с которым сравниваем.
    ИЛИ
    variable_name - имя переменной, с которой сравниваем. Можно использовать переменную окружения
    или сохраненную ранее через шаг "Я сохранил значение элемента"
    """
    field_value = kwargs.get("field_value") or get_from_variables(
        kwargs.get("variable_name")
    )
    try:
        found_field = get_from_json(context.api_resp.json(), kwargs["field_name"])
        assert_that(str(found_field), equal_to(str(field_value)))

    except json.JSONDecodeError as e:
        log.error(
            "Произошла ошибка при попытке обработать json для сравнения со значением %s: %s",
            field_value,
            e,
        )
        assert False

    except AttributeError as e:
        log.error("%s. %s", EM_API_REQUEST_NOT_FOUND, e)


@then('Я убедился что в ответе с сервера поля соответствуют значениям в таблице:')
def check_api_resp_table(context):
    """
    Сравнить поля тела ответа с сервера со значениями, переданными в таблице.
    Таблица должна содержать 2 колонки:
    - имя поля тела ответа
    - ожидаемое значение
    Заголовки колонок обязательны, но могут быть любыми.
    """

    for row in context.table:
        check_api_resp(context, field_name=row[0], field_value=row[1])


@then('Я убедился что в ответе с сервера поля соответствуют переменным в таблице:')
def check_api_resp_table_variables(context):
    """
    Сравнить поля тела ответа с сервера с переменными, переданными в таблице.
    Таблица должна содержать 2 колонки:
    - имя поля тела ответа
    - ожидаемое значение в переменных
    Заголовки колонок обязательны, но могут быть любыми.
    """

    for row in context.table:
        check_api_resp(context, field_name=row[0], variable_name=row[1])


@step('Я сохранил ответ с сервера в переменную "{variable_name}"')
def save_api_resp(context, variable_name):
    """
    Сохранить полный ответ (JSON) на api запрос в переменную для дальнейшего использования

    variable_name - название переменной, в которую хотим сохранить значение
    """
    save_field_from_api_resp(context, None, variable_name)


@step('Я сохранил значение поля "{field_name}" из ответа с сервера в переменную "{variable_name}"')
def save_field_from_api_resp(context, field_name, variable_name):
    """
    Сохранить значение поля из ответа на api запрос в переменную для дальнейшего использования

    field_name - путь до поля из json: "fruits > [0] > color".
    Если указано только название поля, то будет взято значение корня
    variable_name - название переменной, в которую хотим сохранить значение
    """
    try:
        resp_json = context.api_resp.json()
        value = (
            resp_json if field_name is None else get_from_json(resp_json, field_name)
        )

        if value is not None:
            variables[variable_name] = value
            log.debug('Value "%s" saved to variable "%s"', value, variable_name)

    except json.JSONDecodeError as e:
        log.error(
            "Произошла ошибка при попытке обработать json для записи в переменную %s: %s",
            variable_name,
            e,
        )

    except AttributeError as e:
        log.error(f"{EM_API_REQUEST_NOT_FOUND}. {e}")


@step('Я сохранил значения полей из ответа с сервера в переменные по таблице:')
def save_table_fields_from_api_resp(context):
    """
    Сохранить поля тела ответа с сервера в переменные, переданными в таблице.
    Таблица должна содержать 2 колонки:
    - имя поля тела ответа
    - переменная для сохранения
    Заголовки колонок обязательны, но могут быть любыми.
    """
    for row in context.table:
        save_field_from_api_resp(context, field_name=row[0], variable_name=row[1])


@then('Я убедился что ответ соответствует схеме из файла "{schema_file}"')
def validate_json_schema_from_file(context, schema_file):
    """
    Валидация ответа по JSON-схеме из файла

    schema_file - имя файла схемы
    """

    try:
        schema = resolve_json_schema(schema_file)
        validate(
            instance=context.api_resp.json(),
            schema=schema
        )

    except ValidationError as e:
        raise AssertionError(f"Ошибка валидации схемы: {e.message}")

    except FileNotFoundError as e:
        raise AssertionError(f"Файл схемы не найден: {schema_file}")

    except json.JSONDecodeError as e:
        raise AssertionError(f"Ошибка в формате схемы: {str(e)}")

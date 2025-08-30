
import logging

from typing import Union

from behave import *
from hamcrest import *


from zapp.features.core.database import execute_query as pg_query

from zapp.features.core.utils import (
    variables,
)

log = logging.getLogger(__name__)

@when('Я выполнил запрос "{query}" к БД "{database_var}"')
@when('Я выполнил запрос "{query}" к БД "{database_var}" с аргументами "{args}"')
def execute_query(context, query: str, database_var: str, **kwargs):
    """
    Выполнение произвольного запроса в БД

    database_var - имя переменной, содержащей строку подключения к базе данных.
    Переменная должна содержать connection string и может храниться в Vault
    или быть передана через переменные окружения.

    На текущий момент поддерживается работа только postgresql.
        Например:
            pq://user@localhost/postgres?search_path=public

    query - произвольный SQL запрос. Возможно использование prepared statement
    args - аргументы для подстановки в prepared statement, через запятую

    Результат сохраняется для дальнейшего использования в переменной контекста db_query_result

    Пример:
    @When Я выполнил запрос "SELECT 'Hello' as fld1, $1 as fld2, $2 as smth3" к БД "db_mydatabase" с аргументами "Cruel, World"
        @And Я сохранил поле "fld2" результата запроса к БД в переменную "myvar"
        @And Я сохранил поле "smth3" результата запроса к БД в переменную "myvar2"

    В результате выполнения, переменная myvar будет содержать "Cruel",
    а переменная myvar2 - "World"
    """

    query_args = []
    args = kwargs.pop("args", None)

    if args is not None:
        query_args_raw = args.split(",")
        query_args = [arg.strip() for arg in query_args_raw]

    connection_string = variables[database_var]
    res = pg_query(connection_string, query, *query_args)
    log.debug("Database Query result: %s", res)
    context.db_query_result = res


@when(
    'Я сохранил поле "{field}" результата запроса к БД в переменную "{variable_name}"'
)
def save_query_result(context, field: Union[int, str], variable_name: str):
    """
    Сохранение поля результата выполнения запроса в переменную

    field: Имя или номер поля в строке результата запроса
    variable_name: Имя переменной в которую необходимо сохранить результат

    Пример:
    @When Я выполнил запрос "SELECT 'Hello' as fld1, 'World' as fld2" к БД "db_mydatabase"
        @And Я сохранил поле "fld1" результата запроса к БД в переменную "myvar"

    В результате выполнения, переменная myvar будет содержать "Hello"
    """

    variables[variable_name] = context.db_query_result[field]
    log.debug('Variable "%s" saved: %s', variable_name, variables[variable_name])

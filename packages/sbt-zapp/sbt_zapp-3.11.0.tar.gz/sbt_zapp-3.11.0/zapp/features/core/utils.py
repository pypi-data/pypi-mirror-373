import array
import ast
import base64
import hashlib
import hmac
import logging
import os
import random
import re
import time
from typing import Mapping, Sequence, TypeVar
from urllib.parse import urljoin
import json

import validators
from requests.structures import CaseInsensitiveDict

from zapp.features.core.settings import (
    FILE_ENCODING,
    PROJECT_KEY,
    JSONS_DIR,
    SCHEMAS_DIR,
)

T = TypeVar("T")

log = logging.getLogger(__name__)

variables = CaseInsensitiveDict(**os.environ)


class InvalidURLError(Exception):
    pass


def raise_if_not_valid_url(stand):
    validation_result = validators.url(stand)
    if isinstance(validation_result, Exception):
        error = InvalidURLError(
            "Параметр STAND/TEST_STAND должен содержать валидный URL"
        )
        log.exception(error)
        raise error from validation_result
    return stand


def generate_tranzact_number():
    return random.randint(100000000, 9999999999) * 10


def generate_phone_code():
    project_hash = int(hashlib.sha256(PROJECT_KEY.encode("utf-8")).hexdigest(), 16)
    return "5" + str(project_hash)[-2:]


def strip_phone_number(number_text):
    phone = re.sub(r"(\+\s?7|[ ()\-])", "", number_text)
    return f"7{phone}" if len(phone) < 11 else phone


def format_delay(delay: str) -> float:
    return float(delay.replace(",", "."))


def truncate(hmac_sha1):
    offset = int(hmac_sha1[-1], 16)
    binary = int(hmac_sha1[(offset * 2) : ((offset * 2) + 8)], 16) & 0x7FFFFFFF
    return str(binary)


def long_to_byte_array(long_num):
    byte_array = array.array("B")
    for _ in reversed(range(0, 8)):
        byte_array.insert(0, long_num & 0xFF)
        long_num >>= 8
    return byte_array


def hotp(key, counter, digits=6):
    counter_bytes = long_to_byte_array(counter)
    hmac_sha1 = hmac.new(key=key, msg=counter_bytes, digestmod=hashlib.sha1).hexdigest()
    return truncate(hmac_sha1)[-digits:]


def totp(key, digits=6, window=30):
    key = base64.b32decode(key, True)
    counter = int(time.time() / window)
    return hotp(key, counter, digits=digits)


def get_last_downloaded_file(context):
    time_counter = 0
    while True:
        time.sleep(1)
        dirs = os.listdir(context.tempdir)

        if not dirs:
            return

        filename = max(
            [f for f in dirs if not f.startswith(".")],
            key=lambda xa: os.path.getctime(os.path.join(context.tempdir, xa)),
        )
        if time_counter > context.browser.timeout.total_seconds():
            raise Exception("Waited too long for file to download")
        time_counter += 1
        if not (".part" or ".crdownload") in filename:
            break

    log.debug("FILENAME: %s", filename)
    downloaded_file_path = os.path.join(context.tempdir, filename)
    return downloaded_file_path


def get_md5_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_from_variables(name):
    value = get_field_by_chain(name, variables)

    if value is not None:
        log.debug(f'VARIABLES "{name}": {value}')
    else:
        log.error(f'Не найдено значение переменной "{name}"')

    return value


def parse_arguments(arguments_str):
    """Парсинг аргументов из строки в словарь"""
    try:
        # Замена JSON-значений перед парсингом
        fixed_str = (
            arguments_str.replace("true", "True")
            .replace("false", "False")
            .replace("null", "None")
        )
        return ast.literal_eval(fixed_str)
    except (ValueError, SyntaxError) as e:
        log.error(f"Ошибка парсинга аргументов: {arguments_str}")
        raise


def load_json_from_file(context, json_file):
    """Загрузка JSON из файла"""
    try:
        json_path = os.path.join(JSONS_DIR, json_file)
        with open(json_path, "r", encoding=FILE_ENCODING) as f:
            result = json.load(f)
            log.debug(f"JSON: {result}")
            return result
    except Exception as e:
        log.error(f"Ошибка загрузки JSON файла: {json_file}")
        raise


def build_url(url, arguments):
    """Построение полного URL"""
    base_url = get_absolute_url(
        url, arguments.pop("stand_var", None), arguments.pop("link_appendix_var", None)
    )
    return base_url + arguments.pop("link_postfix", "")


def get_field_by_chain(key_string, structure):
    if key_string is None or structure is None:
        return

    keys = re.split("[,.>]", key_string)

    while len(keys) > 0:
        key = keys.pop(0).strip()
        match = re.findall(r"\[(\d+)]", key)

        if match and isinstance(structure, Sequence):
            structure = structure[int(match[0])]

        elif isinstance(structure, Mapping):
            structure = structure.get(key)

        else:
            structure = None
            break

    return structure


def get_from_headers(headers, name):
    """Получение значения из заголовков"""
    log.debug(f"HEADERS: {headers}")
    result = headers.get(name)
    log.debug(f'FOUND IN HEADERS: "{name}": {result}')
    return result


def get_from_json(data, name):
    log.debug(f"JSON: {data}")
    result = get_field_by_chain(name, data)
    log.debug(f'FOUND IN JSON: "{name}": {result}')
    return result


def get_absolute_url(link, stand_var=None, link_appendix_var=None):
    test_stand = (
        get_from_variables(stand_var)
        if stand_var
        else get_from_variables("context_host")
    )
    link_appendix = (
        get_from_variables(link_appendix_var) if link_appendix_var is not None else ""
    )
    return urljoin(test_stand, urljoin(link, str(link_appendix)))


def resolve_variables_in_arguments(arguments):
    """ "Подстановка переменных в аргументы"""
    for argument_name, argument_value in arguments.items():
        if argument_value in variables.keys():
            arguments[argument_name] = get_from_variables(argument_value)
    return arguments


def get_abs_file_path_from_cwd(relative_file_path):
    current_dir = os.getcwd()
    absolute_file_path = os.path.normpath(os.path.join(current_dir, relative_file_path))
    log.debug(f"Absolute path for '{relative_file_path}': '{absolute_file_path}'")
    return absolute_file_path


def generate_valid_snils() -> str:
    snils_number = str(random.randint(5001001999, 5999999999))[1:]
    control_sum = 0
    for index, digit in zip(range(9, 0, -1), snils_number):
        control_sum += index * int(digit)

    if control_sum > 101:
        control_sum %= 101

    snils_code = "{:02}".format(control_sum) if control_sum < 100 else "00"
    return snils_number + snils_code


def slugify(input_str: str) -> str:
    slug = []
    for symbol in input_str:
        code = ord(symbol) % 128
        symbol = "-"
        if 48 < code < 58 or 64 < code < 91 or 96 < code < 123:
            symbol = chr(code)

        slug.append(symbol)

    return "".join(slug)


def resolve_variables(value):
    """Подстановка переменных в URL, если они заданы в шаге как {{имя_переменной}}"""
    if isinstance(value, str) and "{{" in value:
        for var_name, var_value in variables.items():
            value = value.replace("{{%s}}" % var_name, str(var_value))
    return value


def resolve_json_schema(schema_file):
    schema_path = os.path.join(SCHEMAS_DIR, schema_file)
    with open(schema_path, "r", encoding=FILE_ENCODING) as f:
        return json.load(f)


def bytes_to_file(bytes_data: bytes, file_name: str, decode: bool = False):
    prepared_bytes = bytes_data if not decode else base64.b64decode(bytes_data)
    with open(file_name, "wb") as file:
        file.write(prepared_bytes)

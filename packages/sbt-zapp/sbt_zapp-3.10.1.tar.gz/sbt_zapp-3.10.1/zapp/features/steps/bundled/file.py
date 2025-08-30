import logging
import os

from behave import *
from hamcrest import *

from zapp.driver import (
    REMOTE_EXECUTOR,
)
from zapp.features.core.locators import get_locator as locator
from zapp.features.core.utils import (
    get_last_downloaded_file,
    get_md5_hash,
    get_from_variables,
    get_abs_file_path_from_cwd,
)

log = logging.getLogger(__name__)


def fill(context, target, value):
    context.browser.element(locator(target)).highlight().fill(value)


@when('Я загрузил файл "{file_path}", в форму "{target}"')
def file_upload_absolute(context, file_path, target):
    """Записывает абсолютный путь до файла в поле загрузки файла."""
    fill(context, target, file_path)


@when('Я загрузил несколько файлов "{file_list}" в форму "{target}"')
def file_multi_upload_absolute(context, file_list, target):
    """Записывает абсолютные пути до файлов в поле загрузки файла, разделитель - символ ";"."""
    file_path_list_string = file_list.replace(";", "\n")
    fill(context, target, file_path_list_string)


@when(
    'Я загрузил файл по пути относительно корня установки zapp "{relative_file_path}", в форму "{target}"'
)
def file_upload_relative(context, relative_file_path, target):
    """
    Записывает путь до файла относительно папки с zapp в поле загрузки файла,
    например: "features/files/file1.jpg".
    """
    current_dir = os.getcwd()
    log.debug("CURRENT DIRECTORY: %s", current_dir)
    absolute_file_path = os.path.normpath(os.path.join(current_dir, relative_file_path))
    fill(context, target, absolute_file_path)


@when(
    'Я загрузил несколько файлов по пути относительно корня установки zapp "{relative_path_list}" в форму "{target}"'
)
def file_multi_upload_relative(context, relative_path_list, target):
    """
    Записывает пути до файлов относительно папки с zapp в поле загрузки файла, разделитель - символ ";",
    например: "features/files/file1.jpg;features/files/file2".
    """
    relative_file_path_list = relative_path_list.split(";")
    abs_file_path_list = [
        get_abs_file_path_from_cwd(file_path) for file_path in relative_file_path_list
    ]
    file_list_string = "\n".join(abs_file_path_list)
    log.debug(file_list_string)
    fill(context, target, file_list_string)


@when('Я загрузил последний скачанный файл в форму "{target}"')
def downloaded_file_upload(context, target):
    """
    Записывает абсолютный путь до наиболее свежего файла во временной директории ОС в поле загрузки файла.
    Пытается ожидать окончания загрузки файла в течение выставленной задержки ожидания элементов.
    Шаг работает только локально.
    """
    if REMOTE_EXECUTOR:
        log.warning(
            f"Шаг {context.current_step['name']} не может быть выполнен на удаленной машине"
        )
        return

    downloaded_file_path = get_last_downloaded_file(context)

    if downloaded_file_path is None:
        log.error(f"Не удалось найти файлы в директории {context.tempdir}")

    else:
        log.debug("UPLOADING: %s", downloaded_file_path)
        fill(context, target, downloaded_file_path)


@then(
    'Я убедился что у последнего скачанного файла MD5 совпадает со значением "{checksum}"'
)
@then(
    'Я убедился что у последнего скачанного файла MD5 совпадает со значением из переменной "{variable_name}"'
)
def check_md5(context, **kwargs):
    """
    Пытается ожидать окончания загрузки файла в течение выставленной задержки ожидания элементов.
    Если файл найден во временной директории - сравнивает его MD5 с переданным в тест значением.
    Шаг работает только локально.
    """
    if REMOTE_EXECUTOR:
        log.warning(
            f"Шаг {context.current_step['name']} не может быть выполнен на удаленной машине"
        )
        return

    checksum = kwargs.get("checksum")

    if not checksum:
        name = kwargs.get("variable_name")
        checksum = get_from_variables(name)

    if checksum:
        file = get_last_downloaded_file(context)
        log.debug(f'Checking MD5: "{file}"')
        if file:
            generated_hash = get_md5_hash(file)
            log.debug(f'Calculated MD5: "{generated_hash}"')

            assert_that(generated_hash, equal_to(checksum))
        else:
            raise Exception("В каталоге временных загрузок нет файлов")
    else:
        raise Exception("Не найдена контрольная сумма для сравнения")

import logging
import importlib
import os
from typing import Mapping

from zapp.features.core.settings import (
    LOCATORS_DIR,
    LOCATORS_FILE_POSTFIX,
)

_EM_LOCATOR_NOT_FOUND = "Не найден локатор с именем {}. Убедитесь, что локатор добавлен в один из файлов {}*{}"

log = logging.getLogger(__name__)

def import_locators(
    path: str = LOCATORS_DIR,
    postfix: str = LOCATORS_FILE_POSTFIX,
    name: str = "locators",
):
    locators = {}
    for current_dir, _, files in os.walk(path):
        for file in files:
            if file.endswith(postfix):
                module_name = f'{current_dir}.{file.rstrip(".py")}'.replace("/", ".")
                module = importlib.import_module(module_name)
                imported_locators = getattr(module, name, None)

                if imported_locators and isinstance(imported_locators, Mapping):
                    overridden_keys = locators.keys() & imported_locators.keys()
                    locators.update(imported_locators)

                    if overridden_keys:
                        log.warning(
                            "Обнаружены пересечения в словарях локаторов, проверьте поля %s. Один из "
                            "дубликатов в файле %s",
                            overridden_keys,
                            file,
                        )

    return locators

_LOCATORS = import_locators()

def get_locator(target: str) -> str:
    result = _LOCATORS.get(target, None)
    if result is None:
        raise AttributeError(
            _EM_LOCATOR_NOT_FOUND.format(target, LOCATORS_DIR, LOCATORS_FILE_POSTFIX)
        )
    return result

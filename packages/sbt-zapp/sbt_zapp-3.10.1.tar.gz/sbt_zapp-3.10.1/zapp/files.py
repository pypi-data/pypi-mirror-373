import json
import pathlib
import os
import shutil

from zapp.features.core.logging import Color

zapp_path = pathlib.Path(__file__).parent.resolve()
print(Color.BOLD_CYAN.wrap(f"ZAPP_PATH: {zapp_path}"))


def copy_behave_files_if_needed(*paths):
    target = os.path.join(*paths)
    if not os.path.exists(target):
        shutil.copy(os.path.join(zapp_path, target), os.path.join("./", *paths[:-1]))
        print(Color.success(f"Файл был успешно скопирован: {target}"))


def delete_dir(*paths):
    dir_to_del = os.path.join("./", *paths)
    if os.path.isdir(dir_to_del):
        shutil.rmtree(dir_to_del)
        print(Color.success(f"Директория успешно удалена: {dir_to_del}"))


def load_config(filename, encoding: str):
    """Загрузить параметры из json-конфига, последующий фойл переопределяет значения предыдущего"""
    files = filename.split(",")
    data = {}
    for file in files:
        try:
            with open(file, "r", encoding=encoding) as json_file:
                json_data = json.load(json_file)
                data.update(json_data)
                print(Color.success(f"Загружены настройки из файла {file}"))
        except FileNotFoundError:
            print(
                Color.YELLOW.wrap(
                    f"Файл {file} не найден в корневой директории проекта!"
                )
            )
    return data


def get_log_config_file_path():
    return os.path.join(zapp_path, "zapp_logging.ini")

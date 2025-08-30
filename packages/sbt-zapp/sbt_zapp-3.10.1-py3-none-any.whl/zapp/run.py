import logging
import os
import sys
import urllib3

from behave.__main__ import main as behave_main
from envparse import env

from zapp.arguments import (
    CONFIG_PARAM,
    CONFIG_ENCODING_PARAM,
    construct_behave_args,
    inner_struct_to_str,
    parse_cli_args,
    print_args,
)
from zapp.features.core.logging import configure_logging, Color
from zapp.files import (
    copy_behave_files_if_needed,
    delete_dir,
    get_log_config_file_path,
    load_config,
)

from zapp.behave.context import override_context_execute_steps_method


def get_env():
    env = os.environ
    env["PYTHONIOENCODING"] = "utf_8"
    env["PYTHONHOME"] = ""
    venv_path = os.path.dirname(sys.executable)
    env["PATH"] = venv_path + os.pathsep + env["PATH"]
    return env


def configure_runtime():
    configure_logging(
        get_log_config_file_path(),
        logging.DEBUG if env.bool("DEBUG", default=False) else logging.INFO,
    )

    if env.bool("DISABLE_INSECURE_WARNING", default=True):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if env.bool("ADD_SUBSTEPS_TO_ALLURE", default=True):
        override_context_execute_steps_method()


def run_behave():
    copy_behave_files_if_needed("behave.ini")
    copy_behave_files_if_needed("features", "environment.py")
    delete_dir("allure")

    # Получаем все аргументы, переданные через командную строку
    # declared_keys -- содержит все возможные заранее описанные ключи
    # declared_args -- только те, что в итоге были переданы (не None)
    declared_keys, declared_args, dynamic_args = parse_cli_args()
    # Загружаем параметры из конфиг-файлов
    config_args = load_config(
        declared_args.pop(CONFIG_PARAM), declared_args.pop(CONFIG_ENCODING_PARAM)
    )
    # Накладываем параметры из командной строки поверх конфига
    args = {**config_args, **declared_args, **dynamic_args}
    print_args(args)

    declared_keys.remove(CONFIG_PARAM)
    declared_keys.remove(CONFIG_ENCODING_PARAM)
    # Получаем behave-параметры с учетом данных из конфига, а не только cmd
    behave_run_params = construct_behave_args(args, declared_keys)

    # Исключаем из аргументов behave-параметры, остаются только пользовательские из конфига и командной строки
    args_for_env = {
        key: value for key, value in args.items() if key not in declared_keys
    }

    # Теперь все значения мы можем получать через env.str и т. д.
    os.environ = {**get_env(), **inner_struct_to_str(args_for_env)}

    configure_runtime()

    print(Color.PURPLE.success(f"Running behave with args: {behave_run_params}"))
    return behave_main(behave_run_params)


if __name__ == "__main__":
    run_behave()

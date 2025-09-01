import argparse
import json

from zapp.features.core.logging import Color


from behave.configuration import OPTIONS as BEHAVE_OPTIONS

CONFIG_PARAM = "config"
CONFIG_ENCODING_PARAM = "config-encoding"


def configure_parser() -> argparse.ArgumentParser:
    # Behave
    # https://behave.readthedocs.io/en/latest/behave/#command-line-arguments
    parser = argparse.ArgumentParser(description="Run ZAPP")
    for fixed, keywords in BEHAVE_OPTIONS:
        if not fixed:
            continue

        keywords = dict(keywords)
        keywords.pop("config_help", None)
        keywords["default"] = None
        keywords["dest"] = None
        parser.add_argument(*fixed, **keywords)

    # ZAPP
    parser.add_argument(
        f"--{CONFIG_PARAM}",
        type=str,
        help="config file name",
        default="zapp.config.json",
    )
    parser.add_argument(
        f"--{CONFIG_ENCODING_PARAM}",
        type=str,
        help="config file encoding",
        default="utf-8",
    )
    return parser


def parse_cli_args() -> tuple[list, dict, dict]:
    """Получить все параметры, переданные через аргументы командной строки при запуске скрипта"""

    declared_parser = configure_parser()
    declared_before_args, unknown = declared_parser.parse_known_args()
    declared_before_original_args = reset_arg_names_to_original(
        vars(declared_before_args)
    )

    dynamic_parser = configure_to_parse_dynamic_args(unknown)
    dynamic_args, _ = dynamic_parser.parse_known_args()
    return (
        list(declared_before_original_args.keys()),
        remove_none_args(declared_before_original_args),
        vars(dynamic_args),
    )


def remove_none_args(args: dict):
    return {key: value for key, value in args.items() if value is not None}


def reset_arg_names_to_original(args: dict):
    # При парсинге имен аргументов дефис заменяется на нижнее подчеркивание. Возвращаем обратно
    return {key.replace("_", "-"): value for key, value in args.items()}


def configure_to_parse_dynamic_args(unknown) -> argparse.ArgumentParser:
    dynamic_args_parser = argparse.ArgumentParser()
    # Добавляем все кастомные аргументы в парсер
    new_args = {}
    for arg in unknown:
        if arg[0:2] == "--":
            # Обрабатываем ситуацию, когда аргументы передаются через '='
            name_end = arg.find("=")
            arg_name = arg
            if name_end >= 0:
                arg_name = arg[0:name_end]
            # Если аргумент уже есть, то присваиваем ему значение append, чтобы парсер брал из него массив
            if arg_name not in new_args:
                new_args[arg_name] = "store"
    for arg_name in new_args:
        dynamic_args_parser.add_argument(arg_name, type=str, action=new_args[arg_name])
    return dynamic_args_parser


def print_args(args):
    print(Color.BOLD_BLUE.wrap("=====ARGUMENTS====="))
    for key, value in args.items():
        value_to_print = "********" if is_need_to_be_masked(key) else value
        print(f"{Color.BLUE.wrap(key)}: {value_to_print}")


def is_need_to_be_masked(key_name) -> bool:
    words = ["password", "token", "secret", "key"]
    return any(word in key_name.lower() for word in words)


def filter_by_keys(args: dict, keys: list):
    return {key: value for key, value in args.items() if key in keys}


def construct_behave_args(args: dict, desired_keys: list) -> list:
    behave_args = []

    for key, value in filter_by_keys(args, desired_keys).items():
        if not value:
            continue
        if isinstance(value, bool):
            behave_args.append(f"--{key}")
        elif isinstance(value, list):
            for value_entry in value:
                behave_args.append(f"--{key}={value_entry}")
        else:
            behave_args.append(f"--{key}={value}")

    return behave_args


def inner_struct_to_str(args: dict) -> dict:
    copy = {}
    """Проблема использования вложенных полей/массивов в переменных среды возникает при запуске webdriver: тот ожидает только плоские данные"""
    for key, value in args.items():
        copy[key] = (
            json.dumps(value)
            if isinstance(value, dict) or isinstance(value, list)
            else value
        )
    return copy

import re

from envparse import env

STAND = TEST_STAND = env.str("TEST_STAND")

PROJECT_KEY = PROJECT = env.str("PROJECT")
if not re.match(r"^[A-Z]+$", PROJECT_KEY):
    raise Exception(
        "Параметр PROJECT должен содержать идентификатор проекта в том виде, в котором он указывается"
        + "в строке URL в Jira (большими латинскими буквами)"
    )

ENV = env.str("ENV", default="QA")
if not re.match(r"^(QA|STAGE|PROD)$", ENV):
    raise Exception("Параметр ENV может принимать значения QA, STAGE или PROD")

LOCATORS_DIR = env.str("LOCATORS_DIR", default="features/steps")
LOCATORS_FILE_POSTFIX = env.str("LOCATORS_FILE_POSTFIX", default="_locators.py")

SCHEMAS_DIR = env.str("SCHEMAS_DIR", default="resources/schemas")
JSONS_DIR = env.str("JSONS_DIR", default="resources/jsons")

RETRY_AFTER_FAIL = env.bool("RETRY_AFTER_FAIL", default=False)
MAX_ATTEMPTS = env.int("MAX_ATTEMPTS", default=2)

FILE_ENCODING = env.str("FILE_ENCODING", default="utf-8")

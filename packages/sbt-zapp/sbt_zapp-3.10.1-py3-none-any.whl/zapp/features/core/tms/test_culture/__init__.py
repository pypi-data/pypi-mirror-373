from envparse import env

TEST_CULTURE_INTEGRATION_ENABLED = env.bool(
    "TEST_CULTURE_INTEGRATION_ENABLED", default=False
)
TEST_CULTURE_UPDATE_TEST_CASE = env.bool("TEST_CULTURE_UPDATE_TEST_CASE", default=False)
TEST_CULTURE_TOKEN = env.str("TEST_CULTURE_TOKEN", default=None)
TEST_CULTURE_USERNAME = env.str("TEST_CULTURE_USERNAME", default=None)
TEST_CULTURE_PASSWORD = env.str("TEST_CULTURE_PASSWORD", default=None)
TEST_CULTURE_SPACE = env.str("TEST_CULTURE_SPACE", default=None)
TEST_CULTURE_URL = env.str(
    "TEST_CULTURE_URL", default="https://portal.works.prod.sbt/swtr/"
)
TEST_CULTURE_DEFAULT_FOLDER_CODE = env.str(
    "TEST_CULTURE_DEFAULT_FOLDER_CODE", default=f"{TEST_CULTURE_SPACE}_test_case"
)
TEST_CULTURE_DEFAULT_LABEL_NAME = env.str(
    "TEST_CULTURE_DEFAULT_LABEL_NAME", default="label"
)
TEST_CULTURE_ATTRIBUTE_PRODUCT_CODE = env.str("TEST_CULTURE_ATTRIBUTE_PRODUCT_CODE", default=None)
TEST_CULTURE_ATTRIBUTE_COMPONENT_CODE = env.str("TEST_CULTURE_ATTRIBUTE_COMPONENT_CODE", default=None)

_mandatory_parameters = {
    "TEST_CULTURE_SPACE": TEST_CULTURE_SPACE,
    "TEST_CULTURE_URL": TEST_CULTURE_URL,
    "TEST_CULTURE_DEFAULT_FOLDER_CODE": TEST_CULTURE_DEFAULT_FOLDER_CODE,
    "TEST_CULTURE_DEFAULT_LABEL_NAME": TEST_CULTURE_DEFAULT_LABEL_NAME,
}

if TEST_CULTURE_INTEGRATION_ENABLED:
    for name, value in _mandatory_parameters.items():
        if not value:
            raise ValueError(f"Параметр {name} не задан")

    if TEST_CULTURE_DEFAULT_LABEL_NAME == "allure.link.tms":
        raise ValueError("Параметр TEST_CULTURE_DEFAULT_LABEL_NAME задан некорректно")

    if not TEST_CULTURE_TOKEN and (
            not TEST_CULTURE_USERNAME or not TEST_CULTURE_PASSWORD
    ):
        raise ValueError(
            "Параметры TEST_CULTURE_TOKEN или TEST_CULTURE_USERNAME и TEST_CULTURE_PASSWORD не заданы"
        )

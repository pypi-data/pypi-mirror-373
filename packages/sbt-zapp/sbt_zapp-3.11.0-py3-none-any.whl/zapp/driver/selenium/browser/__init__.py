from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

_BROWSER_NAME_FIELD_NAME = "browserName"

CHROMIUM_BROWSER_NAMES = [
    DesiredCapabilities.EDGE[_BROWSER_NAME_FIELD_NAME],
    DesiredCapabilities.CHROME[_BROWSER_NAME_FIELD_NAME],
]

BIDI_LOGS_BROWSER_NAMES = [
    DesiredCapabilities.FIREFOX[_BROWSER_NAME_FIELD_NAME],
    # BiDi есть и у CHROMIUM_BROWSER_NAMES, но на данный момент с хромом корректно не работает получение логов
]

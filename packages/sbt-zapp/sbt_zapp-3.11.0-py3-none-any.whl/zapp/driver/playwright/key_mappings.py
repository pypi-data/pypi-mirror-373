from selenium.webdriver.common.keys import Keys

# Маппинг Selenium Keys => KeyboardEvent.key
SELENIUM_KEYS_TO_KEYBOARD_EVENT_MAP = {
    # Основные клавиши
    Keys.NULL: "",
    Keys.CANCEL: "Cancel",
    Keys.HELP: "Help",
    Keys.BACKSPACE: "Backspace",
    Keys.TAB: "Tab",
    Keys.CLEAR: "Clear",
    Keys.RETURN: "Enter",  # Enter key
    Keys.ENTER: "Enter",  # Same as RETURN for consistency
    Keys.SHIFT: "Shift",
    Keys.CONTROL: "Control",
    Keys.ALT: "Alt",
    Keys.PAUSE: "Pause",
    Keys.ESCAPE: "Escape",
    Keys.SPACE: " ",
    Keys.PAGE_UP: "PageUp",
    Keys.PAGE_DOWN: "PageDown",
    Keys.END: "End",
    Keys.HOME: "Home",
    Keys.LEFT: "ArrowLeft",
    Keys.UP: "ArrowUp",
    Keys.RIGHT: "ArrowRight",
    Keys.DOWN: "ArrowDown",
    Keys.INSERT: "Insert",
    Keys.DELETE: "Delete",
    Keys.SEMICOLON: ";",
    Keys.EQUALS: "=",
    # Цифровые клавиши
    Keys.NUMPAD0: "Numpad0",
    Keys.NUMPAD1: "Numpad1",
    Keys.NUMPAD2: "Numpad2",
    Keys.NUMPAD3: "Numpad3",
    Keys.NUMPAD4: "Numpad4",
    Keys.NUMPAD5: "Numpad5",
    Keys.NUMPAD6: "Numpad6",
    Keys.NUMPAD7: "Numpad7",
    Keys.NUMPAD8: "Numpad8",
    Keys.NUMPAD9: "Numpad9",
    Keys.MULTIPLY: "*",
    Keys.ADD: "+",
    Keys.SUBTRACT: "-",
    Keys.DECIMAL: ".",
    Keys.DIVIDE: "/",
    #
    Keys.F1: "F1",
    Keys.F2: "F2",
    Keys.F3: "F3",
    Keys.F4: "F4",
    Keys.F5: "F5",
    Keys.F6: "F6",
    Keys.F7: "F7",
    Keys.F8: "F8",
    Keys.F9: "F9",
    Keys.F10: "F10",
    Keys.F11: "F11",
    Keys.F12: "F12",
    #
    Keys.META: "Meta",
    Keys.COMMAND: "Meta",  # On MacOS Meta is Command
}


def get_keyboard_event(selenium_key):
    return SELENIUM_KEYS_TO_KEYBOARD_EVENT_MAP.get(selenium_key, selenium_key)

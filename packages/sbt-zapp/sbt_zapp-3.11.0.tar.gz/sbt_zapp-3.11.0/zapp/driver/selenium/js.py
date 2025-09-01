from ..js_func import (
    CREATE_MOUSE_EVENT,
    GET_ELEMENT_CENTER,
    SLEEP,
    MOVE_BY_STEPS,
)

OUTLINE = """
if (window.outlineElement) {
    window.outlineElement.style.cssText = window.outlineElement.style.cssText.replace(/outline: [A-z 0-9]+!important;/, '');
}
window.outlineElement = self;
window.outlineElement.style.cssText = window.outlineElement.style.cssText + '; outline: 2px fuchsia solid !important;'
window.outlineElement.scrollIntoView({
    block: "center"
});
"""

OUTLINE_LIST = """
if (window.locatorElements) {
    window.locatorElements.forEach(function (locatorElement) {
        locatorElement.style.cssText = locatorElement.style.cssText.replace(/outline: [A-z 0-9]+!important;/, '');
    });
}
window.locatorElements = arguments[0];
window.locatorElements.forEach(function (locatorElement) {
    locatorElement.scrollIntoView({
        block: "center"
    });
    locatorElement.style.cssText = locatorElement.style.cssText + '; outline: 2px fuchsia solid !important;'
});
"""

GET_TEXT = """
switch (self.nodeName.toLowerCase()) {
    case 'input':
    case 'textarea':
        return self.value;
    default:
        return self.innerText;
}
"""

CLICK = "self.click();"
SCROLL_BY = "self.scrollBy(arguments[0],arguments[1])"
WINDOW_SCROLL_BY = "window.scrollBy(arguments[0],arguments[1])"
WINDOW_SCROLL_TO = "window.scrollTo(arguments[0],arguments[1])"
DOCUMENT_READY_STATE = "return document.readyState;"
CLEAR = "self.value = '';"

SCROLL_INTO_VIEW = (
    "self.scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});"
)

DRAG_AND_DROP_TO_BY_STEPS = f"""
    const source = arguments[0];
    const target = arguments[1];
    const steps = arguments[2];
    const delay = arguments[3];
    const callback = arguments[4];

    {CREATE_MOUSE_EVENT}
    {GET_ELEMENT_CENTER}
    {SLEEP}
    {MOVE_BY_STEPS}

    const start = getCenter(source);
    const end = getCenter(target);

    (async () => {{
        source.dispatchEvent(createEvent('mousedown', start.x, start.y));

        await sleep(delay);
        await move(target, end.x - start.x, end.y - start.y, steps, delay);

        target.dispatchEvent(createEvent('mouseup', end.x, end.y));
        callback();
    }})();
"""

DRAG_AND_HOVER_ON_BY_STEPS = f"""
    const source = arguments[0];
    const target = arguments[1];
    const steps = arguments[2];
    const delay = arguments[3];
    const callback = arguments[4];

    {CREATE_MOUSE_EVENT}
    {GET_ELEMENT_CENTER}
    {SLEEP}
    {MOVE_BY_STEPS}

    const start = getCenter(source);
    const end = getCenter(target);

    (async () => {{
        source.dispatchEvent(createEvent('mousedown', start.x, start.y));

        await sleep(delay);
        await move(target, end.x - start.x, end.y - start.y, steps, delay);
        callback();
    }})();
"""

HOVER_ON_AND_DROP_TO_BY_STEPS = f"""
    const source = arguments[0];
    const target = arguments[1];
    const steps = arguments[2];
    const delay = arguments[3];
    const callback = arguments[4];

    {CREATE_MOUSE_EVENT}
    {GET_ELEMENT_CENTER}
    {SLEEP}
    {MOVE_BY_STEPS}

    const start = getCenter(source);
    const end = getCenter(target);

    (async () => {{
        await move(target, end.x - start.x, end.y - start.y, steps, delay);

        source.dispatchEvent(createEvent('mouseup', end.x, end.y));
        callback();
    }})();
"""

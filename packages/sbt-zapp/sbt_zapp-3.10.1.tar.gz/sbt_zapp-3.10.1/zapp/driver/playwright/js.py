from ..js_func import (
    CREATE_MOUSE_EVENT,
    GET_ELEMENT_CENTER,
    SLEEP,
    MOVE_BY_STEPS,
)

OUTLINE = """self => {
if (window.outlineElement) {
    window.outlineElement.style.cssText = window.outlineElement.style.cssText.replace(/outline: [A-z 0-9]+!important;/, '');
}
window.outlineElement = self;
window.outlineElement.style.cssText = window.outlineElement.style.cssText + '; outline: 2px fuchsia solid !important;'
window.outlineElement.scrollIntoView({
    block: "center"
});
}
"""

OUTLINE_LIST = """self => {
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
}
"""

GET_TEXT = """self => {
switch (self.nodeName.toLowerCase()) {
    case 'input':
    case 'textarea':
        return self.value;
    default:
        return self.innerText;
}
}
"""

CLICK = "self => self.click();"
WINDOW_SCROLL_TO = "([x,y]) => window.scrollTo(x,y)"
CLEAR_LOCAL_STORAGE = "() => window.localStorage.clear()"
CLEAR_SESSION_STORAGE = "() => window.sessionStorage.clear()"
CLEAR = "self => self.value = '';"

SCROLL_INTO_VIEW = (
    "self => self.scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});"
)

DRAG_AND_DROP_TO_BY_STEPS = f"""(source, [target, steps, delay]) => {{
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
    }})();
}}
"""

DRAG_AND_HOVER_ON_BY_STEPS = f"""(source, [target, steps, delay]) => {{
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
    }})();
}}
"""

HOVER_ON_AND_DROP_TO_BY_STEPS = f"""(source, [target, steps, delay]) => {{
    {CREATE_MOUSE_EVENT}
    {GET_ELEMENT_CENTER}
    {SLEEP}
    {MOVE_BY_STEPS}

    const start = getCenter(source);
    const end = getCenter(target);

    (async () => {{
        await move(target, end.x - start.x, end.y - start.y, steps, delay);

        target.dispatchEvent(createEvent('mouseup', end.x, end.y));
    }})();
}}
"""

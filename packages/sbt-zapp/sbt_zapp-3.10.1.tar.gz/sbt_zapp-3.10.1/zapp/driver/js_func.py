CREATE_MOUSE_EVENT = """
const createEvent = (type, clientX, clientY) => {
    return new MouseEvent(type, {
        bubbles: true,
        cancelable: true,
        view: window,
        clientX: clientX,
        clientY: clientY,
    });
};
"""

GET_ELEMENT_CENTER = """
const getCenter = (element) => {
    const rect = element.getBoundingClientRect();
    return {
        x: Math.round(rect.left + rect.width / 2),
        y: Math.round(rect.top + rect.height / 2),
    };
};
"""

SLEEP = "const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));"

IS_ELEMENT_HAS_ATTRIBUTE = "const isElementHasAttribute = (element, attrName) => element.hasAttribute(attrName);"

MOVE_BY_STEPS = """
const move = async (element, deltaX, deltaY, stepsCount, stepDelay) => {
    const stepDeltaX = deltaX / stepsCount;
    const stepDeltaY = deltaY / stepsCount;
    for (let i = 0; i <= stepsCount; i++) {
        const x = Math.round(stepDeltaX * i);
        const y = Math.round(stepDeltaY * i);
        element.dispatchEvent(createEvent('mousemove', x, y));
        await sleep(stepDelay);
    }
};
"""

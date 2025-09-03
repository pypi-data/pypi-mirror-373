import asyncio

from playwright.async_api import Page

from ..utils.wait_for_network_idle import wait_for_network_idle


def _map_xdotool_key_to_playwright_key(text: str) -> str:
    xdotool_to_playwright_key_map = {
        "A": "KeyA",
        "B": "KeyB",
        "C": "KeyC",
        "D": "KeyD",
        "E": "KeyE",
        "F": "KeyF",
        "G": "KeyG",
        "H": "KeyH",
        "I": "KeyI",
        "J": "KeyJ",
        "K": "KeyK",
        "L": "KeyL",
        "M": "KeyM",
        "N": "KeyN",
        "O": "KeyO",
        "P": "KeyP",
        "Q": "KeyQ",
        "R": "KeyR",
        "S": "KeyS",
        "T": "KeyT",
        "U": "KeyU",
        "V": "KeyV",
        "W": "KeyW",
        "X": "KeyX",
        "Y": "KeyY",
        "Z": "KeyZ",
        "1": "Digit1",
        "2": "Digit2",
        "3": "Digit3",
        "4": "Digit4",
        "5": "Digit5",
        "6": "Digit6",
        "7": "Digit7",
        "8": "Digit8",
        "9": "Digit9",
        "0": "Digit0",
        "Return": "Enter",
        "Escape": "Escape",
        "BackSpace": "Backspace",
        "Tab": "Tab",
        "space": "Space",
        "minus": "Minus",
        "equal": "Equal",
        "bracketleft": "BracketLeft",
        "bracketright": "BracketRight",
        "backslash": "Backslash",
        "semicolon": "Semicolon",
        "apostrophe": "Quote",
        "grave": "Backquote",
        "comma": "Comma",
        "period": "Period",
        "slash": "Slash",
        "Shift_L": "ShiftLeft",
        "Shift_R": "ShiftRight",
        "Control_L": "ControlLeft",
        "Control_R": "ControlRight",
        "Alt_L": "AltLeft",
        "Alt_R": "AltRight",
        "Meta_L": "MetaLeft",
        "Meta_R": "MetaRight",
        "Shift": "ShiftLeft",
        "Control": "ControlLeft",
        "Alt": "AltLeft",
        "Meta": "MetaLeft",
        "Left": "ArrowLeft",
        "Up": "ArrowUp",
        "Right": "ArrowRight",
        "Down": "ArrowDown",
        "Insert": "Insert",
        "Delete": "Delete",
        "Home": "Home",
        "End": "End",
        "Page_Up": "PageUp",
        "Page_Down": "PageDown",
        "Caps_Lock": "CapsLock",
        "Num_Lock": "NumLock",
        "Print": "PrintScreen",
        "Scroll_Lock": "ScrollLock",
    }

    try:
        return xdotool_to_playwright_key_map[text]
    except KeyError:
        return text


@wait_for_network_idle(
    timeout=5,
    max_inflight_requests=0,
)
async def _press_key_combination(page: Page, key_combination: str):
    keys = key_combination.split("+")
    keys = [_map_xdotool_key_to_playwright_key(key) for key in keys]
    for key in keys[:-1]:  # All keys except the last one are considered modifier keys
        await page.keyboard.down(key)

    # Press the last key in the combination
    await page.keyboard.press(keys[-1])

    # Release the modifier keys
    for key in keys[:-1]:
        await page.keyboard.up(key)
    await asyncio.sleep(
        0.1
    )  # sleep for 100ms to allow the mutation observer to detect changes


async def press_key_combination(page: Page, key_combination: str):
    await _press_key_combination(page=page, key_combination=key_combination)

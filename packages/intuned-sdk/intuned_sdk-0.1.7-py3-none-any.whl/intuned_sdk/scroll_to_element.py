import asyncio
from typing import Union

from playwright.async_api import ElementHandle
from playwright.async_api import Locator


async def scroll_to_element(
    target: Union[Locator, ElementHandle],
    duration: int = 500,
    offset: int = 200,
    *,
    timeout: int = 10,
) -> None:
    """
    Smoothly scrolls a Playwright Locator or ElementHandle into view.

    Args:
        target: Playwright Locator or ElementHandle to scroll to
        duration: Animation duration in milliseconds (default: 500)
        offset: Pixels to offset from element top (default: 0)
    """
    scroll_script = """
        async (element, { duration, offset }) => {
            return new Promise((resolve) => {
                const elementRect = element.getBoundingClientRect();
                const targetY = window.scrollY + elementRect.top - offset;
                const startY = window.scrollY;
                const startTime = performance.now();

                function easeInOutCubic(t) {
                    return t < 0.5
                        ? 4 * t * t * t
                        : 1 - Math.pow(-2 * t + 2, 3) / 2;
                }

                function animate(frameId) {
                    const elapsed = performance.now() - startTime;
                    const progress = Math.min(elapsed / duration, 1);

                    const currentY = startY + (targetY - startY) * easeInOutCubic(progress);
                    window.scrollTo(0, currentY);

                    if (progress < 1) {
                        frameId = requestAnimationFrame(() => animate(frameId));
                    } else {
                        cancelAnimationFrame(frameId);
                        resolve();
                    }
                }

                const frameId = requestAnimationFrame(() => animate(frameId));
            });
        }
    """

    options = {"duration": duration, "offset": offset}

    # Handle both Locator and ElementHandle cases
    if isinstance(target, Locator):
        await target.evaluate(scroll_script, options, timeout=timeout * 1000)
    else:
        await target.evaluate_handle(scroll_script, options)
    await asyncio.sleep(2)

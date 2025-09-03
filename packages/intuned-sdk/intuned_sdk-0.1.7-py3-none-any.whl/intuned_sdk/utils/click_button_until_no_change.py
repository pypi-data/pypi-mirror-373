import asyncio
from typing import Callable, Optional

from playwright.async_api import Page, Locator

from .wait_for_network_idle import wait_for_network_idle


@wait_for_network_idle()
async def click_button_and_wait(
    page: Page,
    button_locator: Locator,
    click_delay: float = 0.5,
):
    """
    Click a button and wait briefly for content to load.

    Args:
        page: Playwright Page object
        button_locator: Locator for the button
        click_delay: Delay after clicking the button (in seconds)
    """
    await button_locator.scroll_into_view_if_needed()
    await button_locator.click(force=True)
    await asyncio.sleep(click_delay)


@wait_for_network_idle()
async def click_button_until_no_change(
    page: Page,
    button_locator: Locator,
    heartbeat: Callable[[], None] = lambda: None,
    *,
    container_locator: Optional[Locator] = None,
    max_clicks: int = 50,
    click_delay: float = 0.5,
    no_change_threshold: int = 0,
):
    """
    Repeatedly click a button until no new content appears or max clicks reached.

    Args:
        page: Playwright Page object
        button_locator: Locator for the button to click
        heartbeat: Optional callback function invoked after each click
        container_locator: Optional content container used to detect changes
        max_clicks: Maximum number of times to click the button
        click_delay: Delay after each click
        no_change_threshold: Minimum change in content size to continue clicking
    """

    prev_state = None
    if container_locator:
        prev_state = await get_container_state(container_locator)
        print(f"Initial container state: {prev_state}")

    print(f"Button matches: {await button_locator.count()}")
    for _ in range(max_clicks):
        heartbeat()

        if not (await button_locator.is_visible()):
            print("Button not visible, stopping.")
            break

        if not (await button_locator.is_enabled()):
            print("Button not enabled, stopping.")
            break

        await click_button_and_wait(
            page,
            button_locator,
            click_delay=click_delay,
        )

        if container_locator:
            current_state = await get_container_state(container_locator)
            print(f"Current container state: {current_state}")
            if (
                prev_state is not None
                and current_state - prev_state <= no_change_threshold
            ):
                print(
                    f"No significant change in container state: {current_state} (previous: {prev_state})"
                )
                break
            prev_state = current_state


async def get_container_state(container: Locator) -> int:
    """Measure container state by child count or scroll height."""
    if await container.count() > 0:
        # Prefer child element count if possible
        return await container.locator("> *").count()
    return await container.evaluate("element => element.scrollHeight")

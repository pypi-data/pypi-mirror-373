from playwright.async_api import Page

from ..utils.wait_for_network_idle import wait_for_network_idle


@wait_for_network_idle(max_inflight_requests=0, timeout=5)
async def _enter_text_and_click(
    page: Page, text_selector: str, click_selector: str, text: str, *, timeout: int = 10
):
    await page.locator(text_selector).type(text, timeout=timeout * 1000, delay=100)
    if text_selector == click_selector:
        await page.keyboard.press("Enter")
    else:
        await page.locator(click_selector).click(timeout=timeout * 1000)


async def enter_text_and_click(
    page: Page, text_selector: str, click_selector: str, text: str, *, timeout: int = 10
):
    await _enter_text_and_click(
        page=page,
        text_selector=text_selector,
        click_selector=click_selector,
        text=text,
        timeout=timeout,
    )

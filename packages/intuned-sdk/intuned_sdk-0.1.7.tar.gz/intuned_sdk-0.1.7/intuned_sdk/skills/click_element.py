from playwright.async_api import Page

from ..utils.wait_for_network_idle import wait_for_network_idle

from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError  # type:ignore


@wait_for_network_idle(max_inflight_requests=0, timeout=5)
async def _click_element(page: Page, selector: str, *, timeout: int = 10):
    tag_name = await page.locator(selector).evaluate("el => el.tagName")
    # this matches the logic in codegen/ae/core/skills/click_using_selector.py#L193
    if tag_name.lower() == "option":
        value = await page.locator(selector).evaluate("el => el.value")
        await (
            page.locator(selector)
            .locator("xpath=ancestor::select")
            .select_option(value=value)
        )
        return
    # so screenshots are close to where the user clicks
    try:
        await page.locator(selector).scroll_into_view_if_needed()
    except Exception:
        pass
    try:
        await page.locator(selector).click(timeout=timeout * 1000)
    except PlaywrightTimeoutError:
        await page.locator(selector).click(timeout=timeout * 1000, force=True)


async def click_element(page: Page, selector: str, *, timeout: int = 10):
    await _click_element(page=page, selector=selector, timeout=timeout)

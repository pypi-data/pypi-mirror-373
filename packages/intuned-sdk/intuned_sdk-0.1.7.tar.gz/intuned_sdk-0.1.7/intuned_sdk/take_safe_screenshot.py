from playwright.async_api import Page


async def take_safe_screenshot(
    page: Page, path: str, full_page: bool = False, timeout: int = 5 * 1000
):
    try:
        await page.screenshot(path=path, full_page=full_page, timeout=timeout)
    except Exception as e:
        print(f'Failed to take screenshot and save to "{path}". Error: {e}')

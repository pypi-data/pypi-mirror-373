from playwright.async_api import Page


async def enter_text(page: Page, selector: str, text: str, *, timeout: int = 10):
    await page.locator(selector).type(text, timeout=timeout * 1000, delay=100)

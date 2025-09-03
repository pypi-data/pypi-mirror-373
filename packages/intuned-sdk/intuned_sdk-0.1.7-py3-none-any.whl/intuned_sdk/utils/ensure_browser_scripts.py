from pathlib import Path

from playwright.async_api import Page


async def ensure_browser_scripts(page: Page):
    page_has_script = await page.evaluate(
        '() => typeof window.__INTUNED__ !== "undefined"'
    )

    if page_has_script:
        return

    matching_script = Path(__file__).parent.parent / "browser_scripts.js"
    matching_script = matching_script.read_text()
    await page.evaluate(matching_script)

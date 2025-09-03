import mdformat
from playwright.async_api import Locator
from .utils.ensure_browser_scripts import ensure_browser_scripts


async def convert_locator_to_markdown(locator: Locator) -> str:
    await ensure_browser_scripts(locator.page)
    md = await locator.evaluate(
        "(element)=> window.__INTUNED__.convertElementToMarkdown(element)",
    )
    return mdformat.text(md)

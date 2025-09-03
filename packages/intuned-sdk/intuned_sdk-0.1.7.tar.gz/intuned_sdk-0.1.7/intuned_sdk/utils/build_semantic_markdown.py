import mdformat
from playwright.async_api import Page

from .ensure_browser_scripts import ensure_browser_scripts


async def build_semantic_markdown(page: Page) -> str:
    await ensure_browser_scripts(page)
    md = await page.evaluate(
        """
        window.__INTUNED__.convertHtmlStringToSemanticMarkdown(document.documentElement.outerHTML,{
            enableTableColumnTracking: true,
            overrideElementProcessing: (e) => {
                if (e.tagName?.toLocaleLowerCase() === "code") {
                    return [];
                }
            },
        })
        """
    )

    return mdformat.text(md)


async def build_semantic_markdown_from_html(html: str, page: Page) -> str:
    await ensure_browser_scripts(page)
    md = await page.evaluate(
        """
        (html) => {
            return window.__INTUNED__.convertHtmlStringToSemanticMarkdown(html, {
                enableTableColumnTracking: true,
                overrideElementProcessing: (e) => {
                    if (e.tagName?.toLocaleLowerCase() === "code") {
                        return [];
                    }
                }
            });
        }
        """,
        html,
    )

    # return mdformat.text(md)
    return md

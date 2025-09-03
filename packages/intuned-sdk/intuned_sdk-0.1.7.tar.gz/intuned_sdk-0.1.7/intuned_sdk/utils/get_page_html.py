from playwright.async_api import Page


async def get_page_html(page: Page) -> str:
    """
    Convert a Playwright page object to HTML text, including iframe contents

    Args:
        page (Page): Playwright page object

    Returns:
        str: The extracted HTML content with iframe contents embedded
    """
    # Get main page HTML
    html_content = await page.content()

    # Process iframes
    frames = page.frames

    for frame in frames[1:]:  # Skip main frame
        try:
            # Get frame content
            frame_content = await frame.content()

            # Get frame element
            frame_element = await frame.frame_element()
            src = await frame_element.get_attribute("src") or ""

            # Create replacement div
            replacement = f'<div class="iframe-content" data-original-src="{src}">{frame_content}</div>'

            print(f"replacement {replacement}")

            # Replace iframe with its content
            frame_html = await frame_element.evaluate("el => el.outerHTML")
            html_content = html_content.replace(frame_html, replacement)

        except Exception as e:
            print(f"Error processing frame: {e}")
            continue

    return html_content

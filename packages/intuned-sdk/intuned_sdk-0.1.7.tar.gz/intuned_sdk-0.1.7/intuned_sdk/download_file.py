import logging
import os
from time import time_ns
from typing import Awaitable
from typing import Callable
from typing import TypeGuard
from typing import Union
from contextvars import copy_context
import aiohttp
from playwright.async_api._generated import Download
import validators
import validators.uri
from playwright.async_api import ElementHandle
from playwright.async_api import Locator
from playwright.async_api import Page
from playwright.async_api import TimeoutError

from .convert_relative_url_to_full_url import convert_relative_url_to_full_url_with_page
from .utils.get_mode import is_generate_code_mode

logger = logging.getLogger(__name__)


class PageDoesntHaveImageOrDownload(Exception):
    """Raised when the URL points to an image rather than a downloadable file."""

    pass


async def get_absolute_url(page: Page, url: str) -> str:
    try:
        url_locator = page.locator(f"a[href='{url}']")
        if await url_locator.count() > 0:
            return await url_locator.evaluate("(el) => el.href")
    except Exception:
        pass
    return await convert_relative_url_to_full_url_with_page(page=page, relative_url=url)


async def download_file(
    page: Page,
    trigger: Union[
        str,
        Locator,
        Callable[[Page], None],
    ],
    timeout: int = 5000,
) -> str | Download:
    """
        Download a file from a web page using a trigger.

        This function supports three different ways to trigger a download:
        1. By URL
        2. By clicking on a playwright locator
        3. By executing a callback function that takes a page object as an argument and uses it to initiate the download.

        Args:
            page (Page): The Playwright Page object to use for the download.
            trigger (Union[str, Locator, Callable[[Page], None]]):
                - If str: URL to download from.
                - If Locator: playwright locator to click to download.
                - If Callable: callback function that takes a page object as an argument and uses it to initiate the download.

        Returns:
            url (str): The url of the attachment file.

        Example:
        ```python
        from intuned_sdk import download_file

        async with launch_chromium(headless=False) as (context, page):
            url = await download_file(page, "https://sandbox.intuned.dev/pdfs")
        ```

        ```python
        from intuned_sdk import download_file

        async with launch_chromium(headless=False) as (context, page):
            url = await download_file(page, page.locator("[href='/download/file.pdf']"))
        ```


        ```python
        from intuned_sdk import download_file

        async with launch_chromium(headless=False) as (context, page):
            url = await download_file(page, page.locator("button:has-text('Download')"))
        ```

        ```python
        from intuned_sdk import download_file
    from typing import TypeGuard

        async with launch_chromium(headless=False) as (context, page):
            url = await download_file(page, lambda page: page.locator("button:has-text('Download')").click())
        ```

        Note:
            If a URL is provided as the trigger, a new page will be created and closed
            after the download is complete.
            If a locator is provided as the trigger, the page will be used to click the element and initiate the download.
            If a callback function is provided as the trigger, the function will be called with the page object as an argument and will be responsible for initiating the download.
    """
    page_to_download_from = page
    should_close_after_download = False
    is_invalid_url = False

    def is_url(trigger) -> TypeGuard[str]:
        return isinstance(trigger, str)

    def is_locator(trigger) -> TypeGuard[Union[Locator, ElementHandle]]:
        return isinstance(trigger, (Locator, ElementHandle))

    def is_callable(trigger) -> TypeGuard[Callable[[Page], Awaitable[None]]]:
        return callable(trigger)

    ctx = copy_context()

    def on_new_page(page: Page) -> None:
        """Callback function to handle new page creation."""

        def new_page_logic():
            logger.info(
                f"Detected new page opened while processing the download with URL: {page.url}"
            )

            def download_handler(download):
                ctx.run(
                    lambda: logger.info(
                        f"Detected download with URL: {download.url} happened inside page with URL: {page.url} Note that this page is not the original page that called the function."
                    )
                )

            page.on("download", download_handler)

        ctx.run(new_page_logic)

    if is_url(trigger):
        page_to_download_from = await page.context.new_page()
        should_close_after_download = True

    logger.info(f"start to download from {trigger}")
    page_to_download_from.context.on("page", on_new_page)
    is_image_url = False
    try:
        async with page_to_download_from.expect_download(
            timeout=timeout + 1000
        ) as download_info:
            if is_url(trigger):
                full_url = await get_absolute_url(page=page, url=trigger)
                is_valid = validators.url(full_url)
                if not is_valid:
                    is_invalid_url = True
                try:
                    response = await page_to_download_from.goto(
                        full_url, wait_until="load", timeout=timeout
                    )
                    if response is None:
                        raise ValueError(f"Failed to navigate to URL: {full_url}")
                    content_type = response.headers.get("content-type", "")

                    if content_type.startswith("image/"):
                        is_image_url = True
                    # we know by this point that a download was not triggered
                    raise PageDoesntHaveImageOrDownload("URL points to an image")
                except PageDoesntHaveImageOrDownload:
                    raise
                except Exception:
                    pass

            if is_locator(trigger):
                await trigger.click()

            if is_callable(trigger):
                await trigger(page)

    # these errors are designed to give a user friendly feedback and hence a friendly message to the llm
    except (TimeoutError, PageDoesntHaveImageOrDownload) as e:
        if is_url(trigger) and not is_image_url and not is_invalid_url:
            # Check if page is a 404 page by looking for common 404 patterns
            not_found_patterns = [
                "404",
                "not found",
                "page not found",
                "page doesn't exist",
                "page does not exist",
                "resource not found",
            ]
            for pattern in not_found_patterns:
                if (
                    await page_to_download_from.get_by_text(
                        pattern, exact=False
                    ).count()
                    > 0
                ):
                    page_to_download_from.context.remove_listener("page", on_new_page)
                    raise TimeoutError(
                        f"Download timeout for url:{trigger}. Page appears to be a 404 page."
                    ) from e
            raise TimeoutError(
                f"Download timeout for url:{trigger}. Download was never triggered."
            ) from e
        if is_locator(trigger):
            page_to_download_from.context.remove_listener("page", on_new_page)
            raise TimeoutError(
                f"Download timeout for locator:{trigger}. Download was never triggered."
            ) from e
        if is_callable(trigger):
            page_to_download_from.context.remove_listener("page", on_new_page)
            raise TimeoutError(
                f"Download timeout for callable:{trigger}. Download was never triggered."
            ) from e
        if is_url(trigger) and is_invalid_url:
            page_to_download_from.context.remove_listener("page", on_new_page)
            raise ValueError(
                f"Url is not valid, the download did not trigger correctly. {trigger}"
            ) from e
    finally:
        if should_close_after_download:
            try:
                await page_to_download_from.close()
            except Exception:
                pass

    if is_image_url:
        return await download_image(trigger)  # type: ignore
    download = await download_info.value  # type: ignore
    if is_generate_code_mode():
        await download.cancel()

    logger.info(f"Downloaded file successfully by {trigger}")
    page_to_download_from.context.remove_listener("page", on_new_page)
    return download


async def download_image(url: str) -> str:
    """
    Download an image from a given URL.

    Args:
        url (str): The URL of the image to download.

    Returns:
        str: The path to the downloaded image file.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(
                    f"Failed to download image: HTTP status {response.status}"
                )

            content = await response.read()
            content_type = response.headers.get("content-type", "")
            extension = content_type.split("/")[-1]
            filename = f"downloaded_image-{time_ns()}.{extension}"
            filepath = os.path.join(os.getcwd(), filename)
            if not is_generate_code_mode():
                with open(filepath, "wb") as f:
                    f.write(content)

            return filepath

import os
from typing import Callable
from typing import Union
import logging

from playwright.async_api import Locator
from playwright.async_api import Page

from .download_file import download_file
from .upload_file import upload_file_to_s3
from .upload_file import Attachment
from .utils.get_mode import is_generate_code_mode

logger = logging.getLogger(__name__)


async def save_file_to_s3(
    page: Page,
    trigger: Union[
        str,
        Locator,
        Callable[[Page], None],
    ],
    timeout: int = 5000,
) -> Attachment:
    """
    Download a file from a web page using a trigger.

    This function supports three different ways to trigger a download:
    1. By URL
    2. By clicking on a playwright locator
    3. By executing an async callback function that takes a page object as an argument and uses it to initiate the download.

    Args:
        page (Page): The Playwright Page object to use for the download.
        trigger (Union[str, Locator, Callable[[Page], None]]):
            - If Locator: playwright locator to click to download.
            - If str: URL to download from.
            - If Callable: callback function that takes a page object as an argument and uses it to initiate the download.

    Returns:
        Attachment: The uploaded file object as an Attachment instance.

    Example:
    ```python
    from intuned_sdk import save_file_to_s3

    uploaded_file = await save_file_to_s3(page, page.locator("[href='/download/file.pdf']"))
    ```

    ```python
    from intuned_sdk import save_file_to_s3

    uploaded_file = await save_file_to_s3(page, "https://sandbox.intuned.dev/pdfs")
    ```


    ```python
    from intuned_sdk import save_file_to_s3

    uploaded_file = await save_file_to_s3(page, page.locator("button:has-text('Download')"))
    ```

    ```python
    from intuned_sdk import save_file_to_s3
    async def trigger_download(page: Page):
        await page.locator("button:has-text('Download')").click()
    uploaded_file = await save_file_to_s3(page, trigger_download)
    ```

    Note:
        If a URL is provided as the trigger, a new page will be created and closed
        after the download is complete.
        If a locator is provided as the trigger, the page will be used to click the element and initiate the download.
        If a callback function is provided as the trigger, the function will be called with the page object as an argument and will be responsible for initiating the download.
    """
    if not isinstance(page, Page):
        raise ValueError("page must be a playwright Page object")
    download = await download_file(page, trigger, timeout)
    if not is_generate_code_mode():
        try:
            from runtime_helpers import extend_timeout

            extend_timeout()
        except ImportError:
            logger.info(
                "Intuned Runtime not available: extend_timeout() was not called. Install 'intuned-runtime' to enable this feature."
            )
    uploaded: Attachment = await upload_file_to_s3(download)
    try:
        if isinstance(download, str):
            print(f"Deleting file {download}")
            os.remove(download)
    except Exception as e:
        print(f"Error deleting file {e}")
        pass
    return uploaded

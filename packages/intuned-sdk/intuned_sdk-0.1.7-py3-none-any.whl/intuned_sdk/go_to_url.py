import asyncio
import logging

from playwright.async_api import Page

from .is_page_loaded import is_page_loaded
from .utils.wait_for_network_idle import wait_for_network_idle


_timeout_padding = 3  # seconds


@wait_for_network_idle()
async def go_to_url(*, page: Page, url: str, timeout: int = 10, retries: int = 3):
    "Open URL with retries if open url fails"
    "do_open_url errors with 'load' which means the page is not loaded at all which happen often"
    "retry until pass load then wait for networkidle"
    for i in range(retries):
        try:
            # this should be domcontentloaded and let it fail if it doesn't reach it
            # if you wait for networkidle, then we just slide it
            current_timeout = (timeout * (2**i)) * 1000
            try:
                await asyncio.wait_for(
                    page.goto(url, timeout=current_timeout, wait_until="load"),
                    timeout=current_timeout / 1000 + _timeout_padding,
                )
            except asyncio.TimeoutError as e:
                raise asyncio.TimeoutError(
                    f"Page.goto timed out but did not throw an error. Consider using a proxy.\n"
                    f"(URL: {url}, timeout: {timeout}ms)"
                ) from e
            break
        except Exception as e:
            # loading this website throws immediate error so we wait https://www.tn.gov/generalservices/procurement/central-procurement-office--cpo-/supplier-information/request-for-proposals--rfp--opportunities1.html
            await asyncio.sleep(2)
            if i == retries - 1:
                logging.error(f"Failed to open URL: {url}. Error: {e}")
                raise e
    # if a snapshot, then skip loading check
    if "mhtml-viewer" in page.url:
        await page.wait_for_timeout(1000)
        return
    try:
        is_loaded, _, _ = await is_page_loaded(
            page, model="gpt-4o-2024-08-06", timeout=3
        )
        logging.info(f"is_loaded: {is_loaded}")
        if is_loaded == "True":
            return
    except Exception as e:
        logging.warning(f"Failed to check if page is loaded: {url}. Error: {e}")
        is_loaded = False
    tries = 0
    for _ in range(retries):
        if tries > 3:
            raise ValueError(f"Page never loaded: {url}")
        await asyncio.sleep(5)
        try:
            is_loaded, _, _ = await is_page_loaded(
                page, model="gpt-4o-2024-08-06", timeout=3
            )
            logging.info(f"is_loaded inside while: {is_loaded}")
            if is_loaded == "True":
                return
        except Exception as e:
            logging.warning(f"Failed to check if page is loaded: {url}. Error: {e}")
            is_loaded = False
        tries += 1

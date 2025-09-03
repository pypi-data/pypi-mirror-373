import asyncio
import logging
from typing import Optional

from playwright.async_api import Page

from ..is_page_loaded import is_page_loaded
from ..utils.inject_element_ids_into_page import inject_element_ids_into_page


_timeout_padding = 3  # seconds


# TODO: skip load check if the url is a snapshot
async def go_to_url(
    *,
    page: Page,
    url: str,
    timeout: int = 10,
    retries: int = 3,
    logs_dir: Optional[str] = None,
    inject_element_ids: bool = False,
):
    "Open URL with retries if open url fails"
    "do_open_url errors with 'load' which means the page is not loaded at all which happen often"
    "retry until pass load then wait for networkidle"

    async def inject_ids(page: Page):
        if inject_element_ids:
            await inject_element_ids_into_page(page=page)

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
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout * 1000)
    except Exception as e:
        logging.error(f"Failed to wait for networkidle on URL: {url}. Error: {e}")
    # if a snapshot, then skip loading check
    if "mhtml-viewer" in page.url:
        await page.wait_for_timeout(1000)
        await inject_ids(page=page)
        return
    try:
        is_loaded, _, _ = await is_page_loaded(
            page, model="gpt-4o-2024-08-06", timeout=3
        )
        logging.info(f"is_loaded: {is_loaded}")
        if is_loaded == "True":
            await inject_ids(page=page)
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
                await inject_ids(page=page)
                return
        except Exception as e:
            logging.warning(f"Failed to check if page is loaded: {url}. Error: {e}")
            is_loaded = False
        tries += 1
    await inject_ids(page=page)

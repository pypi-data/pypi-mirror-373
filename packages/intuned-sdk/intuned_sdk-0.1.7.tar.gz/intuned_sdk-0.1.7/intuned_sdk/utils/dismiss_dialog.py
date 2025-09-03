import asyncio
import logging

from playwright.async_api import Page
from playwright.async_api import TimeoutError


async def monitor_and_click(page: Page, selector: str):
    while True:
        try:
            logging.info(f"Waiting for selector: {selector}")
            print(f"Waiting for selector: {selector}")
            await page.wait_for_selector(selector, timeout=300000)

            logging.info(f"Clicking on selector: {selector}")
            print(f"Clicking on selector: {selector}")
            await page.click(selector)
            # was added for dialogs to let the handler close before we capture the snapshot. In general, I think we should wait for page stablity before capturing the snapshot.
            await asyncio.sleep(3)
        except TimeoutError:
            pass
        except Exception:
            break


def monitor_and_dismiss_dialog(page: Page, selector: str):
    asyncio.create_task(monitor_and_click(page, selector))

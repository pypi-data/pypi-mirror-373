import asyncio
import functools
import logging
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Set

from playwright.async_api import Page
from playwright.async_api import Request


# this function is based on a gist mentioned here https://github.com/microsoft/playwright/issues/2515
def wait_for_network_idle(timeout: int = 30, max_inflight_requests: int = 0):
    def decorator(func: Callable[..., Awaitable[Any]]):
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Waits for the network to settle after performing an action on the page.

            Args:
                page (Page): The Playwright page object.
                action (Callable): An asynchronous function representing the action to perform.
                max_inflight_requests (int, optional): Number of additional network polls to wait for. Defaults to 0.

            Returns:
                Any: The result of the action.
            """
            page = next((arg for arg in args if isinstance(arg, Page)), None)
            if page is None:
                page = kwargs.get("page")

            if not page:
                logging.error("No Page object found in function arguments")
                raise ValueError("No Page object found in function arguments")

            async def func_with_args():
                return await func(*args, **kwargs)

            return await wait_for_network_idle_core(
                page=page,
                func=func_with_args,
                timeout=timeout,
                max_inflight_requests=max_inflight_requests,
            )

        return wrapper

    return decorator


async def wait_for_network_idle_core(
    *,
    page: Page,
    func: Callable[..., Awaitable[Any]],
    timeout: int = 30,
    max_inflight_requests: int = 0,
):
    logging.debug(f"Page object: {page}")
    network_settled_event = asyncio.Event()
    is_timeout = False
    request_counter = 0
    action_done = False
    pending_requests: Set[Request] = set()

    async def maybe_settle():
        if action_done and request_counter <= max_inflight_requests:
            network_settled_event.set()

    def on_request(request: Request):
        nonlocal request_counter
        request_counter += 1
        pending_requests.add(request)
        logging.debug(f"+[{request_counter}]: {request.url}")

    async def on_request_done(request: Request):
        nonlocal request_counter
        # Simulate asynchronous handling
        await asyncio.sleep(0)
        if request in pending_requests:
            request_counter -= 1
            pending_requests.discard(request)
            logging.debug(f"-[{request_counter}]: {request.url}")
            await maybe_settle()

    # Define listener functions to allow proper removal later
    async def handle_request_finished(req: Request):
        await on_request_done(req)

    async def handle_request_failed(req: Request):
        await on_request_done(req)

    # Add listeners
    page.on("request", on_request)
    page.on("requestfinished", handle_request_finished)
    page.on("requestfailed", handle_request_failed)

    async def timeout_task():
        nonlocal is_timeout
        await asyncio.sleep(timeout)
        print("waiting for network to settle timed out")
        is_timeout = True
        network_settled_event.set()

    try:
        result = await func()
        action_done = True
        await asyncio.sleep(0.5)
        await maybe_settle()
        timeout_task = asyncio.create_task(timeout_task())  # type: ignore
        print("-- Start waiting for network to settle... --")
        while True:
            print(f"waiting for network to settle, {request_counter} requests pending")
            await network_settled_event.wait()
            await asyncio.sleep(0.5)
            if (action_done and request_counter <= max_inflight_requests) or is_timeout:
                if is_timeout:
                    print("Exiting due to timeout, network did not settle")
                else:
                    print("network settled, no pending requests")
                break
            else:
                network_settled_event = asyncio.Event()
        print("-- Finished waiting for network to settle --")
        return result
    finally:
        # Remove listeners using the same function references
        page.remove_listener("request", on_request)
        page.remove_listener("requestfinished", handle_request_finished)
        page.remove_listener("requestfailed", handle_request_failed)
        try:
            timeout_task.cancel()  # type: ignore
        except Exception:
            pass


# Simplified wrapper for agents
async def run_action_on_page_and_wait_network_idle(
    page: Page, action: Callable[[], Awaitable[Any]]
) -> Any:
    """
    Executes an action on a page and waits for all network requests to completed before returning.
    Useful for ensuring the page is stable after actions like clicks, type, etc.

    Args:
        page: Playwright page object
        action: Async function to execute (should take no parameters)

    Returns:
        Result of the action

    Example:
        # Click on item and wait for network idle
        item = page.locator("selector")
        result = await perform_action_and_wait(page=page, action=item.click)
    """
    return await wait_for_network_idle_core(
        page=page,
        func=action,
        timeout=30,  # 30 second timeout
        max_inflight_requests=0,  # Wait for all requests to complete
    )

import asyncio
from typing import List, NotRequired
from typing import Literal
from typing import TypedDict
from typing import Union

from playwright.async_api import Page
import logging
from .skills import click_element
from .skills import enter_text
from .skills import enter_text_and_click
from .skills import go_to_url
from intuned_sdk.is_page_loaded import is_page_loaded
from .skills import press_key_combination
from .utils.dismiss_dialog import monitor_and_dismiss_dialog
from .utils.inject_element_ids_into_page import inject_element_ids_into_page


class ExecuteCodeAction(TypedDict):
    type: Literal["execute_code"]
    code: str


class PressKeyCombinationAction(TypedDict):
    type: Literal["press_key_combination"]
    key_combination: str


class EnterTextAction(TypedDict):
    type: Literal["entertext"]
    xpath: str
    text: str


class ClickAction(TypedDict):
    type: Literal["click"]
    xpath: str


class OpenUrlAction(TypedDict):
    type: Literal["openurl"]
    url: str
    inject_element_ids: NotRequired[bool]


class EnterTextAndClickAction(TypedDict):
    type: Literal["enter_text_and_click"]
    text_xpath: str
    click_xpath: str
    text: str


class LoadMhtmlAction(TypedDict):
    type: Literal["load_mhtml"]
    # Additional fields would go here if implemented


class SelectOption(TypedDict):
    type: Literal["select_option"]
    xpath: str
    value: str


class DismissDialogAction(TypedDict):
    type: Literal["dismiss_dialog"]
    selector: str


class InjectElementIdsAction(TypedDict):
    type: Literal["inject_element_ids"]


BrowserAction = Union[
    PressKeyCombinationAction,
    EnterTextAction,
    ClickAction,
    OpenUrlAction,
    EnterTextAndClickAction,
    SelectOption,
    LoadMhtmlAction,
    DismissDialogAction,
    InjectElementIdsAction,
    ExecuteCodeAction,
]

BrowserActionList = List[BrowserAction]


async def execute_actions_on_page(
    page: Page,
    actions: BrowserActionList,
    *,
    timeout: int = 20,
    logs_dir: str | None = None,
):
    action_type: str
    for action in actions:
        action_type = action["type"]
        if action_type == "press_key_combination":
            if "key_combination" not in action:
                raise ValueError(
                    "key_combination is required for press_key_combination action"
                )
            await press_key_combination(
                page=page, key_combination=action["key_combination"]
            )
        elif action_type == "entertext":
            if "xpath" not in action or "text" not in action:
                raise ValueError("xpath and text are required for entertext action")
            await enter_text(
                page=page,
                selector=f"xpath={action['xpath']}",
                text=action["text"],
                timeout=timeout,
            )
        elif action_type == "click":
            if "xpath" not in action:
                raise ValueError("xpath is required for click action")
            await click_element(
                page=page, selector=f"xpath={action['xpath']}", timeout=timeout
            )
        elif action_type == "openurl":
            if "url" not in action:
                raise ValueError("url is required for go_to_url action")
            await go_to_url(
                page=page,
                url=action["url"],
                timeout=timeout,
                logs_dir=logs_dir,
                inject_element_ids=action.get("inject_element_ids", False),
            )
        elif action_type == "enter_text_and_click":
            if (
                "text_xpath" not in action
                or "click_xpath" not in action
                or "text" not in action
            ):
                raise ValueError(
                    "text_xpath and click_xpath are required for enter_text_and_click action"
                )
            await enter_text_and_click(
                page=page,
                text_selector=f"xpath={action['text_xpath']}",
                click_selector=f"xpath={action['click_xpath']}",
                text=action["text"],
                timeout=timeout,
            )
        elif action_type == "load_mhtml":
            raise NotImplementedError("load_mhtml action is not implemented")
        elif action_type == "dismiss_dialog":
            if "selector" not in action:
                raise ValueError("selector is required for dismiss_dialog action")
            monitor_and_dismiss_dialog(page=page, selector=action["selector"])
            await page.wait_for_timeout(2000)
        # this is useful to inject element ids after all the actions are executed
        # TODO: not sure this is the best place to do this for the following reasons:
        # 1. It's not an action that a user could do
        # 2. This is only related to code generation step but not running the scraper at intuned
        # 3. All our tasks related to codegen are based on element ids so if this was moved then we need to test those tasks well
        # 4. Same thing can be argued for the load_mthml action
        elif action_type == "inject_element_ids":
            await inject_element_ids_into_page(page=page)

        elif action_type == "select_option":
            if "xpath" not in action:
                raise ValueError("selector is required for select_option action")
            if "value" not in action:
                raise ValueError("value is required for select_option action")
            await page.select_option(
                f"xpath={action['xpath']}",
                value=action["value"],
            )
            await page.wait_for_load_state("networkidle")
            is_loaded = await is_page_loaded(page, model="gpt-4o-2024-08-06", timeout=3)
            if not is_loaded:
                tries = 0
                for _ in range(3):
                    if tries > 3:
                        raise ValueError(f"Page never loaded: {page.url}")
                    await asyncio.sleep(5)
                    try:
                        is_loaded, _, _ = await is_page_loaded(
                            page, model="gpt-4o-2024-08-06", timeout=3
                        )
                        if is_loaded == "True":
                            return
                    except Exception as e:
                        logging.warning(
                            f"Failed to check if page is loaded: {page.url}. Error: {e}"
                        )
                        is_loaded = False
                    tries += 1

        if logs_dir is not None:
            # snapshot_before_snapshots_dir = os.path.join(
            #     logs_dir, f"{time_ns()}_SDK_FUNCTION_execute_actions_on_page"
            # )
            # snapshot_after_snapshots_dir = os.path.join(
            #     snapshot_before_snapshots_dir,
            #     f"{time_ns()}_POST_ACTION_LOG_{action_type}",
            # )
            # await report_browser_snapshot(page=page, input=action, logs_dir=snapshot_after_snapshots_dir, output="N/A")
            logging.info("Logs dir is none.")
        await asyncio.sleep(1)

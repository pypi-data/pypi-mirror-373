import asyncio
import os
from typing import Any
from typing import Callable
from typing import Literal
from typing import Optional

from anthropic import BadRequestError as AnthropicBadRequestError
from anthropic.types.beta import BetaMessageParam
from playwright.async_api import Page
from pydantic import BaseModel
from pydantic import Field  # type: ignore

from .common import create_screenshot_messages
from .loop import APIProvider
from .loop import PROVIDER_TO_DEFAULT_MODEL_NAME
from .loop import sampling_loop
from .utils.conversation_utils import print_diff
from .utils.print_utils import noop  # type: ignore


class ValidationParams:
    page: Page
    # function to validate is an async function that takes a page and can return anything - return type is ignored
    function_to_validate: Callable[[Page], Any]
    # what to validate is a string that describes what to validate
    what_to_validate: str


class ValidationResult(BaseModel):
    reason: str = Field(
        description="Reason for the validation result. Start it with Based on the current state of the page..."
    )

    success: bool = Field(description="Whether the validation was successful")


async def execute_validation_task_on_website(
    *,
    validation_input: ValidationParams,
    format: Literal["markdown", "tty"] = "tty",
    initial_messages: list[BetaMessageParam] | None = None,
) -> tuple[Optional[ValidationResult], list[BetaMessageParam], Optional[str]]:
    messages: list[BetaMessageParam] = []
    if initial_messages:
        messages = initial_messages
    else:
        screenshot_messages = await create_screenshot_messages(validation_input.page)
        messages.extend(screenshot_messages)

    async def converse():
        result_from_call: Optional[ValidationResult] = None
        old_messages: list[BetaMessageParam] = [*messages]
        try:
            _, result_from_call = await sampling_loop(
                model=PROVIDER_TO_DEFAULT_MODEL_NAME[APIProvider.ANTHROPIC],
                api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
                provider=APIProvider.ANTHROPIC,
                messages=messages,  # type: ignore
                system_prompt_suffix="",
                output_callback=lambda _: print_diff(
                    old_messages, messages, format=format
                ),  # type: ignore
                tool_output_callback=lambda _, __: print_diff(
                    old_messages, messages, format=format
                ),  # type: ignore
                api_response_callback=noop,  # type: ignore
                page=validation_input.page,
                submit_results_model=ValidationResult,
                function_to_validate=validation_input.function_to_validate,
            )
        except AnthropicBadRequestError:
            import traceback

            traceback.print_exc()

            # we want to fail on this error so we can handle it
            raise
        except Exception:
            import traceback

            traceback.print_exc()
            return None, "failed because of safety reason"
        await asyncio.sleep(0.1)

        if result_from_call is not None:
            print("result_from_call", result_from_call)
            return result_from_call, None

        return None, None

    # user_message = task
    messages.append(
        {
            "role": "user",
            "content": f""" WHAT TO VALIDATE:  {validation_input.what_to_validate}.

    To kick off the execution of the function, execute the tool.
    """,
        }
    )

    result_from_call, failure_message = await converse()

    return result_from_call, messages, failure_message

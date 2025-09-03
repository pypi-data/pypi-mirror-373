# type: ignore
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Literal

from anthropic.types.beta import BetaToolUnionParam
from playwright.async_api import Page

from ..utils.browser_utils import take_screenshot
from .base import BaseAnthropicTool
from .base import ToolResult


class ValidationFunctionTool(BaseAnthropicTool):
    name: ClassVar[Literal["execute_function_to_validate"]] = (
        "execute_function_to_validate"
    )

    def __init__(self, page: Page, function_to_validate: Callable[[Page], Any]):
        self.page = page
        self.function_to_validate = function_to_validate
        super().__init__()

    async def __call__(self, **kwargs):
        # execute the function
        result = None
        try:
            result = await self.function_to_validate(page=self.page)
        except Exception as _:
            pass

        self.page.wait_for_timeout(2000)
        if result:
            result_message = (
                f"Executed the function and it returned: {result}"
                + "\n Use the result to validate the page."
            )
        else:
            result_message = "Executed the function"
        return ToolResult(
            output=result_message, base64_image=await take_screenshot(self.page)
        )

    def to_params(self) -> BetaToolUnionParam:
        schema = {
            "name": self.name,
            "description": "Execute a function on the page.",
            "input_schema": {"type": "object", "properties": {}, "required": []},
        }
        return schema  # type: ignore

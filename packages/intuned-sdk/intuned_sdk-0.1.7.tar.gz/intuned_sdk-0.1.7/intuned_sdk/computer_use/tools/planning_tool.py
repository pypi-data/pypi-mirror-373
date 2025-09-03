# type: ignore
import json
from datetime import datetime
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Literal
from typing import TypedDict
from typing import Union

from playwright.async_api import Page
from pydantic import BaseModel
from pydantic import Field  # type: ignore

from ...execute_actions_on_page import execute_actions_on_page
from ..utils.browser_utils import scrolling_position
from ..utils.browser_utils import take_screenshot
from .base import BaseAnthropicTool
from .base import ToolFailure
from .base import ToolResult


class PlanningResult(BaseModel):
    success: bool
    plan: str = Field(
        description="Detailed plan on how to complete the task given to a code generator agent"
    )


class LoadExampleAction(TypedDict):
    type: Literal["goto_example"]
    example_number: int


class Action(TypedDict):
    action: Union[LoadExampleAction]


class PlanningTool(BaseAnthropicTool):
    """
    A tool that allows the agent to plan the task
    """

    name: ClassVar[Literal["planning"]] = "planning"

    def __init__(self, page: Page, examples: List[List[Dict[str, Any]]]):
        self.page = page
        self.examples = examples
        super().__init__()

    async def __call__(self, action: Union[LoadExampleAction], **kwargs):
        if isinstance(action, str):
            try:
                action = json.loads(action)
            except json.JSONDecodeError:
                return ToolFailure(error="Invalid action json")
        if "type" not in action:
            return ToolFailure(error="Action must have a type")
        if action["type"] == "goto_example" and isinstance(
            action["example_number"], int
        ):
            return await self._goto_example(action["example_number"])
        return ToolFailure(
            error=f"Invalid action: {action}. Valid actions: goto examples"
        )

    def to_params(self) -> dict:
        return {
            "name": self.name,
            "input_schema": {
                "type": "object",
                "required": ["action"],
                "properties": {
                    "action": {
                        "oneOf": [
                            {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["goto_example"],
                                    },
                                    "example_number": {"type": "integer"},
                                },
                                "required": ["type", "example_number"],
                                "description": "Load the example with a given number into the current page",
                            },
                        ]
                    }
                },
            },
        }

    async def _goto_example(self, example_number: int):
        await execute_actions_on_page(self.page, self.examples[example_number - 1])
        return ToolResult(
            system=f" | Current url: {self.page_url()} | {await self.scrolling_position()} | Current time: {datetime.now().strftime('%H:%M:%S')}",
            output=f"Example number {example_number} loaded",
            base64_image=await take_screenshot(self.page),
        )

    async def scrolling_position(self) -> str:
        return await scrolling_position(self.page)

    def page_url(self) -> str:
        return self.page.url

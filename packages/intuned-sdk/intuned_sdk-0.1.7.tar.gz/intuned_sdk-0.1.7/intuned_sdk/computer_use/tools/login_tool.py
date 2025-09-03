# type: ignore
import json
from datetime import datetime
from typing import ClassVar
from typing import Literal
from typing import TypedDict
from typing import Union

from playwright.async_api import Page
from pydantic import BaseModel
from pydantic import Field  # type: ignore

from ..utils.browser_utils import scrolling_position
from ..utils.browser_utils import take_screenshot
from .base import BaseAnthropicTool
from .base import ToolFailure
from .base import ToolResult


class LoginResult(BaseModel):
    success: bool
    reason: str = Field(
        description="Reason for the login result. Start it with Based on the current state of the page..."
    )


TYPING_DELAY_MS = 12


class TypeUsernameAction(TypedDict):
    type: Literal["type_username"]


class TypePasswordAction(TypedDict):
    type: Literal["type_password"]


class Credentials(TypedDict):
    username: str
    password: str


class Action(TypedDict):
    action: Union[TypeUsernameAction, TypePasswordAction]


class LoginTool(BaseAnthropicTool):
    """
    A tool that allows the agent to login to a website
    """

    name: ClassVar[Literal["login"]] = "login"

    def __init__(self, page: Page, credentials: Credentials):
        self.page = page
        self.credentials = credentials
        super().__init__()

    async def __call__(
        self, action: Union[TypeUsernameAction, TypePasswordAction], **kwargs
    ):
        if isinstance(action, str):
            try:
                action = json.loads(action)
            except json.JSONDecodeError:
                return ToolFailure(error="Invalid action json")
        if "type" not in action:
            return ToolFailure(error="Action must have a type")
        if action["type"] == "type_username":
            return await self._type_username()
        if action["type"] == "type_password":
            return await self._type_password()
        return ToolFailure(error="Invalid action")

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
                                        "enum": ["type_username"],
                                    }
                                },
                                "required": ["type"],
                                "description": "This tool is similar to the `type` tool where it controls the keyboard to write a text. It is used to type the username which is provided by the user. Make sure you click on the username input field before using this tool.",
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["type_password"],
                                    }
                                },
                                "required": ["type"],
                                "description": "This tool is similar to the `type` tool where it controls the keyboard to write a text. It is used to type the password which is provided by the user. Make sure you click on the password input field before using this tool.",
                            },
                        ]
                    }
                },
            },
        }

    async def _type_username(self):
        await self.page.keyboard.type(
            self.credentials["username"], delay=TYPING_DELAY_MS
        )
        return ToolResult(
            system=f" | Current url: {self.page_url()} | {await self.scrolling_position()} | Current time: {datetime.now().strftime('%H:%M:%S')}",
            output="Typed username",
            base64_image=await take_screenshot(self.page),
        )

    async def _type_password(self):
        await self.page.keyboard.type(
            self.credentials["password"], delay=TYPING_DELAY_MS
        )
        return ToolResult(
            system=f" | Current url: {self.page_url()} | {await self.scrolling_position()} | Current time: {datetime.now().strftime('%H:%M:%S')}",
            output="Typed password",
            base64_image=await take_screenshot(self.page),
        )

    async def scrolling_position(self) -> str:
        return await scrolling_position(self.page)

    def page_url(self) -> str:
        return self.page.url

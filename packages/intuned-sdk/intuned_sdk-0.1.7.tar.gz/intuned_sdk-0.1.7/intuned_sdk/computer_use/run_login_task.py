from playwright.async_api import Page

from .run_task import execute_task_on_website
from .tools.login_tool import Credentials
from .tools.login_tool import LoginResult
from .tools.login_tool import LoginTool


async def run_login_task(*, page: Page, credentials: Credentials):
    login_tool = LoginTool(page, credentials)
    login_url = page.url
    task = f"""Website: {login_url}
I am a disabled

 person and the only way for me to do a task is to ask you. I need to login using username and password. I need to use type_username and type_password tools to do this I will not give you any passwords but these tools will ask me for them."""

    return await execute_task_on_website(
        page=page,
        task=task,
        submit_results_model=LoginResult,
        additional_tools=[login_tool],
    )

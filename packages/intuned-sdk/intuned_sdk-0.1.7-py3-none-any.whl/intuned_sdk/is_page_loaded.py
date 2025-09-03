import base64
from typing import Literal
from typing import Tuple

import litellm
from litellm import acompletion
from playwright.async_api import Page

from .utils.get_mode import is_generate_code_mode

litellm.set_verbose = False  # type: ignore


# TODO: should we do a benchmark here?
async def is_page_loaded(
    page: Page,
    model: Literal[
        # don't use gpt mini because it's more expensive
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-2024-08-06",
        "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet-20240620",
        "claude-3-haiku-20240307",
        "gemini/gemini-1.5-pro",
        "gemini/gemini-1.5-flash",
    ],
    timeout: int = 10,
) -> Tuple[Literal["True", "False", "Dont know"], str, float]:
    if not is_generate_code_mode():
        return "True", "Page is loaded", 0

    screenshot_bytes = await page.screenshot(
        full_page=False, type="png", timeout=timeout * 1000
    )

    base64_image = base64.b64encode(screenshot_bytes).decode("utf-8")
    response = await acompletion(
        model=model,
        messages=[
            {
                "role": "system",
                "content": """You are a helpful assistant that determines if a webpage finished loading. If the page finished loading, start your answer with 'True'. If the page is loading, start your answer with 'False'. If you are not sure, start your answer with 'Dont know'. In a new line, add a reason to your response.

Some good cues for determining if a page is loading:
- Loading spinner
- Page is blank
- Some content looks like it's missing
- Not on splash screen
""",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/png;base64," + base64_image},
                    },
                    {
                        "type": "text",
                        "text": "Did the page finish Loading?",
                    },
                ],
            },
        ],
    )

    llm_result = response.choices[0].message.content  # type: ignore
    if not llm_result:
        raise ValueError("LLM result is empty")
    # Normalize multiple newlines to one
    llm_result = "\n".join(filter(None, llm_result.split("\n")))
    if llm_result is None:
        raise ValueError("LLM result is None")
    is_true = "True" in llm_result
    is_false = "False" in llm_result
    is_dont_know = "Dont know" in llm_result
    reason = llm_result.split("\n")[1] if len(llm_result.split("\n")) > 1 else None
    result: Literal["True", "False", "Dont know"]
    if is_true:
        result = "True"
    elif is_false:
        result = "False"
    elif is_dont_know:
        result = "Dont know"
    else:
        raise ValueError("LLM result is not valid")
    return result, (reason or llm_result), response._hidden_params["response_cost"]

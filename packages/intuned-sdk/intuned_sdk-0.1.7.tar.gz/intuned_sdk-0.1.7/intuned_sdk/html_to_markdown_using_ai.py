import io
import os
from typing import Literal

import google.generativeai as genai
from PIL import Image
from playwright.async_api import Page

from .utils.clean_html import clean_html

SUPPORTED_GEMINI_MODELS_TYPE = Literal[
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
]

CONVERSION_MODE_TYPE = Literal["html", "screenshot", "hybrid"]

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]


def configure_gemini_client():
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=gemini_api_key)  # type: ignore


async def convert_html_to_markdown(
    page: Page, model: SUPPORTED_GEMINI_MODELS_TYPE, mode: CONVERSION_MODE_TYPE
) -> str:
    configure_gemini_client()

    model_client = genai.GenerativeModel(  # type: ignore
        model_name=model,
        generation_config={"temperature": 0.0},
        safety_settings=safety_settings,
        system_instruction="""
        Your task is to convert the content of the provided HTML into the corresponding markdown representation.
        You need to convert the structure, elements, and attributes of the HTML into equivalent representations in markdown format.
        ensuring that no important information is lost. The output should strictly be in markdown format, without any additional explanations.
        list of entities should be converted to markdown, dropping any information will lead to a loss of information.

        You should not use any type of html in the output, only markdown.
        do not drop important information, any entities or list of entities in the page should be converted to markdown.
        even if the item isn't visible in the page, it should be converted to markdown.
        ONLY DROP URLS IF THEY ARE PART OF A NAV BAR, DO NOT DROP ANY URL THAT IS NOT PART OF A NAV BAR.

        """,
    )

    if mode == "html":
        page_content = await page.content()
        cleaned_html = clean_html(page_content)
        content = [cleaned_html]
    elif mode == "screenshot":
        screenshot = await create_pil_image(page)
        content = [screenshot]
    else:
        page_content = await page.content()
        cleaned_html = clean_html(page_content)
        screenshot = await create_pil_image(page)

        content = [cleaned_html, screenshot]

    response = model_client.generate_content(content)

    print_cost(response.usage_metadata, model)

    return response.text


def print_cost(usage_metadata, model_type: SUPPORTED_GEMINI_MODELS_TYPE):  # type: ignore
    prompt_tokens = usage_metadata.prompt_token_count  # type: ignore
    output_tokens = usage_metadata.candidates_token_count  # type: ignore

    if model_type == "gemini-1.5-flash":
        input_cost_per_million = 0.075
        output_cost_per_million = 0.30
    elif model_type == "gemini-1.5-pro":
        input_cost_per_million = 1.25
        output_cost_per_million = 5.00
    elif model_type == "gemini-2.0-flash":
        input_cost_per_million = 0.10
        output_cost_per_million = 0.40
    else:
        raise ValueError("Invalid model_type. Choose 'flash' or 'pro'.")

    input_cost = (prompt_tokens / 1_000_000) * input_cost_per_million  # type: ignore
    output_cost = (output_tokens / 1_000_000) * output_cost_per_million  # type: ignore

    total_cost = input_cost + output_cost  # type: ignore

    print(f"Total cost: ${total_cost:.6f}")


async def create_pil_image(page: Page) -> Image.Image:
    screenshot_bytes = await page.screenshot(full_page=True)
    image = Image.open(io.BytesIO(screenshot_bytes))
    return image


def get_simple_text() -> str:
    """
    Returns a simple text string.

    Returns:
        str: A simple text message.
    """
    return "This is a simple text 2 returned by the function."

from urllib.parse import quote
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse

from playwright.async_api import ElementHandle
from playwright.async_api import Locator
from playwright.async_api import Page


def convert_relative_url_to_full_url(*, relative_url: str, base_url: str) -> str:
    parsed_relative = urlparse(relative_url)
    is_full_url = bool(parsed_relative.scheme and parsed_relative.netloc)
    if is_full_url:
        return relative_url

    # Join base and relative URLs
    full_url = urljoin(base_url, relative_url)

    # Parse the full URL
    parsed_full = urlparse(full_url)

    # Encode the path, but don't re-encode %
    encoded_path = quote(parsed_full.path, safe="/%")

    # Encode the query, but don't re-encode % and other safe characters
    encoded_query = quote(parsed_full.query, safe="=&%")

    # Reconstruct the URL with encoded components
    encoded_full_url = urlunparse(
        (
            parsed_full.scheme,
            parsed_full.netloc,
            encoded_path,
            parsed_full.params,
            encoded_query,
            parsed_full.fragment,
        )
    )

    return encoded_full_url


async def convert_relative_url_to_full_url_with_page(
    *, relative_url: str, page: Page
) -> str:
    url = page.url
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return convert_relative_url_to_full_url(
        relative_url=relative_url, base_url=base_url
    )


async def get_absolute_url_using_anchor(*, locator: Locator | ElementHandle) -> str:
    """Get the absolute URL from an anchor element.

    This function takes a Playwright Locator or ElementHandle pointing to an anchor (<a>) element
    and returns its absolute href URL. It verifies that the element is actually an anchor tag
    before attempting to get the href.

    Parameters
    ----------
    locator : Union[Locator, ElementHandle]
        A Playwright Locator or ElementHandle pointing to the anchor element

    Returns
    -------
    str
        The absolute URL from the anchor element's href attribute

    Raises
    ------
    ValueError
        If the element is not an anchor (<a>) tag
        If the locator matches multiple elements
    """
    # get the element name from the locator
    element_name = await locator.evaluate("(element) => element.tagName")
    if element_name != "A":
        raise ValueError(f"Expected an anchor element, got {element_name}")
    if isinstance(locator, Locator):
        return await locator.evaluate("(element) => element.href", timeout=2000)
    return await locator.evaluate("(element) => element.href")

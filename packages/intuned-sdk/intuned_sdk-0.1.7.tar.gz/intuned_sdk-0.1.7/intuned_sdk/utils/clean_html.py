import re

from bs4 import BeautifulSoup
from bs4 import Comment


def clean_html(html_string: str, for_generate_code: bool = False) -> str:
    # Parse the HTML
    soup = BeautifulSoup(html_string, "html.parser")

    # Remove all script, style, and svg elements
    for script in soup(["script", "style", "svg"]):
        script.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
        comment.extract()

    # Remove long attributes (>500 characters) and style attributes
    for tag in soup.find_all():
        for attr, value in list(tag.attrs.items()):  # type: ignore
            if attr in ["class", "src"]:
                continue
            if attr == "style" or len(str(value)) > 500:
                del tag.attrs[attr]  # type: ignore

    if not for_generate_code:
        # Remove empty tags, but keep images
        for tag in soup.find_all():
            if (
                tag.name != "img"  # type: ignore
                and len(tag.get_text(strip=True)) == 0
                and len(tag.find_all()) == 0  # type: ignore
            ):
                tag.decompose()

    # Get the cleaned HTML as a string
    cleaned_html = str(soup)

    # Remove white spaces between tags
    cleaned_html = cleaned_html.replace(">\n<", "><")

    # Remove multiple empty lines
    cleaned_html = re.sub(r"\n\s*\n", "\n", cleaned_html)

    return cleaned_html


# All clean operations here are based on Mozilla's Readability.js
def _mozilla_readability_clean(soup: BeautifulSoup):
    # Cleaning tags that are unlikely to be useful content
    # https://github.com/mozilla/readability/blob/65578aeba436aa7dbaa16ceadc89b7ebd6dc6035/Readability.js#L1101-L1123

    unlikely_candidates_expression = re.compile(
        r"-ad-|ai2html|banner|combx|comment|community|cover-wrap|disqus|extra"
        r"|gdpr|legends|menu|related|remark|replies|rss"
        r"|shoutbox|sidebar|skyscraper|sponsor|supplemental|ad-break|agegate"
        r"|pager|popup|yom-remote"
    )

    candidates_expression = re.compile(r"and|article|body|column|content|main|shadow")

    unlikely_roles = [
        "menu",
        "menubar",
        "complementary",
        "navigation",
        "alert",
        "alertdialog",
        "dialog",
    ]

    for tag in soup.find_all():
        # try:
        if tag.decomposed:
            continue
        match_string = f"{tag.get('class', '')} {tag.get('id', '')}"  # type: ignore
        if (
            unlikely_candidates_expression.search(match_string)
            and not candidates_expression.search(match_string)
            and not tag.find_parent(["table", "code"])
            and tag.name not in ["body", "a"]  # type: ignore
        ):
            print(f"{tag.name} is an unlikely candidate {match_string}")  # type: ignore
            tag.decompose()
            continue

        if tag.get("role") in unlikely_roles:  # type: ignore
            print(f"{tag.name} is an unlikely candidate {tag.get("role")}")  # type: ignore
            tag.decompose()

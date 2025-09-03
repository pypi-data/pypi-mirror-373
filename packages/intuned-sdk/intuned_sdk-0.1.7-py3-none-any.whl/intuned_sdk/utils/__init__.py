# __init__.py

from .clean_html import clean_html

from .ensure_browser_scripts import ensure_browser_scripts
from .get_mode import is_generate_code_mode
from .get_s3_client import get_s3_client
from .get_proxy_env import get_proxy_env
from .scroll_to_bottom_until_no_more_data import scroll_to_bottom_until_no_more_data
from .wait_for_network_idle import wait_for_network_idle

__all__ = [
    "clean_html",
    "ensure_browser_scripts",
    "is_generate_code_mode",
    "get_s3_client",
    "get_proxy_env",
    "wait_for_network_idle",
    "scroll_to_bottom_until_no_more_data",
]

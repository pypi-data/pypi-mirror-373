import os
from typing import Optional

from playwright.async_api import ProxySettings


def get_proxy_env() -> Optional[ProxySettings]:
    server = os.getenv("PROXY_SERVER")
    username = os.getenv("PROXY_USERNAME")
    password = os.getenv("PROXY_PASSWORD")
    if server is None or username is None or password is None:
        return None
    return {
        "server": server,
        "username": username,
        "password": password,
    }

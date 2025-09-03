import os


def is_generate_code_mode():
    return os.environ.get("MODE") == "generate_code"

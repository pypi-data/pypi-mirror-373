########################################################################################################################
# IMPORTS

import time
from random import randint

from playwright.sync_api import Page


########################################################################################################################
# FUNCTIONS


def human_type(page: Page, text: str, delay: int = 100):
    for char in text:
        page.keyboard.type(char, delay=randint(int(delay * 0.5), int(delay * 1.5)))  # noqa: S311


def human_press_key(page: Page, key: str, count: int = 1, delay: int = 100, sleep=True):
    for _ in range(count):
        page.keyboard.press(key, delay=randint(int(delay * 0.5), int(delay * 1.5)))  # noqa: S311
        if sleep:
            time.sleep(randint(int(delay * 1.5), int(delay * 2.5)) / 1000)  # noqa: S311

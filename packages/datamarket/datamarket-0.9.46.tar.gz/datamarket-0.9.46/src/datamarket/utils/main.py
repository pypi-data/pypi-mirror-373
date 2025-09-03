########################################################################################################################
# IMPORTS

import asyncio
import logging
import random
import re
import shlex
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Literal, Self, Union

import pendulum
import requests
from bs4 import BeautifulSoup
from croniter import croniter
from dynaconf import Dynaconf, add_converter
from requests.exceptions import ProxyError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    retry_if_not_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
)

from ..exceptions import NotFoundError, RedirectionDetectedError
from ..interfaces.proxy import ProxyInterface

########################################################################################################################
# FUNCTIONS

logger = logging.getLogger(__name__)


class NoProjectFoundError(Exception):
    def __init__(self):
        super().__init__("Could not detect project. Did you add the config file?")


class NoPackageFoundError(Exception):
    def __init__(self):
        super().__init__("A project was detected but it has no packages inside the 'src' directory")


########################################################################################################################
# FUNCTIONS


def get_granular_date(
    granularity: Union[Literal["monthly", "biweekly", "weekly", "daily"], str],
    tz: str = "Europe/Madrid",
) -> pendulum.DateTime:
    """
    Returns the most recent date based on the given granularity or a custom cron expression.

    Args:
        granularity: Either a predefined value ("monthly", "biweekly", "weekly") or a custom cron expression.
        tz: Timezone to use for date calculations (default: "Europe/Madrid").

    Returns:
        A string representing the most recent date in the format "YYYY-MM-DD".

    Raises:
        ValueError: If the provided granularity or cron expression is invalid.
    """
    now = pendulum.now(tz)

    predefined_patterns = {
        "monthly": "0 0 1 * *",
        "biweekly": "0 0 1,15 * *",
        "weekly": "0 0 * * MON",
        "daily": "0 0 * * *",
        "now": "* * * * *",
    }

    cron_pattern = predefined_patterns.get(granularity, granularity)

    try:
        cron = croniter(cron_pattern, now)
        return cron.get_prev(pendulum.DateTime)
    except Exception as e:
        raise ValueError("Invalid cron expression or granularity specified.") from e


def read_converter(path_str: str):
    with open(path_str) as f:
        return f.read()


class Project:
    CONFIG_FILE_NAME = "config.toml"

    def __init__(self, path: Path):
        self.path = path

        try:
            self.pkg_name = next((self.path / "src").glob("*")).name
        except StopIteration as e:
            raise NoPackageFoundError() from e

        self.env_name = f"{self.pkg_name}_env"
        self.config_path = self.path / self.CONFIG_FILE_NAME
        self.tests_path = self.path / "tests"
        self.cmd_prefix = "dix vnc run --" if shutil.which("dix") else ""

    @classmethod
    def from_file(cls, file: Path | str) -> Self:
        file_path = Path(file).resolve()

        while file_path != file_path.parent:
            config_file = file_path / cls.CONFIG_FILE_NAME

            if not config_file.is_file():
                file_path = file_path.parent
                continue

            if file_path.parent == Path("/home"):
                raise NoProjectFoundError()

            return cls(file_path)

        raise NoProjectFoundError()

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_path": self.path,
            "cmd_prefix": self.cmd_prefix,
            "env_name": self.env_name,
            "pkg_name": self.pkg_name,
            "config_path": self.config_path,
        }

    def get_config(self, tz: str = "Europe/Madrid") -> Dynaconf:
        add_converter("read", read_converter)

        dt_now = get_granular_date("now", tz)
        dt_weekly = get_granular_date("weekly", tz)
        dt_biweekly = get_granular_date("biweekly", tz)

        config = Dynaconf(
            environments=True,
            env_switcher="SYSTYPE",
        )

        config.load_file(path=self.config_path)
        config.load_file(path=Path.home() / self.config_path.name)

        config.vars = {
            "year": dt_now.strftime("%Y"),
            "month": dt_now.strftime("%m"),
            "day": dt_now.strftime("%d"),
            "now": dt_now.strftime("%Y-%m-%d %H:%M:%S"),
            "now_stripped": dt_now.strftime("%Y%m%d%H%M%S"),
            "today": dt_now.strftime("%Y-%m-%d"),
            "today_stripped": dt_now.strftime("%Y%m%d"),
            "weekly_date": dt_weekly.strftime("%Y-%m-%d"),
            "weekly_date_stripped": dt_weekly.strftime("%Y%m%d"),
            "biweekly_date": dt_biweekly.strftime("%Y-%m-%d"),
            "biweekly_date_stripped": dt_biweekly.strftime("%Y%m%d"),
            "dynaconf_merge": True,
        }

        return config


def set_logger(level):
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(level.upper())
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    log.addHandler(ch)


def ban_sleep(max_time, min_time=0):
    sleep_time = int(random.uniform(min_time, max_time))  # noqa: S311
    logger.info(f"sleeping for {sleep_time} seconds...")
    time.sleep(sleep_time)


async def ban_sleep_async(max_time, min_time=0):
    sleep_time = int(random.uniform(min_time, max_time))  # noqa: S311
    logger.info(f"sleeping for {sleep_time} seconds...")
    await asyncio.sleep(sleep_time)


def run_bash_command(command):
    p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    text_lines = []
    for line_b in iter(p.stdout.readline, ""):
        line_str = line_b.decode().strip()

        if not line_str:
            break

        logger.info(line_str)
        text_lines.append(line_str)

    return "\n".join(text_lines)


def text_to_int(text):
    max_int32 = 2147483647
    parsed_str = re.sub(r"[^\d]", "", text)
    if parsed_str:
        num = int(parsed_str)
    else:
        return None

    if -max_int32 < num < max_int32:
        return num


def sleep_out_interval(from_h, to_h, tz="Europe/Madrid", seconds=1800):
    while pendulum.now(tz=tz).hour >= to_h or pendulum.now(tz=tz).hour < from_h:
        logger.warning("time to sleep and not scrape anything...")
        ban_sleep(seconds, seconds)


def sleep_in_interval(from_h, to_h, tz="Europe/Madrid", seconds=1800):
    while from_h <= pendulum.now(tz=tz).hour < to_h:
        logger.warning("time to sleep and not scrape anything...")
        ban_sleep(seconds, seconds)


def parse_field(dict_struct, field_path, format_method=None):
    if not isinstance(field_path, list):
        raise ValueError("Argument field_path must be of type list")

    field_value = dict_struct
    for field in field_path:
        if isinstance(field_value, dict):
            field_value = field_value.get(field)
        elif isinstance(field_value, list):
            field_value = field_value[field] if len(field_value) > field else None
        if field_value is None:
            return None
    return format_method(field_value) if format_method else field_value


@retry(
    retry=retry_if_not_exception_type((NotFoundError, RedirectionDetectedError, ProxyError)),
    wait=wait_exponential(exp_base=3, multiplier=3, max=60),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def get_data(
    url: str,
    method: str = "GET",
    output: str = "json",
    sleep: tuple = (6, 3),
    proxy_interface: ProxyInterface = None,
    use_auth_proxies: bool = False,
    max_proxy_delay: int = 1800,
    **kwargs,
):
    retry_type = retry_if_exception_type(ProxyError)
    wait = wait_exponential(exp_base=3, multiplier=3, max=60)
    stop = stop_after_delay(max_proxy_delay)
    before_sleep = before_sleep_log(logger, logging.WARNING)

    @retry(retry=retry_type, wait=wait, stop=stop, before_sleep=before_sleep, reraise=True)
    def _fetch_with_proxy_retry(url, method, proxy_interface, use_auth, **params):
        logger.info(f"Fetching data from {url} ...")
        proxy_cfg = None
        if proxy_interface:
            host, port, user, pwd = proxy_interface.get_proxies(raw=True, use_auth=use_auth)
            if host and port:
                proxy_url = f"http://{host}:{port}"
                proxy_auth_url = f"http://{user}:{pwd}@{host}:{port}"
                proxy_cfg = {"http": proxy_url, "https": proxy_url}
                if user and pwd:
                    proxy_cfg = {"http": proxy_auth_url, "https": proxy_auth_url}
                logger.info(f"Using proxy: {proxy_url}")
        response = getattr(requests, method.lower())(url, proxies=proxy_cfg, **params)
        return response

    params = {"timeout": 30} | kwargs
    r = _fetch_with_proxy_retry(url, method, proxy_interface, use_auth_proxies, **params)

    ban_sleep(*sleep)

    if r.status_code == 404:
        raise NotFoundError(f"404 Not Found error for {url}")
    r.raise_for_status()
    r.encoding = "utf-8"

    if output == "json":
        return r.json()
    elif output == "text":
        return r.text
    elif output == "soup":
        return BeautifulSoup(r.content, "html.parser")
    elif output == "response":
        return r

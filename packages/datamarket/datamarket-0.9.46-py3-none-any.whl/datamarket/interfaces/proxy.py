########################################################################################################################
# IMPORTS

import logging
import random
import time

import requests
from stem import Signal
from stem.control import Controller

########################################################################################################################
# CLASSES

logger = logging.getLogger(__name__)
logging.getLogger("stem").setLevel(logging.WARNING)


class ProxyInterface:
    CHECK_IP_URL = "https://wtfismyip.com/json"

    def __init__(self, config):
        if "proxy" in config:
            self.config = config["proxy"]
            self.current_index = 0  # Initialize index for round robin
        else:
            logger.warning("no proxy section in config")

    @property
    def proxies(self):
        return self.get_proxies(use_tor="tor_password" in self.config)

    @staticmethod
    def get_proxy_url(host, port, user=None, password=None, use_socks=True):
        proxy_url = f"{host}:{port}"

        if user and password:
            proxy_url = f"{user}:{password}@{proxy_url}"

        proxy_url = f"socks5://{proxy_url}" if use_socks else f"http://{proxy_url}"
        return proxy_url

    def get_proxies(self, use_tor=False, randomize=False):
        if use_tor:
            proxy_url = self.get_proxy_url("127.0.0.1", 9050)
        else:
            current_host, current_port = self.get_random_host_port() if randomize else self.get_current_host_port()

            user = self.config.get("user")
            password = self.config.get("password")
            use_socks = self.config.get("socks", "false").lower() == "true"

            proxy_url = self.get_proxy_url(current_host, current_port, user, password, use_socks)

        return {
            "http": proxy_url,
            "https": proxy_url,
        }

    def get_current_host_port(self):
        host_port_pairs = [hp.split(":") for hp in self.config["hosts"]]
        current_host, current_port = host_port_pairs[self.current_index]
        self.current_index = (self.current_index + 1) % len(host_port_pairs)
        return current_host, current_port

    def get_random_host_port(self):
        host_port_pairs = [hp.split(":") for hp in self.config["hosts"]]
        self.current_index = random.randint(0, len(host_port_pairs) - 1)  # noqa: S311
        return host_port_pairs[self.current_index]

    def check_current_ip(self):
        try:
            return requests.get(self.CHECK_IP_URL, proxies=self.proxies, timeout=30).json()["YourFuckingIPAddress",]
        except Exception as ex:
            logger.error(ex)

    def renew_tor_ip(self):
        try:
            logger.info(f"renewing Tor ip: {self.check_current_ip()}...")
            with Controller.from_port(port=9051) as controller:
                controller.authenticate(password=self.config["tor_password"])
                controller.signal(Signal.NEWNYM)

            time.sleep(5)
            logger.info(f"new Tor IP: {self.check_current_ip()}")

        except Exception as ex:
            logger.error("unable to renew Tor ip")
            logger.error(ex)

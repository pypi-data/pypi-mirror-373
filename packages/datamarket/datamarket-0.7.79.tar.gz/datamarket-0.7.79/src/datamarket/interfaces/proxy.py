import logging
import time
import random
import requests
from stem import Signal
from stem.control import Controller

logger = logging.getLogger(__name__)
logging.getLogger("stem").setLevel(logging.WARNING)


class ProxyInterface:
    """
    Manage HTTP, HTTPS, and SOCKS5 proxies configured in the [proxy] section.
    """

    CHECK_IP_URL = "https://wtfismyip.com/json"

    def __init__(self, config):
        self._load_from_config(config)
        self.current_index = random.randrange(len(self.entries)) if self.entries else 0

    def _load_from_config(self, cfg):
        # Tor password (optional)
        self.tor_password = cfg.get("proxy", "tor_password", fallback=None)

        # Comma-separated list of hosts
        hosts_raw = cfg.get("proxy", "hosts", fallback="")
        if not hosts_raw:
            raise RuntimeError("[proxy] hosts list is empty")

        entries = []
        for host_entry in (h.strip() for h in hosts_raw.split(",") if h.strip()):
            host, port, user, password = self._parse_host_entry(host_entry)
            entries.append((host, port, user, password))

        self.entries = entries

    def _parse_host_entry(self, host_entry):
        if "@" in host_entry:
            auth_part, host_part = host_entry.rsplit("@", 1)
            host, port = host_part.split(":")
            user, password = auth_part.split(":", 1)
            return host, port, user, password
        else:
            host, port = host_entry.split(":")
            return host, port, None, None

    @property
    def proxies(self):
        return self.get_proxies(use_tor=bool(self.tor_password))

    @staticmethod
    def get_proxy_url(host, port, user=None, password=None, schema="http"):
        auth = f"{user}:{password}@" if user and password else ""
        return f"{schema}://{auth}{host}:{port}"

    def get_proxies(self, use_tor=False, randomize=False, raw=False, use_auth=False):
        """
        Return parsed proxy URLs or raw entry tuple.

        :param use_tor: route via local Tor SOCKS5 if True
        :param randomize: select a random proxy if True, otherwise round-robin
        :param raw: return raw (host, port, user, password) tuple if True
        :param use_auth: include proxies that require authentication if True; otherwise only credential-free
        """
        # Tor handling
        if use_tor:
            if raw:
                return ("127.0.0.1", "9050", None, None)
            return {"socks5": self.get_proxy_url("127.0.0.1", 9050, schema="socks5")}

        # Select entry based on strategy and auth preference
        host, port, user, password = self.get_random(use_auth) if randomize else self.get_next(use_auth)

        if raw:
            return host, port, user, password

        # Build mapping of proxy URLs
        return {
            "http": self.get_proxy_url(host, port, user, password, "http"),
            "https": self.get_proxy_url(host, port, user, password, "https"),
            "socks5": self.get_proxy_url(host, port, user, password, "socks5"),
        }

    def get_next(self, use_auth=False):
        # Round-robin selection, optionally filtering out authenticated proxies
        if not self.entries:
            raise RuntimeError("No proxies available")

        pool = self.entries if use_auth else [e for e in self.entries if not e[2] and not e[3]]
        if not pool:
            pool = self.entries

        # Find next in pool using current_index
        for _ in range(len(self.entries)):
            idx = self.current_index
            self.current_index = (self.current_index + 1) % len(self.entries)
            entry = self.entries[idx]
            if entry in pool:
                return entry

        # Fallback to first entry
        return self.entries[0]

    def get_random(self, use_auth=False):
        # Random selection, optionally filtering out authenticated proxies
        if not self.entries:
            raise RuntimeError("No proxies available")

        pool = self.entries if use_auth else [e for e in self.entries if not e[2] and not e[3]]
        if not pool:
            pool = self.entries

        entry = random.choice(pool)
        # Update index to after selected entry for round-robin continuity
        try:
            pos = self.entries.index(entry)
            self.current_index = (pos + 1) % len(self.entries)
        except ValueError:
            pass

        return entry

    def check_current_ip(self):
        try:
            resp = requests.get(self.CHECK_IP_URL, proxies={"http": self.proxies["http"]})
            return resp.json().get("YourFuckingIPAddress")
        except Exception as ex:
            logger.error(ex)

    def renew_tor_ip(self):
        if not self.tor_password:
            logger.error("Tor password not configured")
            return

        try:
            logger.info(f"Current IP: {self.check_current_ip()}")
            with Controller.from_port(port=9051) as controller:
                controller.authenticate(password=self.tor_password)
                controller.signal(Signal.NEWNYM)

            time.sleep(5)
            logger.info(f"New IP: {self.check_current_ip()}")
        except Exception as ex:
            logger.error("Failed to renew Tor IP")
            logger.error(ex)

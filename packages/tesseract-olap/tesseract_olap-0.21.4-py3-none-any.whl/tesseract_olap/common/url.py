import re
from collections import defaultdict
from typing import Optional
from urllib.parse import ParseResult, parse_qs, urlencode, urlparse, urlunparse


def hide_dsn_password(dsn: str) -> str:
    return re.sub(r"(\w+://[^:]+:)[^@]+(@)", r"\1***\2", dsn)


class URL:
    scheme: str
    username: Optional[str]
    password: Optional[str]
    hostname: str
    port: Optional[int]
    path: str
    params: str
    fragment: str
    query_params: "dict[str, list[str]]"

    def __init__(self, url: str):
        self.query_params = defaultdict(list)

        parsed_url = urlparse(url)

        self.scheme = parsed_url.scheme
        self.username = parsed_url.username
        self.password = parsed_url.password
        self.hostname = parsed_url.hostname or ""
        self.port = parsed_url.port
        self.path = parsed_url.path
        self.params = parsed_url.params
        self.fragment = parsed_url.fragment
        self.query_params.update(parse_qs(parsed_url.query))

    def __repr__(self):
        return f"<URL='{self!s}'>"

    def __str__(self):
        parsed_url = ParseResult(
            self.scheme,
            self.netloc,
            self.path,
            self.params,
            self.query,
            self.fragment,
        )
        return urlunparse(parsed_url)

    @property
    def netloc(self):
        userinfo = f"{self.username or ''}:{self.password or ''}"

        netloc = f"{userinfo}@{self.hostname}" if userinfo != ":" else self.hostname

        if self.port is not None:
            netloc += f":{self.port}"

        return netloc

    @property
    def query(self):
        return urlencode(self.query_params, doseq=True)

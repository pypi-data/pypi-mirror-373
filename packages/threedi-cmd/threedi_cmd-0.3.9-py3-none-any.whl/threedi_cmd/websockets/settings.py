from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class WebSocketSettings:
    api_base_url: str
    token: str
    host: str = field(init=False)
    proto: str = field(init=False)
    api_version: str = field(init=False)

    def __post_init__(self):
        parsed_url = urlparse(self.api_base_url)
        self.host = parsed_url.netloc
        self.proto = "wss" if parsed_url.scheme == "https" else "ws"
        self.api_version = parsed_url.path.lstrip("/")

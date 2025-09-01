from requests_toolbelt.sessions import BaseUrlSession
from urllib.parse import urlunparse
from typing import Callable, List


class HttpClient:
    def __init__(
        self,
        host: str,
        port: int | None = None,
        apikey: str | None = None,
        is_https: bool = False
    ):
        self.host = host
        self.port = port
        self.apikey = apikey
        self.token = None
        self.user_id = None
        self.agent_id = None
        self.is_https = is_https
        self.headers = {}

        self.middlewares: List[Callable] = [
            self.__before_secure_request,
            self.__before_jwt_request,
        ]

    def set_token(self, token: str):
        self.token = token
        return self

    def get_http_uri(self) -> str:
        scheme = "https" if self.is_https else "http"
        netloc = f"{self.host}:{self.port}" if self.port else self.host

        return urlunparse((scheme, netloc, "", "", "", ""))

    def __before_secure_request(self):
        if self.apikey:
            self.headers["Authorization"] = f"Bearer {self.apikey}"
        if self.user_id:
            self.headers["user_id"] = self.user_id
        if self.agent_id:
            self.headers["agent_id"] = self.agent_id

    def __before_jwt_request(self):
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
        if self.agent_id:
            self.headers["agent_id"] = self.agent_id

    def get_client(self, agent_id: str | None = None, user_id: str | None = None) -> BaseUrlSession:
        if not self.apikey and not self.token:
            raise ValueError("You must provide an apikey or a token")

        self.agent_id = agent_id
        self.user_id = user_id

        for middleware in self.middlewares:
            middleware()

        session = BaseUrlSession(base_url=self.get_http_uri())
        session.headers = self.headers

        return session

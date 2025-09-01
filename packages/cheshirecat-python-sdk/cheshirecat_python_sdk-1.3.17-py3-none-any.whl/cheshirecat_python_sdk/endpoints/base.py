from abc import ABC
from typing import Dict, Any, List, Tuple, Type
import requests
from pydantic import BaseModel
from websockets import ClientConnection

from cheshirecat_python_sdk.utils import T, deserialize


class MultipartPayload(BaseModel):
    data: Dict[str, Any] | None = None
    files: List[Tuple] | None = None


class AbstractEndpoint(ABC):
    def __init__(self, client: "CheshireCatClient"):
        self.client = client
        self.prefix = ""
        self.system_id = "system"

    def format_url(self, endpoint: str) -> str:
        return f"/{self.prefix}/{endpoint}".replace("//", "/")

    def get_http_client(self, agent_id: str | None = None, user_id: str | None = None) -> requests.Session:
        return self.client.http_client.get_client(agent_id, user_id)

    async def get_ws_client(self, agent_id: str, user_id: str) -> ClientConnection:
        return await self.client.ws_client.get_client(agent_id, user_id)

    def get(
        self,
        endpoint: str,
        agent_id: str,
        output_class: Type[T] | None = None,
        query: Dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> T:
        options = {}
        if query:
            options["params"] = query

        response = self.get_http_client(agent_id, user_id).get(endpoint, **options)
        response.raise_for_status()

        if output_class is None:
            return response.json()
        return deserialize(response.json(), output_class)

    def post_json(
        self,
        endpoint: str,
        agent_id: str,
        output_class: Type[T] | None = None,
        payload: Dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> T:
        options = {}
        if payload:
            options["json"] = payload

        response = self.get_http_client(agent_id, user_id).post(endpoint, **options)
        response.raise_for_status()

        if output_class is None:
            return response.json()
        return deserialize(response.json(), output_class)

    def post_multipart(
        self,
        endpoint: str,
        agent_id: str,
        output_class: Type[T] | None = None,
        payload: MultipartPayload | None = None,
        user_id: str | None = None,
    ) -> T:
        options = {}
        if payload.data:
            options["data"] = payload.data
        if payload.files:
            options["files"] = payload.files

        response = self.get_http_client(agent_id, user_id).post(endpoint, **options)
        response.raise_for_status()

        if output_class is None:
            return response.json()
        return deserialize(response.json(), output_class)

    def put(
        self,
        endpoint: str,
        agent_id: str,
        output_class: Type[T] | None = None,
        payload: Dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> T:
        options = {}
        if payload:
            options["json"] = payload

        response = self.get_http_client(agent_id, user_id).put(endpoint, **options)
        response.raise_for_status()

        if output_class is None:
            return response.json()
        return deserialize(response.json(), output_class)

    def delete(
        self,
        endpoint: str,
        agent_id: str,
        output_class: Type[T] | None = None,
        user_id: str | None = None,
        payload: Dict[str, Any] | None = None,
    ) -> T:
        options = {}
        if payload:
            options["json"] = payload

        response = self.get_http_client(agent_id, user_id).delete(endpoint, **options)
        response.raise_for_status()

        if output_class is None:
            return response.json()
        return deserialize(response.json(), output_class)

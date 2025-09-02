import json
from pathlib import Path
from typing import Dict, Any, List

from cheshirecat_python_sdk.endpoints.base import AbstractEndpoint, MultipartPayload
from cheshirecat_python_sdk.models.api.rabbit_holes import (
    AllowedMimeTypesOutput,
    UploadSingleFileResponse,
    UploadUrlResponse,
)
from cheshirecat_python_sdk.utils import deserialize, file_attributes


class RabbitHoleEndpoint(AbstractEndpoint):
    def __init__(self, client: "CheshireCatClient"):
        super().__init__(client)
        self.prefix = "/rabbithole"

    def post_file(
        self,
        file_path,
        agent_id: str,
        file_name: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> UploadSingleFileResponse:
        """
        This method posts a file to the RabbitHole API. The file is uploaded to the RabbitHole server and ingested into
        the RAG system. The file is then processed by the RAG system and the results are stored in the RAG database.
        The process is asynchronous and the results are returned in a batch.
        The CheshireCat processes the injection in background and the client will be informed at the end of the process.
        :param file_path: The path to the file to upload.
        :param agent_id: The ID of the agent.
        :param file_name: The name of the file.
        :param metadata: The metadata to include with the file.
        :return: The response from the RabbitHole API.
        """
        file_name = file_name or Path(file_path).name

        payload = MultipartPayload(data={})
        if metadata is not None:
            payload.data["metadata"] = json.dumps(metadata)

        with open(file_path, "rb") as file:
            payload.files = [("file", file_attributes(file_name, file))]
            result = self.post_multipart(self.prefix, agent_id, output_class=UploadSingleFileResponse, payload=payload)

        return result

    def post_files(
        self,
        file_paths: List[str],
        agent_id: str,
        metadata: Dict[str, Any] | None = None
    ) -> Dict[str, UploadSingleFileResponse]:  # type: ignore
        """
        Posts multiple files to the RabbitHole API. The files are uploaded to the RabbitHole server and
        ingested into the RAG system. The files are processed in a batch. The process is asynchronous.
        The CheshireCat processes the injection in background and the client will be informed at the end of the process.
        :param file_paths: The paths to the files to upload.
        :param agent_id: The ID of the agent.
        :param metadata: The metadata to include with the files.
        :return: The response from the RabbitHole API.
        """
        data = {}
        if metadata is not None:
            data["metadata"] = json.dumps(metadata)

        files = []
        file_handles = []
        try:
            for file_path in file_paths:
                file = open(file_path, "rb")
                file_handles.append(file)
                files.append(("files", file_attributes(Path(file_path).name, file)))

            response = self.get_http_client(agent_id).post(self.format_url("/batch"), data=data, files=files)
            response.raise_for_status()

            result = {}
            for key, item in response.json().items():
                result[key] = deserialize(item, UploadSingleFileResponse)
            return result
        finally:
            for file in file_handles:
                file.close()

    def post_web(
        self,
        web_url: str,
        agent_id: str,
        metadata: Dict[str, Any] | None = None
    ) -> UploadUrlResponse:
        """
        Posts a web URL to the RabbitHole API. The web URL is ingested into the RAG system. The web URL is
        processed by the RAG system by Web scraping, and the results are stored in the RAG database.
        The process is asynchronous.
        The CheshireCat processes the injection in background, and the client will be informed at the end of the process.
        :param web_url: The URL of the website to ingest.
        :param agent_id: The ID of the agent.
        :param metadata: The metadata to include with the files.
        :return: The response from the RabbitHole API.
        """
        payload = {"url": web_url}
        if metadata is not None:
            payload["metadata"] = metadata  # type: ignore

        return self.post_json(self.format_url("/web"), agent_id, output_class=UploadUrlResponse, payload=payload)

    def post_memory(
        self,
        file_path: str,
        agent_id: str,
        file_name: str | None = None,
    ) -> UploadSingleFileResponse:
        """
        Posts a memory point, for the agent identified by the agent_id parameter.
        The memory point is ingested into the RAG system. The process is asynchronous. The provided file must be in JSON
        format. The CheshireCat processes the injection in the background, and the client will be informed at the end of
        the process.
        :param file_path: The path to the file to upload.
        :param agent_id: The ID of the agent.
        :param file_name: The name of the file (optional).
        :return: The response from the RabbitHole API.
        """
        file_name = file_name or Path(file_path).name

        payload = MultipartPayload()
        with open(file_path, "rb") as file:
            payload.files = [("file", file_attributes(file_name, file))]
            result = self.post_multipart(
                self.format_url("/memory"), agent_id, output_class=UploadSingleFileResponse, payload=payload
            )

        return result

    def get_allowed_mime_types(self, agent_id: str) -> AllowedMimeTypesOutput:
        """
        Retrieves the allowed MIME types for the RabbitHole API. The allowed MIME types are the MIME types
        that are allowed to be uploaded to the RabbitHole API. The allowed MIME types are returned in a list.
        :param agent_id: The ID of the agent.
        :return: AllowedMimeTypesOutput, the details of the allowed MIME types.
        """
        return self.get(
            self.format_url("/allowed-mimetypes"),
            agent_id,
            output_class=AllowedMimeTypesOutput
        )

    def get_web_sources(self, agent_id: str) -> List[str]:
        """
        This method retrieves the web sources for the RabbitHole API. The web sources are the web URLs that are allowed
        to be uploaded to the RabbitHole API. The web sources are returned in a list.
        :param agent_id: The ID of the agent.
        :return: List[str]
        """
        return self.get(
            self.format_url("/web"),
            agent_id,
        )

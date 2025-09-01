from typing import Dict, Any
from requests import Response

from cheshirecat_python_sdk.endpoints.base import AbstractEndpoint
from cheshirecat_python_sdk.models.api.factories import FactoryObjectSettingOutput, FactoryObjectSettingsOutput
from cheshirecat_python_sdk.models.api.file_managers import FileManagerAttributes


class FileManagerEndpoint(AbstractEndpoint):
    def __init__(self, client: "CheshireCatClient"):
        super().__init__(client)
        self.prefix = "/file_manager"

    def get_file_managers_settings(self, agent_id: str) -> FactoryObjectSettingsOutput:
        """
        Get all file managers settings for the agent specified by agent_id
        :param agent_id: The agent id
        :return: FactoryObjectSettingsOutput, the settings of all file managers
        """
        return self.get(
            self.format_url("/settings"),
            agent_id,
            output_class=FactoryObjectSettingsOutput,
        )

    def get_file_manager_settings(self, file_manager: str, agent_id: str) -> FactoryObjectSettingOutput:
        """
        Get the settings of a file manager by name for the agent specified by agent_id
        :param file_manager: str, the name of the file manager
        :param agent_id: The agent id
        :return: FactoryObjectSettingOutput, the settings of the file manager
        """
        return self.get(
            self.format_url(f"/settings/{file_manager}"),
            agent_id,
            output_class=FactoryObjectSettingOutput,
        )

    def put_file_manager_settings(
        self, file_manager: str, agent_id: str, values: Dict[str, Any]
    ) -> FactoryObjectSettingOutput:
        """
        Update the settings of a file manager by name with the given values, for the agent specified by agent_id
        :param file_manager: str, the name of the file manager
        :param agent_id: The agent id
        :param values: Dict[str, Any], the values to update
        :return: FactoryObjectSettingOutput, the updated settings of the file manager
        """
        return self.put(
            self.format_url(f"/settings/{file_manager}"),
            agent_id,
            output_class=FactoryObjectSettingOutput,
            payload=values,
        )

    def get_file_manager_attributes(self, agent_id: str) -> FileManagerAttributes:
        """
        Get the attributes of the file manager for the agent specified by agent_id
        :param agent_id: The agent id
        :return: FileManagerAttributes, the attributes of the file manager
        """
        return self.get(self.prefix, agent_id, output_class=FileManagerAttributes)

    def get_file(self, agent_id: str, file_path: str) -> Response:
        """
        Download a file from the file manager for the agent specified by agent_id
        :param agent_id: The agent id
        :param file_path: The path of the file to download
        :return: Response, the response containing the file content
        """
        response = self.get_http_client(agent_id).get(
            self.format_url(f"/download/{file_path}"),
            stream=True,
            headers={"Accept": "application/octet-stream"}
        )
        response.raise_for_status()

        return response

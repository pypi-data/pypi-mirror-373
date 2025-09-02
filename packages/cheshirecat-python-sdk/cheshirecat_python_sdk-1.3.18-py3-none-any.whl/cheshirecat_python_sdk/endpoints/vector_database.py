from typing import Dict, Any

from cheshirecat_python_sdk.endpoints.base import AbstractEndpoint
from cheshirecat_python_sdk.models.api.factories import FactoryObjectSettingsOutput, FactoryObjectSettingOutput


class VectorDatabaseEndpoint(AbstractEndpoint):
    def __init__(self, client: "CheshireCatClient"):
        super().__init__(client)
        self.prefix = "/vector_database"

    def get_vector_databases_settings(self, agent_id: str) -> FactoryObjectSettingsOutput:
        """
        Get all vector databases settings for the agent specified by agent_id
        :param agent_id: The agent id
        :return: FactoryObjectSettingsOutput, a list of vector database settings
        """
        return self.get(
            self.format_url("/settings"),
            agent_id,
            output_class=FactoryObjectSettingsOutput,
        )

    def get_vector_database_settings(self, vector_database: str, agent_id: str) -> FactoryObjectSettingOutput:
        """
        Get the vector database settings for the vector database specified by vector_database and agent_id
        :param vector_database: The name of the vector database
        :param agent_id: The agent id
        :return: FactoryObjectSettingOutput, the vector database settings
        """
        return self.get(
            self.format_url(f"/settings/{vector_database}"),
            agent_id,
            output_class=FactoryObjectSettingOutput,
        )

    def put_vector_database_settings(
        self, vector_database: str, agent_id: str, values: Dict[str, Any]
    ) -> FactoryObjectSettingOutput:
        """
        Update the vector database settings for the vector database specified by vector_database and agent_id
        :param vector_database: The name of the vector database
        :param agent_id: The agent id
        :param values: The new settings
        :return: FactoryObjectSettingOutput, the updated vector database settings
        """
        return self.put(
            self.format_url(f"/settings/{vector_database}"),
            agent_id,
            output_class=FactoryObjectSettingOutput,
            payload=values,
        )

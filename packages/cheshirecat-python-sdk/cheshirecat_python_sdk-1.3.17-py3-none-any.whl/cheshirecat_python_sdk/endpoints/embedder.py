from typing import Dict, Any

from cheshirecat_python_sdk.endpoints.base import AbstractEndpoint
from cheshirecat_python_sdk.models.api.factories import FactoryObjectSettingOutput, FactoryObjectSettingsOutput


class EmbedderEndpoint(AbstractEndpoint):
    def __init__(self, client: "CheshireCatClient"):
        super().__init__(client)
        self.prefix = "/embedder"

    def get_embedders_settings(self) -> FactoryObjectSettingsOutput:
        """
        Get all embedders settings for the system
        :return: FactoryObjectSettingsOutput, a list of embedders settings
        """
        return self.get(
            self.format_url("/settings"),
            self.system_id,
            output_class=FactoryObjectSettingsOutput,
        )

    def get_embedder_settings(self, embedder: str) -> FactoryObjectSettingOutput:
        """
        Get embedder settings for the system by embedder name
        :param embedder: The embedder name
        :return: FactoryObjectSettingOutput, embedder settings
        """
        return self.get(
            self.format_url(f"/settings/{embedder}"),
            self.system_id,
            output_class=FactoryObjectSettingOutput,
        )

    def put_embedder_settings(self, embedder: str, values: Dict[str, Any]) -> FactoryObjectSettingOutput:
        """
        Update embedder settings for the system by embedder name
        :param embedder: The embedder name
        :param values: The embedder settings
        :return: FactoryObjectSettingOutput, embedder settings
        """
        return self.put(
            self.format_url(f"/settings/{embedder}"),
            self.system_id,
            output_class=FactoryObjectSettingOutput,
            payload=values,
        )

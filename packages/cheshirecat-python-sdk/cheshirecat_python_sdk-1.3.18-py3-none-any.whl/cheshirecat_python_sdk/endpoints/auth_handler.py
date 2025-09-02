from typing import Dict, Any

from cheshirecat_python_sdk.endpoints.base import AbstractEndpoint
from cheshirecat_python_sdk.models.api.factories import FactoryObjectSettingsOutput, FactoryObjectSettingOutput


class AuthHandlerEndpoint(AbstractEndpoint):
    def __init__(self, client: "CheshireCatClient"):
        super().__init__(client)
        self.prefix = "/auth_handler"

    def get_auth_handlers_settings(self, agent_id: str) -> FactoryObjectSettingsOutput:
        """
        Get all auth handler settings for the agent with the given ID.
        :param agent_id: The ID of the agent.
        :return: FactoryObjectSettingsOutput, containing the settings for all auth handlers.
        """
        return self.get(
            self.format_url("/settings"),
            agent_id,
            output_class=FactoryObjectSettingsOutput,
        )

    def get_auth_handler_settings(self, auth_handler: str, agent_id: str) -> FactoryObjectSettingOutput:
        """
        Get the settings for the auth handler with the given name.
        :param auth_handler: The name of the auth handler.
        :param agent_id: The ID of the agent.
        :return: FactoryObjectSettingOutput, containing the settings for the auth handler.
        """
        return self.get(
            self.format_url(f"/settings/{auth_handler}"),
            agent_id,
            output_class=FactoryObjectSettingOutput,
        )

    def put_auth_handler_settings(
        self, auth_handler: str, agent_id: str, values: Dict[str, Any]
    ) -> FactoryObjectSettingOutput:
        """
        Update the settings for the auth handler with the given name.
        :param auth_handler: The name of the auth handler.
        :param agent_id: The ID of the agent.
        :param values: The new settings for the auth handler.
        :return: FactoryObjectSettingOutput, containing the updated settings for the auth handler.
        """
        return self.put(
            self.format_url(f"/settings/{auth_handler}"),
            agent_id,
            output_class=FactoryObjectSettingOutput,
            payload=values,
        )

from cheshirecat_python_sdk.endpoints.base import AbstractEndpoint
from cheshirecat_python_sdk.models.api.nested.plugins import PluginSettingsOutput
from cheshirecat_python_sdk.models.api.plugins import PluginCollectionOutput, PluginToggleOutput, PluginsSettingsOutput


class PluginsEndpoint(AbstractEndpoint):
    def __init__(self, client: "CheshireCatClient"):
        super().__init__(client)
        self.prefix = "/plugins"

    def get_available_plugins(self, agent_id: str, plugin_name: str | None = None) -> PluginCollectionOutput:
        """
        This endpoint returns the available plugins.
        :param agent_id: The id of the agent
        :param plugin_name: The name of the plugin to get
        :return: PluginCollectionOutput, the available plugins
        """
        return self.get(
            self.prefix,
            agent_id,
            output_class=PluginCollectionOutput,
            query={"query": plugin_name} if plugin_name else {},
        )

    def put_toggle_plugin(self, plugin_id: str, agent_id: str) -> PluginToggleOutput:
        """
        This endpoint toggles a plugin, for the agent identified by the agent_id parameter.
        :param plugin_id: The id of the plugin to toggle
        :param agent_id: The id of the agent
        :return: PluginToggleOutput, the toggled plugin
        """
        return self.put(
            self.format_url(f"/toggle/{plugin_id}"),
            agent_id,
            output_class=PluginToggleOutput,
        )

    def get_plugins_settings(self, agent_id: str) -> PluginsSettingsOutput:
        """
        This endpoint retrieves the plugins settings.
        :param agent_id: The id of the agent
        :return: PluginsSettingsOutput, the plugins settings
        """
        return self.get(
            self.format_url("/settings"),
            agent_id,
            output_class=PluginsSettingsOutput,
        )

    def get_plugin_settings(self, plugin_id: str, agent_id: str) -> PluginSettingsOutput:
        """
        This endpoint retrieves the plugin settings.
        :param plugin_id: The id of the plugin
        :param agent_id: The id of the agent
        :return: PluginSettingsOutput, the plugin settings
        """
        return self.get(
            self.format_url(f"/settings/{plugin_id}"),
            agent_id,
            output_class=PluginSettingsOutput,
        )

    def put_plugin_settings(self, plugin_id: str, agent_id: str, values: dict) -> PluginSettingsOutput:
        """
        This endpoint updates the plugin settings.
        :param plugin_id: The id of the plugin
        :param agent_id: The id of the agent
        :param values: The values to update
        :return: PluginSettingsOutput, the updated plugin settings
        """
        return self.put(
            self.format_url(f"/settings/{plugin_id}"),
            agent_id,
            output_class=PluginSettingsOutput,
            payload=values,
        )

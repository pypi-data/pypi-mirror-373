from typing import List, Any

from cheshirecat_python_sdk.endpoints.base import AbstractEndpoint, MultipartPayload
from cheshirecat_python_sdk.models.api.admins import (
    AdminOutput,
    ResetOutput,
    CreatedOutput,
    PluginInstallOutput,
    PluginInstallFromRegistryOutput,
    PluginDetailsOutput,
    PluginDeleteOutput,
)
from cheshirecat_python_sdk.models.api.nested.plugins import PluginSettingsOutput
from cheshirecat_python_sdk.models.api.plugins import PluginCollectionOutput, PluginsSettingsOutput
from cheshirecat_python_sdk.models.api.tokens import TokenOutput
from cheshirecat_python_sdk.utils import deserialize, file_attributes


class AdminsEndpoint(AbstractEndpoint):
    def __init__(self, client: "CheshireCatClient"):
        super().__init__(client)
        self.prefix = "/admins"

    def token(self, username: str, password: str) -> TokenOutput:
        """
        This endpoint is used to get a token for the user. The token is used to authenticate the user in the system.
        When the token expires, the user must request a new token.
        :param username: The username of the user.
        :param password: The password of the user.
        :return: TokenOutput, the token of the user.
        """
        response = self.get_http_client().post(
            self.format_url("/auth/token"),
            json={"username": username, "password": password},
        )
        response.raise_for_status()

        result = deserialize(response.json(), TokenOutput)
        self.client.add_token(result.access_token)
        return result

    def get_available_permissions(self) -> dict[int | str, Any]:
        """
        This endpoint is used to get a list of available permissions in the system. The permissions are used to define
        the access rights of the users in the system. The permissions are defined by the system administrator.
        :return array<int|string, Any>, the available permissions
        """
        response = self.get_http_client().get(self.format_url("/auth/available-permissions"))
        response.raise_for_status()

        return response.json()

    def post_admin(self, username: str, password: str, permissions: dict | None = None) -> AdminOutput:
        """
        Create a new admin user.
        :param username: The username of the user.
        :param password: The password of the user.
        :param permissions: The permissions of the user.
        :return: AdminOutput, the details of the user.
        """
        payload = {"username": username, "password": password}
        if permissions:
            payload["permissions"] = permissions  # type: ignore

        return self.post_json(self.format_url("/users"), self.system_id, output_class=AdminOutput, payload=payload)

    def get_admins(self, limit: int | None = None, skip: int | None = None) -> List[AdminOutput]:
        """
        Get a list of all admin users.
        :param limit: The maximum number of users to return.
        :param skip: The number of users to skip.
        :return: List[AdminOutput], the details
        """
        query = {}
        if limit:
            query["limit"] = limit
        if skip:
            query["skip"] = skip

        response = self.get_http_client(self.system_id).get(self.format_url("/users"), params=query)
        response.raise_for_status()

        result = []
        for item in response.json():
            result.append(deserialize(item, AdminOutput))
        return result

    def get_admin(self, admin_id: str) -> AdminOutput:
        """
        Get the details of an admin user.
        :param admin_id: The ID of the user.
        :return: AdminOutput, the details of the user.
        """
        return self.get(self.format_url(f"/users/{admin_id}"), self.system_id, output_class=AdminOutput)

    def put_admin(
        self,
        admin_id: str,
        username: str | None = None,
        password: str | None = None,
        permissions: dict | None = None,
    ) -> AdminOutput:
        """
        Update the details of an admin user.
        :param admin_id: The ID of the user.
        :param username: The new username.
        :param password: The new password.
        :param permissions: The new permissions.
        :return: AdminOutput, the details of the user.
        """
        payload = {}
        if username:
            payload["username"] = username
        if password:
            payload["password"] = password
        if permissions:
            payload["permissions"] = permissions

        return self.put(self.format_url(f"/users/{admin_id}"), self.system_id, output_class=AdminOutput, payload=payload)

    def delete_admin(self, admin_id: str) -> AdminOutput:
        """
        Delete an admin user.
        :param admin_id: The ID of the user.
        :return: AdminOutput, the details of the user.
        """
        return self.delete(self.format_url(f"/users/{admin_id}"), self.system_id, output_class=AdminOutput)

    def post_factory_reset(self) -> ResetOutput:
        """
        Reset the system to the factory settings.
        :return: ResetOutput, the details of the reset.
        """
        return self.post_json(self.format_url("/utils/factory/reset/"), self.system_id, output_class=ResetOutput)

    def get_agents(self) -> List[str]:
        """
        Get a list of all agents.
        :return: List[str], the IDs of the agents.
        """
        return self.get(self.format_url("/utils/agents/"), self.system_id)

    def post_agent_create(self, agent_id: str) -> CreatedOutput:
        """
        Create a new agent.
        :param agent_id: The ID of the agent.
        :return: CreatedOutput, the details of the agent.
        """
        return self.post_json(self.format_url("/utils/agent/create/"), agent_id, output_class=CreatedOutput)

    def post_agent_reset(self, agent_id: str) -> ResetOutput:
        """
        Reset an agent to the factory settings.
        :param agent_id: The ID of the agent.
        :return: ResetOutput, the details of the reset.
        """
        return self.post_json(self.format_url("/utils/agent/reset/"), agent_id, output_class=ResetOutput)

    def post_agent_destroy(self, agent_id: str) -> ResetOutput:
        """
        Destroy an agent.
        :param agent_id: The ID of the agent.
        :return: ResetOutput, the details of the reset.
        """
        return self.post_json(self.format_url("/utils/agent/destroy/"), agent_id, output_class=ResetOutput)

    def get_available_plugins(self, plugin_name: str | None = None) -> PluginCollectionOutput:
        """
        Get a list of all available plugins.
        :param plugin_name: The name of the plugin.
        :return: PluginCollectionOutput, the details of the plugins.
        """
        return self.get(
            self.format_url("/plugins"),
            self.system_id,
            output_class=PluginCollectionOutput,
            query={"query": plugin_name} if plugin_name else None,
        )

    def post_install_plugin_from_zip(self, path_zip: str) -> PluginInstallOutput:
        payload = MultipartPayload()

        with open(path_zip, "rb") as file:
            payload.files = [("file", file_attributes(path_zip, file))]
            result = self.post_multipart(
                self.format_url("/plugins/upload"),
                self.system_id,
                output_class=PluginInstallOutput,
                payload=payload,
            )
        return result

    def post_install_plugin_from_registry(self, url: str) -> PluginInstallFromRegistryOutput:
        """
        Install a new plugin from a registry. The plugin is installed asynchronously.
        :param url: The URL of the plugin.
        :return: PluginInstallFromRegistryOutput, the details of the installation.
        """
        return self.post_json(
            self.format_url("/plugins/upload/registry"),
            self.system_id,
            output_class=PluginInstallFromRegistryOutput,
            payload={"url": url},
        )

    def get_plugins_settings(self) -> PluginsSettingsOutput:
        """
        Get the default settings of all the plugins.
        :return: PluginsSettingsOutput, the details of the settings.
        """
        return self.get(self.format_url("/plugins/settings"), self.system_id, output_class=PluginsSettingsOutput)

    def get_plugin_settings(self, plugin_id: str) -> PluginSettingsOutput:
        """
        Get the default settings of a specific plugin.
        :param plugin_id: The ID of the plugin.
        :return: PluginSettingsOutput, the details of the settings.
        """
        return self.get(
            self.format_url(f"/plugins/settings/{plugin_id}"), self.system_id, output_class=PluginSettingsOutput
        )

    def get_plugin_details(self, plugin_id: str) -> PluginDetailsOutput:
        """
        Get the details of a specific plugin.
        :param plugin_id: The ID of the plugin.
        :return: PluginDetailsOutput, the details of the plugin.
        """
        return self.get(self.format_url(f"/plugins/{plugin_id}"), self.system_id, output_class=PluginDetailsOutput)

    def delete_plugin(self, plugin_id: str) -> PluginDeleteOutput:
        """
        Delete a specific plugin.
        :param plugin_id: The ID of the plugin.
        :return: PluginDeleteOutput, the details of the plugin.
        """
        return self.delete(self.format_url(f"/plugins/{plugin_id}"), self.system_id, output_class=PluginDeleteOutput)

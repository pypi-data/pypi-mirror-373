from cheshirecat_python_sdk.endpoints.base import AbstractEndpoint
from cheshirecat_python_sdk.models.api.settings import SettingsOutputCollection, SettingOutputItem, SettingDeleteOutput


class SettingsEndpoint(AbstractEndpoint):
    def __init__(self, client: "CheshireCatClient"):
        super().__init__(client)
        self.prefix = "/settings"

    def get_settings(self, agent_id: str) -> SettingsOutputCollection:
        """
        This endpoint returns the settings of the agent identified by the agent_id parameter.
        :param agent_id: The id of the agent to get settings for
        :return: SettingsOutputCollection, the settings of the agent
        """
        return self.get(self.prefix, agent_id, output_class=SettingsOutputCollection)

    def post_setting(self, agent_id: str, values: dict) -> SettingOutputItem:
        """
        This method creates a new setting for the agent identified by the agent_id parameter.
        :param agent_id: The id of the agent to create the setting for
        :param values: The values of the setting to create
        :return: SettingOutputItem, the created setting
        """
        return self.post_json(self.prefix, agent_id, output_class=SettingOutputItem, payload=values)

    def get_setting(self, setting_id: str, agent_id: str) -> SettingOutputItem:
        """
        This endpoint returns the setting identified by the setting_id parameter.
        :param setting_id: The id of the setting to get
        :param agent_id: The id of the agent to get the setting for
        :return: SettingOutputItem, the setting
        """
        return self.get(self.format_url(setting_id), agent_id, output_class=SettingOutputItem)

    def put_setting(self, setting_id: str, agent_id: str, values: dict) -> SettingOutputItem:
        """
        This method updates the setting identified by the setting_id parameter. The setting must belong to the agent
        identified by the agent_id parameter.
        :param setting_id: The id of the setting to update
        :param agent_id: The id of the agent to update the setting for
        :param values: The values to update the setting with
        :return: SettingOutputItem, the updated setting
        """
        return self.put(self.format_url(setting_id), agent_id, output_class=SettingOutputItem, payload=values)

    def delete_setting(self, setting_id: str, agent_id: str) -> SettingDeleteOutput:
        """
        This endpoint deletes the setting identified by the setting_id parameter. The setting must belong to the agent
        identified by the agent_id parameter.
        :param setting_id: The id of the setting to delete
        :param agent_id: The id of the agent to delete the setting for
        :return: SettingDeleteOutput, the deleted setting
        """
        return self.delete(self.format_url(setting_id), agent_id, output_class=SettingDeleteOutput)

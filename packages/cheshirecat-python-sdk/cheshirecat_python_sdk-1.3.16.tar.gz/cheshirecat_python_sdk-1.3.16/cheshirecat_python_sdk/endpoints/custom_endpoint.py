from typing import Any, Dict

from cheshirecat_python_sdk.endpoints.base import AbstractEndpoint


class CustomEndpoint(AbstractEndpoint):
    def get_custom(
        self, url: str, agent_id: str, user_id: str | None = None, query: Dict[str, Any] | None = None
    ) -> Any:
        """
        This method is used to trigger a custom endpoint with GET method
        :param url: The url of the custom endpoint to trigger
        :param agent_id: The id of the agent to get settings for (optional)
        :param user_id: The id of the user to get settings for (optional)
        :param query: The query parameters to send to the custom endpoint (optional)
        :return Any, the response from the custom endpoint
        """
        return self.get(url, agent_id, user_id=user_id, query=query)

    def post_custom(
        self, url: str, agent_id: str, payload: Dict[str, Any] | None = None, user_id: str | None = None
    ) -> Any:
        """
        This method is used to trigger a custom endpoint with POST method
        :param url: The url of the custom endpoint to trigger
        :param agent_id: The id of the agent to get settings for (optional)
        :param payload: The payload to send to the custom endpoint (optional)
        :param user_id: The id of the user to get settings for (optional)
        :return Any, the response from the custom endpoint
        """
        return self.post_json(url, agent_id, payload=payload, user_id=user_id)

    def put_custom(
        self, url: str, agent_id: str, payload: Dict[str, Any] | None = None, user_id: str | None = None
    ) -> Any:
        """
        The method is used to trigger a custom endpoint with PUT method
        :param url: The url of the custom endpoint to trigger
        :param agent_id: The id of the agent to get settings for (optional)
        :param payload: The payload to send to the custom endpoint (optional)
        :param user_id: The id of the user to get settings for (optional)
        :return Any, the response from the custom endpoint
        """
        return self.put(url, agent_id, payload=payload, user_id=user_id)

    def delete_custom(
        self, url: str, agent_id: str, payload: Dict[str, Any] | None = None, user_id: str | None = None
    ) -> Any:
        """
        This method is used to trigger a custom endpoint with DELETE method
        :param url: The url of the custom endpoint to trigger
        :param agent_id: The id of the agent to get settings for (optional)
        :param payload: The payload to send to the custom endpoint (optional)
        :param user_id: The id of the user to get settings for (optional)
        :return Any, the response from the custom endpoint
        """
        return self.delete(url, agent_id, payload=payload, user_id=user_id)

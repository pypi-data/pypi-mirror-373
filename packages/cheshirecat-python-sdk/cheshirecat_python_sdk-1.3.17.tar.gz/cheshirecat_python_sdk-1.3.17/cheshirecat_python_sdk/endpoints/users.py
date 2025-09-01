from typing import Any, List, Dict

from cheshirecat_python_sdk.endpoints.base import AbstractEndpoint
from cheshirecat_python_sdk.models.api.tokens import TokenOutput
from cheshirecat_python_sdk.models.api.users import UserOutput
from cheshirecat_python_sdk.utils import deserialize


class UsersEndpoint(AbstractEndpoint):
    def __init__(self, client: "CheshireCatClient"):
        super().__init__(client)
        self.prefix = "/users"

    def token(self, username: str, password: str) -> TokenOutput:
        """
        This endpoint is used to get a token for the user. The token is used to authenticate the user in the system. When
        the token expires, the user must request a new token.
        """
        response = self.get_http_client().post("/auth/token", json={
            "username": username,
            "password": password,
        })
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
        response = self.get_http_client().get("/auth/available-permissions")
        response.raise_for_status()

        return response.json()

    def post_user(
        self, agent_id: str, username: str, password: str, permissions: dict[str, Any] | None = None
    ) -> UserOutput:
        """
        This endpoint is used to create a new user in the system. The user is created with the specified username and
        password. The user is assigned the specified permissions. The permissions are used to define the access rights
        of the user in the system and are defined by the system administrator.
        The endpoint can be used for the agent identified by the agentId parameter.
        :param agent_id: The id of the agent to create the user for
        :param username: The username of the user to create
        :param password: The password of the user to create
        :param permissions: The permissions of the user to create (optional)
        :return UserOutput, the created user
        """
        payload = {
            "username": username,
            "password": password,
        }
        if permissions is not None:
            payload["permissions"] = permissions  # type: ignore

        return self.post_json(
            self.prefix,
            agent_id,
            output_class=UserOutput,
            payload=payload,
        )

    def get_users(self, agent_id: str) -> List[UserOutput]:
        """
        This endpoint is used to get a list of users in the system. The list includes the username and the permissions of
        each user. The permissions are used to define the access rights of the users in the system and are defined by the
        system administrator.
        The endpoint can be used for the agent identified by the agentId parameter.
        :param agent_id: The id of the agent to get users for
        :return List[UserOutput], the users in the system with their permissions for the agent identified by agent_id
        """
        response = self.get_http_client(agent_id).get(self.prefix)
        response.raise_for_status()

        result = []
        for item in response.json():
            result.append(deserialize(item, UserOutput))
        return result

    def get_user(self, user_id: str, agent_id: str) -> UserOutput:
        """
        This endpoint is used to get a user in the system. The user is identified by the userId parameter, previously
        provided by the CheshireCat API when the user was created. The endpoint returns the username and the permissions
        of the user. The permissions are used to define the access rights of the user in the system and are defined by
        the system administrator.
        The endpoint can be used for the agent identified by the agentId parameter.
        :param user_id: The id of the user to get
        :param agent_id: The id of the agent to get the user for
        :return UserOutput, the user
        """
        return self.get(self.format_url(user_id), agent_id, output_class=UserOutput)

    def put_user(
        self,
        user_id: str,
        agent_id: str,
        username: str | None = None,
        password: str | None = None,
        permissions: Dict[str, Any] | None = None,
    ) -> UserOutput:
        """
        The endpoint is used to update the user in the system. The user is identified by the userId parameter, previously
        provided by the CheshireCat API when the user was created. The endpoint updates the username, the password, and
        the permissions of the user. The permissions are used to define the access rights of the user in the system and
        are defined by the system administrator.
        The endpoint can be used for the agent identified by the agentId parameter.
        :param user_id: The id of the user to update
        :param agent_id: The id of the agent to update the user for
        :param username: The new username of the user (optional)
        :param password: The new password of the user (optional)
        :param permissions: The new permissions of the user (optional)
        :return UserOutput, the updated user
        """
        payload = {}
        if username is not None:
            payload["username"] = username
        if password is not None:
            payload["password"] = password
        if permissions is not None:
            payload["permissions"] = permissions

        return self.put(self.format_url(user_id), agent_id, output_class=UserOutput, payload=payload)

    def delete_user(self, user_id: str, agent_id: str) -> UserOutput:
        """
        This endpoint is used to delete the user in the system. The user is identified by the userId parameter, previously
        provided by the CheshireCat API when the user was created.
        The endpoint can be used for the agent identified by the agentId parameter.
        :param user_id: The id of the user to delete
        :param agent_id: The id of the agent to delete the user for
        :return UserOutput, the deleted user
        """
        return self.delete(self.format_url(user_id), agent_id, output_class=UserOutput)

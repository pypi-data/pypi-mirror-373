from typing import Callable
import json

from cheshirecat_python_sdk.endpoints.base import AbstractEndpoint
from cheshirecat_python_sdk.models.api.messages import MessageOutput
from cheshirecat_python_sdk.models.dtos import Message
from cheshirecat_python_sdk.utils import deserialize


class MessageEndpoint(AbstractEndpoint):
    def send_http_message(self, message: Message, agent_id: str, user_id: str) -> MessageOutput:
        """
        This endpoint sends a message to the agent identified by the agentId parameter. The message is sent via HTTP.
        :param message: Message object, the message to send
        :param agent_id: the agent id
        :param user_id: the user id
        """
        return self.post_json(
            '/message',
            agent_id,
            output_class=MessageOutput,
            payload=message.model_dump(),
            user_id=user_id,
        )

    async def send_websocket_message(
        self,
        message: Message,
        agent_id: str,
        user_id: str,
        callback: Callable[[str], None] | None = None
    ) -> MessageOutput:
        """
        This endpoint sends a message to the agent identified by the agentId parameter. The message is sent via WebSocket.
        :param message: Message object, the message to send
        :param agent_id: the agent id
        :param user_id: the user id
        :param callback: callable, a callback function that will be called for each message received
        """
        try:
            json_data = json.dumps(message.model_dump())
        except Exception:
            raise RuntimeError("Error encoding message")

        client = await self.get_ws_client(agent_id, user_id)

        try:
            await client.send(json_data)

            while True:
                response = await client.recv()
                if not response:
                    raise RuntimeError("Error receiving message")

                if '"type":"chat"' not in response:
                    if callback:
                        callback(response)
                    continue
                break
        except Exception as e:
            await client.close()
            raise Exception(f"WebSocket error: {str(e)}")

        await client.close()
        return deserialize(json.loads(response), MessageOutput)

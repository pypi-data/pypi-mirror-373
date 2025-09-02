from typing import Optional

from bigdata_client.api.chat import CreateNewChat
from bigdata_client.connection_protocol import BigdataConnectionProtocol
from bigdata_client.models.chat import (
    Chat,
    DefaultFormatter,
    InlineAttributionFormatter,
)


class ChatService:
    """For interacting with Chat objects"""

    def __init__(self, api_connection: BigdataConnectionProtocol):
        self._api = api_connection

    def new(
        self,
        name: str,
        formatter: Optional[InlineAttributionFormatter] = None,
    ) -> Chat:
        """Create a new chat"""
        response = self._api.create_chat(CreateNewChat(name=name))
        formatter = formatter or DefaultFormatter()
        return response.to_chat_model(self._api, formatter=formatter)

    def list(
        self, formatter: Optional[InlineAttributionFormatter] = None
    ) -> list[Chat]:
        response = self._api.get_all_chats()
        formatter = formatter or DefaultFormatter()
        return response.to_chat_list(self._api, formatter=formatter)

    def get(
        self,
        id_: str,
        formatter: Optional[InlineAttributionFormatter] = None,
    ) -> Chat:
        """Return a Chat by its id"""
        response = self._api.get_chat(id_)
        formatter = formatter or DefaultFormatter()
        return response.to_chat_model(self._api, formatter=formatter)

    def delete(self, id_: str):
        """Delete a Chat by its id"""
        self._api.delete_chat(id_)

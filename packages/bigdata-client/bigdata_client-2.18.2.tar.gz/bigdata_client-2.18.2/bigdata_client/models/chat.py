from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field, computed_field, field_validator

from bigdata_client.connection_protocol import BigdataConnectionProtocol
from bigdata_client.constants import MAX_CHAT_QUESTION_LENGTH, MIN_CHAT_QUESTION_LENGTH
from bigdata_client.enum_utils import StrEnum
from bigdata_client.exceptions import BigdataClientChatInvalidQuestion
from bigdata_client.models.sources import Source


class ChatScope(StrEnum):
    EARNING_CALLS = "earnings_calls"
    FILES = "files"
    NEWS = "news"
    REGULATORY_FILINGS = "filings"
    FACTSET_TRANSCRIPTS = "transcripts"


class ChatSource(BaseModel):
    """Represents a source in a chat message"""

    id: str
    headline: str
    url: Optional[str]
    document_scope: Optional[str]
    rp_provider_id: Optional[str]
    timestamp: Optional[str] = None
    image_urls: list[str] = Field(default_factory=list)


class QuotaUsage(BaseModel):
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    searches_count: Optional[int] = None


class InlineAttributionFormatter(ABC):
    """Interface for formatting inline attributions in chat messages"""

    @abstractmethod
    def format(self, index: int, source: ChatSource) -> str:
        """
        Format an inline attribution.

        Args:
            index (int): The index of the attribution within the list of attributions.
            source (ChatSource): The inline attribution to format.

        Returns:
            str: A string representing the formatted attribution.
        """


class DefaultFormatter(InlineAttributionFormatter):
    """Default formatter for inline attributions in chat messages"""

    def format(self, index: int, source: ChatSource) -> str:
        """
        Format an inline attribution using a default reference style.

        Args:
            index (int): The index of the attribution within the list of attributions.
            source (ChatSource): The inline attribution to format.

        Returns:
            str: A string representing the formatted attribution in default reference style.
        """
        return f"`:ref[{index}]` "


class MarkdownLinkFormatter(InlineAttributionFormatter):
    """Formatter for inline attributions in chat messages that uses Markdown links"""

    def __init__(
        self, headline_length: Optional[int] = None, skip_empty_urls: bool = True
    ):
        """
        Initialize the MarkdownLinkInlineAttributionFormatter.

        Args:
            headline_length (int): The maximum length of the headline to be displayed in the link. Default is 10.
        """
        self.headline_length = headline_length

    def format(self, index: int, source: ChatSource) -> str:
        """
        Format an inline attribution as a Markdown link.

        Args:
            index (int): The index of the attribution within the list of attributions.
            source (ChatSource): The inline attribution to format.

        Returns:
            str: A string representing the formatted attribution as a Markdown link.
        """
        hd = source.headline
        if self.headline_length:
            hd = source.headline[: self.headline_length]
        url = source.url or ""
        if url == "":
            return ""
        return f"[{hd}]({url}) "


class ChatInteraction(BaseModel):
    """Represents a single interaction with chat"""

    question: str
    answer: str
    interaction_timestamp: str
    date_created: datetime
    last_updated: datetime
    scope: Optional[ChatScope] = None
    sources: list[ChatSource] = Field(default_factory=list)
    usage: Optional[QuotaUsage] = None

    @field_validator("scope", mode="before")
    @classmethod
    def validate_scope(cls, value):
        if isinstance(value, str):
            try:
                return ChatScope(value)
            except ValueError:
                return None
        return value


def handle_ws_chat_response(
    chat,
    question,
    scope,
    complete_enriched_message: "ChatWSCompleteEnrichedResponse",  # noqa: F821
    sources,
    formatter,
):
    from bigdata_client.api.chat import ChatInteraction as ApiChatInteraction

    answer = complete_enriched_message.calculated_content_block.get("value", "")
    usage = complete_enriched_message.usage
    parsed_answer = ApiChatInteraction._parse_references(answer, sources, formatter)
    now = datetime.utcnow()
    interation = ChatInteraction(
        question=question,
        answer=parsed_answer,
        interaction_timestamp=complete_enriched_message.interaction_timestamp,
        date_created=now,
        last_updated=now,
        scope=scope,
        sources=sources,
        usage=usage.model_dump() if usage else None,
    )
    chat._interactions.append(interation)
    return interation


def deduplicate_sources(
    existing_sources: list[ChatSource], new_sources: list[ChatSource]
) -> list[ChatSource]:
    """
    Deduplicate sources when extending an existing list with new sources.
    If a source ID already exists, the existing source is kept and the new one is skipped.

    Args:
        existing_sources: List of existing ChatSource objects
        new_sources: List of new ChatSource objects to add

    Returns:
        List of ChatSource objects with duplicates removed
    """
    existing_ids = {source.id for source in existing_sources}
    deduplicated_sources = existing_sources.copy()

    for new_source in new_sources:
        if new_source.id not in existing_ids:
            deduplicated_sources.append(new_source)
            existing_ids.add(new_source.id)

    return deduplicated_sources


class StreamingChatInteraction(ChatInteraction):
    """
    Represents a streaming interaction in a chat session.

    This class handles live interactions where the response is obtained in chunks,
    allowing for real-time processing while the interaction is ongoing.
    """

    _chat: "Chat"
    _formatter: InlineAttributionFormatter
    _response: Optional[iter] = None

    source_filter: Optional[list[str]] = None

    def __init__(self, _chat, _formatter, **values):
        super().__init__(**values)

        self._chat = _chat
        self._formatter = _formatter
        self._response = None

    def __iter__(self):
        self._response = self._chat._api_connection.ask_chat(
            self._chat.id,
            self.question,
            scope=self.scope,
            source_filter=self.source_filter,
        )
        return self

    def __next__(self):
        from bigdata_client.api.chat import ChatInteraction as ApiChatInteraction
        from bigdata_client.api.chat import (
            ChatWSAuditTraceResponse,
            ChatWSCompleteEnrichedResponse,
            ChatWSSourcesResponse,
        )

        try:
            chunk = next(self._response)
            if isinstance(chunk, str):
                parsed_chunk = ApiChatInteraction._parse_references(
                    chunk, self.sources, self._formatter
                )
                return parsed_chunk
            elif isinstance(chunk, ChatWSCompleteEnrichedResponse):
                ws_chat_response = chunk
                interaction = handle_ws_chat_response(
                    chat=self._chat,
                    question=self.question,
                    scope=self.scope,
                    complete_enriched_message=ws_chat_response,
                    sources=self.sources,
                    formatter=self._formatter,
                )
                self.question = interaction.question
                self.answer = interaction.answer
                self.interaction_timestamp = interaction.interaction_timestamp
                self.date_created = interaction.date_created
                self.last_updated = interaction.last_updated
                self.scope = interaction.scope
                self.sources = interaction.sources
                self.usage = ws_chat_response.usage
                return ""
            elif isinstance(chunk, ChatWSAuditTraceResponse):
                new_sources = chunk.to_chat_source()
                self.sources = deduplicate_sources(self.sources, new_sources)
                return ""
            elif isinstance(chunk, ChatWSSourcesResponse):
                chunk.parse_sources(sources=self.sources)
                return ""
            else:
                return ""
        except StopIteration:
            raise


class Chat(BaseModel):
    id: str
    name: str
    user_id: str
    date_created: datetime
    last_updated: datetime

    @computed_field
    @property
    def interactions(self) -> list[ChatInteraction]:
        if not self._loaded:
            self.reload_from_server()
        return self._interactions

    _api_connection: BigdataConnectionProtocol
    _interactions: list[ChatInteraction]
    _formatter: InlineAttributionFormatter
    _loaded: bool

    def __init__(
        self,
        _api_connection: BigdataConnectionProtocol,
        _interactions: Optional[list[ChatInteraction]],
        _formatter: Optional[InlineAttributionFormatter],
        _loaded: bool = False,
        **values,
    ):
        super().__init__(**values)
        self._api_connection = _api_connection
        self._loaded = _loaded

        if _interactions is not None:
            self._interactions = _interactions

        self._formatter = _formatter or DefaultFormatter()

    def ask(
        self,
        question: str,
        *,
        scope: Optional[ChatScope] = None,
        source_filter: Optional[Union[list[Source], list[str]]] = None,
        formatter: Optional[InlineAttributionFormatter] = None,
        streaming: bool = False,
    ) -> Union[ChatInteraction, StreamingChatInteraction]:
        """Ask a question in the chat"""
        self._validate_question(question)
        formatter = formatter or self._formatter
        chat_scope = scope.value if scope else None

        # Convert source_filter if it's a list of Source objects
        if source_filter:
            for idx, source in enumerate(source_filter):
                if isinstance(source, Source):
                    source_filter[idx] = source.id

        if streaming:
            now = datetime.utcnow()
            return StreamingChatInteraction(
                question=question,
                answer="",
                interaction_timestamp=now.isoformat() + "Z",
                date_created=now,
                last_updated=now,
                scope=chat_scope,
                source_filter=source_filter,
                _chat=self,
                _formatter=formatter,
            )

        response = self._api_connection.ask_chat(
            self.id,
            question,
            scope=chat_scope,
            source_filter=source_filter,
        )

        from bigdata_client.api.chat import (
            ChatWSAuditTraceResponse,
            ChatWSCompleteEnrichedResponse,
            ChatWSSourcesResponse,
        )

        sources = []
        for chunk in response:
            if isinstance(chunk, str):
                pass
            elif isinstance(chunk, ChatWSCompleteEnrichedResponse):
                complete_message = chunk
            elif isinstance(chunk, ChatWSAuditTraceResponse):
                new_sources = chunk.to_chat_source()
                sources = deduplicate_sources(sources, new_sources)
            elif isinstance(chunk, ChatWSSourcesResponse):
                chunk.parse_sources(sources=sources)

        interation = handle_ws_chat_response(
            chat=self,
            question=question,
            scope=scope,
            complete_enriched_message=complete_message,  # noqa
            sources=sources,
            formatter=formatter,
        )

        return interation

    def reload_from_server(self):
        chat = self._api_connection.get_chat(self.id).to_chat_model(
            self._api_connection, self._formatter
        )
        self.name = chat.name
        self.user_id = chat.user_id
        self.date_created = chat.date_created
        self.last_updated = chat.last_updated
        self._interactions = chat._interactions
        self._loaded = True

    def delete(self):
        """Delete the chat"""
        self._api_connection.delete_chat(self.id)

    @staticmethod
    def _validate_question(question: str):
        message_length = len(question or "")
        if not (MIN_CHAT_QUESTION_LENGTH < message_length < MAX_CHAT_QUESTION_LENGTH):
            raise BigdataClientChatInvalidQuestion(message_length)

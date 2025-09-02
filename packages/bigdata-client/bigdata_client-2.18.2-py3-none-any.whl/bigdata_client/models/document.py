from enum import Enum
from functools import cached_property
from typing import Optional

from pydantic import BaseModel

from bigdata_client.api.knowledge_graph import ByIdsRequest
from bigdata_client.connection_protocol import BigdataConnectionProtocol
from bigdata_client.query_type import QueryType


class DocumentSource(BaseModel):
    """The source of a document"""

    key: str
    name: str
    rank: int


class DocumentScope(Enum):
    """
    The type of the document.
    """

    NEWS = "news"
    FILINGS = "filings"
    TRANSCRIPTS = "transcripts"
    FILES = "files"


class DocumentSentenceEntity(BaseModel):
    """
    A detection instance of an entity in a sentence
    """

    key: str
    start: int
    end: int
    query_type: QueryType


class DocumentSentence(BaseModel):
    paragraph: int
    sentence: int


class DocumentChunk(BaseModel):
    """
    A chunk of text representing a contextual unit within the document
    """

    text: str
    chunk: int
    entities: list[DocumentSentenceEntity]
    sentences: list[DocumentSentence]
    relevance: float
    sentiment: float
    section_metadata: Optional[list[str]]
    speaker: Optional[str]

    # Keeps track of the connection to Bigdata
    _api: BigdataConnectionProtocol

    def __init__(self, **data):
        super().__init__(**data)
        if "_api" in data:
            self._api = data["_api"]

    @cached_property
    def resolved_speaker(self):
        if not self.speaker:
            return None

        by_ids_results = self._api.by_ids(
            ByIdsRequest.model_validate(
                [{"key": self.speaker, "queryType": QueryType.ENTITY}]
            )
        )
        speaker_entity = by_ids_results.root.get(self.speaker)
        return speaker_entity.name if speaker_entity else None

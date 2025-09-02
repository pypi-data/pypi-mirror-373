import datetime
from contextlib import suppress
from functools import cached_property
from typing import ForwardRef, Optional

from pydantic import BaseModel

from bigdata_client.api.knowledge_graph import ByIdsRequest
from bigdata_client.api.search import ChunkedDocumentResponse
from bigdata_client.connection_protocol import BigdataConnectionProtocol
from bigdata_client.models.advanced_search_query import TranscriptTypes
from bigdata_client.models.document import (
    DocumentChunk,
    DocumentScope,
    DocumentSentence,
    DocumentSentenceEntity,
    DocumentSource,
)
from bigdata_client.query_type import QueryType

Document = ForwardRef("Document")


class Document(BaseModel):
    """A document object"""

    id: str
    headline: str
    sentiment: float
    document_scope: DocumentScope
    source: DocumentSource
    timestamp: datetime.datetime
    chunks: list[DocumentChunk]
    language: str

    # Keeps track of the connection to Bigdata
    _api: BigdataConnectionProtocol

    cluster: Optional[list[Document]] = None
    reporting_period: Optional[list[str]] = None
    document_type: Optional[str] = None
    reporting_entities: Optional[list[str]] = None
    url: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context):
        """All returned timestamps are in UTC"""
        self.timestamp = self.timestamp.replace(tzinfo=datetime.timezone.utc)

    def __init__(self, **data):
        super().__init__(**data)
        if "_api" in data:
            self._api = data["_api"]

    @cached_property
    def resolved_reporting_entities(self):
        if not self.reporting_entities:
            return None

        by_ids_results = self._api.by_ids(
            ByIdsRequest.model_validate(
                (
                    {"key": entity_id, "queryType": QueryType.ENTITY}
                    for entity_id in self.reporting_entities
                )
            )
        )
        return [entity.name for entity in by_ids_results.root.values()]

    @classmethod
    def from_response(
        cls, response: ChunkedDocumentResponse, api: BigdataConnectionProtocol
    ) -> "Document":
        source = DocumentSource(
            key=response.source_key,
            name=response.source_name,
            rank=response.source_rank,
        )
        chunks = [
            DocumentChunk(
                text=s.text,
                chunk=s.cnum,
                entities=[
                    DocumentSentenceEntity(
                        key=e.key, start=e.start, end=e.end, query_type=e.queryType
                    )
                    for e in s.entities
                ],
                sentences=[
                    DocumentSentence(paragraph=e.pnum, sentence=e.snum)
                    for e in s.sentences
                ],
                relevance=s.relevance,
                sentiment=s.sentiment / 100.0,
                section_metadata=s.section_metadata,
                speaker=s.speaker,
                _api=api,
            )
            for s in response.chunks
        ]

        return cls(
            id=response.id,
            headline=response.headline,
            sentiment=response.sentiment / 100.0,
            document_scope=response.document_scope,
            document_type=response.document_type,
            source=source,
            timestamp=response.timestamp,
            chunks=chunks,
            language=response.language,
            reporting_entities=response.reporting_entities,
            cluster=(
                [
                    Document.from_response(doc_chunk, api)
                    for doc_chunk in response.cluster
                ]
                if response.cluster
                else None
            ),
            _api=api,
            url=response.url,
        )

    def download_annotated_dict(self) -> dict:
        """Returns annotated document as a dictionary."""
        return self._api.download_annotated_dict(self.id)

    def __str__(self) -> str:
        """
        Returns a string representation of the document.
        """

        def _format_section(section_name: str, value: str, left_padding=50):
            section_name = str(section_name)
            value = str(value)
            dynamic_padding = (
                left_padding - len(section_name)
                if left_padding > len(section_name)
                else 0
            )
            padded_value = value.rjust(dynamic_padding)
            return f"{section_name}: {padded_value}"

        def _get_document_type_repr():
            with suppress(ValueError):
                TranscriptTypes(self.document_type)
                return _format_section("Document Type", self.document_type.title())

        def _get_chunk_repr(chunk_: DocumentChunk):
            section = (
                _format_section("Section", str(chunk_.section_metadata))
                if chunk_.section_metadata
                else None
            )
            speaker = (
                _format_section("Speaker", chunk_.resolved_speaker)
                if chunk_.speaker and chunk_.resolved_speaker
                else None
            )
            return section, speaker, f"*{chunk_.text}\n--"

        chunks_repr = [
            chunk_row_repr
            for chunk in self.chunks
            for chunk_row_repr in _get_chunk_repr(chunk)
        ]

        reporting_entities_repr = (
            _format_section("Reporting Entity", str(self.resolved_reporting_entities))
            if self.reporting_entities
            else None
        )
        document_id = _format_section("Document ID", self.id)
        timestamp = _format_section(
            "Timestamp", self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        )
        scope = _format_section("Scope", self.document_scope.value.title())

        document_type = _get_document_type_repr()
        source = _format_section(
            "Source (Rank)", f"{self.source.name} ({self.source.rank})"
        )
        title = _format_section("Title", self.headline)
        document_url = _format_section("Document Url", self.url) if self.url else None
        language = _format_section("Language", self.language)
        sentiment = _format_section("Sentiment", str(self.sentiment))
        chunks_separator = "====Sentence matches===="

        return "\n".join(
            filter(
                None,
                (
                    document_id,
                    timestamp,
                    scope,
                    document_type,
                    source,
                    title,
                    document_url,
                    reporting_entities_repr,
                    language,
                    sentiment,
                    chunks_separator,
                    *chunks_repr,
                ),
            )
        )


Document.model_rebuild()

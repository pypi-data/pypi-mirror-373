"""
Models, classes and functions to handle the interaction with the API for the
search functionality.
"""

import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

from bigdata_client.models.document import DocumentScope
from bigdata_client.models.entities import (
    Company,
    Concept,
    Facility,
    Landmark,
    Organization,
    OrganizationType,
    Person,
    Place,
    Product,
    ProductType,
)
from bigdata_client.models.languages import Language
from bigdata_client.models.search import (
    DocumentType,
    Expression,
    Ranking,
    SearchChain,
    SearchPaginationByCursor,
    SearchPaginationByOffset,
    SortBy,
)
from bigdata_client.models.sharing import SharePermission
from bigdata_client.models.sources import Source
from bigdata_client.models.topics import Topic
from bigdata_client.query_type import QueryType
from bigdata_client.settings import settings

# Save a search


class SaveSearchQueryRequest(BaseModel):
    """Model to represent the "query" attribute of a request to save a search"""

    expression: Expression
    scope: DocumentType = Field(default=DocumentType.ALL)
    sort: SortBy = Field(default=SortBy.RELEVANCE)
    ranking: Ranking = Field(default=settings.LLM.RANKING)
    search_chain: Optional[SearchChain] = Field(alias="searchChain", default=None)
    hybrid: bool = settings.LLM.USE_HYBRID
    # The date expression neds a type=ExpressionTypes.DATE
    # the value is coming from date_range.to_expression()
    date: Optional[list[Expression]] = None
    rerank_threshold: Optional[float] = Field(None, alias="rerankThreshold")

    model_config = ConfigDict(populate_by_name=True)


class SaveSearchRequest(BaseModel):
    """Model to represent the request to create a search"""

    name: str
    query: SaveSearchQueryRequest
    save_status: Literal["saved"] = Field(default="saved", alias="saveStatus")


class UpdateSearchRequest(BaseModel):
    """Model to represent the request to update a search"""

    name: Optional[str]
    query: SaveSearchQueryRequest


# Share a saved search


class UserQueryShareCompanyContext(BaseModel):
    permission: SharePermission


class UserQueryShareUserContext(BaseModel):
    id: str
    permission: SharePermission


class UserQueryShareContext(BaseModel):
    company: UserQueryShareCompanyContext
    users: list[UserQueryShareUserContext]


class ShareSavedSearchRequest(UserQueryShareContext): ...


# Get saved searches


class SavedSearchQueryResponse(BaseModel):
    """
    Model to represent the "query" attribute of a response from getting a saved
    search.
    """

    expression: Expression
    scope: DocumentType = Field(default=DocumentType.ALL)
    sort: SortBy = Field(default=SortBy.RELEVANCE)
    ranking: Ranking = Field(default=settings.LLM.RANKING)
    hybrid: bool = settings.LLM.USE_HYBRID
    date: Optional[list[Expression]] = None
    rerank_threshold: Optional[float] = Field(None, alias="rerankThreshold")
    rerank_freshness_weight: Optional[float] = Field(
        None, alias="rerankFreshnessWeight"
    )


class SavedSearchResponse(BaseModel):
    """Model to represent the response from getting a saved search"""

    id: str
    name: str
    query: SavedSearchQueryResponse
    save_status: Literal["saved"] = Field(default="saved", alias="saveStatus")
    shared: UserQueryShareContext
    # TODO: Add dateCreated, lastExecuted, lastUpdated, owner, ownerName, permissions


# Delete a saved search


class DeleteSavedSearchResponse(BaseModel):
    """Model to represent the response from deleting a saved search"""

    id: str


# List saved searches


class ListSavedSearchResponse(BaseModel):
    """
    Part of the response from listing saved searches. It represents a single
    saved search, without all the details.
    """

    id: str
    name: str
    owner: str
    save_status: Literal["saved"] = Field(default="saved", alias="saveStatus")
    last_executed: datetime.datetime = Field(alias="lastExecuted")
    date_created: datetime.datetime = Field(alias="dateCreated")
    last_updated: datetime.datetime = Field(alias="lastUpdated")
    pinned: bool
    owner_name: str = Field(alias="ownerName")
    shared: dict

    @model_validator(mode="after")
    def set_tz(self):
        self.last_executed = self.last_executed.replace(tzinfo=datetime.timezone.utc)
        self.date_created = self.date_created.replace(tzinfo=datetime.timezone.utc)
        self.last_updated = self.last_updated.replace(tzinfo=datetime.timezone.utc)

        return self


class ListSavedSearchesResponse(BaseModel):
    """Model to represent the response from listing saved searches"""

    results: list[ListSavedSearchResponse]


# Run a search


class QueryChunksRequest(BaseModel):
    """Model to represent a request to run a search"""

    expression: Expression
    scope: DocumentType = Field(default=DocumentType.ALL)
    sort: SortBy = Field(default=SortBy.RELEVANCE)
    ranking: Ranking = Field(default=settings.LLM.RANKING)
    pagination: Union[SearchPaginationByCursor, SearchPaginationByOffset]
    search_chain: Optional[SearchChain] = Field(alias="searchChain", default=None)
    hybrid: bool = settings.LLM.USE_HYBRID
    rerank_threshold: Optional[float] = Field(alias="rerankThreshold", default=None)
    model_config = ConfigDict(populate_by_name=True)


class ChunkedDocumentResponse(BaseModel):
    """
    Helper class to parse the response from the API.
    It should be used only internally to parse the JSON response from the API,
    and not passed around.
    """

    model_config = ConfigDict(populate_by_name=True)

    headline: str = Field(validation_alias="hd")
    id: str
    sentiment: float = Field(validation_alias="sent")
    document_scope: DocumentScope = Field(validation_alias="documentScope")
    timestamp: datetime.datetime = Field(validation_alias="ts")
    document_type: Optional[str] = Field(default=None, validation_alias="documentType")
    source_key: str = Field(validation_alias="srcKey")
    source_name: str = Field(validation_alias="srcName")
    reporting_entities: Optional[list[str]] = Field(
        default=None, alias="reportingEntities"
    )
    cluster: Optional[list["ChunkedDocumentResponse"]] = None

    source_rank: int = Field(validation_alias="sourceRank")
    language: str
    url: Optional[str] = None

    class ChunkedDocumentResponseSentence(BaseModel):
        text: str
        cnum: int
        relevance: float
        sentiment: float
        section_metadata: Optional[list[str]] = Field(
            default=None, alias="sectionMetadata"
        )
        speaker: Optional[str] = None

        class DocumentResponseEntity(BaseModel):
            key: str
            start: int
            end: int
            queryType: QueryType

        entities: list[DocumentResponseEntity]

        class DocumentResponseSentence(BaseModel):
            pnum: int
            snum: int

        sentences: list[DocumentResponseSentence]

    chunks: list[ChunkedDocumentResponseSentence]


class QueryChunksResponse(BaseModel):
    """Model to represent the Backend response from running a search"""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    count: int
    document_count: int
    coverage: dict  # Not worth to model this yet
    timing: dict  # Not worth to model this yet
    stories: list[ChunkedDocumentResponse]
    next_cursor: Optional[int] = None
    chunks_count: int


# Comentions


class DiscoveryPanelRequest(BaseModel):
    """Model to represent a request to get comentions"""

    expression: Expression
    scope: DocumentType = Field(default=DocumentType.ALL)
    sort: SortBy = Field(default=SortBy.RELEVANCE)
    ranking: Ranking = Field(default=settings.LLM.RANKING)
    search_chain: Optional[SearchChain] = Field(alias="searchChain", default=None)
    hybrid: bool = settings.LLM.USE_HYBRID


class DiscoveryPanelResponse(BaseModel):
    """Model to represent the response from getting comentions"""

    companies: list[Company] = Field(default=[])
    concepts: list[Concept] = Field(default=[])
    languages: list[Language] = Field(default=[])
    organizations: list[Union[Organization, OrganizationType]] = Field(default=[])
    places: list[Union[Place, Facility, Landmark]] = Field(default=[])
    products: list[Union[Product, ProductType]] = Field(default=[])
    sources: list[Source] = Field(default=[])
    topics: list[Topic] = Field(default=[])
    people: list[Person] = Field(default=[])

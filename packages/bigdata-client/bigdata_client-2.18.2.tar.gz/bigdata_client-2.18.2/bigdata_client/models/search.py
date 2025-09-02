from typing import Optional, Union

from pydantic import BaseModel, Field, model_validator

from bigdata_client.constants import SEARCH_PAGE_DEFAULT_SIZE
from bigdata_client.enum_utils import StrEnum

OLDEST_RECORDS = 2000


class ExpressionOperation(StrEnum):
    IN = "in"
    ALL = "all"
    GREATER_THAN = "greater-than"
    LOWER_THAN = "lower-than"
    BETWEEN = "between"


class ExpressionTypes(StrEnum):
    AND = "and"
    CONTENT_TYPE = "content_type"
    DATE = "date"
    DOCUMENT = "document"
    RP_DOCUMENT_SUBTYPE = "rp_document_subtype"
    ENTITY = "entity"
    KEYWORD = "keyword"
    LANGUAGE = "language"
    NOT = "not"
    OR = "or"
    REPORTING_ENTITIES = "reporting_entities"
    REPORTING_PERIOD = "reporting_period"
    SECTION_METADATA = "section_metadata"
    SENTIMENT_RANGE = "sentiment_range"
    SIMILARITY = "similarity"
    SOURCE = "source"
    TAGS = "tags"
    TOPIC = "rp_topic"
    DOCUMENT_VERSION = "rp_document_version"


class FiscalQuarterValidator(BaseModel):
    value: int = Field(ge=1, le=4)

    def get_string(self):
        return f"FQ{self.value}"


class SentimentRangeValidator(BaseModel):
    range_start: float = Field(ge=-1, le=1)
    range_end: float = Field(ge=-1, le=1)

    @model_validator(mode="after")
    def validate_range(self):
        if self.range_start > self.range_end:
            raise ValueError(
                "First element in the interval must be greater than the second one "
                f"but received: [{self.range_start},{self.range_end}]"
            )
        return self


class FiscalYearValidator(BaseModel):
    value: int = Field(ge=OLDEST_RECORDS)

    def get_string(self):
        return f"{self.value}FY"


class Expression(BaseModel):
    type: ExpressionTypes
    value: Union[list[Union[str, float, "Expression"]], str, float, "Expression"]
    operation: Optional[ExpressionOperation] = None

    @classmethod
    def new(cls, etype: ExpressionTypes, values: Optional[list[str]]) -> "Expression":
        if not values:
            return None
        return cls(type=etype, operation=ExpressionOperation.IN, value=values)


class DocumentType(StrEnum):
    ALL = "all"
    FILINGS = "filings"
    TRANSCRIPTS = "transcripts"
    NEWS = "news"
    FILES = "files"


class SortBy(StrEnum):
    """Defines the order of the search results"""

    RELEVANCE = "relevance"
    DATE = "date"
    DATE_ASC = "date_asc"


class Ranking(StrEnum):
    STABLE = "stable"
    EXPERIMENTAL = "experimental"
    SIMILARITY = "similarity"


class SearchChain(StrEnum):
    DEDUPLICATION = "deduplication"
    ENRICHER = "enricher"  # NO LONGER USED
    DEFAULT = "default"  # NO LONGER USED?
    CLUSTERING = "clustering"
    CLUSTERING_RERANK = "clustering-rerank"


class SearchPaginationByCursor(BaseModel):

    limit: int = Field(default=SEARCH_PAGE_DEFAULT_SIZE, gt=0, lt=1001)
    cursor: int = Field(default=1, gt=0)


class SearchPaginationByOffset(BaseModel):

    limit: int = Field(default=SEARCH_PAGE_DEFAULT_SIZE, gt=0)
    offset: int = Field(default=0, ge=0)
